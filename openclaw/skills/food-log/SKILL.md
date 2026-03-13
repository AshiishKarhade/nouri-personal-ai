---
name: food-log
description: Log a meal or analyze a food photo by calling the Python backend API
triggers:
  - keywords: [ate, eating, food, meal, breakfast, lunch, dinner, snack, calories, protein, hungry]
  - media: [photo, image]
---

# Food Log Skill

## On Text Message
When user reports eating something (e.g., "had 2 rotis and dal"), call:
POST http://localhost:8000/api/v1/meals
Body: { "description": "<user's exact words>", "meal_type": "<inferred type>", "date": "<today>" }

## On Photo Message
When user sends a food photo, call:
POST http://localhost:8000/api/v1/analyze-photo
Body: { "base64_image": "<base64>", "mime_type": "image/jpeg" }

Then present the analysis to the user and ask for confirmation:
"I see: [item list with cals]. Total: ~X-Y calories, Zg protein. Should I log this?"

On confirmation, call POST /api/v1/meals with the analyzed data.

## Response Format
Always report:
1. What was logged
2. Calories (range: low-high)
3. Protein grams
4. Running daily total and remaining calories
5. Protein check if behind target
