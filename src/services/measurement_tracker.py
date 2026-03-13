"""Weight, waist, and body composition measurement service."""

from datetime import date
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Measurement
from src.models.schemas import MeasurementResponse
from src.utils.helpers import get_week_number

log = structlog.get_logger(__name__)


async def log_measurement(
    db: AsyncSession,
    for_date: date,
    weight_kg: Optional[float] = None,
    waist_cm: Optional[float] = None,
    body_fat_pct: Optional[float] = None,
    notes: Optional[str] = None,
) -> Measurement:
    """Persist a measurement row and return the ORM object."""
    try:
        week_number = get_week_number(for_date)
        measurement = Measurement(
            date=for_date,
            week_number=week_number,
            weight_kg=weight_kg,
            waist_cm=waist_cm,
            body_fat_pct=body_fat_pct,
            notes=notes,
        )
        db.add(measurement)
        await db.flush()
        log.info(
            "Measurement logged",
            date=str(for_date),
            weight_kg=weight_kg,
            waist_cm=waist_cm,
        )
        return measurement
    except Exception:
        log.exception("Failed to log measurement", date=str(for_date))
        raise


async def get_latest_measurement(db: AsyncSession) -> Optional[MeasurementResponse]:
    """Return the most recent measurement row as a Pydantic schema."""
    try:
        result = await db.execute(
            select(Measurement).order_by(Measurement.date.desc()).limit(1)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return MeasurementResponse.model_validate(row)
    except Exception:
        log.exception("Failed to get latest measurement")
        return None


async def get_trend(
    db: AsyncSession,
    weeks: int = 8,
) -> list[dict]:
    """Return measurement history with deltas for the last N weeks.

    Each entry in the returned list is a dict with the measurement fields
    plus weight_delta_kg and waist_delta_cm relative to the previous entry.
    """
    try:
        result = await db.execute(
            select(Measurement).order_by(Measurement.date.asc())
        )
        rows = result.scalars().all()

        # Filter to last `weeks` weeks
        if rows:
            latest_date = rows[-1].date
            from datetime import timedelta

            cutoff = latest_date - timedelta(weeks=weeks)
            rows = [r for r in rows if r.date >= cutoff]

        enriched: list[dict] = []
        prev_weight: Optional[float] = None
        prev_waist: Optional[float] = None

        for row in rows:
            weight_delta = None
            waist_delta = None
            if prev_weight is not None and row.weight_kg is not None:
                weight_delta = round(row.weight_kg - prev_weight, 2)
            if prev_waist is not None and row.waist_cm is not None:
                waist_delta = round(row.waist_cm - prev_waist, 2)

            enriched.append(
                {
                    "id": row.id,
                    "date": row.date,
                    "week_number": row.week_number,
                    "weight_kg": row.weight_kg,
                    "waist_cm": row.waist_cm,
                    "body_fat_pct": row.body_fat_pct,
                    "notes": row.notes,
                    "created_at": row.created_at,
                    "weight_delta_kg": weight_delta,
                    "waist_delta_cm": waist_delta,
                }
            )

            if row.weight_kg is not None:
                prev_weight = row.weight_kg
            if row.waist_cm is not None:
                prev_waist = row.waist_cm

        return enriched
    except Exception:
        log.exception("Failed to get measurement trend")
        return []
