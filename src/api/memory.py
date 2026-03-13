"""Memory/profile endpoint — read-only user profile for Settings page."""

import structlog
from fastapi import APIRouter

from src.services.memory_manager import get_user_profile

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/memory")
async def get_memory() -> dict:
    return get_user_profile()
