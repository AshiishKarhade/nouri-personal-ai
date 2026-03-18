# Handoff — Transformation Coach AI (as of March 18, 2026)

## What's working

- **FastAPI backend** — running on Azure VM at `http://localhost:8000` (via nginx at your public IP)
- **SQLite DB** — at `/opt/transformation-coach/nouri-personal-ai/data/transformation.db`
- **React dashboard** — served by FastAPI, accessible at `http://<your-vm-ip>/`
- **Telegram bot** — OpenClaw gateway running, Iron + Nouri respond to messages
- **Google Sheets sync** — wired up; every meal/measurement/summary write syncs to Sheets
- **5 days of historical data** — March 9–13 backfilled from ChatGPT JSON dump
- **OpenClaw agent tools** — set to `profile: "full"` so agent can run bash/curl

## What's broken / pending

### 1. Food calorie analysis returns null (CRITICAL)
**Root cause:** OpenAI account has no billing credits → 429 `insufficient_quota` on every call.

**Fix options (pick one):**
- **Option A (easiest):** Add $5 to [platform.openai.com/settings/billing](https://platform.openai.com/settings/billing). Code is already correct, it'll just work.
- **Option B:** Switch food analyzer to Gemini free tier (I can do this in one session).
- **Option C:** Build a static Indian food calorie lookup table (no API, instant, works offline).

**Affected file:** `src/services/food_analyzer.py` — `analyze_food_text()` and `analyze_food_photo()`

### 2. March 15 meals never logged to DB
The Telegram bot wrote to `memory/2026-03-15.md` instead of the API. Not in DB or Sheets.

**To manually log March 15 meals (run on VM):**
```bash
BASE="http://localhost:8000/api/v1"
curl -s -X POST "$BASE/meals" -H "Content-Type: application/json" \
  -d '{"description": "banana and fruit bowl", "meal_type": "breakfast", "date": "2026-03-15"}'
curl -s -X POST "$BASE/meals" -H "Content-Type: application/json" \
  -d '{"description": "chicken biryani", "meal_type": "lunch", "date": "2026-03-15"}'
curl -s -X POST "$BASE/meals" -H "Content-Type: application/json" \
  -d '{"description": "SuperYou protein shake and Epigamia Greek yogurt", "meal_type": "snack", "date": "2026-03-15"}'
curl -s -X POST "$BASE/meals" -H "Content-Type: application/json" \
  -d '{"description": "chicken masala with rice", "meal_type": "dinner", "date": "2026-03-15"}'
```
(Calories will be null until OpenAI quota is fixed — but meals will at least exist in DB.)

### 3. Telegram bot may still write to memory files
Confirmed working for basic replies, but unconfirmed whether `tools: {profile: "full"}` in openclaw.json actually enables curl execution. After fixing OpenAI quota, test by sending a meal to the bot and checking:
```bash
curl -s "http://localhost:8000/api/v1/meals/$(date +%Y-%m-%d)" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d), 'meals')"
```

### 4. March 16–17 meals not logged
You'll need to manually log or re-send to the bot after quota is fixed.

---

## VM details

| Item | Value |
|------|-------|
| SSH | `ssh -i <your.pem> ashiishk@<vm-ip>` |
| App dir | `/opt/transformation-coach/nouri-personal-ai/` |
| FastAPI service | `sudo systemctl [start\|stop\|restart\|status] coach-api` |
| OpenClaw service | `systemctl --user [start\|stop\|restart\|status] openclaw-gateway` |
| OpenClaw logs | `journalctl --user -u openclaw-gateway -f` |
| FastAPI logs | `journalctl -u coach-api -f` |
| nginx | `sudo systemctl status nginx` |
| DB location | `data/transformation.db` |
| .env location | `/opt/transformation-coach/nouri-personal-ai/.env` |
| OpenClaw config | `~/.openclaw/openclaw.json` |
| OpenClaw workspace | `~/.openclaw/workspace/` (SOUL.md, USER.md) |

## To deploy code changes from local

```bash
# On VM
cd /opt/transformation-coach/nouri-personal-ai
git pull
sudo systemctl restart coach-api
```

## Key env vars (in .env on VM)

```
OPENAI_API_KEY=sk-proj-...        # ← insufficient quota, needs billing credits
TELEGRAM_BOT_TOKEN=8743874883:...
TELEGRAM_USER_ID=536807264
ANTHROPIC_API_KEY=...             # Not currently used (OpenClaw uses OpenAI)
GOOGLE_SHEETS_ID=...
```

## Architecture reminder

```
Telegram → OpenClaw Gateway (Node.js, port 18789)
                ↓ curl to localhost:8000
         FastAPI Backend (Python, port 8000)
                ↓
         SQLite DB  +  Google Sheets (async)
                ↓
         React Dashboard (served by FastAPI at /)
```

OpenClaw handles ALL Telegram communication. Python never touches Telegram directly.

## Recent commits

```
7786a26 Auto-analyze meal descriptions on POST /meals
98e26f4 Force agent to use curl for all data logging
00875bc Update skills to use curl — fix agent logging to DB not memory files
fbfdd97 Add OpenClaw workspace files (SOUL.md, USER.md)
0882e67 Switch food photo analysis from Anthropic to OpenAI gpt-4o vision
e92498c Fix Google Sheets sync — wire up all write paths + backfill
63ad67f Fix openclaw.json schema for v2026.3.x
1bfc7aa Add complete Azure VM deployment script
```

## Next session — suggested order

1. Fix OpenAI quota (or switch to Gemini free tier)
2. Log March 15–17 meals manually via curl (commands above)
3. Verify Telegram bot correctly calls API for new meals
4. Log today's meals going forward via bot and confirm they appear in dashboard + Sheets
