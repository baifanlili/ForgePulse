from datetime import datetime
from typing import Literal

from pydantic import BaseModel

AlarmSeverity = Literal["critical", "warning", "info"]
AlarmStatus = Literal["active", "acknowledged", "cleared"]


class Alarm(BaseModel):
    alarm_code: str
    device_code: str
    severity: AlarmSeverity
    title: str
    description: str | None = None
    status: AlarmStatus
    started_at: datetime
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None
    cleared_at: datetime | None = None
    cleared_by: str | None = None


class AlarmEvent(BaseModel):
    event_type: str
    operator: str
    note: str | None = None
    created_at: datetime


class AlarmDetail(BaseModel):
    alarm: Alarm
    events: list[AlarmEvent]


class AlarmSummary(BaseModel):
    alarm_code: str
    device_code: str | None = None
    severity: AlarmSeverity | None = None
    title: str | None = None
    description: str | None = None
    status: AlarmStatus | None = None
    started_at: datetime | None = None
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None
    cleared_at: datetime | None = None
    cleared_by: str | None = None


class AckBody(BaseModel):
    operator: str = "operator"
    note: str = ""


class ClearBody(BaseModel):
    operator: str = "operator"
    note: str = ""
