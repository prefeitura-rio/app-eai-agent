from fastapi import APIRouter, Depends, Body, HTTPException, status, Query
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.db import get_db
from src.services.letta.system_prompt_service import system_prompt_service
from src.services.letta.letta_service import letta_service
from src.repositories.system_prompt_repository import SystemPromptRepository
from src.schemas.system_prompt_schema import (
    SystemPromptUpdateRequest,
    SystemPromptUpdateResponse,
    SystemPromptGetResponse,
    SystemPromptHistoryResponse,
    SystemPromptHistoryItem,
    SystemPromptResetResponse,
    SystemPromptDeleteResponse,
)

router = APIRouter(
    prefix="/system-prompt",
    tags=["System Prompt"],
    dependencies=[Depends(validar_token)],
)


@router.get("/agent-types", response_model=List[str])
async def get_agent_types():
    """
    Obtém os tipos de agentes disponíveis baseados nas tags que contêm 'agentic'.

    Returns:
        List[str]: Lista de tags de agentes
    """
    try:
        agent_types = await letta_service.get_agentic_tags()
        return agent_types
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter tipos de agentes: {str(e)}",
        )


@router.get("", response_model=SystemPromptGetResponse)
async def get_system_prompt(
    agent_type: str = "agentic_search", db: Session = Depends(get_db)
):
    """
    Obtém o system prompt atual para o tipo de agente especificado.

    Args:
        agent_type: Tipo do agente
        db: Sessão do banco de dados

    Returns:
        SystemPromptGetResponse: Resposta contendo o system prompt atual
    """
    try:
        if not agent_type or agent_type.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário especificar um tipo de agente válido",
            )

        prompt_text = await system_prompt_service.get_current_system_prompt(
            agent_type, db
        )

        active_prompt = SystemPromptRepository.get_active_prompt(db, agent_type)
        if active_prompt:
            return SystemPromptGetResponse(
                prompt=prompt_text,
                agent_type=agent_type,
                version=active_prompt.version,
                prompt_id=active_prompt.prompt_id,
                created_at=active_prompt.created_at,
            )
        else:
            return SystemPromptGetResponse(prompt=prompt_text, agent_type=agent_type)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter system prompt: {str(e)}",
        )


@router.post("", response_model=SystemPromptUpdateResponse)
async def update_system_prompt(
    request: SystemPromptUpdateRequest = Body(...), db: Session = Depends(get_db)
):
    """
    Atualiza o system prompt e/ou em todos os agentes existentes.

    Args:
        request: Dados para atualização do system prompt
        db: Sessão do banco de dados

    Returns:
        SystemPromptUpdateResponse: Resposta contendo o resultado da operação
    """
    try:
        result = await system_prompt_service.update_system_prompt(
            new_prompt=request.new_prompt,
            agent_type=request.agent_type,
            update_agents=request.update_agents,
            tags=request.tags,
            metadata=request.metadata,
            db=db,
        )

        message = "System prompt atualizado com sucesso"

        if request.update_agents:
            updated_agents = sum(
                1 for success in result["agents_updated"].values() if success
            )
            total_agents = len(result["agents_updated"])

            if total_agents > 0:
                message += (
                    f", {updated_agents}/{total_agents} agentes foram atualizados"
                )

        return SystemPromptUpdateResponse(
            success=result["success"],
            prompt_id=result.get("prompt_id"),
            agents_updated=result.get("agents_updated", {}),
            message=message,
            version=result.get("unified_version", None),
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar system prompt: {str(e)}",
        )


@router.get("/history", response_model=SystemPromptHistoryResponse)
async def get_system_prompt_history(
    agent_type: str = "agentic_search",
    limit: int = Query(10, ge=1, description="Limite de resultados"),
    db: Session = Depends(get_db),
):
    """
    Obtém o histórico de versões de system prompts para um tipo de agente.

    Args:
        agent_type: Tipo do agente
        limit: Limite de resultados
        db: Sessão do banco de dados

    Returns:
        SystemPromptHistoryResponse: Histórico de versões
    """
    try:
        history = await system_prompt_service.get_prompt_history(
            agent_type=agent_type, limit=limit, db=db
        )

        prompts = [SystemPromptHistoryItem(**item) for item in history]

        return SystemPromptHistoryResponse(agent_type=agent_type, prompts=prompts)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter histórico de system prompts: {str(e)}",
        )


@router.get("/by-id/{prompt_id}", response_model=SystemPromptGetResponse)
async def get_system_prompt_by_id(prompt_id: str, db: Session = Depends(get_db)):
    """
    Obtém um system prompt específico pelo ID.

    Args:
        prompt_id: ID do system prompt
        db: Sessão do banco de dados

    Returns:
        SystemPromptGetResponse: Resposta contendo o system prompt específico
    """
    try:
        prompt = SystemPromptRepository.get_prompt_by_id(db, prompt_id)

        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"System prompt com ID {prompt_id} não encontrado",
            )

        return SystemPromptGetResponse(
            prompt=prompt.content,
            agent_type=prompt.agent_type,
            version=prompt.version,
            prompt_id=prompt.prompt_id,
            created_at=prompt.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter system prompt por ID: {str(e)}",
        )


@router.delete("/last", response_model=SystemPromptDeleteResponse)
async def delete_last_system_prompt(
    agent_type: str = Query(..., description="Tipo do agente"),
    update_agents: bool = Query(
        False, description="Atualizar também os agentes existentes com o prompt anterior"
    ),
    db: Session = Depends(get_db),
):
    """
    Deleta apenas o último system prompt do histórico e reativa o anterior.
    
    Este endpoint é útil quando você quer desfazer a última atualização de prompt
    sem perder todo o histórico.

    Args:
        agent_type: Tipo do agente
        update_agents: Se verdadeiro, também atualiza os agentes existentes com o prompt anterior
        db: Sessão do banco de dados

    Returns:
        SystemPromptDeleteResponse: Resposta contendo o resultado da operação
        
    Raises:
        HTTPException 400: Se não houver prompts suficientes para deletar
        HTTPException 500: Se houver erro durante a operação
    """
    try:
        if not agent_type or agent_type.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário especificar um tipo de agente válido",
            )

        result = await system_prompt_service.delete_last_system_prompt(
            agent_type=agent_type, update_agents=update_agents, db=db
        )

        message = f"Versão {result['deleted_version']} deletada, versão {result['active_version']} agora está ativa"

        if update_agents:
            updated_agents = sum(
                1 for success in result["agents_updated"].values() if success
            )
            total_agents = len(result["agents_updated"])

            if total_agents > 0:
                message += (
                    f", {updated_agents}/{total_agents} agentes foram atualizados"
                )

        return SystemPromptDeleteResponse(
            success=result["success"],
            agent_type=agent_type,
            deleted_version=result.get("deleted_version"),
            active_version=result.get("active_version"),
            previous_prompt_id=result.get("previous_prompt_id"),
            agents_updated=result.get("agents_updated", {}),
            message=message,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar último system prompt: {str(e)}",
        )


@router.delete("/reset", response_model=SystemPromptResetResponse)
async def reset_system_prompt(
    agent_type: str = Query(..., description="Tipo do agente para resetar o prompt"),
    update_agents: bool = Query(
        False, description="Atualizar também os agentes existentes"
    ),
    db: Session = Depends(get_db),
):
    """
    Remove todos os system prompts históricos para o tipo de agente especificado
    e restaura para o valor padrão.

    Args:
        agent_type: Tipo do agente
        update_agents: Se verdadeiro, também atualiza os agentes existentes
        db: Sessão do banco de dados

    Returns:
        SystemPromptResetResponse: Resposta contendo o resultado da operação
    """
    try:
        if not agent_type or agent_type.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário especificar um tipo de agente válido",
            )

        result = await system_prompt_service.reset_system_prompt(
            agent_type=agent_type, update_agents=update_agents, db=db
        )

        message = "System prompt resetado com sucesso"

        if update_agents:
            updated_agents = sum(
                1 for success in result["agents_updated"].values() if success
            )
            total_agents = len(result["agents_updated"])

            if total_agents > 0:
                message += (
                    f", {updated_agents}/{total_agents} agentes foram atualizados"
                )

        return SystemPromptResetResponse(
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
            detail=f"Erro ao resetar system prompt: {str(e)}",
        )
