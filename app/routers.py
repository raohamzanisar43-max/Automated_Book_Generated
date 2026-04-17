from fastapi import APIRouter
from app.api.v1 import books_router

router = APIRouter()

# Include books router
router.include_router(
    books_router,
    prefix="/books",
    tags=["books"]
)
