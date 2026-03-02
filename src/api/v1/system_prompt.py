from fastapi import APIRouter, Depends, Body, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.db import get_db
from src.services.letta.system_prompt_service import system_prompt_service
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

DEFAULT_AGENT_TYPE = "agentic_search"


@router.get("", response_model=SystemPromptGetResponse)
async def get_system_prompt(
    agent_type: str = DEFAULT_AGENT_TYPE, db: Session = Depends(get_db)
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
        agent_type = (agent_type or "").strip() or DEFAULT_AGENT_TYPE

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
            agent_type=(request.agent_type or "").strip() or DEFAULT_AGENT_TYPE,
            metadata=request.metadata,
            db=db,
        )

        message = "System prompt atualizado com sucesso"

        return SystemPromptUpdateResponse(
            success=result["success"],
            prompt_id=result.get("prompt_id"),
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
    agent_type: str = DEFAULT_AGENT_TYPE,
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
        agent_type = (agent_type or "").strip() or DEFAULT_AGENT_TYPE
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
    agent_type: str = Query(DEFAULT_AGENT_TYPE, description="Tipo do agente"),
    db: Session = Depends(get_db),
):
    """
    Deleta apenas o último system prompt do histórico e reativa o anterior.
    
    Este endpoint é útil quando você quer desfazer a última atualização de prompt
    sem perder todo o histórico.

    Args:
        agent_type: Tipo do agente
        db: Sessão do banco de dados

    Returns:
        SystemPromptDeleteResponse: Resposta contendo o resultado da operação
        
    Raises:
        HTTPException 400: Se não houver prompts suficientes para deletar
        HTTPException 500: Se houver erro durante a operação
    """
    try:
        agent_type = (agent_type or "").strip() or DEFAULT_AGENT_TYPE

        result = await system_prompt_service.delete_last_system_prompt(
            agent_type=agent_type, db=db
        )

        message = f"Versão {result['deleted_version']} deletada, versão {result['active_version']} agora está ativa"

        return SystemPromptDeleteResponse(
            success=result["success"],
            agent_type=agent_type,
            deleted_version=result.get("deleted_version"),
            active_version=result.get("active_version"),
            previous_prompt_id=result.get("previous_prompt_id"),
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
    agent_type: str = Query(DEFAULT_AGENT_TYPE, description="Tipo do agente para resetar o prompt"),
    db: Session = Depends(get_db),
):
    """
    Remove todos os system prompts históricos para o tipo de agente especificado
    e restaura para o valor padrão.

    Args:
        agent_type: Tipo do agente
        db: Sessão do banco de dados

    Returns:
        SystemPromptResetResponse: Resposta contendo o resultado da operação
    """
    try:
        agent_type = (agent_type or "").strip() or DEFAULT_AGENT_TYPE

        result = await system_prompt_service.reset_system_prompt(
            agent_type=agent_type, db=db
        )

        message = "System prompt resetado com sucesso"

        return SystemPromptResetResponse(
            success=result["success"],
            agent_type=agent_type,
            message=message,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao resetar system prompt: {str(e)}",
        )
