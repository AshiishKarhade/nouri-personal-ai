"""Meal logging and food photo analysis endpoints."""

from datetime import date, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Meal, get_db
from src.models.schemas import (
    AnalyzePhotoRequest,
    FoodAnalysisResponse,
    MealCreate,
    MealResponse,
    MessageResponse,
)
from src.services.calorie_tracker import upsert_daily_summary
from src.utils.helpers import compute_cal_mid

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/meals/{meal_date}", response_model=list[MealResponse])
async def get_meals_for_date(
    meal_date: date, db: AsyncSession = Depends(get_db)
) -> list[MealResponse]:
    result = await db.execute(
        select(Meal).where(Meal.date == meal_date).order_by(Meal.created_at)
    )
    meals = result.scalars().all()
    return [MealResponse.model_validate(m) for m in meals]


@router.post("/meals", response_model=MealResponse, status_code=201)
async def create_meal(body: MealCreate, db: AsyncSession = Depends(get_db)) -> MealResponse:
    cal_mid = compute_cal_mid(body.cal_low, body.cal_high)
    now_str = datetime.now().strftime("%H:%M")

    meal = Meal(
        date=body.date,
        meal_type=body.meal_type,
        time=body.time or now_str,
        description=body.description,
        cal_low=body.cal_low,
        cal_high=body.cal_high,
        cal_mid=cal_mid,
        protein_g=body.protein_g,
        carbs_g=body.carbs_g,
        fats_g=body.fats_g,
        fiber_g=body.fiber_g,
        photo_path=body.photo_path,
        ai_analysis=body.ai_analysis,
        raw_input=body.raw_input,
        parse_failed=False,
    )
    db.add(meal)
    await db.flush()

    # Keep daily summary in sync
    try:
        await upsert_daily_summary(db, body.date)
    except Exception:
        log.warning("Failed to upsert daily summary after meal create", date=str(body.date))

    await db.refresh(meal)
    log.info("Meal logged", meal_type=body.meal_type, cal_mid=cal_mid, date=str(body.date))
    return MealResponse.model_validate(meal)


@router.delete("/meals/{meal_id}", response_model=MessageResponse)
async def delete_meal(meal_id: int, db: AsyncSession = Depends(get_db)) -> MessageResponse:
    result = await db.execute(select(Meal).where(Meal.id == meal_id))
    meal = result.scalar_one_or_none()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    meal_date = meal.date
    await db.delete(meal)
    await db.flush()
    try:
        await upsert_daily_summary(db, meal_date)
    except Exception:
        pass
    return MessageResponse(message=f"Meal {meal_id} deleted")


@router.post("/analyze-photo", response_model=FoodAnalysisResponse)
async def analyze_photo(body: AnalyzePhotoRequest) -> FoodAnalysisResponse:
    """Analyze a food photo using Claude Vision. Does NOT save to DB.

    The caller (OpenClaw skill) should confirm with the user then POST /meals.
    """
    from src.services.food_analyzer import analyze_food_photo

    try:
        result = await analyze_food_photo(body.base64_image, body.mime_type)
        return result
    except Exception as exc:
        log.exception("Food photo analysis failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
