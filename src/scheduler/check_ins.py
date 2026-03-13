"""APScheduler proactive check-in jobs.

Each job builds a message and fires it via OpenClaw CLI:
  openclaw message send --channel telegram --target <CHAT_ID> --message "..."
"""

import subprocess
from datetime import date

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import settings
from src.utils.helpers import get_day_number, get_week_number

log = structlog.get_logger(__name__)


def _send(message: str) -> None:
    """Fire a message through OpenClaw CLI (non-blocking fire-and-forget)."""
    chat_id = settings.telegram_chat_id
    if not chat_id or chat_id == "REPLACE_ME":
        log.debug("Telegram chat_id not configured — skipping scheduled message")
        return

    try:
        subprocess.run(
            [
                "openclaw",
                "message",
                "send",
                "--channel",
                "telegram",
                "--target",
                chat_id,
                "--message",
                message,
            ],
            timeout=15,
            capture_output=True,
            check=False,
        )
        log.info("Scheduled message sent", preview=message[:60])
    except FileNotFoundError:
        log.warning("openclaw CLI not found — is OpenClaw installed?")
    except Exception:
        log.exception("Failed to send scheduled message")


async def morning_check_in() -> None:
    today = date.today()
    day = get_day_number(today)
    week = get_week_number(today)
    msg = (
        f"Good morning! Day {day}/56, Week {week}.\n\n"
        "How did you sleep? Log with: 'slept X hours, quality Y/5'\n"
        "Don't forget to log breakfast when you eat."
    )
    _send(msg)


async def protein_check() -> None:
    msg = (
        "Quick protein check — how's lunch looking?\n"
        "Target: 160g/day. Should be at 60g+ by now.\n"
        "Log what you ate: 'had chicken rice for lunch'"
    )
    _send(msg)


async def evening_summary() -> None:
    msg = (
        "Evening check-in time!\n"
        "Log today's dinner and any remaining meals.\n"
        "Also log your steps if you haven't: 'X steps today'\n"
        "Type 'summary' to see your full day."
    )
    _send(msg)


async def sleep_reminder() -> None:
    msg = (
        "Getting close to bedtime. Target: 8 hours of sleep.\n"
        "Sleep is when the gains happen — prioritize it.\n"
        "Wind down in the next 30-60 minutes."
    )
    _send(msg)


async def weekly_weigh_in() -> None:
    week = get_week_number(date.today())
    msg = (
        f"Weekly check-in time! (Week {week})\n\n"
        "Log your measurements:\n"
        "• Weight: 'weight X kg'\n"
        "• Waist: 'waist X cm'\n\n"
        "Same time, same conditions as last week for accurate tracking."
    )
    _send(msg)


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the APScheduler with all check-in jobs."""
    scheduler = AsyncIOScheduler(timezone=settings.timezone)

    # 7:30 AM — Morning check-in
    scheduler.add_job(morning_check_in, "cron", hour=7, minute=30, id="morning_check_in")

    # 1:00 PM — Protein check
    scheduler.add_job(protein_check, "cron", hour=13, minute=0, id="protein_check")

    # 7:00 PM — Evening summary
    scheduler.add_job(evening_summary, "cron", hour=19, minute=0, id="evening_summary")

    # 10:00 PM — Sleep reminder
    scheduler.add_job(sleep_reminder, "cron", hour=22, minute=0, id="sleep_reminder")

    # Sunday 8:00 PM — Weekly weigh-in (day_of_week=6 = Sunday)
    scheduler.add_job(
        weekly_weigh_in, "cron", day_of_week=6, hour=20, minute=0, id="weekly_weigh_in"
    )

    return scheduler
