---
name: body-metrics
description: Log sleep, steps, workout, weight, and waist measurements
triggers:
  - keywords: [sleep, slept, steps, walked, workout, gym, weight, waist, measured]
---

# Body Metrics Skill

## Sleep Logging
Pattern: "slept X hours" or "sleep was X/5"
Call: POST http://localhost:8000/api/v1/sleep
Body: { "hours": X, "quality": Y (optional, 1-5), "date": "<today>" }

## Steps Logging
Pattern: "X steps today" or "walked X steps"
Call: POST http://localhost:8000/api/v1/steps
Body: { "steps": X, "date": "<today>" }

## Workout Logging
Pattern: "did gym", "trained today", "rest day"
Call: POST http://localhost:8000/api/v1/workout
Body: { "done": true/false, "notes": "<optional notes>", "date": "<today>" }

## Measurement Logging
Pattern: "weight X kg", "waist X cm"
Call: POST http://localhost:8000/api/v1/measurements
Body: { "weight_kg": X, "waist_cm": Y, "date": "<today>" }

## Response Format
Confirm what was logged. If steps < 8000, flag it. If sleep < 7 hours, note recovery impact.
