from fastapi import APIRouter

from app.core.db import db_cursor
from app.schemas.analytics import BinCount, LotYield, SpcPoint, WaferYield, YieldData

router = APIRouter()


@router.get("/yield", response_model=YieldData)
def yield_trend() -> YieldData:
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
        lots = [LotYield(**row) for row in cur.fetchall()]

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
        wafers = [WaferYield(**row) for row in cur.fetchall()]

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
        bins = [BinCount(**row) for row in cur.fetchall()]

    return YieldData(lots=lots, wafers=wafers, bins=bins)


@router.get("/spc", response_model=list[SpcPoint])
def spc_points() -> list[SpcPoint]:
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
        return [SpcPoint(**row) for row in cur.fetchall()]
