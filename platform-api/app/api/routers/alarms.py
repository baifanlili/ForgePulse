from typing import Any

from fastapi import APIRouter

from app.core.db import db_cursor

router = APIRouter()


@router.get("")
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
