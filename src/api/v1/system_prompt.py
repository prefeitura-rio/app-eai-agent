from fastapi import APIRouter, Depends, Body, HTTPException, status
from typing import Dict, List, Optional

from src.core.security.dependencies import validar_token
from src.services.letta.system_prompt_service import system_prompt_service
from src.schemas.system_prompt_schema import (
    SystemPromptUpdateRequest,
    SystemPromptUpdateResponse,
    SystemPromptGetResponse
)

router = APIRouter(prefix="/system-prompt", tags=["System Prompt"], dependencies=[Depends(validar_token)])


@router.get("", response_model=SystemPromptGetResponse)
async def get_system_prompt(
    agent_type: str = "agentic_search"
):
    """
    Obtém o system prompt atual para o tipo de agente especificado.
    
    Args:
        agent_type: Tipo do agente
        
    Returns:
        SystemPromptGetResponse: Resposta contendo o system prompt atual
    """
    try:
        prompt = await system_prompt_service.get_current_system_prompt(agent_type)
        return SystemPromptGetResponse(
            prompt=prompt,
            agent_type=agent_type
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter system prompt: {str(e)}"
        )


@router.post("", response_model=SystemPromptUpdateResponse)
async def update_system_prompt(
    request: SystemPromptUpdateRequest = Body(...),
):
    """
    Atualiza o system prompt no template e/ou em todos os agentes existentes.
    
    Args:
        request: Dados para atualização do system prompt
        
    Returns:
        SystemPromptUpdateResponse: Resposta contendo o resultado da operação
    """
    try:
        result = await system_prompt_service.update_system_prompt(
            new_prompt=request.new_prompt,
            agent_type=request.agent_type,
            update_template=request.update_template,
            update_agents=request.update_agents,
            tags=request.tags
        )
        
        message = "System prompt atualizado com sucesso"
        
        if request.update_template and result["template_updated"]:
            message += ", template foi atualizado"
        
        if request.update_agents:
            updated_agents = sum(1 for success in result["agents_updated"].values() if success)
            total_agents = len(result["agents_updated"])
            
            if total_agents > 0:
                message += f", {updated_agents}/{total_agents} agentes foram atualizados"
        
        return SystemPromptUpdateResponse(
            success=result["success"],
            template_updated=result.get("template_updated", False),
            agents_updated=result.get("agents_updated", {}),
            message=message
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar system prompt: {str(e)}"
        ) 