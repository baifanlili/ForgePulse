import os
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row

app = FastAPI(title="ForgePulse Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def database_url() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "forgepulse")
    user = os.getenv("POSTGRES_USER", "forgepulse")
    password = os.getenv("POSTGRES_PASSWORD", "forgepulse")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


@contextmanager
def db_cursor() -> Iterator[psycopg.Cursor[dict[str, Any]]]:
    with psycopg.connect(database_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            yield cur


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "platform-api"}


@app.get("/api/devices")
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


@app.get("/api/alarms")
def list_alarms() -> list[dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                alarm_code,
                device_code,
                severity,
                title,
                description,
                status,
                started_at,
                cleared_at
            FROM alarms
            ORDER BY
                CASE status WHEN 'active' THEN 0 ELSE 1 END,
                started_at DESC
            LIMIT 20
            """
        )
        return list(cur.fetchall())


@app.get("/api/analytics/yield")
def yield_trend() -> dict[str, Any]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                lot_code,
                product_code,
                wafer_count,
                total_die,
                pass_die,
                fail_die,
                yield_rate,
                started_at,
                completed_at
            FROM lots
            ORDER BY started_at
            """
        )
        lots = list(cur.fetchall())

        cur.execute(
            """
            SELECT
                wafer_id,
                yield_rate,
                pass_die,
                fail_die
            FROM wafer_yields
            WHERE lot_code = (
                SELECT lot_code
                FROM lots
                ORDER BY COALESCE(completed_at, NOW()) DESC
                LIMIT 1
            )
            ORDER BY wafer_id
            """
        )
        wafers = list(cur.fetchall())

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

    return {"lots": lots, "wafers": wafers, "bins": bins}


@app.get("/api/analytics/spc")
def spc_points() -> list[dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                metric_name,
                sample_time,
                value,
                center_line,
                upper_control_limit,
                lower_control_limit
            FROM spc_points
            ORDER BY sample_time
            """
        )
        return list(cur.fetchall())


@app.get("/api/dashboard")
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
