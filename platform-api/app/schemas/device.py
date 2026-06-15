from datetime import datetime
from typing import Literal

from pydantic import BaseModel

DeviceStatus = Literal["running", "warning", "offline"]


class Device(BaseModel):
    device_code: str
    device_name: str
    device_type: str
    area: str | None = None
    line: str | None = None
    status: DeviceStatus
    last_heartbeat_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MetricPoint(BaseModel):
    device_code: str
    metric_name: str
    metric_value: float
    time: datetime
    tags: dict | None = None


class LatestMetric(BaseModel):
    metric_name: str
    metric_value: float
    time: datetime


class DeviceDetail(BaseModel):
    device: Device
    latest_metrics: list[LatestMetric]
    alarms: list["AlarmSummary"]


class DeviceTelemetry(BaseModel):
    device_code: str
    metric_name: str | None = None
    all_history: bool = False
    hours: int = 1
    limit: int = 200
    metrics: list[str]
    points: list[MetricPoint]


from app.schemas.alarm import AlarmSummary  # noqa: E402
