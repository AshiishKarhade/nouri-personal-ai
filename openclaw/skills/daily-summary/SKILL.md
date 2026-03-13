---
name: daily-summary
description: Fetch and display today's summary as a chat-friendly message
triggers:
  - keywords: [summary, today, how am I doing, progress, dashboard]
---

# Daily Summary Skill

## Fetch Summary
Call: GET http://localhost:8000/api/v1/today

## Format Response
Present as a clean summary:
📊 **Day X/56 — [Date]**

🔥 Calories: X/2000 (Y remaining)
🥩 Protein: Xg/160g
🚶 Steps: X
😴 Sleep: X hrs (quality: X/5)
💪 Workout: ✅/❌

**Meals today:**
- [emoji] X:XX — Description (X cal, Xg P)

**Notes:**
[Iron's and Nouri's notes if any]
