from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.db import get_db
from src.services.letta.unified_history_service import unified_history_service
from src.schemas.unified_history_schema import (
    UnifiedHistoryResponse,
    UnifiedHistoryItem,
    UnifiedVersionDetailsResponse,
)

router = APIRouter(
    prefix="/unified-history",
    tags=["Unified History"],
    dependencies=[Depends(validar_token)],
)


@router.get("", response_model=UnifiedHistoryResponse)
async def get_unified_history(
    agent_type: str = Query("agentic_search", description="Tipo do agente"),
    limit: int = Query(50, ge=1, le=200, description="Limite de resultados"),
    db: Session = Depends(get_db),
):
    """
    Obtém o histórico unificado de alterações (system prompts e configurações)
    para um tipo de agente.

    Args:
        agent_type: Tipo do agente
        limit: Limite de resultados (1-200)
        db: Sessão do banco de dados

    Returns:
        UnifiedHistoryResponse: Histórico unificado de alterações
    """
    try:
        history = await unified_history_service.get_unified_history(
            agent_type=agent_type, limit=limit, db=db
        )

        items = [UnifiedHistoryItem(**item) for item in history]

        return UnifiedHistoryResponse(
            agent_type=agent_type,
            total_items=len(items),
            items=items
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter histórico unificado: {str(e)}",
        )


@router.get("/version/{version_number}", response_model=UnifiedVersionDetailsResponse)
async def get_version_details(
    version_number: int,
    agent_type: str = Query("agentic_search", description="Tipo do agente"),
    db: Session = Depends(get_db),
):
    """
    Obtém detalhes completos de uma versão específica do histórico unificado.

    Args:
        version_number: Número da versão
        agent_type: Tipo do agente
        db: Sessão do banco de dados

    Returns:
        UnifiedVersionDetailsResponse: Detalhes completos da versão
    """
    try:
        details = await unified_history_service.get_version_details(
            agent_type=agent_type, version_number=version_number, db=db
        )

        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Versão {version_number} não encontrada para o tipo de agente {agent_type}",
            )

        return UnifiedVersionDetailsResponse(**details)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter detalhes da versão: {str(e)}",
        ) 