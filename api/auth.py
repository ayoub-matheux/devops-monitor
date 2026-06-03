"""API key authentication dependency."""

import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY", "dev-secret-key")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(key: str = Security(api_key_header)) -> str:
    """Validate the X-API-Key header.

    Raises HTTP 403 if the key is missing or invalid.
    """
    if key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key.",
        )
    return key
