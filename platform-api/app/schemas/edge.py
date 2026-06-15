from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

CommandType = Literal["pause", "resume", "set_interval", "inject_fault"]


class EdgeCommandRequest(BaseModel):
    command_type: CommandType
    parameters: dict[str, Any] = Field(default_factory=dict)
    operator: str = "demo-operator"


class EdgeCommand(BaseModel):
    command_id: str
    gateway_id: str
    command_type: CommandType
    parameters: dict[str, Any]
    status: str
    operator: str
    created_at: datetime
    published_at: datetime | None = None


class EdgeGateway(BaseModel):
    gateway_id: str
    line_id: str | None = None
    latest_seen_at: datetime
    latest_sequence: int | None = None
    sample_period_ms: int | None = None
    telemetry_point_count: int
    degraded_point_count: int
    latest_quality: str | None = None
    latest_status_reason: str | None = None
    latest_command: EdgeCommand | None = None
