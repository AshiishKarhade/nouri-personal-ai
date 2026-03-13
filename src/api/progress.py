"""Progress endpoint — trend data for the React dashboard charts."""

from datetime import date, timedelta

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import DailySummary, Measurement, get_db
from src.models.schemas import DayProgressPoint, MeasurementResponse, ProgressResponse
from src.utils.helpers import PROGRAM_START_DATE, get_day_number

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/progress", response_model=ProgressResponse)
async def get_progress(
    weeks: int = Query(default=8, ge=1, le=52),
    db: AsyncSession = Depends(get_db),
) -> ProgressResponse:
    end_date = date.today()
    start_date = max(PROGRAM_START_DATE, end_date - timedelta(weeks=weeks))

    # Pull daily summaries in range
    ds_result = await db.execute(
        select(DailySummary)
        .where(DailySummary.date >= start_date, DailySummary.date <= end_date)
        .order_by(DailySummary.date)
    )
    summaries = {row.date: row for row in ds_result.scalars().all()}

    # Pull measurements in range
    meas_result = await db.execute(
        select(Measurement)
        .where(Measurement.date >= start_date, Measurement.date <= end_date)
        .order_by(Measurement.date)
    )
    measurements_list = meas_result.scalars().all()
    # Map measurements by date for quick lookup
    meas_by_date: dict[date, Measurement] = {}
    for m in measurements_list:
        meas_by_date[m.date] = m

    # Build day-by-day progress points
    days: list[DayProgressPoint] = []
    current = start_date
    while current <= end_date:
        ds = summaries.get(current)
        m = meas_by_date.get(current)
        days.append(
            DayProgressPoint(
                date=current,
                day_number=get_day_number(current),
                cal_actual_mid=ds.cal_actual_mid if ds else None,
                cal_target=ds.cal_target if ds else 2000,
                protein_g=ds.protein_g if ds else None,
                steps=ds.steps if ds else None,
                sleep_hrs=ds.sleep_hrs if ds else None,
                weight_kg=m.weight_kg if m else None,
                waist_cm=m.waist_cm if m else None,
                workout_done=ds.workout_done if ds else None,
            )
        )
        current += timedelta(days=1)

    return ProgressResponse(
        weeks=weeks,
        start_date=start_date,
        end_date=end_date,
        days=days,
        measurements=[MeasurementResponse.model_validate(m) for m in measurements_list],
    )
