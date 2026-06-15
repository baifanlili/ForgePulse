from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    device_count: int
    running_count: int
    warning_count: int
    offline_count: int
    active_alarm_count: int
    average_yield: float


class LatestMetricPoint(BaseModel):
    device_code: str
    metric_name: str
    metric_value: float
    time: datetime


class RecentAlarm(BaseModel):
    alarm_code: str
    device_code: str
    severity: str
    title: str
    status: str
    started_at: datetime


class YieldTrend(BaseModel):
    lot_code: str
    product_code: str
    yield_rate: float
    started_at: datetime


class BinDistItem(BaseModel):
    bin_name: str
    die_count: int


class DashboardData(BaseModel):
    summary: DashboardSummary
    latest_metrics: list[LatestMetricPoint]
    recent_alarms: list[RecentAlarm]
    yield_trend: list[YieldTrend]
    bin_distribution: list[BinDistItem]
