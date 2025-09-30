"""Authentication utilities"""

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from api.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key for admin endpoints.

    Args:
        api_key: API key from request header

    Returns:
        The verified API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key"
        )
    return api_key