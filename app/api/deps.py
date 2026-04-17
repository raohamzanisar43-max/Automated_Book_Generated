from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import settings
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_db_session(db: AsyncSession = Depends(get_db)):
    """Dependency to get current database session"""
    return db

# Simple authentication (you may want to replace with JWT or OAuth)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token"""
    # For now, we'll use a simple token verification
    # In production, implement proper JWT validation
    token = credentials.credentials
    
    if token != settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": "demo_user"}  # Return user info

# Optional authentication for endpoints that don't require auth
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication - returns None if no valid token"""
    try:
        return await verify_token(credentials)
    except HTTPException:
        return None
