from typing import Any

from fastapi import APIRouter

from app.core.db import db_cursor

router = APIRouter()


@router.get("/overview")
def system_overview() -> dict[str, Any]:
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM devices")
        device_count = cur.fetchone()["count"]

        cur.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM devices
            GROUP BY status
            """
        )
        device_status = {row["status"]: row["count"] for row in cur.fetchall()}

        cur.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM alarms
            GROUP BY status
            """
        )
        alarm_status = {row["status"]: row["count"] for row in cur.fetchall()}

        cur.execute(
            """
            SELECT
                COUNT(*) AS telemetry_count,
                MAX(time) AS latest_telemetry_at,
                EXTRACT(EPOCH FROM (NOW() - MAX(time)))::integer AS telemetry_lag_seconds
            FROM telemetry_points
            """
        )
        telemetry = cur.fetchone()

        cur.execute(
            """
            SELECT
                device_code,
                MAX(time) AS latest_time,
                COUNT(*) AS point_count
            FROM telemetry_points
            WHERE time >= NOW() - INTERVAL '15 minutes'
            GROUP BY device_code
            ORDER BY latest_time DESC
            LIMIT 8
            """
        )
        recent_device_ingestion = list(cur.fetchall())

        cur.execute(
            """
            SELECT metric_name, COUNT(*) AS point_count
            FROM telemetry_points
            WHERE time >= NOW() - INTERVAL '15 minutes'
            GROUP BY metric_name
            ORDER BY point_count DESC, metric_name
            LIMIT 12
            """
        )
        metric_ingestion = list(cur.fetchall())

        cur.execute(
            """
            SELECT
                'devices' AS table_name,
                COUNT(*) AS row_count
            FROM devices
            UNION ALL
            SELECT 'telemetry_points', COUNT(*) FROM telemetry_points
            UNION ALL
            SELECT 'alarms', COUNT(*) FROM alarms
            UNION ALL
            SELECT 'alarm_events', COUNT(*) FROM alarm_events
            UNION ALL
            SELECT 'lots', COUNT(*) FROM lots
            UNION ALL
            SELECT 'wafer_yields', COUNT(*) FROM wafer_yields
            UNION ALL
            SELECT 'bin_counts', COUNT(*) FROM bin_counts
            UNION ALL
            SELECT 'spc_points', COUNT(*) FROM spc_points
            ORDER BY table_name
            """
        )
        table_counts = list(cur.fetchall())

    telemetry_lag = telemetry["telemetry_lag_seconds"]
    ingestion_status = "ok"
    if telemetry_lag is None:
        ingestion_status = "no_data"
    elif telemetry_lag > 120:
        ingestion_status = "stale"

    return {
        "services": [
            {"name": "platform-api", "status": "ok", "detail": "FastAPI 服务可用"},
            {"name": "postgres", "status": "ok", "detail": "数据库查询成功"},
            {"name": "stream-worker", "status": ingestion_status, "detail": "根据最新遥测延迟推断"},
            {"name": "edge-gateway", "status": ingestion_status, "detail": "根据 MQTT 入库数据推断"},
        ],
        "summary": {
            "device_count": device_count,
            "running_count": device_status.get("running", 0),
            "warning_count": device_status.get("warning", 0),
            "offline_count": device_status.get("offline", 0),
            "active_alarm_count": alarm_status.get("active", 0),
            "acknowledged_alarm_count": alarm_status.get("acknowledged", 0),
            "cleared_alarm_count": alarm_status.get("cleared", 0),
            "telemetry_count": telemetry["telemetry_count"],
            "latest_telemetry_at": telemetry["latest_telemetry_at"],
            "telemetry_lag_seconds": telemetry_lag,
        },
        "recent_device_ingestion": recent_device_ingestion,
        "metric_ingestion": metric_ingestion,
        "table_counts": table_counts,
    }
