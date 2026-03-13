# CLAUDE.md — Transformation Coach AI Application

## Project Overview

An AI-powered 8-week body transformation tracker with two agent personalities (Coach + Nutritionist), deployed via OpenClaw Gateway on an Azure VM with Telegram as the primary channel. Includes a minimal React dashboard and Google Sheets sync.

**User:** Ashish | **Goal:** 10-12% body fat by Oct 19, 2026 | **Supplement stack:** Multivitamins, Zinc, Omega-3

---

## Architecture (High Level)

```
┌─────────────────────────────────┐
│     Telegram (via OpenClaw)     │   ← OpenClaw Gateway handles Telegram channel
│     React Dashboard (Vite)      │   ← FastAPI serves static build + REST API
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│   OpenClaw Gateway (Node.js)    │   ← Runs on Azure VM, manages channels
│   ┌───────────────────────────┐ │
│   │ Agent: Coach ("Iron")     │ │   ← Lifestyle, gym, recovery, sleep, steps
│   │ Agent: Nutritionist       │ │   ← Food analysis, calories, macros, portions
│   │   ("Nouri")               │ │
│   └───────────────────────────┘ │
│   Skills: food-analyzer,        │   ← OpenClaw skills for domain expertise
│   calorie-tracker, meal-logger  │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│         Python Backend          │   ← FastAPI: REST API + services
│   SQLite ← source of truth     │
│   Google Sheets ← async mirror  │
│   memory.md ← user profile     │
│   APScheduler ← proactive msgs │
└─────────────────────────────────┘
```

---

## Key Decision: OpenClaw + Telegram (not python-telegram-bot)

OpenClaw replaces `python-telegram-bot`. Here's why and how:

**What OpenClaw does:**
- Runs as a Node.js Gateway process — handles Telegram Bot API via grammY internally
- Manages channels (Telegram, WhatsApp, iMessage via BlueBubbles, Discord — all from one gateway)
- Provides agent routing, sessions, streaming, inline buttons, media handling
- Has a built-in Control UI (web dashboard at `http://localhost:18789`)
- Supports skills (domain expertise loaded on demand) and tools

**What we still build in Python (FastAPI):**
- REST API for the React dashboard (`/api/v1/*`)
- Claude Vision API calls for food photo analysis
- SQLite database (meals, activities, measurements, sleep, steps)
- Google Sheets sync service
- memory.md manager
- Scheduled check-ins via APScheduler → sends messages through OpenClaw CLI or API

**How they connect:**
- OpenClaw Gateway receives Telegram messages → routes to the right agent (Coach or Nouri)
- Agents use OpenClaw skills that call our Python API endpoints for data operations
- Scheduled messages: APScheduler triggers → `openclaw message send --channel telegram --target <chat_id> --message "..."` 
- Python FastAPI runs alongside on the same VM (different port)

**Config (`~/.openclaw/openclaw.json`):**
```json
{
  "agent": {
    "model": "anthropic/claude-sonnet-4-20250514"
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "${TELEGRAM_BOT_TOKEN}",
      "dmPolicy": "allowlist",
      "allowFrom": ["${TELEGRAM_USER_ID}"]
    }
  }
}
```

---

## Deployment: Azure VM (Students Subscription)

**Azure for Students gives you $100 credit + free B1s VM (750 hrs/month for 12 months).**

We use the free **B1s VM** (1 vCPU, 1 GB RAM) — sufficient for a single-user bot + lightweight API.

**Why VM over App Service:**
- App Service Free tier (F1) has no always-on, sleeps after 20 min idle — kills the bot and scheduler
- App Service Basic (B1) costs ~$13/month — eats into $100 credit fast
- B1s VM is FREE for 750 hrs/month (essentially always-on for one VM) under Students plan
- VM gives full control: run Docker, OpenClaw, cron, anything

**VM Setup Plan:**
1. Create B1s Ubuntu 24.04 VM (Azure Portal → Virtual Machines)
2. Open ports: 22 (SSH), 80/443 (dashboard), 18789 (OpenClaw, optional internal only)
3. Install: Node 22+, Python 3.12, Docker (optional), SQLite
4. Install OpenClaw: `curl -fsSL https://openclaw.ai/install.sh | bash`
5. Run `openclaw onboard --install-daemon` (sets up as systemd service)
6. Deploy Python backend via systemd service or Docker
7. Nginx reverse proxy: port 80 → FastAPI (dashboard + API), port 18789 → OpenClaw Control UI
8. SSL via Let's Encrypt (certbot) if using a domain

**Cost Breakdown (Azure Students):**
- B1s VM: FREE (750 hrs/month included)
- 64 GB OS disk: FREE (included with VM)
- Public IP: ~$3/month (or free if you use Tailscale instead)
- Bandwidth: 15 GB/month free outbound
- **Total: ~$0-3/month from your $100 credit**

---

## Project Structure

```
transformation-coach/
├── CLAUDE.md                      # THIS FILE — project overview + conventions
│
├── .claude/
│   ├── agents/                    # Claude Code subagents (for development)
│   │   ├── backend-dev.md         # Backend development agent
│   │   ├── frontend-dev.md        # React dashboard agent
│   │   ├── openclaw-setup.md      # OpenClaw configuration agent
│   │   └── azure-deployer.md      # Azure VM deployment agent
│   │
│   └── skills/                    # Claude Code skills (for development)
│       ├── food-analyzer/
│       │   └── SKILL.md           # Claude Vision food photo analysis
│       ├── nutritionist-prompts/
│       │   └── SKILL.md           # Nouri agent system prompt + Indian food knowledge
│       ├── coach-prompts/
│       │   └── SKILL.md           # Iron agent system prompt + training science
│       ├── sheets-sync/
│       │   └── SKILL.md           # Google Sheets integration patterns
│       └── azure-vm-deploy/
│           └── SKILL.md           # Azure Students VM deployment guide
│
├── openclaw/                      # OpenClaw workspace & skills
│   ├── AGENTS.md                  # OpenClaw agent definitions (Coach + Nouri)
│   ├── skills/
│   │   ├── food-log/SKILL.md      # Skill: log meals via Python API
│   │   ├── body-metrics/SKILL.md  # Skill: log weight/waist/sleep/steps
│   │   └── daily-summary/SKILL.md # Skill: fetch & display daily summary
│   └── openclaw.json              # OpenClaw gateway config
│
├── src/                           # Python backend (FastAPI)
│   ├── main.py                    # Entry point — FastAPI + scheduler
│   ├── config.py                  # Pydantic Settings
│   ├── api/                       # REST API endpoints
│   │   ├── router.py
│   │   ├── today.py               # GET /api/v1/today
│   │   ├── meals.py               # GET /api/v1/meals/:date
│   │   ├── progress.py            # GET /api/v1/progress
│   │   ├── measurements.py        # GET /api/v1/measurements
│   │   └── stats.py               # GET /api/v1/stats
│   ├── services/
│   │   ├── food_analyzer.py       # Claude Vision → calorie estimation
│   │   ├── calorie_tracker.py     # Daily intake tracking
│   │   ├── measurement_tracker.py # Weight, waist, body fat
│   │   ├── memory_manager.py      # Read/write memory.md
│   │   └── sheets_sync.py         # Google Sheets async sync
│   ├── models/
│   │   ├── database.py            # SQLAlchemy async models
│   │   └── schemas.py             # Pydantic models
│   ├── scheduler/
│   │   └── check_ins.py           # APScheduler proactive messages via OpenClaw CLI
│   └── utils/
│       ├── prompts.py             # All system prompts (single source of truth)
│       └── helpers.py
│
├── dashboard/                     # React frontend (Vite + TypeScript + Tailwind)
│   ├── src/
│   │   ├── pages/                 # Today, History, Progress, Settings
│   │   └── components/            # ProgressRing, CalorieMeter, MacroBar, etc.
│   └── ...
│
├── memory/
│   └── memory.md                  # Persistent user profile
│
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── .env.example
└── azure/
    └── setup.sh                   # Azure VM provisioning script
```

---

## Implementation Phases

### Phase 1: Foundation
- Project scaffolding, config, SQLite models, memory.md manager
- FastAPI skeleton with health check

### Phase 2: OpenClaw Setup
- Install OpenClaw on dev machine, configure Telegram channel
- Define Coach + Nutritionist agents in AGENTS.md
- Create OpenClaw skills that bridge to Python API
- Test: send message → agent responds via Telegram

### Phase 3: Food Intelligence + Sheets
- Claude Vision food photo analysis (called from OpenClaw skill → Python API)
- Natural language meal logging
- Daily calorie/macro tracking
- Google Sheets sync (async, non-blocking)

### Phase 4: Lifestyle Tracking
- Sleep, steps, workout, measurement logging
- Weekly progress computation

### Phase 5: React Dashboard
- FastAPI REST endpoints (`/api/v1/*`)
- React app: Today, History, Progress pages
- Dark mode, mobile-first, Recharts

### Phase 6: Proactive Scheduler
- APScheduler sends messages via `openclaw message send`
- Smart skip logic, evening summary generation

### Phase 7: Azure VM Deployment
- Provision B1s VM, install Node + Python + OpenClaw
- Systemd services for OpenClaw gateway + Python backend
- Nginx reverse proxy + optional SSL
- Persistent storage for SQLite + memory.md

---

## Code Conventions

- Python 3.12+, async everywhere, type hints, Pydantic models
- Google-style docstrings, structlog for logging
- All prompts in `src/utils/prompts.py`
- No hardcoded values — everything via .env or memory.md

## Critical Rules

1. Never lose a meal log — if AI analysis fails, store raw input and retry
2. Calorie estimates are always ranges (low-high), never single numbers
3. Protein tracking is aggressive — flag if behind by lunch
4. Overeating → adjustment plan, never guilt
5. Indian food knowledge is essential for Nouri
6. SQLite is source of truth; Sheets is async mirror
7. Dashboard is read-only; all writes go through Telegram → OpenClaw → Python API
8. OpenClaw handles all Telegram communication; Python never talks to Telegram directly
9. Scheduled messages use `openclaw message send` CLI, not Telegram API

---

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_USER_ID=your_numeric_id
TIMEZONE=Asia/Kolkata
DATABASE_URL=sqlite+aiosqlite:///data/transformation.db
GOOGLE_SHEETS_ID=spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/google-service-account.json
DASHBOARD_PORT=8000
```

---

## Detailed Specs

For detailed specifications, Claude Code should read the relevant skill files:

| Topic | Skill/Agent File |
|-------|-----------------|
| Backend architecture, DB schema, API contracts | `.claude/skills/food-analyzer/SKILL.md` |
| Nutritionist personality, Indian food knowledge | `.claude/skills/nutritionist-prompts/SKILL.md` |
| Coach personality, training science | `.claude/skills/coach-prompts/SKILL.md` |
| Google Sheets tab structure, sync logic | `.claude/skills/sheets-sync/SKILL.md` |
| React dashboard design, pages, components | `.claude/agents/frontend-dev.md` |
| Azure VM setup, systemd, nginx | `.claude/skills/azure-vm-deploy/SKILL.md` |
| OpenClaw config, agents, skills | `.claude/agents/openclaw-setup.md` |

This keeps CLAUDE.md focused on the big picture while domain expertise lives in skills that load on demand.
