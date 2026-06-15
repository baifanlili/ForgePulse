from fastapi import APIRouter

from app.core.db import db_cursor
from app.schemas.system import (
    MetricIngestion,
    RecentDeviceIngestion,
    SystemOverview,
    SystemOverviewSummary,
    SystemServiceStatus,
    TableCount,
    WorkerHealth,
)

router = APIRouter()


def ensure_worker_heartbeats_table() -> None:
    with db_cursor() as cur:
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


def _worker_status() -> tuple[str, str, WorkerHealth | None]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                worker_id,
                status,
                last_heartbeat_at,
                telemetry_processed,
                alarms_triggered,
                EXTRACT(EPOCH FROM (NOW() - last_heartbeat_at))::integer AS lag_seconds
            FROM worker_heartbeats
            ORDER BY last_heartbeat_at DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        if row is None:
            return "no_data", "未找到 worker 心跳记录", None

        worker = WorkerHealth(
            worker_id=row["worker_id"],
            status=row["status"],
            last_heartbeat_at=row["last_heartbeat_at"],
            telemetry_processed=row["telemetry_processed"],
            alarms_triggered=row["alarms_triggered"],
            lag_seconds=row["lag_seconds"],
        )

        lag = row["lag_seconds"]
        if lag is None or lag > 60:
            return "stale", f"Worker 最后心跳 {lag or '未知'} 秒前", worker
        return "ok", f"Worker 正常，最后心跳 {lag} 秒前", worker


@router.get("/overview", response_model=SystemOverview)
def system_overview() -> SystemOverview:
    ensure_worker_heartbeats_table()

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
        recent_device_ingestion = [RecentDeviceIngestion(**row) for row in cur.fetchall()]

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
        metric_ingestion = [MetricIngestion(**row) for row in cur.fetchall()]

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
            UNION ALL
            SELECT 'worker_heartbeats', COUNT(*) FROM worker_heartbeats
            ORDER BY table_name
            """
        )
        table_counts = [TableCount(**row) for row in cur.fetchall()]

    worker_status, worker_detail, worker_health = _worker_status()

    telemetry_lag = telemetry["telemetry_lag_seconds"]
    edge_status = "ok"
    edge_detail = "MQTT 边缘遥测正常入库"
    if telemetry_lag is None:
        edge_status = "no_data"
        edge_detail = "暂无边缘遥测数据"
    elif telemetry_lag > 120:
        edge_status = "stale"
        edge_detail = f"边缘遥测延迟 {telemetry_lag} 秒"

    return SystemOverview(
        services=[
            SystemServiceStatus(name="platform-api", status="ok", detail="FastAPI 服务可用"),
            SystemServiceStatus(name="postgres", status="ok", detail="数据库查询成功"),
            SystemServiceStatus(name="stream-worker", status=worker_status, detail=worker_detail),
            SystemServiceStatus(name="edge-gateway", status=edge_status, detail=edge_detail),
        ],
        summary=SystemOverviewSummary(
            device_count=device_count,
            running_count=device_status.get("running", 0),
            warning_count=device_status.get("warning", 0),
            offline_count=device_status.get("offline", 0),
            active_alarm_count=alarm_status.get("active", 0),
            acknowledged_alarm_count=alarm_status.get("acknowledged", 0),
            cleared_alarm_count=alarm_status.get("cleared", 0),
            telemetry_count=telemetry["telemetry_count"],
            latest_telemetry_at=telemetry["latest_telemetry_at"],
            telemetry_lag_seconds=telemetry_lag,
        ),
        recent_device_ingestion=recent_device_ingestion,
        metric_ingestion=metric_ingestion,
        table_counts=table_counts,
        worker=worker_health,
    )
