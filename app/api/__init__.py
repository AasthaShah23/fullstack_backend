"""
API package — aggregates all versioned routers.

Add new feature routers here so main.py stays clean.
"""

from fastapi import APIRouter

from app.api.admin import admin_router
from app.api.auth import auth_router
from app.api.profile import profile_router

api_router = APIRouter(prefix="/api")

# --- Feature routers --------------------------------------------------------
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(profile_router)

__all__ = ["api_router"]
