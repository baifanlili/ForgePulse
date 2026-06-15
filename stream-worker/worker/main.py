import json
import os
import signal
import time
from datetime import UTC, datetime
from threading import Lock, Thread
from typing import Any

import paho.mqtt.client as mqtt
import psycopg
import psycopg.rows

from worker.rules import RuleEngine

MQTT_TOPIC = os.getenv("MQTT_TELEMETRY_TOPIC", "forgepulse/telemetry")
HEARTBEAT_TIMEOUT_SECONDS = int(os.getenv("HEARTBEAT_TIMEOUT_SECONDS", "120"))
HEARTBEAT_CHECK_INTERVAL = int(os.getenv("HEARTBEAT_CHECK_INTERVAL", "30"))
WORKER_HEARTBEAT_INTERVAL = int(os.getenv("WORKER_HEARTBEAT_INTERVAL", "10"))
WORKER_ID = os.getenv("WORKER_ID", "stream-worker-01")
RUNNING = True

_stats_lock = Lock()
_stats = {"telemetry_processed": 0, "alarms_triggered": 0}


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
            return psycopg.connect(database_url(), row_factory=psycopg.rows.dict_row)
        except Exception as exc:
            last_error = exc
            print(f"Database connection failed, retry {attempt}/{retries}: {exc}", flush=True)
            time.sleep(2)
    raise RuntimeError("Unable to connect to PostgreSQL") from last_error


def ensure_worker_heartbeats_table(conn: psycopg.Connection[Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS worker_heartbeats (
                id BIGSERIAL PRIMARY KEY,
                worker_id VARCHAR(64) NOT NULL,
                last_heartbeat_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                status VARCHAR(32) NOT NULL DEFAULT 'healthy',
                telemetry_processed BIGINT NOT NULL DEFAULT 0,
                alarms_triggered BIGINT NOT NULL DEFAULT 0,
                detail TEXT,
                recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_worker_heartbeats_worker_time
            ON worker_heartbeats (worker_id, last_heartbeat_at DESC)
            """
        )
    conn.commit()


def clear_heartbeat_alarm(cur: psycopg.Cursor[Any], device_code: str, timestamp: datetime) -> None:
    alarm_code = f"HB-{device_code}-TIMEOUT".upper()
    cur.execute(
        """
        UPDATE alarms
        SET status = 'cleared',
            cleared_at = %s,
            cleared_by = 'system'
        WHERE alarm_code = %s
          AND status IN ('active', 'acknowledged')
        RETURNING alarm_code
        """,
        (timestamp, alarm_code),
    )
    if cur.fetchone() is None:
        return

    cur.execute(
        """
        INSERT INTO alarm_events (alarm_code, event_type, operator, note, created_at)
        VALUES (%s, 'cleared', 'system', %s, %s)
        """,
        (alarm_code, "设备心跳已恢复，自动关闭心跳超时告警", timestamp),
    )


def upsert_alarm(
    cur: psycopg.Cursor[Any],
    rules: RuleEngine,
    device_code: str,
    metric_name: str,
    value: float,
    timestamp: datetime,
) -> None:
    triggered = rules.evaluate(metric_name, value)
    alarm_code = f"RT-{device_code}-{metric_name}".upper()

    if triggered:
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
                acknowledged_at,
                acknowledged_by,
                cleared_at,
                cleared_by
            )
            VALUES (%s, %s, %s, %s, %s, 'active', %s, NULL, NULL, NULL, NULL)
            ON CONFLICT (alarm_code) DO UPDATE SET
                severity = EXCLUDED.severity,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                status = 'active',
                started_at = COALESCE(alarms.started_at, EXCLUDED.started_at),
                acknowledged_at = NULL,
                acknowledged_by = NULL,
                cleared_at = NULL,
                cleared_by = NULL
            """,
            (alarm_code, device_code, triggered.severity, triggered.title, triggered.description, timestamp),
        )
        cur.execute(
            """
            INSERT INTO alarm_events (alarm_code, event_type, operator, note, created_at)
            VALUES (%s, 'created', 'system', %s, %s)
            """,
            (alarm_code, f"{metric_name}={value:.2f} 超过阈值 {triggered.threshold:.2f}", timestamp),
        )
    elif rules.clearance_check(metric_name, value):
        cur.execute(
            """
            UPDATE alarms
            SET status = 'cleared',
                cleared_at = %s,
                cleared_by = 'system'
            WHERE alarm_code = %s
              AND status IN ('active', 'acknowledged')
            RETURNING alarm_code
            """,
            (timestamp, alarm_code),
        )
        if cur.fetchone() is not None:
            rule = rules.rules.get(metric_name)
            cur.execute(
                """
                INSERT INTO alarm_events (alarm_code, event_type, operator, note, created_at)
                VALUES (%s, 'cleared', 'system', %s, %s)
                """,
                (alarm_code, f"{metric_name}={value:.2f} 已恢复到阈值 {rule.threshold:.2f} 以下", timestamp),
            )


def persist_message(
    conn: psycopg.Connection[Any],
    rules: RuleEngine,
    message: dict[str, Any],
) -> None:
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
        clear_heartbeat_alarm(cur, device_code, timestamp)

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
            upsert_alarm(cur, rules, device_code, metric_name, value, timestamp)

    conn.commit()
    with _stats_lock:
        _stats["telemetry_processed"] += 1


def check_heartbeats(conn: psycopg.Connection[Any], timeout_seconds: int) -> None:
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE devices
                SET status = 'offline',
                    updated_at = NOW()
                WHERE status != 'offline'
                  AND last_heartbeat_at < NOW() - (%s * INTERVAL '1 second')
                RETURNING device_code, device_name, last_heartbeat_at
                """,
                (timeout_seconds,),
            )
            expired = cur.fetchall()
            for row in expired:
                device_code = row["device_code"]
                device_name = row["device_name"]
                last_hb = row["last_heartbeat_at"]
                alarm_code = f"HB-{device_code}-TIMEOUT".upper()
                note = f"设备 {device_name} 最后心跳 {last_hb}，已超过 {timeout_seconds} 秒，自动置为 offline"
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
                        acknowledged_at,
                        acknowledged_by,
                        cleared_at,
                        cleared_by
                    )
                    VALUES (%s, %s, 'warning', '心跳超时', %s, 'active', NOW(), NULL, NULL, NULL, NULL)
                    ON CONFLICT (alarm_code) DO UPDATE SET
                        description = EXCLUDED.description,
                        started_at = alarms.started_at
                    """,
                    (alarm_code, device_code, note),
                )
                cur.execute(
                    """
                    INSERT INTO alarm_events (alarm_code, event_type, operator, note, created_at)
                    VALUES (%s, 'created', 'system', %s, NOW())
                    """,
                    (alarm_code, note),
                )
                print(f"Device {device_code} marked offline (heartbeat timeout)", flush=True)
        conn.commit()
        if expired:
            with _stats_lock:
                _stats["alarms_triggered"] += len(expired)
    except Exception as exc:
        conn.rollback()
        print(f"Heartbeat check failed: {exc}", flush=True)


def report_health(conn: psycopg.Connection[Any]) -> None:
    try:
        with _stats_lock:
            telemetry_processed = _stats["telemetry_processed"]
            alarms_triggered = _stats["alarms_triggered"]
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO worker_heartbeats (worker_id, status, telemetry_processed, alarms_triggered, detail)
                VALUES (%s, 'healthy', %s, %s, %s)
                """,
                (
                    WORKER_ID,
                    telemetry_processed,
                    alarms_triggered,
                    f"MQTT 订阅 {MQTT_TOPIC}，已处理 {telemetry_processed} 条遥测",
                ),
            )
            cur.execute(
                """
                DELETE FROM worker_heartbeats
                WHERE worker_id = %s
                  AND recorded_at < NOW() - INTERVAL '24 hours'
                """,
                (WORKER_ID,),
            )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f"Health report failed: {exc}", flush=True)


def health_reporter() -> None:
    conn = connect_db()
    ensure_worker_heartbeats_table(conn)
    while RUNNING:
        time.sleep(WORKER_HEARTBEAT_INTERVAL)
        if not RUNNING:
            break
        report_health(conn)
    conn.close()


def heartbeat_monitor() -> None:
    conn = connect_db()
    while RUNNING:
        time.sleep(HEARTBEAT_CHECK_INTERVAL)
        if not RUNNING:
            break
        check_heartbeats(conn, HEARTBEAT_TIMEOUT_SECONDS)
    conn.close()


def main() -> None:
    mqtt_host = env("MQTT_HOST", "mqtt")
    mqtt_port = int(env("MQTT_PORT", "1883"))
    conn = connect_db()
    rules = RuleEngine.from_env()

    def stop(_signum: int, _frame: Any) -> None:
        global RUNNING
        RUNNING = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    monitor_thread = Thread(target=heartbeat_monitor, daemon=True)
    monitor_thread.start()

    health_thread = Thread(target=health_reporter, daemon=True)
    health_thread.start()

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
            persist_message(conn, rules, payload)
            print(f"Persisted telemetry from {payload['device_code']}", flush=True)
        except Exception as exc:
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
        except Exception as exc:
            print(f"MQTT loop failed: {exc}", flush=True)
            time.sleep(3)

    conn.close()


if __name__ == "__main__":
    main()
