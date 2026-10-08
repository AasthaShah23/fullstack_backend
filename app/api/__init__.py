"""
API package — aggregates all versioned routers.

Add new feature routers here so main.py stays clean.
"""

from fastapi import APIRouter

from app.api.auth import auth_router

api_router = APIRouter(prefix="/api")

# --- Feature routers --------------------------------------------------------
api_router.include_router(auth_router)
# api_router.include_router(users_router)   # future: user management
# api_router.include_router(products_router) # future: products

__all__ = ["api_router"]

