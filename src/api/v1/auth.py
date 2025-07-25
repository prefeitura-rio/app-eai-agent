from fastapi import APIRouter, HTTPException

from src.config import env

router = APIRouter()

import logging

logger = logging.getLogger(__name__)


@router.get("/auth", tags=["Authentication"])
async def check_auth(token: str):
    """
    Endpoint to check if the provided token is valid.
    A successful response (200 OK) indicates a valid token.
    An unsuccessful response (401 Unauthorized) indicates an invalid token.
    """
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token is required",
        )

    if token != env.EAI_AGENT_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    return {"status": "ok"}
