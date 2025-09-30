"""Health check routes"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from api.database import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic API health check"""
    return {
        "status": "healthy",
        "service": "lunaxcode-api",
        "version": "0.1.0"
    }


@router.get("/db")
async def database_health(db: AsyncSession = Depends(get_db)):
    """Database connection health check"""
    try:
        # Execute simple query to test connection
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }