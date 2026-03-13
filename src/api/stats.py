"""Aggregate stats endpoint."""

from datetime import date, timedelta

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import DailySummary, Meal, Measurement, get_db
from src.models.schemas import StatsResponse, WeeklyStats
from src.services.measurement_tracker import get_latest_measurement
from src.utils.helpers import CALORIES_TRAINING, PROTEIN_TARGET_G, get_day_number, get_week_number

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)) -> StatsResponse:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)

    # Total meals logged ever
    meals_count_result = await db.execute(select(func.count(Meal.id)))
    total_meals = meals_count_result.scalar_one() or 0

    # Days tracked (have a daily summary)
    days_tracked_result = await db.execute(select(func.count(DailySummary.id)))
    days_tracked = days_tracked_result.scalar_one() or 0

    # This week's summaries
    week_result = await db.execute(
        select(DailySummary).where(
            DailySummary.date >= week_start,
            DailySummary.date <= week_end,
        )
    )
    week_summaries = week_result.scalars().all()

    avg_cals = _safe_avg([s.cal_actual_mid for s in week_summaries if s.cal_actual_mid])
    avg_protein = _safe_avg([s.protein_g for s in week_summaries if s.protein_g])
    avg_steps = _safe_avg([s.steps for s in week_summaries if s.steps])
    avg_sleep = _safe_avg([s.sleep_hrs for s in week_summaries if s.sleep_hrs])
    days_on_target = sum(
        1
        for s in week_summaries
        if s.cal_actual_mid and s.cal_target and s.cal_actual_mid <= s.cal_target * 1.05
    )
    workouts_this_week = sum(1 for s in week_summaries if s.workout_done)

    # Latest measurements
    latest = await get_latest_measurement(db)

    # Start measurement (first measurement ever)
    first_meas_result = await db.execute(
        select(Measurement).order_by(Measurement.date.asc())
    )
    first_meas = first_meas_result.scalars().first()

    weight_delta = None
    waist_delta = None
    if latest and first_meas and latest.id != first_meas.id:
        if latest.weight_kg and first_meas.weight_kg:
            weight_delta = round(latest.weight_kg - first_meas.weight_kg, 1)
        if latest.waist_cm and first_meas.waist_cm:
            waist_delta = round(latest.waist_cm - first_meas.waist_cm, 1)

    # Weekly history (last 8 weeks)
    weekly_history: list[WeeklyStats] = []
    for w in range(8, 0, -1):
        w_start = today - timedelta(weeks=w - 1, days=today.weekday())
        w_end = w_start + timedelta(days=6)
        w_result = await db.execute(
            select(DailySummary).where(
                DailySummary.date >= w_start, DailySummary.date <= w_end
            )
        )
        w_summaries = w_result.scalars().all()
        if not w_summaries:
            continue
        weekly_history.append(
            WeeklyStats(
                week_number=get_week_number(w_start),
                avg_calories=_safe_avg([s.cal_actual_mid for s in w_summaries if s.cal_actual_mid]),
                avg_protein_g=_safe_avg([s.protein_g for s in w_summaries if s.protein_g]),
                days_on_target=sum(
                    1
                    for s in w_summaries
                    if s.cal_actual_mid
                    and s.cal_target
                    and s.cal_actual_mid <= s.cal_target * 1.05
                ),
                days_over_target=sum(
                    1
                    for s in w_summaries
                    if s.cal_actual_mid
                    and s.cal_target
                    and s.cal_actual_mid > s.cal_target * 1.05
                ),
                avg_steps=_safe_avg([s.steps for s in w_summaries if s.steps]),
                avg_sleep_hrs=_safe_avg([s.sleep_hrs for s in w_summaries if s.sleep_hrs]),
                workouts_completed=sum(1 for s in w_summaries if s.workout_done),
            )
        )

    return StatsResponse(
        current_day_number=get_day_number(today),
        current_week_number=get_week_number(today),
        total_meals_logged=total_meals,
        days_tracked=days_tracked,
        avg_calories_this_week=avg_cals,
        avg_protein_this_week=avg_protein,
        days_on_target_this_week=days_on_target,
        avg_steps_this_week=avg_steps,
        avg_sleep_this_week=avg_sleep,
        workouts_this_week=workouts_this_week,
        current_weight_kg=latest.weight_kg if latest else None,
        current_waist_cm=latest.waist_cm if latest else None,
        weight_delta_kg=weight_delta,
        waist_delta_cm=waist_delta,
        weekly_history=weekly_history,
    )


def _safe_avg(values: list) -> float | None:
    filtered = [v for v in values if v is not None]
    if not filtered:
        return None
    return round(sum(filtered) / len(filtered), 1)
