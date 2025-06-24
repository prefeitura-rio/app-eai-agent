from fastapi import APIRouter, Depends, Body, HTTPException, status, Query
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.db import get_db
from src.services.letta.agent_config_service import agent_config_service
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


@router.get("", response_model=AgentConfigGetResponse)
async def get_agent_config(
    agent_type: str = "agentic_search", db: Session = Depends(get_db)
):
    """Obtém a configuração atual (ativa) para o tipo de agente especificado."""
    try:
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
            created_at=active_cfg.created_at.isoformat() if active_cfg and active_cfg.created_at else None,
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
    """Atualiza a configuração do agente e, opcionalmente, propaga para agentes existentes."""
    try:
        new_cfg_values = {
            "memory_blocks": request.memory_blocks,
            "tools": request.tools,
            "model_name": request.model_name,
            "embedding_name": request.embedding_name,
        }

        result = await agent_config_service.update_agent_configs(
            new_cfg_values=new_cfg_values,
            agent_type=request.agent_type,
            update_agents=request.update_agents,
            tags=request.tags,
            metadata=request.metadata,
            db=db,
        )

        message = "Configuração de agente atualizada com sucesso"
        if request.update_agents:
            updated_agents = sum(1 for success in result["agents_updated"].values() if success)
            total_agents = len(result["agents_updated"])
            if total_agents > 0:
                message += f", {updated_agents}/{total_agents} agentes foram atualizados"

        return AgentConfigUpdateResponse(
            success=result["success"],
            config_id=result.get("config_id"),
            agents_updated=result.get("agents_updated", {}),
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
    agent_type: str = "agentic_search",
    limit: int = Query(10, ge=1, description="Limite de resultados"),
    db: Session = Depends(get_db),
):
    """Obtém histórico de configurações."""
    try:
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
    agent_type: str = Query(..., description="Tipo do agente para resetar config"),
    update_agents: bool = Query(False, description="Atualizar também os agentes existentes"),
    db: Session = Depends(get_db),
):
    """Remove todas as configs e restaura padrão."""
    try:
        if not agent_type or agent_type.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário especificar um tipo de agente válido",
            )

        result = await agent_config_service.reset_agent_config(
            agent_type=agent_type, update_agents=update_agents, db=db
        )

        message = "Configuração resetada com sucesso"
        if update_agents:
            upd = sum(1 for s in result["agents_updated"].values() if s)
            total = len(result["agents_updated"])
            if total > 0:
                message += f", {upd}/{total} agentes foram atualizados"

        return AgentConfigResetResponse(
            success=result["success"],
            agent_type=agent_type,
            agents_updated=result.get("agents_updated", {}),
            message=message,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao resetar configuração: {str(e)}",
        ) 