---
name: food-log
description: Log a meal or analyze a food photo by calling the Python backend API
triggers:
  - keywords: [ate, eating, food, meal, breakfast, lunch, dinner, snack, calories, protein, hungry]
  - media: [photo, image]
---

# Food Log Skill

## CRITICAL: Always use curl to call the API. NEVER write to memory files.

## On Text Message
When user reports eating something (e.g., "had 2 rotis and dal"), use bash:

```bash
curl -s -X POST http://localhost:8000/api/v1/meals \
  -H "Content-Type: application/json" \
  -d '{"description": "<user exact words>", "meal_type": "<breakfast|lunch|dinner|snack|pre_workout|post_workout>", "date": "<YYYY-MM-DD>"}'
```

## On Photo Message
When user sends a food photo, call:

```bash
curl -s -X POST http://localhost:8000/api/v1/analyze-photo \
  -H "Content-Type: application/json" \
  -d '{"base64_image": "<base64_string>", "mime_type": "image/jpeg"}'
```

Then present the analysis and ask for confirmation before logging with POST /api/v1/meals.

## Get Daily Totals
```bash
curl -s http://localhost:8000/api/v1/today
```

## Response Format
Always report:
1. What was logged
2. Calories (range: low-high)
3. Protein grams
4. Running daily total and remaining calories
5. Protein check if behind target
