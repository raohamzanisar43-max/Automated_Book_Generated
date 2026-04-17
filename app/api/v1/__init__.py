"""
API v1 module for the Automated Book Generation System
"""

from fastapi import APIRouter
from .books import router as books_router
from .database import router as database_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    books_router,
    prefix="/books",
    tags=["books"]
)

api_router.include_router(
    database_router,
    prefix="/database",
    tags=["database"]
)

__all__ = ["api_router", "books_router"]
