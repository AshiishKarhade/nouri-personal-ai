"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.router import api_router
from src.config import settings
from src.models.database import create_tables
from src.scheduler.check_ins import create_scheduler

log = structlog.get_logger(__name__)

# Resolve project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    log.info("Creating database tables...")
    await create_tables()
    log.info("Database tables ready")

    scheduler = create_scheduler()
    scheduler.start()
    log.info("Scheduler started", jobs=len(scheduler.get_jobs()))

    yield

    # ── Shutdown ─────────────────────────────────────────────────
    scheduler.shutdown(wait=False)
    log.info("Scheduler stopped")


app = FastAPI(
    title="Transformation Coach API",
    version="1.0.0",
    description="Backend for the 8-week body transformation tracker",
    lifespan=lifespan,
)

# CORS — allow Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ────────────────────────────────────────────────────────────────
app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
    }


# ── Static dashboard (React build) ───────────────────────────────────────────
if DASHBOARD_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(DASHBOARD_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str, request: Request):
        # Let API routes pass through (handled above)
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        index = DASHBOARD_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return JSONResponse({"detail": "Dashboard not built yet. Run: cd dashboard && npm run build"}, status_code=404)
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "message": "Transformation Coach API",
            "docs": "/docs",
            "dashboard": "Run `cd dashboard && npm run build` to build the React dashboard",
        }
