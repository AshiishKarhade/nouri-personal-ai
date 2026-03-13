#!/usr/bin/env python3
"""
Bulk seed script — paste your Week 1 data here and run:
    python scripts/seed_history.py

Fill in the WEEK1_DATA dict below with your actual data from ChatGPT,
then run the script. It will POST to the running FastAPI backend.
"""

import httpx
import asyncio
from datetime import date

BASE = "http://127.0.0.1:8000"

# ─────────────────────────────────────────────────────────────────────────────
# FILL THIS IN with your actual data from ChatGPT
# Each key is a date string "YYYY-MM-DD"
# ─────────────────────────────────────────────────────────────────────────────

WEEK1_DATA = {
    "2026-03-09": {  # Day 1
        "day_type": "training",  # or "rest"
        "meals": [
            # Each meal: description, meal_type, cal_low, cal_high, protein_g, carbs_g, fats_g
            # Example:
            # {"description": "2 eggs scrambled + 2 rotis", "meal_type": "breakfast", "cal_low": 320, "cal_high": 380, "protein_g": 18, "carbs_g": 32, "fats_g": 12},
            # {"description": "chicken rice bowl", "meal_type": "lunch", "cal_low": 450, "cal_high": 530, "protein_g": 42, "carbs_g": 45, "fats_g": 10},
        ],
        "sleep_hours": None,   # e.g. 7.5
        "sleep_quality": None, # 1-5
        "steps": None,         # e.g. 8200
        "workout_done": None,  # True / False
        "workout_notes": None, # e.g. "chest + triceps, 45 min"
        "weight_kg": None,     # log only on measurement days
        "waist_cm": None,
    },
    "2026-03-10": {  # Day 2
        "day_type": "rest",
        "meals": [],
        "sleep_hours": None,
        "sleep_quality": None,
        "steps": None,
        "workout_done": False,
        "workout_notes": None,
        "weight_kg": None,
        "waist_cm": None,
    },
    "2026-03-11": {  # Day 3
        "day_type": "training",
        "meals": [],
        "sleep_hours": None,
        "sleep_quality": None,
        "steps": None,
        "workout_done": None,
        "workout_notes": None,
        "weight_kg": None,
        "waist_cm": None,
    },
    "2026-03-12": {  # Day 4
        "day_type": "training",
        "meals": [],
        "sleep_hours": None,
        "sleep_quality": None,
        "steps": None,
        "workout_done": None,
        "workout_notes": None,
        "weight_kg": None,
        "waist_cm": None,
    },
    "2026-03-13": {  # Day 5 (today)
        "day_type": "training",
        "meals": [],
        "sleep_hours": None,
        "sleep_quality": None,
        "steps": None,
        "workout_done": None,
        "workout_notes": None,
        "weight_kg": None,
        "waist_cm": None,
    },
}

# ─────────────────────────────────────────────────────────────────────────────

async def seed():
    async with httpx.AsyncClient(base_url=BASE, timeout=30) as client:
        for date_str, day in WEEK1_DATA.items():
            print(f"\n── {date_str} ──")

            # Meals
            for meal in day.get("meals", []):
                if not meal.get("description"):
                    continue
                cal_low = meal.get("cal_low")
                cal_high = meal.get("cal_high") or cal_low
                payload = {
                    "date": date_str,
                    "meal_type": meal.get("meal_type", "snack"),
                    "description": meal["description"],
                    "cal_low": cal_low,
                    "cal_high": cal_high,
                    "protein_g": meal.get("protein_g"),
                    "carbs_g": meal.get("carbs_g"),
                    "fats_g": meal.get("fats_g"),
                    "fiber_g": meal.get("fiber_g"),
                }
                r = await client.post("/api/v1/meals", json=payload)
                if r.status_code == 201:
                    d = r.json()
                    print(f"  ✓ {meal['meal_type']}: {meal['description'][:40]} — {d.get('cal_mid')} kcal")
                else:
                    print(f"  ✗ meal failed: {r.status_code} {r.text[:100]}")

            # Sleep
            if day.get("sleep_hours"):
                r = await client.post("/api/v1/sleep", json={
                    "date": date_str,
                    "hours": day["sleep_hours"],
                    "quality": day.get("sleep_quality"),
                })
                print(f"  ✓ sleep: {day['sleep_hours']}h" + (f" quality {day['sleep_quality']}/5" if day.get("sleep_quality") else ""))

            # Steps
            if day.get("steps"):
                r = await client.post("/api/v1/steps", json={
                    "date": date_str,
                    "step_count": day["steps"],
                })
                print(f"  ✓ steps: {day['steps']:,}")

            # Workout
            if day.get("workout_done") is not None:
                r = await client.post("/api/v1/workout", json={
                    "date": date_str,
                    "done": day["workout_done"],
                    "notes": day.get("workout_notes"),
                })
                status = "done" if day["workout_done"] else "rest day"
                print(f"  ✓ workout: {status}" + (f" — {day['workout_notes']}" if day.get("workout_notes") else ""))

            # Measurement
            if day.get("weight_kg") or day.get("waist_cm"):
                r = await client.post("/api/v1/measurements", json={
                    "date": date_str,
                    "weight_kg": day.get("weight_kg"),
                    "waist_cm": day.get("waist_cm"),
                })
                parts = []
                if day.get("weight_kg"):
                    parts.append(f"{day['weight_kg']}kg")
                if day.get("waist_cm"):
                    parts.append(f"waist {day['waist_cm']}cm")
                print(f"  ✓ measurement: {', '.join(parts)}")

    print("\n✅ Done! Refresh the dashboard.")

if __name__ == "__main__":
    asyncio.run(seed())
