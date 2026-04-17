"""
API module for the Automated Book Generation System
"""

from fastapi import APIRouter
from app.api.v1 import books_router

api_router = APIRouter()

# Include v1 routes
api_router.include_router(
    books_router,
    prefix="/books",
    tags=["books"]
)
