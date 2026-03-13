"""Aggregate all API sub-routers under /api/v1."""

from fastapi import APIRouter

from src.api.history import router as history_router
from src.api.meals import router as meals_router
from src.api.measurements import router as measurements_router
from src.api.memory import router as memory_router
from src.api.progress import router as progress_router
from src.api.stats import router as stats_router
from src.api.today import router as today_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(today_router, tags=["today"])
api_router.include_router(meals_router, tags=["meals"])
api_router.include_router(measurements_router, tags=["measurements"])
api_router.include_router(progress_router, tags=["progress"])
api_router.include_router(history_router, tags=["history"])
api_router.include_router(stats_router, tags=["stats"])
api_router.include_router(memory_router, tags=["memory"])
