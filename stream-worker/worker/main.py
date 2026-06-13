import json
import os
import signal
import time
from datetime import UTC, datetime
from typing import Any

import paho.mqtt.client as mqtt
import psycopg


MQTT_TOPIC = os.getenv("MQTT_TELEMETRY_TOPIC", "forgepulse/telemetry")
RUNNING = True


def env(name: str, fallback: str) -> str:
    return os.getenv(name, fallback)


def database_url() -> str:
    host = env("POSTGRES_HOST", "localhost")
    port = env("POSTGRES_PORT", "5432")
    db = env("POSTGRES_DB", "forgepulse")
    user = env("POSTGRES_USER", "forgepulse")
    password = env("POSTGRES_PASSWORD", "forgepulse")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(UTC)


def connect_db(retries: int = 30) -> psycopg.Connection[Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return psycopg.connect(database_url())
        except Exception as exc:  # noqa: BLE001 - startup retry should log any connection failure
            last_error = exc
            print(f"Database connection failed, retry {attempt}/{retries}: {exc}", flush=True)
            time.sleep(2)
    raise RuntimeError("Unable to connect to PostgreSQL") from last_error


def upsert_alarm(cur: psycopg.Cursor[Any], device_code: str, metric_name: str, value: float, timestamp: datetime) -> None:
    thresholds = {
        "temperature": (76.0, "腔体温度偏高", "设备温度超过阈值，请检查冷却与工艺状态。"),
        "pressure": (2.85, "压力波动偏高", "设备压力超过阈值，请检查气路与腔体状态。"),
    }
    if metric_name not in thresholds:
        return

    limit, title, description = thresholds[metric_name]
    alarm_code = f"RT-{device_code}-{metric_name}".upper()

    if value >= limit:
        cur.execute(
            """
            INSERT INTO alarms (
                alarm_code,
                device_code,
                severity,
                title,
                description,
                status,
                started_at,
                cleared_at
            )
            VALUES (%s, %s, %s, %s, %s, 'active', %s, NULL)
            ON CONFLICT (alarm_code) DO UPDATE SET
                severity = EXCLUDED.severity,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                status = 'active',
                started_at = COALESCE(alarms.started_at, EXCLUDED.started_at),
                cleared_at = NULL
            """,
            (alarm_code, device_code, "warning", title, description, timestamp),
        )
    else:
        cur.execute(
            """
            UPDATE alarms
            SET status = 'cleared',
                cleared_at = %s
            WHERE alarm_code = %s
              AND status = 'active'
            """,
            (timestamp, alarm_code),
        )


def persist_message(conn: psycopg.Connection[Any], message: dict[str, Any]) -> None:
    device_code = str(message["device_code"])
    status = str(message.get("status", "running"))
    timestamp = parse_timestamp(str(message["timestamp"]))
    metrics = message.get("metrics", {})
    payload = message.get("payload", {})

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO devices (
                device_code,
                device_name,
                device_type,
                area,
                line,
                status,
                last_heartbeat_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (device_code) DO UPDATE SET
                status = EXCLUDED.status,
                last_heartbeat_at = EXCLUDED.last_heartbeat_at,
                updated_at = NOW()
            """,
            (
                device_code,
                device_code,
                "Simulated Tool",
                "FAB-A",
                "Realtime",
                status,
                timestamp,
            ),
        )

        for metric_name, raw_value in metrics.items():
            value = float(raw_value)
            cur.execute(
                """
                INSERT INTO telemetry_points (
                    time,
                    device_code,
                    metric_name,
                    metric_value,
                    tags
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    timestamp,
                    device_code,
                    metric_name,
                    value,
                    json.dumps({"source": "mqtt", **payload}, ensure_ascii=False),
                ),
            )
            upsert_alarm(cur, device_code, metric_name, value, timestamp)

    conn.commit()


def main() -> None:
    mqtt_host = env("MQTT_HOST", "mqtt")
    mqtt_port = int(env("MQTT_PORT", "1883"))
    conn = connect_db()

    def stop(_signum: int, _frame: Any) -> None:
        global RUNNING
        RUNNING = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="forgepulse-stream-worker")

    def on_connect(
        _client: mqtt.Client,
        _userdata: Any,
        _flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        _properties: mqtt.Properties | None,
    ) -> None:
        if reason_code == 0:
            print(f"Connected to MQTT, subscribing {MQTT_TOPIC}", flush=True)
            _client.subscribe(MQTT_TOPIC)
        else:
            print(f"MQTT connection failed: {reason_code}", flush=True)

    def on_message(_client: mqtt.Client, _userdata: Any, msg: mqtt.MQTTMessage) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            persist_message(conn, payload)
            print(f"Persisted telemetry from {payload['device_code']}", flush=True)
        except Exception as exc:  # noqa: BLE001 - keep worker alive on malformed messages
            conn.rollback()
            print(f"Failed to process MQTT message: {exc}", flush=True)

    client.on_connect = on_connect
    client.on_message = on_message

    while RUNNING:
        try:
            print(f"Connecting MQTT {mqtt_host}:{mqtt_port}", flush=True)
            client.connect(mqtt_host, mqtt_port, keepalive=30)
            client.loop_start()
            while RUNNING:
                time.sleep(1)
            client.loop_stop()
            client.disconnect()
        except Exception as exc:  # noqa: BLE001 - long-running service should retry
            print(f"MQTT loop failed: {exc}", flush=True)
            time.sleep(3)

    conn.close()


if __name__ == "__main__":
    main()
