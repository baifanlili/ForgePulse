from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from app.core.auth import get_current_user
from app.core.db import db_cursor
from app.schemas.alarm import (
    AckBody,
    Alarm,
    AlarmDetail,
    AlarmEvent,
    AlarmStatus,
    ClearBody,
)

router = APIRouter()


def fetch_alarm(alarm_code: str) -> AlarmDetail:
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
                acknowledged_at,
                acknowledged_by,
                cleared_at,
                cleared_by
            FROM alarms
            WHERE alarm_code = %s
            """,
            (alarm_code,),
        )
        alarm_row = cur.fetchone()
        if alarm_row is None:
            raise HTTPException(status_code=404, detail="Alarm not found")

        cur.execute(
            """
            SELECT event_type, operator, note, created_at
            FROM alarm_events
            WHERE alarm_code = %s
            ORDER BY created_at DESC, id DESC
            """,
            (alarm_code,),
        )
        events = [AlarmEvent(**row) for row in cur.fetchall()]

    return AlarmDetail(alarm=Alarm(**alarm_row), events=events)


@router.get("", response_model=list[Alarm])
def list_alarms(
    status: AlarmStatus | None = Query(default=None),
    severity: str | None = Query(default=None),
    device_code: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[Alarm]:
    filters: list[str] = []
    params: list[Any] = []

    if status:
        filters.append("status = %s")
        params.append(status)
    if severity:
        filters.append("severity = %s")
        params.append(severity)
    if device_code:
        filters.append("device_code = %s")
        params.append(device_code)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    params.append(limit)

    with db_cursor() as cur:
        cur.execute(
            f"""
            SELECT
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
            FROM alarms
            {where_clause}
            ORDER BY
                CASE status
                    WHEN 'active' THEN 0
                    WHEN 'acknowledged' THEN 1
                    ELSE 2
                END,
                started_at DESC
            LIMIT %s
            """,
            params,
        )
        return [Alarm(**row) for row in cur.fetchall()]


@router.get("/{alarm_code}", response_model=AlarmDetail)
def get_alarm(alarm_code: str) -> AlarmDetail:
    return fetch_alarm(alarm_code)


@router.patch("/{alarm_code}/acknowledge", response_model=AlarmDetail)
def acknowledge_alarm(
    alarm_code: str,
    body: AckBody = Body(default_factory=AckBody),
    user: dict = Depends(get_current_user),
) -> AlarmDetail:
    operator = body.operator if body.operator != "operator" else user["display_name"]

    with db_cursor() as cur:
        cur.execute(
            """
            UPDATE alarms
            SET status = 'acknowledged',
                acknowledged_at = NOW(),
                acknowledged_by = %s
            WHERE alarm_code = %s
              AND status = 'active'
            RETURNING alarm_code
            """,
            (operator, alarm_code),
        )
        updated = cur.fetchone() is not None
        if not updated:
            cur.execute("SELECT status FROM alarms WHERE alarm_code = %s", (alarm_code,))
            alarm = cur.fetchone()
            if alarm is None:
                raise HTTPException(status_code=404, detail="Alarm not found")
            if alarm["status"] != "acknowledged":
                raise HTTPException(status_code=409, detail="Alarm cannot be acknowledged")

        if updated:
            cur.execute(
                """
                INSERT INTO alarm_events (alarm_code, event_type, operator, note)
                VALUES (%s, 'acknowledged', %s, %s)
                """,
                (alarm_code, operator, body.note),
            )
            cur.execute(
                """
                INSERT INTO audit_log (action, target_type, target_id, operator, detail)
                VALUES ('alarm_acknowledge', 'alarm', %s, %s, %s::jsonb)
                """,
                (alarm_code, operator, '{"note":"' + body.note + '"}'),
            )

    return fetch_alarm(alarm_code)


@router.patch("/{alarm_code}/clear", response_model=AlarmDetail)
def clear_alarm(
    alarm_code: str,
    body: ClearBody = Body(default_factory=ClearBody),
    user: dict = Depends(get_current_user),
) -> AlarmDetail:
    operator = body.operator if body.operator != "operator" else user["display_name"]

    with db_cursor() as cur:
        cur.execute(
            """
            UPDATE alarms
            SET status = 'cleared',
                cleared_at = NOW(),
                cleared_by = %s
            WHERE alarm_code = %s
              AND status IN ('active', 'acknowledged')
            RETURNING alarm_code
            """,
            (operator, alarm_code),
        )
        updated = cur.fetchone() is not None
        if not updated:
            cur.execute("SELECT status FROM alarms WHERE alarm_code = %s", (alarm_code,))
            alarm = cur.fetchone()
            if alarm is None:
                raise HTTPException(status_code=404, detail="Alarm not found")
            if alarm["status"] != "cleared":
                raise HTTPException(status_code=409, detail="Alarm cannot be cleared")

        if updated:
            cur.execute(
                """
                INSERT INTO alarm_events (alarm_code, event_type, operator, note)
                VALUES (%s, 'cleared', %s, %s)
                """,
                (alarm_code, operator, body.note),
            )
            cur.execute(
                """
                INSERT INTO audit_log (action, target_type, target_id, operator, detail)
                VALUES ('alarm_clear', 'alarm', %s, %s, %s::jsonb)
                """,
                (alarm_code, operator, '{"note":"' + body.note + '"}'),
            )

    return fetch_alarm(alarm_code)
