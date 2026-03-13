"""Pydantic v2 schemas for all API request/response types."""

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Meals
# ---------------------------------------------------------------------------


class MealCreate(BaseModel):
    date: date
    meal_type: str = Field(
        ...,
        description="One of: breakfast, lunch, dinner, snack, pre_workout, post_workout",
    )
    time: Optional[str] = Field(None, description="HH:MM format")
    description: Optional[str] = None
    cal_low: Optional[int] = None
    cal_high: Optional[int] = None
    cal_mid: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fats_g: Optional[float] = None
    fiber_g: Optional[float] = None
    photo_path: Optional[str] = None
    ai_analysis: Optional[str] = None
    raw_input: Optional[str] = None

    @field_validator("meal_type")
    @classmethod
    def validate_meal_type(cls, v: str) -> str:
        allowed = {
            "breakfast",
            "lunch",
            "dinner",
            "snack",
            "pre_workout",
            "post_workout",
        }
        if v.lower() not in allowed:
            raise ValueError(f"meal_type must be one of: {', '.join(sorted(allowed))}")
        return v.lower()


class MealResponse(BaseModel):
    id: int
    date: date
    meal_type: str
    time: Optional[str]
    description: Optional[str]
    cal_low: Optional[int]
    cal_high: Optional[int]
    cal_mid: Optional[int]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fats_g: Optional[float]
    fiber_g: Optional[float]
    photo_path: Optional[str]
    ai_analysis: Optional[str]
    parse_failed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Daily Summary
# ---------------------------------------------------------------------------


class DailySummaryResponse(BaseModel):
    id: int
    date: date
    day_number: Optional[int]
    day_type: Optional[str]
    cal_target: Optional[int]
    cal_actual_mid: Optional[int]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fats_g: Optional[float]
    fiber_g: Optional[float]
    meals_count: int
    steps: Optional[int]
    sleep_hrs: Optional[float]
    sleep_quality: Optional[int]
    workout_done: Optional[bool]
    workout_notes: Optional[str]
    coach_notes: Optional[str]
    nouri_notes: Optional[str]
    synced_to_sheets: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------


class MeasurementCreate(BaseModel):
    date: date
    weight_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    body_fat_pct: Optional[float] = None
    notes: Optional[str] = None


class MeasurementResponse(BaseModel):
    id: int
    date: date
    week_number: Optional[int]
    weight_kg: Optional[float]
    waist_cm: Optional[float]
    body_fat_pct: Optional[float]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Sleep & Steps
# ---------------------------------------------------------------------------


class SleepLogCreate(BaseModel):
    date: date
    hours: Optional[float] = Field(None, ge=0, le=24)
    quality: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class SleepLogResponse(BaseModel):
    id: int
    date: date
    hours: Optional[float]
    quality: Optional[int]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class StepsLogCreate(BaseModel):
    date: date
    step_count: int = Field(..., ge=0)
    source: str = "manual"


class StepsLogResponse(BaseModel):
    id: int
    date: date
    step_count: Optional[int]
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Workout
# ---------------------------------------------------------------------------


class WorkoutLogCreate(BaseModel):
    date: date
    done: bool = True
    notes: Optional[str] = None
    duration_min: Optional[int] = None
    activity_type: str = "gym"


# ---------------------------------------------------------------------------
# Food Analysis (photo)
# ---------------------------------------------------------------------------


class FoodItem(BaseModel):
    name: str
    portion_g: Optional[float] = None
    calories_low: Optional[int] = None
    calories_high: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fats_g: Optional[float] = None


class FoodAnalysisTotal(BaseModel):
    calories_low: Optional[int] = None
    calories_high: Optional[int] = None
    calories_mid: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fats_g: Optional[float] = None
    fiber_g: Optional[float] = None


class FoodAnalysisResponse(BaseModel):
    items: list[FoodItem] = []
    total: FoodAnalysisTotal = FoodAnalysisTotal()
    notes: Optional[str] = None
    parse_failed: bool = False
    raw_response: Optional[str] = None


class AnalyzePhotoRequest(BaseModel):
    base64_image: str
    mime_type: str = "image/jpeg"


# ---------------------------------------------------------------------------
# Today dashboard
# ---------------------------------------------------------------------------


class CalorieSummary(BaseModel):
    target: int
    consumed_low: int = 0
    consumed_high: int = 0
    consumed_mid: int = 0
    remaining_mid: int = 0
    on_track: bool = True


class MacroSummary(BaseModel):
    protein_g: float = 0.0
    protein_target_g: float = 160.0
    carbs_g: float = 0.0
    fats_g: float = 0.0
    fiber_g: float = 0.0


class TodayResponse(BaseModel):
    date: date
    day_number: int
    day_type: str  # training / rest
    calories: CalorieSummary
    macros: MacroSummary
    meals: list[MealResponse] = []
    meals_count: int = 0
    steps: Optional[int] = None
    steps_target: int = 8000
    sleep_hrs: Optional[float] = None
    sleep_quality: Optional[int] = None
    workout_done: Optional[bool] = None
    latest_weight_kg: Optional[float] = None
    latest_waist_cm: Optional[float] = None
    protein_on_track: bool = True
    summary: Optional[DailySummaryResponse] = None


# ---------------------------------------------------------------------------
# Progress / History
# ---------------------------------------------------------------------------


class DayProgressPoint(BaseModel):
    date: date
    day_number: Optional[int]
    cal_actual_mid: Optional[int]
    cal_target: Optional[int]
    protein_g: Optional[float]
    steps: Optional[int]
    sleep_hrs: Optional[float]
    weight_kg: Optional[float]
    waist_cm: Optional[float]
    workout_done: Optional[bool]


class ProgressResponse(BaseModel):
    weeks: int
    start_date: date
    end_date: date
    days: list[DayProgressPoint] = []
    measurements: list[MeasurementResponse] = []


class HistoryDayResponse(BaseModel):
    date: date
    day_number: Optional[int]
    summary: Optional[DailySummaryResponse]
    meals: list[MealResponse] = []


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


class WeeklyStats(BaseModel):
    week_number: int
    avg_calories: Optional[float]
    avg_protein_g: Optional[float]
    days_on_target: int
    days_over_target: int
    avg_steps: Optional[float]
    avg_sleep_hrs: Optional[float]
    workouts_completed: int


class StatsResponse(BaseModel):
    current_day_number: int
    current_week_number: int
    total_meals_logged: int
    days_tracked: int
    avg_calories_this_week: Optional[float]
    avg_protein_this_week: Optional[float]
    days_on_target_this_week: int
    avg_steps_this_week: Optional[float]
    avg_sleep_this_week: Optional[float]
    workouts_this_week: int
    current_weight_kg: Optional[float]
    current_waist_cm: Optional[float]
    weight_delta_kg: Optional[float]
    waist_delta_cm: Optional[float]
    weekly_history: list[WeeklyStats] = []


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------


class MessageResponse(BaseModel):
    message: str
    data: Optional[Any] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
