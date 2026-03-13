"""History endpoint — day-by-day log for the React dashboard."""

from datetime import date, timedelta

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import DailySummary, Meal, get_db
from src.models.schemas import DailySummaryResponse, HistoryDayResponse, MealResponse
from src.utils.helpers import PROGRAM_START_DATE

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/history", response_model=list[HistoryDayResponse])
async def get_history(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> list[HistoryDayResponse]:
    end_date = date.today()
    start_date = max(PROGRAM_START_DATE, end_date - timedelta(days=days - 1))

    # Fetch all summaries in range
    ds_result = await db.execute(
        select(DailySummary)
        .where(DailySummary.date >= start_date, DailySummary.date <= end_date)
        .order_by(DailySummary.date.desc())
    )
    summaries = {row.date: row for row in ds_result.scalars().all()}

    # Fetch all meals in range
    meals_result = await db.execute(
        select(Meal)
        .where(Meal.date >= start_date, Meal.date <= end_date)
        .order_by(Meal.date.desc(), Meal.created_at)
    )
    all_meals = meals_result.scalars().all()

    # Group meals by date
    meals_by_date: dict[date, list] = {}
    for meal in all_meals:
        meals_by_date.setdefault(meal.date, []).append(meal)

    # Only return dates that have some data
    result: list[HistoryDayResponse] = []
    current = end_date
    while current >= start_date:
        ds = summaries.get(current)
        meals = meals_by_date.get(current, [])
        if ds or meals:
            result.append(
                HistoryDayResponse(
                    date=current,
                    day_number=ds.day_number if ds else None,
                    summary=DailySummaryResponse.model_validate(ds) if ds else None,
                    meals=[MealResponse.model_validate(m) for m in meals],
                )
            )
        current -= timedelta(days=1)

    return result
