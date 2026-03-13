"""SQLAlchemy async models for the Transformation Coach database."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncSession:  # type: ignore[return]
    """FastAPI dependency — yields a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """Create all database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Meals
# ---------------------------------------------------------------------------


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # breakfast/lunch/dinner/snack/pre_workout/post_workout
    time: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)  # HH:MM
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cal_low: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cal_high: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cal_mid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    protein_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    carbs_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fats_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fiber_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    photo_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_input: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parse_failed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Daily Summary
# ---------------------------------------------------------------------------


class DailySummary(Base):
    __tablename__ = "daily_summary"

    __table_args__ = (UniqueConstraint("date", name="uq_daily_summary_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    day_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    day_type: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # training / rest
    cal_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cal_actual_mid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    protein_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    carbs_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fats_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fiber_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    meals_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sleep_hrs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleep_quality: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # 1-5 scale
    workout_done: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    workout_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    coach_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nouri_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    synced_to_sheets: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    week_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    body_fat_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calories_burned: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Sleep Log
# ---------------------------------------------------------------------------


class SleepLog(Base):
    __tablename__ = "sleep_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Steps Log
# ---------------------------------------------------------------------------


class StepsLog(Base):
    __tablename__ = "steps_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    step_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
