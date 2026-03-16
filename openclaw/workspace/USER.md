# USER.md — Ashish Karhade

- **Name:** Ashish Karhade
- **What to call them:** Ashish
- **Pronouns:** he/him
- **Timezone:** Asia/Kolkata (IST, UTC+5:30)

## Transformation Program

- **Program start:** March 9, 2026 (Day 1)
- **Phase 1 target:** May 2, 2026 — reach 15-18% body fat
- **Final target:** October 19, 2026 — reach 10-12% body fat
- **Age:** 27 | **Height:** 178 cm (5'10")

## Daily Targets

| Metric | Training Day | Rest Day |
|--------|-------------|----------|
| Calories | 1700 kcal | 1500 kcal |
| Protein | 150-160g | 150-160g |
| Steps | 8000-10,000 | 8000-10,000 |
| Sleep | ≥7 hours | ≥7 hours |

## Food Preferences

- Primarily Indian home-cooked + cafeteria meals
- Protein sources: chicken, eggs, paneer, whey (SuperYou + The Whole Truth)
- Chai habit (80-100 cal with milk/sugar) — trying to reduce
- Tends to undereat protein at breakfast — flag if behind by 1 PM

## Training Schedule

- Gym 4-5 days/week, progressive overload
- Rest/deload every 4-6 weeks (reduce volume 40-50%)
- Day types: "training" or "rest"

## Supplement Stack (currently not taking regularly)

- Multivitamins (daily, with breakfast)
- Zinc (daily, evening)
- Omega-3 / Fish oil (daily, with meals)

## Python API (Backend)

All data goes to: http://localhost:8000
- Log meal: POST /api/v1/meals
- Analyze photo: POST /api/v1/analyze-photo
- Log sleep: POST /api/v1/sleep
- Log steps: POST /api/v1/steps
- Log workout: POST /api/v1/workout
- Log measurement: POST /api/v1/measurements
- Today's summary: GET /api/v1/today
