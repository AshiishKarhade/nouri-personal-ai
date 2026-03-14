"""Google Sheets async sync service.

All public methods are fire-and-forget — callers should wrap them in
``asyncio.create_task()`` so they never block the API response.

SQLite is always the source of truth.  If Sheets sync fails at any point,
we log the error and continue.  Nothing here should ever raise to the caller.
"""

import asyncio
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Optional

import structlog
from sqlalchemy import select, update

from src.config import settings

log = structlog.get_logger(__name__)

# Sheets tab names
TAB_MEALS = "Meals"
TAB_DAILY_SUMMARY = "Daily Summary"
TAB_MEASUREMENTS = "Measurements"
TAB_WEEKLY_REPORT = "Weekly Report"

# Header rows — used to initialise tabs on first run
_MEALS_HEADERS = [
    "Date", "Day", "Meal Type", "Time", "Description",
    "Cal Low", "Cal High", "Cal Mid",
    "Protein (g)", "Carbs (g)", "Fats (g)", "Fiber (g)",
    "Photo?", "AI Notes",
]
_DAILY_HEADERS = [
    "Date", "Day", "Day Type", "Cal Target", "Cal Actual Mid", "Cal Delta",
    "Protein (g)", "Protein Target", "Protein Delta",
    "Carbs (g)", "Fats (g)", "Fiber (g)",
    "Meals Count", "Steps", "Sleep Hrs", "Sleep Quality",
    "Workout", "Coach Notes", "Nouri Notes",
]
_MEASUREMENT_HEADERS = [
    "Date", "Day", "Week",
    "Weight (kg)", "Weight Delta", "Waist (cm)", "Waist Delta",
    "Body Fat %", "Notes",
]
_WEEKLY_HEADERS = [
    "Week", "Avg Cal", "Avg Protein", "Days On Target", "Days Over",
    "Avg Steps", "Avg Sleep", "Workouts",
    "Weight Start (kg)", "Weight End (kg)", "Week Delta (kg)", "Waist Delta (cm)",
]


def _get_client():
    """Return an authenticated gspread client, or None if credentials are missing."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds_path = Path(settings.google_service_account_file)
        if not creds_path.exists():
            log.warning(
                "Google service account file not found — Sheets sync disabled",
                path=str(creds_path),
            )
            return None

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
        return gspread.authorize(creds)
    except ImportError:
        log.warning("gspread not installed — Sheets sync disabled")
        return None
    except Exception:
        log.exception("Failed to initialise Google Sheets client")
        return None


def _get_or_create_worksheet(spreadsheet, title: str, headers: list[str]):
    """Return the named worksheet, creating it with headers if it doesn't exist."""
    try:
        return spreadsheet.worksheet(title)
    except Exception:
        ws = spreadsheet.add_worksheet(title=title, rows=2000, cols=len(headers) + 2)
        ws.append_row(headers, value_input_option="USER_ENTERED")
        return ws


def _with_backoff(fn, *args, max_retries: int = 3, **kwargs) -> Any:
    """Call fn with exponential backoff on rate-limit errors."""
    delay = 2.0
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            error_str = str(exc).lower()
            if "quota" in error_str or "rate" in error_str or "429" in error_str:
                if attempt < max_retries - 1:
                    log.warning(
                        "Sheets rate limit hit, backing off",
                        delay=delay,
                        attempt=attempt + 1,
                    )
                    time.sleep(delay)
                    delay *= 2
                    continue
            raise
    return None  # unreachable


class SheetsSync:
    """Async wrapper around synchronous gspread calls.

    Each method runs the blocking gspread work in the default executor so the
    event loop is never blocked.
    """

    def __init__(self) -> None:
        self._client = None
        self._spreadsheet = None
        self._enabled = bool(settings.google_sheets_id)

    def _ensure_connection(self) -> bool:
        """Lazily connect and cache the spreadsheet handle."""
        if not self._enabled:
            return False
        if self._spreadsheet is not None:
            return True
        try:
            self._client = _get_client()
            if self._client is None:
                self._enabled = False
                return False
            self._spreadsheet = self._client.open_by_key(settings.google_sheets_id)
            log.info("Connected to Google Sheets", sheet_id=settings.google_sheets_id)
            return True
        except Exception:
            log.exception("Failed to open Google Spreadsheet")
            self._enabled = False
            return False

    # ------------------------------------------------------------------
    # Public async methods (fire-and-forget via asyncio.create_task)
    # ------------------------------------------------------------------

    async def sync_meal(self, meal_data: dict) -> None:
        """Append a meal row to the Meals tab."""
        if not self._enabled:
            return
        await asyncio.get_event_loop().run_in_executor(
            None, self._sync_meal_blocking, meal_data
        )

    async def sync_daily_summary(self, for_date: date, summary_data: dict) -> None:
        """Upsert the Daily Summary row for a given date."""
        if not self._enabled:
            return
        await asyncio.get_event_loop().run_in_executor(
            None, self._sync_daily_summary_blocking, for_date, summary_data
        )

    async def sync_measurement(self, measurement_data: dict) -> None:
        """Append a Measurements row."""
        if not self._enabled:
            return
        await asyncio.get_event_loop().run_in_executor(
            None, self._sync_measurement_blocking, measurement_data
        )

    async def update_weekly_report(self, week_data: dict) -> None:
        """Upsert a Weekly Report row."""
        if not self._enabled:
            return
        await asyncio.get_event_loop().run_in_executor(
            None, self._update_weekly_report_blocking, week_data
        )

    async def backfill_all(self, db_session_factory) -> int:
        """Push every unsynced DB row to Sheets.

        Reads all meals, daily_summary rows, and measurements that have not
        yet been synced (``synced_to_sheets == False`` for daily_summary;
        presence check via date for meals and measurements).

        Returns the number of daily-summary rows pushed.  Designed to be
        called once at startup or via the admin endpoint.
        """
        if not self._enabled:
            log.info("Sheets sync disabled — skipping backfill")
            return 0

        # Import here to avoid circular imports at module load time
        from src.models.database import DailySummary, Meal, Measurement

        pushed = 0
        try:
            async with db_session_factory() as session:
                # ── Meals ──────────────────────────────────────────────────
                meals_result = await session.execute(select(Meal).order_by(Meal.date, Meal.created_at))
                meals = meals_result.scalars().all()
                for meal in meals:
                    meal_data = {
                        "date": meal.date,
                        "day_number": None,  # not on Meal model; Sheets row still gets date
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
                    await self.sync_meal(meal_data)

                log.info("Backfill: meals queued", count=len(meals))

                # ── Daily summaries (unsynced only) ────────────────────────
                ds_result = await session.execute(
                    select(DailySummary)
                    .where(DailySummary.synced_to_sheets == False)  # noqa: E712
                    .order_by(DailySummary.date)
                )
                summaries = ds_result.scalars().all()
                for summary in summaries:
                    summary_data = {
                        "day_number": summary.day_number,
                        "day_type": summary.day_type or "training",
                        "cal_target": summary.cal_target,
                        "cal_actual_mid": summary.cal_actual_mid,
                        "protein_g": summary.protein_g,
                        "carbs_g": summary.carbs_g,
                        "fats_g": summary.fats_g,
                        "fiber_g": summary.fiber_g,
                        "meals_count": summary.meals_count,
                        "steps": summary.steps,
                        "sleep_hrs": summary.sleep_hrs,
                        "sleep_quality": summary.sleep_quality,
                        "workout_done": summary.workout_done,
                        "coach_notes": summary.coach_notes,
                        "nouri_notes": summary.nouri_notes,
                    }
                    await self.sync_daily_summary(summary.date, summary_data)
                    # Mark synced in DB so subsequent startups skip it
                    await session.execute(
                        update(DailySummary)
                        .where(DailySummary.id == summary.id)
                        .values(synced_to_sheets=True)
                    )
                    pushed += 1

                await session.commit()
                log.info("Backfill: daily summaries pushed", count=pushed)

                # ── Measurements ───────────────────────────────────────────
                meas_result = await session.execute(
                    select(Measurement).order_by(Measurement.date)
                )
                measurements = meas_result.scalars().all()
                # Build a delta map: each row compared to the previous one
                prev_weight: Optional[float] = None
                prev_waist: Optional[float] = None
                for m in measurements:
                    weight_delta = (
                        round(m.weight_kg - prev_weight, 2)
                        if m.weight_kg is not None and prev_weight is not None
                        else None
                    )
                    waist_delta = (
                        round(m.waist_cm - prev_waist, 2)
                        if m.waist_cm is not None and prev_waist is not None
                        else None
                    )
                    meas_data = {
                        "date": m.date,
                        "day_number": None,
                        "week_number": m.week_number,
                        "weight_kg": m.weight_kg,
                        "weight_delta_kg": weight_delta,
                        "waist_cm": m.waist_cm,
                        "waist_delta_cm": waist_delta,
                        "body_fat_pct": m.body_fat_pct,
                        "notes": m.notes,
                    }
                    await self.sync_measurement(meas_data)
                    if m.weight_kg is not None:
                        prev_weight = m.weight_kg
                    if m.waist_cm is not None:
                        prev_waist = m.waist_cm

                log.info("Backfill: measurements queued", count=len(measurements))

        except Exception:
            log.exception("Backfill to Sheets failed")

        return pushed

    # ------------------------------------------------------------------
    # Blocking implementations (run in executor)
    # ------------------------------------------------------------------

    def _sync_meal_blocking(self, meal_data: dict) -> None:
        try:
            if not self._ensure_connection():
                return
            ws = _get_or_create_worksheet(
                self._spreadsheet, TAB_MEALS, _MEALS_HEADERS
            )
            row = [
                str(meal_data.get("date", "")),
                meal_data.get("day_number", ""),
                meal_data.get("meal_type", ""),
                meal_data.get("time", ""),
                meal_data.get("description", ""),
                meal_data.get("cal_low", ""),
                meal_data.get("cal_high", ""),
                meal_data.get("cal_mid", ""),
                meal_data.get("protein_g", ""),
                meal_data.get("carbs_g", ""),
                meal_data.get("fats_g", ""),
                meal_data.get("fiber_g", ""),
                "Yes" if meal_data.get("photo_path") else "No",
                meal_data.get("ai_analysis", "")[:500] if meal_data.get("ai_analysis") else "",
            ]
            _with_backoff(ws.append_row, row, value_input_option="USER_ENTERED")
            log.info("Synced meal to Sheets", date=str(meal_data.get("date")))
        except Exception:
            log.exception("Failed to sync meal to Sheets")

    def _sync_daily_summary_blocking(self, for_date: date, summary_data: dict) -> None:
        try:
            if not self._ensure_connection():
                return
            ws = _get_or_create_worksheet(
                self._spreadsheet, TAB_DAILY_SUMMARY, _DAILY_HEADERS
            )
            date_str = str(for_date)
            all_values = _with_backoff(ws.get_all_values)
            if not all_values:
                all_values = []

            # Find existing row for this date (skip header row at index 0)
            existing_row_idx: Optional[int] = None
            for idx, row in enumerate(all_values):
                if row and row[0] == date_str:
                    existing_row_idx = idx + 1  # 1-indexed for gspread
                    break

            cal_target = summary_data.get("cal_target", 0) or 0
            cal_mid = summary_data.get("cal_actual_mid", 0) or 0
            protein = summary_data.get("protein_g", 0) or 0
            new_row = [
                date_str,
                summary_data.get("day_number", ""),
                summary_data.get("day_type", ""),
                cal_target,
                cal_mid,
                cal_mid - cal_target,
                protein,
                160,  # protein target
                protein - 160,
                summary_data.get("carbs_g", ""),
                summary_data.get("fats_g", ""),
                summary_data.get("fiber_g", ""),
                summary_data.get("meals_count", ""),
                summary_data.get("steps", ""),
                summary_data.get("sleep_hrs", ""),
                summary_data.get("sleep_quality", ""),
                "Yes" if summary_data.get("workout_done") else "No",
                summary_data.get("coach_notes", ""),
                summary_data.get("nouri_notes", ""),
            ]

            if existing_row_idx is not None:
                col_end = chr(ord("A") + len(new_row) - 1)
                cell_range = f"A{existing_row_idx}:{col_end}{existing_row_idx}"
                _with_backoff(
                    ws.update,
                    cell_range,
                    [new_row],
                    value_input_option="USER_ENTERED",
                )
            else:
                _with_backoff(ws.append_row, new_row, value_input_option="USER_ENTERED")

            log.info("Synced daily summary to Sheets", date=date_str)
        except Exception:
            log.exception("Failed to sync daily summary to Sheets", date=str(for_date))

    def _sync_measurement_blocking(self, measurement_data: dict) -> None:
        try:
            if not self._ensure_connection():
                return
            ws = _get_or_create_worksheet(
                self._spreadsheet, TAB_MEASUREMENTS, _MEASUREMENT_HEADERS
            )
            row = [
                str(measurement_data.get("date", "")),
                measurement_data.get("day_number", ""),
                measurement_data.get("week_number", ""),
                measurement_data.get("weight_kg", ""),
                measurement_data.get("weight_delta_kg", ""),
                measurement_data.get("waist_cm", ""),
                measurement_data.get("waist_delta_cm", ""),
                measurement_data.get("body_fat_pct", ""),
                measurement_data.get("notes", ""),
            ]
            _with_backoff(ws.append_row, row, value_input_option="USER_ENTERED")
            log.info("Synced measurement to Sheets", date=str(measurement_data.get("date")))
        except Exception:
            log.exception("Failed to sync measurement to Sheets")

    def _update_weekly_report_blocking(self, week_data: dict) -> None:
        try:
            if not self._ensure_connection():
                return
            ws = _get_or_create_worksheet(
                self._spreadsheet, TAB_WEEKLY_REPORT, _WEEKLY_HEADERS
            )
            week_num = str(week_data.get("week_number", ""))
            all_values = _with_backoff(ws.get_all_values) or []

            existing_row_idx: Optional[int] = None
            for idx, row in enumerate(all_values):
                if row and row[0] == week_num:
                    existing_row_idx = idx + 1
                    break

            new_row = [
                week_num,
                week_data.get("avg_cal", ""),
                week_data.get("avg_protein", ""),
                week_data.get("days_on_target", ""),
                week_data.get("days_over", ""),
                week_data.get("avg_steps", ""),
                week_data.get("avg_sleep", ""),
                week_data.get("workouts", ""),
                week_data.get("weight_start", ""),
                week_data.get("weight_end", ""),
                week_data.get("week_delta_kg", ""),
                week_data.get("waist_delta_cm", ""),
            ]

            if existing_row_idx is not None:
                col_end = chr(ord("A") + len(new_row) - 1)
                cell_range = f"A{existing_row_idx}:{col_end}{existing_row_idx}"
                _with_backoff(
                    ws.update,
                    cell_range,
                    [new_row],
                    value_input_option="USER_ENTERED",
                )
            else:
                _with_backoff(ws.append_row, new_row, value_input_option="USER_ENTERED")

            log.info("Updated weekly report in Sheets", week=week_num)
        except Exception:
            log.exception("Failed to update weekly report in Sheets")


# Module-level singleton
sheets_sync = SheetsSync()
