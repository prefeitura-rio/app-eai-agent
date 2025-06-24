from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.services.letta.letta_service import letta_service
from src.db import get_db

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
    dependencies=[Depends(validar_token)],
)


@router.delete("/tests", status_code=200)
async def delete_test_agents():
    """Remove todos os agentes que possuam a tag 'test'."""
    try:
        await letta_service.deletar_agentes_teste()
        return {"success": True, "message": "Agentes de teste removidos"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar agentes de teste: {str(e)}",
        ) 