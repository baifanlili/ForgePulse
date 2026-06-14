import json
import os
from typing import Any
from uuid import uuid4

import paho.mqtt.client as mqtt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.db import db_cursor

router = APIRouter()


class EdgeCommandRequest(BaseModel):
    command_type: str = Field(pattern="^(pause|resume|set_interval|inject_fault)$")
    parameters: dict[str, Any] = Field(default_factory=dict)
    operator: str = "demo-operator"


def env(name: str, fallback: str) -> str:
    return os.getenv(name, fallback)


def mqtt_port() -> int:
    return int(env("MQTT_PORT", "1883"))


def ensure_edge_commands_table() -> None:
    with db_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS edge_commands (
                id BIGSERIAL PRIMARY KEY,
                command_id VARCHAR(64) NOT NULL UNIQUE,
                gateway_id VARCHAR(64) NOT NULL,
                command_type VARCHAR(64) NOT NULL,
                parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
                status VARCHAR(32) NOT NULL DEFAULT 'published',
                operator VARCHAR(128) NOT NULL DEFAULT 'demo-operator',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                published_at TIMESTAMPTZ
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_edge_commands_gateway_created
            ON edge_commands (gateway_id, created_at DESC)
            """
        )


def publish_command(gateway_id: str, payload: dict[str, Any]) -> None:
    topic_template = env("MQTT_COMMAND_TOPIC_TEMPLATE", "forgepulse/commands/{gateway_id}")
    topic = topic_template.format(gateway_id=gateway_id)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"forgepulse-api-{uuid4().hex[:8]}")
    client.connect(env("MQTT_HOST", "mqtt"), mqtt_port(), keepalive=10)
    result = client.publish(topic, json.dumps(payload, ensure_ascii=False), qos=1)
    result.wait_for_publish(timeout=5)
    client.disconnect()
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError(f"MQTT publish failed: {result.rc}")


@router.get("/gateways")
def list_gateways() -> list[dict[str, Any]]:
    ensure_edge_commands_table()
    with db_cursor() as cur:
        cur.execute(
            """
            WITH gateway_points AS (
                SELECT
                    time,
                    tags,
                    tags->>'gateway_id' AS gateway_id
                FROM telemetry_points
                WHERE tags ? 'gateway_id'
            ),
            latest AS (
                SELECT DISTINCT ON (gateway_id)
                    gateway_id,
                    tags->>'line_id' AS line_id,
                    time AS latest_seen_at,
                    (tags->>'sequence')::bigint AS latest_sequence,
                    (tags->>'sample_period_ms')::integer AS sample_period_ms,
                    tags->>'quality' AS latest_quality,
                    tags->>'status_reason' AS latest_status_reason
                FROM gateway_points
                ORDER BY gateway_id, time DESC
            ),
            counts AS (
                SELECT
                    gateway_id,
                    COUNT(*) AS telemetry_point_count,
                    COUNT(*) FILTER (WHERE tags->>'quality' = 'degraded') AS degraded_point_count
                FROM gateway_points
                GROUP BY gateway_id
            )
            SELECT
                latest.gateway_id,
                latest.line_id,
                latest.latest_seen_at,
                latest.latest_sequence,
                latest.sample_period_ms,
                counts.telemetry_point_count,
                counts.degraded_point_count,
                latest.latest_quality,
                latest.latest_status_reason
            FROM latest
            JOIN counts ON counts.gateway_id = latest.gateway_id
            ORDER BY latest.latest_seen_at DESC
            """
        )
        gateways = list(cur.fetchall())

        cur.execute(
            """
            SELECT DISTINCT ON (gateway_id)
                gateway_id,
                command_id,
                command_type,
                parameters,
                status,
                operator,
                created_at,
                published_at
            FROM edge_commands
            ORDER BY gateway_id, created_at DESC
            """
        )
        latest_commands = {row["gateway_id"]: row for row in cur.fetchall()}

    for gateway in gateways:
        gateway["latest_command"] = latest_commands.get(gateway["gateway_id"])
    return gateways


@router.get("/gateways/{gateway_id}/commands")
def list_gateway_commands(gateway_id: str) -> list[dict[str, Any]]:
    ensure_edge_commands_table()
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                command_id,
                gateway_id,
                command_type,
                parameters,
                status,
                operator,
                created_at,
                published_at
            FROM edge_commands
            WHERE gateway_id = %s
            ORDER BY created_at DESC
            LIMIT 30
            """,
            (gateway_id,),
        )
        return list(cur.fetchall())


@router.post("/gateways/{gateway_id}/commands")
def create_gateway_command(gateway_id: str, body: EdgeCommandRequest) -> dict[str, Any]:
    ensure_edge_commands_table()
    command_id = f"CMD-{uuid4().hex[:12].upper()}"
    payload = {
        "command_id": command_id,
        "gateway_id": gateway_id,
        "command_type": body.command_type,
        "parameters": body.parameters,
        "operator": body.operator,
    }

    try:
        publish_command(gateway_id, payload)
    except Exception as exc:  # noqa: BLE001 - surface command publish failure to UI
        raise HTTPException(status_code=502, detail=f"Command publish failed: {exc}") from exc

    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO edge_commands (
                command_id,
                gateway_id,
                command_type,
                parameters,
                status,
                operator,
                published_at
            )
            VALUES (%s, %s, %s, %s::jsonb, 'published', %s, NOW())
            RETURNING
                command_id,
                gateway_id,
                command_type,
                parameters,
                status,
                operator,
                created_at,
                published_at
            """,
            (command_id, gateway_id, body.command_type, json.dumps(body.parameters), body.operator),
        )
        command = cur.fetchone()
    return command
