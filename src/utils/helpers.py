"""Utility helpers for date arithmetic and day number calculations."""

from datetime import date, timedelta

# Program constants
PROGRAM_START_DATE = date(2026, 3, 9)   # Day 1 = March 9 2026 (today = Day 5)
PROGRAM_TARGET_DATE = date(2026, 10, 19)
CALORIES_TRAINING = 1700
CALORIES_REST = 1500
PROTEIN_TARGET_G = 155.0  # midpoint of 150-160g target
STEPS_TARGET = 8000


def get_day_number(for_date: date | None = None) -> int:
    """Return the program day number (Day 1 = Jan 6 2026).

    Days before the start return 0; days past the program length are
    counted beyond 56.
    """
    if for_date is None:
        for_date = date.today()
    delta = (for_date - PROGRAM_START_DATE).days + 1
    return max(1, delta)


def get_week_number(for_date: date | None = None) -> int:
    """Return the program week number (Week 1 = days 1-7)."""
    day = get_day_number(for_date)
    return ((day - 1) // 7) + 1


def get_calorie_target(day_type: str) -> int:
    """Return calorie target based on day type (training / rest)."""
    return CALORIES_TRAINING if day_type.lower() == "training" else CALORIES_REST


def compute_cal_mid(low: int | None, high: int | None) -> int | None:
    """Return the midpoint of a calorie range, or None if both are None."""
    if low is None and high is None:
        return None
    low = low or 0
    high = high or low
    return (low + high) // 2


def date_range(start: date, end: date) -> list[date]:
    """Return a list of dates from start to end inclusive."""
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]
