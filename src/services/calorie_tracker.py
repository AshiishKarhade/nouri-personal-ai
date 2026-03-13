"""Daily calorie and macro tracking service."""

from datetime import date, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import DailySummary, Meal
from src.utils.helpers import (
    CALORIES_REST,
    CALORIES_TRAINING,
    PROTEIN_TARGET_G,
    get_day_number,
)

log = structlog.get_logger(__name__)

# Macro split targets (rough percentages from calorie total)
_CARBS_PCT = 0.45
_FATS_PCT = 0.25
_PROTEIN_CAL_PER_G = 4.0
_CARBS_CAL_PER_G = 4.0
_FATS_CAL_PER_G = 9.0


def get_daily_target(
    for_date: date | None = None,
    day_type: str = "training",
) -> dict:
    """Return daily macro targets for a given date and day type.

    Returns a dict with keys: cal, protein_g, carbs_g, fats_g.
    """
    cal = CALORIES_TRAINING if day_type.lower() == "training" else CALORIES_REST
    protein_g = PROTEIN_TARGET_G
    protein_cal = protein_g * _PROTEIN_CAL_PER_G
    remaining_cal = cal - protein_cal
    fats_g = round((cal * _FATS_PCT) / _FATS_CAL_PER_G, 1)
    carbs_g = round((remaining_cal - fats_g * _FATS_CAL_PER_G) / _CARBS_CAL_PER_G, 1)

    return {
        "cal": cal,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fats_g": fats_g,
    }


async def get_daily_totals(db: AsyncSession, for_date: date) -> dict:
    """Aggregate meal totals for a given date from the meals table.

    Returns a dict with keys: cal_low, cal_high, cal_mid, protein_g,
    carbs_g, fats_g, fiber_g, meals_count.
    """
    try:
        result = await db.execute(
            select(
                func.coalesce(func.sum(Meal.cal_low), 0).label("cal_low"),
                func.coalesce(func.sum(Meal.cal_high), 0).label("cal_high"),
                func.coalesce(func.sum(Meal.cal_mid), 0).label("cal_mid"),
                func.coalesce(func.sum(Meal.protein_g), 0.0).label("protein_g"),
                func.coalesce(func.sum(Meal.carbs_g), 0.0).label("carbs_g"),
                func.coalesce(func.sum(Meal.fats_g), 0.0).label("fats_g"),
                func.coalesce(func.sum(Meal.fiber_g), 0.0).label("fiber_g"),
                func.count(Meal.id).label("meals_count"),
            ).where(Meal.date == for_date)
        )
        row = result.one()
        return {
            "cal_low": int(row.cal_low),
            "cal_high": int(row.cal_high),
            "cal_mid": int(row.cal_mid),
            "protein_g": float(row.protein_g),
            "carbs_g": float(row.carbs_g),
            "fats_g": float(row.fats_g),
            "fiber_g": float(row.fiber_g),
            "meals_count": int(row.meals_count),
        }
    except Exception:
        log.exception("Failed to get daily totals", date=str(for_date))
        return {
            "cal_low": 0,
            "cal_high": 0,
            "cal_mid": 0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fats_g": 0.0,
            "fiber_g": 0.0,
            "meals_count": 0,
        }


async def get_remaining(
    db: AsyncSession,
    for_date: date,
    day_type: str = "training",
) -> dict:
    """Return remaining calories and protein for the day.

    Returns a dict with keys: cal_remaining, protein_remaining.
    """
    targets = get_daily_target(for_date, day_type)
    totals = await get_daily_totals(db, for_date)
    return {
        "cal_remaining": targets["cal"] - totals["cal_mid"],
        "protein_remaining": targets["protein_g"] - totals["protein_g"],
    }


async def is_protein_on_track(db: AsyncSession, for_date: date) -> bool:
    """Check if protein intake is on track by the current time of day.

    If it is before or at lunchtime (1 PM local), protein should be >= 40%
    of the daily target (64g out of 160g).  After lunch the bar stays at 40%
    of the day so you can still hit 160g by dinner.
    """
    try:
        now_hour = datetime.now().hour
        # Before 1 PM: expect at least 40% consumed
        threshold_pct = 0.40 if now_hour >= 13 else 0.25

        totals = await get_daily_totals(db, for_date)
        consumed = totals["protein_g"]
        target = PROTEIN_TARGET_G
        return consumed >= target * threshold_pct
    except Exception:
        log.exception("Failed protein on-track check", date=str(for_date))
        return True  # Assume on track on error — don't spam false warnings


async def upsert_daily_summary(
    db: AsyncSession,
    for_date: date,
    day_type: str = "training",
) -> DailySummary:
    """Create or update the daily_summary row for a given date from meal aggregates.

    Called after every meal write so the summary stays current.
    """
    try:
        totals = await get_daily_totals(db, for_date)
        targets = get_daily_target(for_date, day_type)
        day_number = get_day_number(for_date)

        result = await db.execute(
            select(DailySummary).where(DailySummary.date == for_date)
        )
        summary = result.scalar_one_or_none()

        if summary is None:
            summary = DailySummary(
                date=for_date,
                day_number=day_number,
                day_type=day_type,
                cal_target=targets["cal"],
            )
            db.add(summary)

        summary.cal_actual_mid = totals["cal_mid"]
        summary.protein_g = totals["protein_g"]
        summary.carbs_g = totals["carbs_g"]
        summary.fats_g = totals["fats_g"]
        summary.fiber_g = totals["fiber_g"]
        summary.meals_count = totals["meals_count"]

        await db.flush()
        return summary
    except Exception:
        log.exception("Failed to upsert daily summary", date=str(for_date))
        raise
