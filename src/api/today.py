"""GET /api/v1/today — today's full dashboard summary."""

from datetime import date

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import DailySummary, Meal, Measurement, SleepLog, StepsLog, get_db
from src.models.schemas import (
    CalorieSummary,
    DailySummaryResponse,
    MacroSummary,
    MealResponse,
    TodayResponse,
)
from src.services.calorie_tracker import get_daily_target, get_daily_totals, is_protein_on_track
from src.services.measurement_tracker import get_latest_measurement
from src.utils.helpers import CALORIES_TRAINING, STEPS_TARGET, get_day_number, get_week_number

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/today", response_model=TodayResponse)
async def get_today(db: AsyncSession = Depends(get_db)) -> TodayResponse:
    today = date.today()
    day_number = get_day_number(today)

    # Determine day type from daily_summary if set, else default training
    summary_result = await db.execute(
        select(DailySummary).where(DailySummary.date == today)
    )
    summary_row = summary_result.scalar_one_or_none()
    day_type = summary_row.day_type if summary_row and summary_row.day_type else "training"

    targets = get_daily_target(today, day_type)
    totals = await get_daily_totals(db, today)
    protein_ok = await is_protein_on_track(db, today)

    # Meals for today
    meals_result = await db.execute(
        select(Meal).where(Meal.date == today).order_by(Meal.created_at)
    )
    meals = meals_result.scalars().all()

    # Latest measurement
    latest = await get_latest_measurement(db)

    # Steps today
    steps_result = await db.execute(
        select(StepsLog).where(StepsLog.date == today).order_by(StepsLog.created_at.desc())
    )
    steps_row = steps_result.scalars().first()
    steps = steps_row.step_count if steps_row else None

    # Sleep today
    sleep_result = await db.execute(
        select(SleepLog).where(SleepLog.date == today).order_by(SleepLog.created_at.desc())
    )
    sleep_row = sleep_result.scalars().first()

    cal_target = targets["cal"]
    consumed_mid = totals["cal_mid"]
    ratio = consumed_mid / cal_target if cal_target > 0 else 0

    return TodayResponse(
        date=today,
        day_number=day_number,
        day_type=day_type,
        calories=CalorieSummary(
            target=cal_target,
            consumed_low=totals["cal_low"],
            consumed_high=totals["cal_high"],
            consumed_mid=consumed_mid,
            remaining_mid=max(0, cal_target - consumed_mid),
            on_track=ratio <= 1.05,
        ),
        macros=MacroSummary(
            protein_g=totals["protein_g"],
            protein_target_g=targets["protein_g"],
            carbs_g=totals["carbs_g"],
            fats_g=totals["fats_g"],
            fiber_g=totals["fiber_g"],
        ),
        meals=[MealResponse.model_validate(m) for m in meals],
        meals_count=totals["meals_count"],
        steps=steps,
        steps_target=STEPS_TARGET,
        sleep_hrs=sleep_row.hours if sleep_row else None,
        sleep_quality=sleep_row.quality if sleep_row else None,
        workout_done=summary_row.workout_done if summary_row else None,
        latest_weight_kg=latest.weight_kg if latest else None,
        latest_waist_cm=latest.waist_cm if latest else None,
        protein_on_track=protein_ok,
        summary=DailySummaryResponse.model_validate(summary_row) if summary_row else None,
    )
