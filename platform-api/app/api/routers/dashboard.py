from typing import Any

from fastapi import APIRouter

from app.core.db import db_cursor

router = APIRouter()


@router.get("/dashboard")
def dashboard() -> dict[str, Any]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM devices
            GROUP BY status
            """
        )
        status_counts = {row["status"]: row["count"] for row in cur.fetchall()}

        cur.execute("SELECT COUNT(*) AS count FROM devices")
        device_count = cur.fetchone()["count"]

        cur.execute(
            """
            SELECT COUNT(*) AS count
            FROM alarms
            WHERE status = 'active'
            """
        )
        active_alarm_count = cur.fetchone()["count"]

        cur.execute(
            """
            SELECT ROUND(AVG(yield_rate)::numeric, 2) AS average_yield
            FROM lots
            WHERE started_at >= NOW() - INTERVAL '24 hours'
            """
        )
        average_yield = cur.fetchone()["average_yield"]

        cur.execute(
            """
            SELECT
                device_code,
                metric_name,
                metric_value,
                time
            FROM (
                SELECT
                    device_code,
                    metric_name,
                    metric_value,
                    time,
                    ROW_NUMBER() OVER (
                        PARTITION BY device_code, metric_name
                        ORDER BY time DESC
                    ) AS row_num
                FROM telemetry_points
            ) latest
            WHERE row_num = 1
            ORDER BY device_code, metric_name
            """
        )
        latest_metrics = list(cur.fetchall())

        cur.execute(
            """
            SELECT
                alarm_code,
                device_code,
                severity,
                title,
                status,
                started_at
            FROM alarms
            ORDER BY
                CASE status WHEN 'active' THEN 0 ELSE 1 END,
                started_at DESC
            LIMIT 5
            """
        )
        recent_alarms = list(cur.fetchall())

        cur.execute(
            """
            SELECT lot_code, product_code, yield_rate, started_at
            FROM lots
            ORDER BY started_at
            """
        )
        lots = list(cur.fetchall())

        cur.execute(
            """
            SELECT bin_name, die_count
            FROM bin_counts
            WHERE lot_code = (
                SELECT lot_code
                FROM lots
                ORDER BY COALESCE(completed_at, NOW()) DESC
                LIMIT 1
            )
            ORDER BY die_count DESC
            """
        )
        bins = list(cur.fetchall())

    return {
        "summary": {
            "device_count": device_count,
            "running_count": status_counts.get("running", 0),
            "warning_count": status_counts.get("warning", 0),
            "offline_count": status_counts.get("offline", 0),
            "active_alarm_count": active_alarm_count,
            "average_yield": float(average_yield or 0),
        },
        "latest_metrics": latest_metrics,
        "recent_alarms": recent_alarms,
        "yield_trend": lots,
        "bin_distribution": bins,
    }
