---
name: body-metrics
description: Log sleep, steps, workout, weight, and waist measurements
triggers:
  - keywords: [sleep, slept, steps, walked, workout, gym, weight, waist, measured]
---

# Body Metrics Skill

## CRITICAL: Always use curl to call the API. NEVER write to memory files.

## Sleep Logging
```bash
curl -s -X POST http://localhost:8000/api/v1/sleep \
  -H "Content-Type: application/json" \
  -d '{"hours": X, "quality": Y, "date": "<YYYY-MM-DD>"}'
```

## Steps Logging
```bash
curl -s -X POST http://localhost:8000/api/v1/steps \
  -H "Content-Type: application/json" \
  -d '{"step_count": X, "date": "<YYYY-MM-DD>"}'
```

## Workout Logging
```bash
curl -s -X POST http://localhost:8000/api/v1/workout \
  -H "Content-Type: application/json" \
  -d '{"done": true, "notes": "<notes>", "activity_type": "gym", "date": "<YYYY-MM-DD>"}'
```

## Measurement Logging
```bash
curl -s -X POST http://localhost:8000/api/v1/measurements \
  -H "Content-Type: application/json" \
  -d '{"weight_kg": X, "waist_cm": Y, "date": "<YYYY-MM-DD>"}'
```

## Response Format
Confirm what was logged. If steps < 8000, flag it. If sleep < 7 hours, note recovery impact.
