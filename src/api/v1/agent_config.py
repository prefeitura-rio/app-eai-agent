from fastapi import APIRouter, Depends, Body, HTTPException, status, Query
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.db import get_db
from src.services.agent_settings.agent_config_service import agent_config_service
from src.repositories.agent_config_repository import AgentConfigRepository
from src.schemas.agent_config_schema import (
    AgentConfigUpdateRequest,
    AgentConfigUpdateResponse,
    AgentConfigGetResponse,
    AgentConfigHistoryResponse,
    AgentConfigHistoryItem,
    AgentConfigResetResponse,
)

router = APIRouter(
    prefix="/agent-config",
    tags=["Agent Config"],
    dependencies=[Depends(validar_token)],
)

DEFAULT_AGENT_TYPE = "agentic_search"


@router.get("", response_model=AgentConfigGetResponse)
async def get_agent_config(
    agent_type: str = DEFAULT_AGENT_TYPE, db: Session = Depends(get_db)
):
    """Obtém a configuração atual (ativa) para o tipo de agente especificado."""
    try:
        agent_type = (agent_type or "").strip() or DEFAULT_AGENT_TYPE
        cfg = await agent_config_service.get_current_config(agent_type, db)
        active_cfg = AgentConfigRepository.get_active_config(db, agent_type)
        return AgentConfigGetResponse(
            config_id=cfg.get("config_id"),
            agent_type=agent_type,
            version=active_cfg.version if active_cfg else None,
            memory_blocks=cfg.get("memory_blocks"),
            tools=cfg.get("tools"),
            model_name=cfg.get("model_name"),
            embedding_name=cfg.get("embedding_name"),
            created_at=(
                active_cfg.created_at.isoformat()
                if active_cfg and active_cfg.created_at
                else None
            ),
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter configuração do agente: {str(e)}",
        )


@router.post("", response_model=AgentConfigUpdateResponse)
async def update_agent_config(
    request: AgentConfigUpdateRequest = Body(...), db: Session = Depends(get_db)
):
    """Atualiza a configuração do agente no banco de dados."""
    try:
        new_cfg_values = {
            "memory_blocks": request.memory_blocks,
            "tools": request.tools,
            "model_name": request.model_name,
            "embedding_name": request.embedding_name,
        }

        result = await agent_config_service.update_agent_configs(
            new_cfg_values=new_cfg_values,
            agent_type=(request.agent_type or "").strip() or DEFAULT_AGENT_TYPE,
            metadata=request.metadata,
            db=db,
        )

        message = "Configuração de agente atualizada com sucesso"

        return AgentConfigUpdateResponse(
            success=result["success"],
            config_id=result.get("config_id"),
            message=message,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar configuração: {str(e)}",
        )


@router.get("/history", response_model=AgentConfigHistoryResponse)
async def get_agent_config_history(
    agent_type: str = DEFAULT_AGENT_TYPE,
    limit: int = Query(10, ge=1, description="Limite de resultados"),
    db: Session = Depends(get_db),
):
    """Obtém histórico de configurações."""
    try:
        agent_type = (agent_type or "").strip() or DEFAULT_AGENT_TYPE
        history = await agent_config_service.get_config_history(agent_type, limit, db)
        configs = [AgentConfigHistoryItem(**item) for item in history]
        return AgentConfigHistoryResponse(agent_type=agent_type, configs=configs)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter histórico de configurações: {str(e)}",
        )


@router.get("/by-id/{config_id}", response_model=AgentConfigGetResponse)
async def get_agent_config_by_id(config_id: str, db: Session = Depends(get_db)):
    """Obtém uma configuração específica pelo ID."""
    try:
        cfg = AgentConfigRepository.get_config_by_id(db, config_id)
        if not cfg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuração com ID {config_id} não encontrada",
            )

        return AgentConfigGetResponse(
            config_id=cfg.config_id,
            agent_type=cfg.agent_type,
            version=cfg.version,
            memory_blocks=cfg.memory_blocks,
            tools=cfg.tools,
            model_name=cfg.model_name,
            embedding_name=cfg.embedding_name,
            created_at=cfg.created_at.isoformat() if cfg.created_at else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter configuração por ID: {str(e)}",
        )


@router.delete("/reset", response_model=AgentConfigResetResponse)
async def reset_agent_config(
    agent_type: str = Query(DEFAULT_AGENT_TYPE, description="Tipo do agente para resetar config"),
    db: Session = Depends(get_db),
):
    """Remove todas as configs e restaura padrão."""
    try:
        agent_type = (agent_type or "").strip() or DEFAULT_AGENT_TYPE

        result = await agent_config_service.reset_agent_config(
            agent_type=agent_type, db=db
        )

        message = "Configuração resetada com sucesso"

        return AgentConfigResetResponse(
            success=result["success"],
            agent_type=agent_type,
            message=message,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao resetar configuração: {str(e)}",
        )
