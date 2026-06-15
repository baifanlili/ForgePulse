from datetime import datetime
from typing import Literal

from pydantic import BaseModel

ServiceStatus = Literal["ok", "stale", "no_data", "error"]


class SystemServiceStatus(BaseModel):
    name: str
    status: ServiceStatus
    detail: str


class WorkerHealth(BaseModel):
    worker_id: str | None = None
    status: str | None = None
    last_heartbeat_at: datetime | None = None
    telemetry_processed: int = 0
    alarms_triggered: int = 0
    lag_seconds: int | None = None


class SystemOverviewSummary(BaseModel):
    device_count: int
    running_count: int
    warning_count: int
    offline_count: int
    active_alarm_count: int
    acknowledged_alarm_count: int
    cleared_alarm_count: int
    telemetry_count: int
    latest_telemetry_at: datetime | None = None
    telemetry_lag_seconds: int | None = None


class RecentDeviceIngestion(BaseModel):
    device_code: str
    latest_time: datetime
    point_count: int


class MetricIngestion(BaseModel):
    metric_name: str
    point_count: int


class TableCount(BaseModel):
    table_name: str
    row_count: int


class SystemOverview(BaseModel):
    services: list[SystemServiceStatus]
    summary: SystemOverviewSummary
    recent_device_ingestion: list[RecentDeviceIngestion]
    metric_ingestion: list[MetricIngestion]
    table_counts: list[TableCount]
    worker: WorkerHealth | None = None
