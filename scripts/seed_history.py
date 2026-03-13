#!/usr/bin/env python3
"""Bulk seed — Week 1 data (Mar 9–13 2026). Run: python scripts/seed_history.py"""

import httpx
import asyncio

BASE = "http://127.0.0.1:8000"

WEEK1_DATA = {
    "2026-03-09": {
        "day_type": "training",
        "meals": [
            {"meal_type": "breakfast", "description": "2 boiled eggs, 1 scoop SuperYou protein, 1/2 scoop The Whole Truth whey isolate", "cal_low": 300, "cal_high": 340, "protein_g": 51, "carbs_g": 5, "fats_g": 12, "fiber_g": 0},
            {"meal_type": "lunch", "description": "cafeteria thali with white rice, 2 chapati, chicken curry, dal, curd, salad", "cal_low": 760, "cal_high": 860, "protein_g": 42, "carbs_g": 111, "fats_g": 23, "fiber_g": 8},
            {"meal_type": "pre_workout", "description": "2 medium bananas", "cal_low": 200, "cal_high": 220, "protein_g": 2, "carbs_g": 54, "fats_g": 0, "fiber_g": 6},
            {"meal_type": "dinner", "description": "white rice, rajma, chicken curry pieces, onion slices", "cal_low": 560, "cal_high": 640, "protein_g": 56, "carbs_g": 67, "fats_g": 8, "fiber_g": 7},
        ],
        "sleep_hours": None, "sleep_quality": None, "steps": 9000,
        "workout_done": True, "workout_notes": "gym session",
        "weight_kg": None, "waist_cm": None,
    },
    "2026-03-10": {
        "day_type": "training",
        "meals": [
            {"meal_type": "breakfast", "description": "2 boiled eggs, 1 scoop SuperYou protein, 1/2 scoop The Whole Truth whey isolate, black coffee", "cal_low": 300, "cal_high": 340, "protein_g": 51, "carbs_g": 5, "fats_g": 12, "fiber_g": 0},
            {"meal_type": "lunch", "description": "cafeteria thali with rice, 1 chapati, chicken curry, curd, vegetable stir fry, salad", "cal_low": 630, "cal_high": 700, "protein_g": 33, "carbs_g": 83, "fats_g": 21, "fiber_g": 7},
            {"meal_type": "pre_workout", "description": "1 banana", "cal_low": 95, "cal_high": 110, "protein_g": 1, "carbs_g": 27, "fats_g": 0, "fiber_g": 3},
            {"meal_type": "post_workout", "description": "1 scoop The Whole Truth whey isolate and 1/2 scoop SuperYou protein", "cal_low": 170, "cal_high": 200, "protein_g": 42, "carbs_g": 4, "fats_g": 1, "fiber_g": 0},
            {"meal_type": "dinner", "description": "white rice with vegetable curry and 1 boiled egg", "cal_low": 330, "cal_high": 380, "protein_g": 12, "carbs_g": 51, "fats_g": 11, "fiber_g": 4},
            {"meal_type": "snack", "description": "100g Milky Mist natural Greek yogurt", "cal_low": 55, "cal_high": 65, "protein_g": 10, "carbs_g": 4, "fats_g": 0, "fiber_g": 0},
        ],
        "sleep_hours": None, "sleep_quality": None, "steps": 9000,
        "workout_done": True, "workout_notes": "gym session",
        "weight_kg": None, "waist_cm": None,
    },
    "2026-03-11": {
        "day_type": "training",
        "meals": [
            {"meal_type": "breakfast", "description": "2 boiled eggs, 1 scoop SuperYou protein, 1/2 scoop The Whole Truth whey isolate, black coffee", "cal_low": 300, "cal_high": 340, "protein_g": 51, "carbs_g": 5, "fats_g": 12, "fiber_g": 0},
            {"meal_type": "lunch", "description": "cafeteria thali with rice, 1 chapati, chicken curry, dal, curd, salad", "cal_low": 680, "cal_high": 740, "protein_g": 39, "carbs_g": 94, "fats_g": 21, "fiber_g": 8},
            {"meal_type": "pre_workout", "description": "2 bananas", "cal_low": 200, "cal_high": 220, "protein_g": 2, "carbs_g": 54, "fats_g": 0, "fiber_g": 6},
            {"meal_type": "dinner", "description": "rice with chicken curry (1.5 portions)", "cal_low": 640, "cal_high": 700, "protein_g": 42, "carbs_g": 74, "fats_g": 21, "fiber_g": 3},
        ],
        "sleep_hours": None, "sleep_quality": None, "steps": 9000,
        "workout_done": True, "workout_notes": "gym session",
        "weight_kg": None, "waist_cm": None,
    },
    "2026-03-12": {
        "day_type": "training",
        "meals": [
            {"meal_type": "breakfast", "description": "2 boiled eggs, 1 scoop SuperYou protein, 1/2 scoop The Whole Truth whey isolate, milk tea", "cal_low": 370, "cal_high": 410, "protein_g": 53, "carbs_g": 15, "fats_g": 14, "fiber_g": 0},
            {"meal_type": "lunch", "description": "cafeteria thali with rice, chapati, chicken curry, curd, vegetable sabzi, salad", "cal_low": 600, "cal_high": 650, "protein_g": 34, "carbs_g": 71, "fats_g": 22, "fiber_g": 7},
            {"meal_type": "pre_workout", "description": "1 banana", "cal_low": 95, "cal_high": 110, "protein_g": 1, "carbs_g": 27, "fats_g": 0, "fiber_g": 3},
            {"meal_type": "post_workout", "description": "1 scoop The Whole Truth whey isolate", "cal_low": 110, "cal_high": 130, "protein_g": 30, "carbs_g": 2, "fats_g": 1, "fiber_g": 0},
            {"meal_type": "dinner", "description": "boiled chicken with rice and beans", "cal_low": 520, "cal_high": 620, "protein_g": 58, "carbs_g": 56, "fats_g": 8, "fiber_g": 8},
            {"meal_type": "snack", "description": "100g Greek yogurt", "cal_low": 55, "cal_high": 65, "protein_g": 8, "carbs_g": 4, "fats_g": 2, "fiber_g": 0},
        ],
        "sleep_hours": None, "sleep_quality": None, "steps": 9000,
        "workout_done": True, "workout_notes": "gym session",
        "weight_kg": None, "waist_cm": None,
    },
    "2026-03-13": {
        "day_type": "training",
        "meals": [
            {"meal_type": "breakfast", "description": "2 boiled eggs, 1 scoop SuperYou protein, 1/2 scoop The Whole Truth whey isolate, black coffee", "cal_low": 300, "cal_high": 340, "protein_g": 51, "carbs_g": 5, "fats_g": 12, "fiber_g": 0},
            {"meal_type": "lunch", "description": "cafeteria thali with rice, chapati, chicken curry, curd, vegetable sabzi, salad", "cal_low": 600, "cal_high": 650, "protein_g": 34, "carbs_g": 77, "fats_g": 22, "fiber_g": 7},
            {"meal_type": "pre_workout", "description": "1 banana", "cal_low": 95, "cal_high": 110, "protein_g": 1, "carbs_g": 27, "fats_g": 0, "fiber_g": 3},
            {"meal_type": "post_workout", "description": "1 scoop The Whole Truth whey isolate and 1/2 scoop SuperYou protein", "cal_low": 170, "cal_high": 200, "protein_g": 42, "carbs_g": 4, "fats_g": 1, "fiber_g": 0},
            {"meal_type": "dinner", "description": "fried rice with vegetables and eggs plus 100g paneer", "cal_low": 520, "cal_high": 620, "protein_g": 25, "carbs_g": 55, "fats_g": 20, "fiber_g": 4},
        ],
        "sleep_hours": None, "sleep_quality": None, "steps": 9000,
        "workout_done": True, "workout_notes": "gym session",
        "weight_kg": 72.6, "waist_cm": None,
    },
}


async def seed():
    async with httpx.AsyncClient(base_url=BASE, timeout=30) as client:
        for date_str, day in WEEK1_DATA.items():
            print(f"\n{'─'*50}")
            print(f"  {date_str}  ({day['day_type'].upper()})")
            print(f"{'─'*50}")

            total_cal = 0
            total_protein = 0

            for meal in day.get("meals", []):
                cal_low = meal.get("cal_low")
                cal_high = meal.get("cal_high") or cal_low
                cal_mid = ((cal_low or 0) + (cal_high or 0)) // 2
                payload = {
                    "date": date_str,
                    "meal_type": meal["meal_type"],
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
                    total_cal += cal_mid
                    total_protein += meal.get("protein_g") or 0
                    tag = meal["meal_type"].upper().ljust(13)
                    desc = meal["description"][:42]
                    print(f"  ✓ {tag}  {cal_mid:>4} kcal  {int(meal.get('protein_g',0)):>3}g P   {desc}")
                else:
                    print(f"  ✗ {meal['meal_type']} FAILED: {r.status_code}")

            print(f"  {'─'*44}")
            print(f"  TOTAL             {total_cal:>4} kcal  {int(total_protein):>3}g P")

            if day.get("sleep_hours"):
                r = await client.post("/api/v1/sleep", json={"date": date_str, "hours": day["sleep_hours"], "quality": day.get("sleep_quality")})
                print(f"  ✓ SLEEP           {day['sleep_hours']}h")

            if day.get("steps"):
                r = await client.post("/api/v1/steps", json={"date": date_str, "step_count": day["steps"]})
                print(f"  ✓ STEPS           {day['steps']:,}")

            if day.get("workout_done") is not None:
                r = await client.post("/api/v1/workout", json={"date": date_str, "done": day["workout_done"], "notes": day.get("workout_notes"), "activity_type": "gym"})
                print(f"  ✓ GYM             {'✓ done' if day['workout_done'] else 'rest day'}")

            if day.get("weight_kg") or day.get("waist_cm"):
                r = await client.post("/api/v1/measurements", json={"date": date_str, "weight_kg": day.get("weight_kg"), "waist_cm": day.get("waist_cm")})
                parts = []
                if day.get("weight_kg"): parts.append(f"{day['weight_kg']} kg")
                if day.get("waist_cm"): parts.append(f"waist {day['waist_cm']} cm")
                print(f"  ✓ MEASUREMENT     {', '.join(parts)}")

    print(f"\n{'═'*50}")
    print("  ✅  All 5 days seeded. Refresh the dashboard.")
    print(f"{'═'*50}\n")


if __name__ == "__main__":
    asyncio.run(seed())
