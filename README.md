# Transformation Coach — AI Health Tracker

8-week body transformation tracker with AI coaching via Telegram. Two agent personalities (Iron the Coach + Nouri the Nutritionist) powered by Claude, deployed via OpenClaw Gateway.

## Quick Start (Local Dev)

### 1. Python backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start API server (port 8000)
uvicorn src.main:app --reload
```

API docs: http://localhost:8000/docs

### 2. React dashboard (separate terminal)

```bash
cd dashboard
npm install
npm run dev
```

Dashboard: http://localhost:5173

### 3. Environment

The `.env` file is already configured with API keys. Check `.env.example` for the full variable reference.

### 4. OpenClaw (Telegram bot)

```bash
# Install OpenClaw globally if not already done:
curl -fsSL https://openclaw.ai/install.sh | bash

# Run gateway (reads openclaw/openclaw.json):
cd openclaw
openclaw start
```

## Architecture

```
Telegram → OpenClaw Gateway (Node.js) → Python FastAPI (port 8000)
                                              ↓
                                        SQLite database
                                        Google Sheets (async mirror)
                                        Claude Vision API (food photos)
React Dashboard ← FastAPI REST API ────────────┘
```

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/today` | Today's full summary |
| `POST /api/v1/meals` | Log a meal |
| `POST /api/v1/analyze-photo` | Analyze food photo (Claude Vision) |
| `POST /api/v1/sleep` | Log sleep |
| `POST /api/v1/steps` | Log steps |
| `POST /api/v1/workout` | Log workout |
| `POST /api/v1/measurements` | Log weight/waist |
| `GET /api/v1/progress` | Trend data for charts |
| `GET /api/v1/history` | Day-by-day history |
| `GET /api/v1/stats` | Aggregate stats |
| `GET /api/v1/memory` | User profile |

## Azure VM Deployment

See `azure/setup.sh` for the complete provisioning script.

```bash
# On your Azure B1s Ubuntu VM:
bash azure/setup.sh
```

## Targets

- **User:** Ashish Khatri
- **Goal:** 10-12% body fat by Oct 19, 2026
- **Program:** Day 1 = Jan 6, 2026 (56-day blocks)
- **Calories:** 2000 kcal (training) / 1700 kcal (rest)
- **Protein:** 160g/day
