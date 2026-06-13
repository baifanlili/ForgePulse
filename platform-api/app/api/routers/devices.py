from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.core.db import db_cursor

router = APIRouter()


@router.get("")
def list_devices() -> list[dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                device_code,
                device_name,
                device_type,
                area,
                line,
                status,
                last_heartbeat_at
            FROM devices
            ORDER BY area, line, device_code
            """
        )
        return list(cur.fetchall())


@router.get("/{device_code}")
def get_device(device_code: str) -> dict[str, Any]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                device_code,
                device_name,
                device_type,
                area,
                line,
                status,
                last_heartbeat_at,
                created_at,
                updated_at
            FROM devices
            WHERE device_code = %s
            """,
            (device_code,),
        )
        device = cur.fetchone()
        if device is None:
            raise HTTPException(status_code=404, detail="Device not found")

        cur.execute(
            """
            SELECT
                metric_name,
                metric_value,
                time
            FROM (
                SELECT
                    metric_name,
                    metric_value,
                    time,
                    ROW_NUMBER() OVER (
                        PARTITION BY metric_name
                        ORDER BY time DESC
                    ) AS row_num
                FROM telemetry_points
                WHERE device_code = %s
            ) latest
            WHERE row_num = 1
            ORDER BY metric_name
            """,
            (device_code,),
        )
        latest_metrics = list(cur.fetchall())

        cur.execute(
            """
            SELECT
                alarm_code,
                severity,
                title,
                description,
                status,
                started_at,
                cleared_at
            FROM alarms
            WHERE device_code = %s
            ORDER BY
                CASE status WHEN 'active' THEN 0 ELSE 1 END,
                started_at DESC
            LIMIT 10
            """,
            (device_code,),
        )
        alarms = list(cur.fetchall())

    return {
        "device": device,
        "latest_metrics": latest_metrics,
        "alarms": alarms,
    }


@router.get("/{device_code}/telemetry")
def device_telemetry(
    device_code: str,
    metric_name: str | None = None,
    all_history: bool = False,
    hours: int = Query(default=1, ge=1, le=168),
    limit: int = Query(default=200, ge=1, le=1000),
) -> dict[str, Any]:
    with db_cursor() as cur:
        cur.execute("SELECT 1 FROM devices WHERE device_code = %s", (device_code,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Device not found")

        params: list[Any] = [device_code]
        time_filter = ""
        if not all_history:
            time_filter = "AND time >= NOW() - (%s * INTERVAL '1 hour')"
            params.append(hours)

        metric_filter = ""
        if metric_name:
            metric_filter = "AND metric_name = %s"
            params.append(metric_name)
        params.append(limit)

        cur.execute(
            f"""
            SELECT
                time,
                device_code,
                metric_name,
                metric_value,
                tags
            FROM telemetry_points
            WHERE device_code = %s
              {time_filter}
              {metric_filter}
            ORDER BY time DESC
            LIMIT %s
            """,
            params,
        )
        points = list(reversed(cur.fetchall()))

        cur.execute(
            """
            SELECT DISTINCT metric_name
            FROM telemetry_points
            WHERE device_code = %s
            ORDER BY metric_name
            """,
            (device_code,),
        )
        metrics = [row["metric_name"] for row in cur.fetchall()]

    return {
        "device_code": device_code,
        "metric_name": metric_name,
        "all_history": all_history,
        "hours": hours,
        "limit": limit,
        "metrics": metrics,
        "points": points,
    }
