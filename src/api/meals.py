"""Meal logging and food photo analysis endpoints."""

import asyncio
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
from src.services.sheets_sync import sheets_sync
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
    # Auto-analyze description if no calorie data was provided
    cal_low, cal_high, protein_g, carbs_g, fats_g, fiber_g, ai_analysis = (
        body.cal_low, body.cal_high, body.protein_g,
        body.carbs_g, body.fats_g, body.fiber_g, body.ai_analysis,
    )
    if cal_low is None and body.description:
        try:
            from src.services.food_analyzer import analyze_food_text
            analysis = await analyze_food_text(body.description)
            t = analysis.total
            cal_low = t.calories_low
            cal_high = t.calories_high
            protein_g = t.protein_g
            carbs_g = t.carbs_g
            fats_g = t.fats_g
            fiber_g = t.fiber_g
            ai_analysis = analysis.notes
        except Exception:
            log.warning("Auto food analysis failed, storing without calories", desc=body.description)

    cal_mid = compute_cal_mid(cal_low, cal_high)
    now_str = datetime.now().strftime("%H:%M")

    meal = Meal(
        date=body.date,
        meal_type=body.meal_type,
        time=body.time or now_str,
        description=body.description,
        cal_low=cal_low,
        cal_high=cal_high,
        cal_mid=cal_mid,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fats_g=fats_g,
        fiber_g=fiber_g,
        photo_path=body.photo_path,
        ai_analysis=ai_analysis,
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

    # Fire-and-forget Sheets sync (meal row)
    asyncio.create_task(
        sheets_sync.sync_meal(
            {
                "date": meal.date,
                "day_number": None,
                "meal_type": meal.meal_type,
                "time": meal.time or "",
                "description": meal.description or "",
                "cal_low": meal.cal_low,
                "cal_high": meal.cal_high,
                "cal_mid": meal.cal_mid,
                "protein_g": meal.protein_g,
                "carbs_g": meal.carbs_g,
                "fats_g": meal.fats_g,
                "fiber_g": meal.fiber_g,
                "photo_path": meal.photo_path,
                "ai_analysis": meal.ai_analysis,
            }
        )
    )

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
