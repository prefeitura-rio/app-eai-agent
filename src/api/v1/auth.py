from fastapi import APIRouter, Depends, HTTPException

from src.config import env
from src.core.security.dependencies import validar_token

router = APIRouter(
    dependencies=[Depends(validar_token)],
)


@router.get("/auth", tags=["Authentication"])
async def check_auth():
    """
    Endpoint to check if the provided token is valid.
    A successful response (200 OK) indicates a valid token.
    An unsuccessful response (401 Unauthorized) indicates an invalid token.
    """

    return {"status": "ok"}
