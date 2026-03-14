"""Endpoints for measurements, sleep, steps, and workout logging."""

import asyncio
from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Activity, DailySummary, Measurement, SleepLog, StepsLog, get_db
from src.models.schemas import (
    MeasurementCreate,
    MeasurementResponse,
    MessageResponse,
    SleepLogCreate,
    SleepLogResponse,
    StepsLogCreate,
    StepsLogResponse,
    WorkoutLogCreate,
)
from src.services.sheets_sync import sheets_sync
from src.utils.helpers import get_week_number

log = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Measurements (weight / waist / body fat)
# ---------------------------------------------------------------------------


@router.get("/measurements", response_model=list[MeasurementResponse])
async def list_measurements(db: AsyncSession = Depends(get_db)) -> list[MeasurementResponse]:
    result = await db.execute(select(Measurement).order_by(Measurement.date.desc()))
    return [MeasurementResponse.model_validate(m) for m in result.scalars().all()]


@router.post("/measurements", response_model=MeasurementResponse, status_code=201)
async def log_measurement(
    body: MeasurementCreate, db: AsyncSession = Depends(get_db)
) -> MeasurementResponse:
    week = get_week_number(body.date)
    measurement = Measurement(
        date=body.date,
        week_number=week,
        weight_kg=body.weight_kg,
        waist_cm=body.waist_cm,
        body_fat_pct=body.body_fat_pct,
        notes=body.notes,
    )
    db.add(measurement)
    await db.flush()
    await db.refresh(measurement)
    log.info("Measurement logged", date=str(body.date), weight=body.weight_kg, waist=body.waist_cm)

    # Compute weight/waist deltas relative to the most recent prior measurement
    prev_result = await db.execute(
        select(Measurement)
        .where(Measurement.date < body.date)
        .order_by(Measurement.date.desc())
    )
    prev = prev_result.scalars().first()
    weight_delta = (
        round(measurement.weight_kg - prev.weight_kg, 2)
        if measurement.weight_kg is not None and prev is not None and prev.weight_kg is not None
        else None
    )
    waist_delta = (
        round(measurement.waist_cm - prev.waist_cm, 2)
        if measurement.waist_cm is not None and prev is not None and prev.waist_cm is not None
        else None
    )

    # Fire-and-forget Sheets sync
    asyncio.create_task(
        sheets_sync.sync_measurement(
            {
                "date": measurement.date,
                "day_number": None,
                "week_number": measurement.week_number,
                "weight_kg": measurement.weight_kg,
                "weight_delta_kg": weight_delta,
                "waist_cm": measurement.waist_cm,
                "waist_delta_cm": waist_delta,
                "body_fat_pct": measurement.body_fat_pct,
                "notes": measurement.notes,
            }
        )
    )

    return MeasurementResponse.model_validate(measurement)


# ---------------------------------------------------------------------------
# Sleep
# ---------------------------------------------------------------------------


@router.post("/sleep", response_model=SleepLogResponse, status_code=201)
async def log_sleep(body: SleepLogCreate, db: AsyncSession = Depends(get_db)) -> SleepLogResponse:
    sleep = SleepLog(date=body.date, hours=body.hours, quality=body.quality, notes=body.notes)
    db.add(sleep)
    await db.flush()

    # Update daily summary
    ds_result = await db.execute(select(DailySummary).where(DailySummary.date == body.date))
    summary = ds_result.scalar_one_or_none()
    if summary:
        summary.sleep_hrs = body.hours
        summary.sleep_quality = body.quality
    else:
        summary = DailySummary(
            date=body.date,
            sleep_hrs=body.hours,
            sleep_quality=body.quality,
        )
        db.add(summary)

    await db.flush()
    await db.refresh(sleep)
    log.info("Sleep logged", date=str(body.date), hours=body.hours, quality=body.quality)
    return SleepLogResponse.model_validate(sleep)


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------


@router.post("/steps", response_model=StepsLogResponse, status_code=201)
async def log_steps(
    body: StepsLogCreate, db: AsyncSession = Depends(get_db)
) -> StepsLogResponse:
    steps = StepsLog(date=body.date, step_count=body.step_count, source=body.source)
    db.add(steps)
    await db.flush()

    # Update daily summary
    ds_result = await db.execute(select(DailySummary).where(DailySummary.date == body.date))
    summary = ds_result.scalar_one_or_none()
    if summary:
        summary.steps = body.step_count
    else:
        summary = DailySummary(date=body.date, steps=body.step_count)
        db.add(summary)

    await db.flush()
    await db.refresh(steps)
    log.info("Steps logged", date=str(body.date), steps=body.step_count)
    return StepsLogResponse.model_validate(steps)


# ---------------------------------------------------------------------------
# Workout
# ---------------------------------------------------------------------------


@router.post("/workout", response_model=MessageResponse, status_code=201)
async def log_workout(
    body: WorkoutLogCreate, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    # Log as activity
    activity = Activity(
        date=body.date,
        activity_type=body.activity_type,
        duration_min=body.duration_min,
        notes=body.notes,
    )
    db.add(activity)
    await db.flush()

    # Update daily summary
    ds_result = await db.execute(select(DailySummary).where(DailySummary.date == body.date))
    summary = ds_result.scalar_one_or_none()
    if summary:
        summary.workout_done = body.done
        summary.workout_notes = body.notes
    else:
        summary = DailySummary(
            date=body.date,
            workout_done=body.done,
            workout_notes=body.notes,
        )
        db.add(summary)

    await db.flush()
    status = "completed" if body.done else "rest day"
    log.info("Workout logged", date=str(body.date), status=status)
    return MessageResponse(message=f"Workout logged: {status}")
