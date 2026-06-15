from datetime import datetime

from pydantic import BaseModel


class LotYield(BaseModel):
    lot_code: str
    product_code: str
    wafer_count: int | None = None
    total_die: int | None = None
    pass_die: int | None = None
    fail_die: int | None = None
    yield_rate: float
    started_at: datetime | None = None
    completed_at: datetime | None = None


class WaferYield(BaseModel):
    wafer_id: str
    yield_rate: float
    pass_die: int | None = None
    fail_die: int | None = None


class BinCount(BaseModel):
    bin_name: str
    die_count: int


class SpcPoint(BaseModel):
    metric_name: str
    sample_time: datetime
    value: float
    center_line: float
    upper_control_limit: float
    lower_control_limit: float


class YieldData(BaseModel):
    lots: list[LotYield]
    wafers: list[WaferYield]
    bins: list[BinCount]
