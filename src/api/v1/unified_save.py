from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from loguru import logger

from src.core.security.dependencies import validar_token
from src.db import get_db_session
from src.repositories.unified_version_repository import UnifiedVersionRepository
from src.repositories.system_prompt_repository import SystemPromptRepository
from src.repositories.agent_config_repository import AgentConfigRepository
from src.services.letta.system_prompt_service import system_prompt_service
from src.services.letta.agent_config_service import agent_config_service
from src.services.discord.notification_service import discord_service

router = APIRouter(
    prefix="/unified-save",
    tags=["Unified Save"],
    dependencies=[Depends(validar_token)],
)


class UnifiedSaveRequest(BaseModel):
    """Schema para salvar alterações unificadas."""
    agent_type: str = Field(..., description="Tipo do agente")
    prompt_content: Optional[str] = Field(None, description="Conteúdo do system prompt")
    clickup_cards: Optional[List[Dict[str, Any]]] = Field(None, description="ClickUp cards")
    tools: Optional[List[str]] = Field(None, description="Lista de ferramentas")
    model_name: Optional[str] = Field(None, description="Nome do modelo")
    embedding_name: Optional[str] = Field(None, description="Nome do embedding")
    update_agents: bool = Field(False, description="Atualizar agentes existentes")
    author: Optional[str] = Field(None, description="Autor da alteração")
    reason: Optional[str] = Field(None, description="Motivo da alteração")


class UnifiedSaveResponse(BaseModel):
    """Schema para resposta do save unificado."""
    success: bool
    unified_version_number: int
    version_display: str
    change_type: str
    prompt_id: Optional[str] = None
    config_id: Optional[str] = None
    agents_updated: Dict[str, bool] = Field(default_factory=dict)
    message: str


@router.post("", response_model=UnifiedSaveResponse)
async def save_unified_changes(request: UnifiedSaveRequest):
    """
    Salva alterações unificadas em prompt e/ou configuração em uma única versão.
    
    Returns:
        UnifiedSaveResponse: Resultado da operação
    """
    try:
        # Determinar tipo de alteração
        has_prompt_changes = request.prompt_content is not None
        has_config_changes = any([
            request.clickup_cards is not None,
            request.tools is not None,
            request.model_name is not None,
            request.embedding_name is not None
        ])
        
        if not has_prompt_changes and not has_config_changes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário fornecer pelo menos uma alteração (prompt ou configuração)"
            )
        
        change_type = "both" if (has_prompt_changes and has_config_changes) else (
            "prompt" if has_prompt_changes else "config"
        )

        result = {
            "success": True,
            "change_type": change_type,
            "agents_updated": {},
            "message": "Alterações salvas com sucesso"
        }

        with get_db_session() as db:
            # Obter próximo número de versão
            version_number = UnifiedVersionRepository.get_next_version_number(db, request.agent_type)
            
            # Gerar nome da versão no padrão eai-YYYY-MM-DD-vX (horário do Brasil)
            from datetime import datetime, timezone, timedelta
            brazil_tz = timezone(timedelta(hours=-3))  # UTC-3 (horário de Brasília)
            today = datetime.now(brazil_tz)
            version_display = f"eai-{today.strftime('%Y-%m-%d')}-v{version_number}"
            
            prompt_id = None
            config_id = None
            
            # Obter configuração atual para usar como base (mesmo se não houver mudanças de config)
            current_config = AgentConfigRepository.get_active_config(db, request.agent_type)
            
            # Preparar valores de configuração (usar valores fornecidos ou fallback para configuração atual)
            clickup_cards_value = request.clickup_cards if request.clickup_cards is not None else (current_config.memory_blocks if current_config else [])
            tools_value = request.tools if request.tools is not None else (current_config.tools if current_config else [])
            model_name_value = request.model_name if request.model_name is not None else (current_config.model_name if current_config else "")
            embedding_name_value = request.embedding_name if request.embedding_name is not None else (current_config.embedding_name if current_config else "")
            
            # Salvar prompt se fornecido
            if has_prompt_changes:
                prompt = SystemPromptRepository.create_prompt(
                    db=db,
                    agent_type=request.agent_type,
                    content=request.prompt_content,
                    version=version_number,
                    metadata={
                        "author": request.author or "API",
                        "reason": request.reason or "Alteração via API",
                        "version_display": version_display
                    },
                )
                prompt_id = prompt.prompt_id

            # Salvar configuração se fornecida
            if has_config_changes:
                
                config = AgentConfigRepository.create_config(
                    db=db,
                    agent_type=request.agent_type,
                    memory_blocks=clickup_cards_value,
                    tools=tools_value,
                    model_name=model_name_value,
                    embedding_name=embedding_name_value,
                    version=version_number,
                    metadata={
                        "author": request.author or "API",
                        "reason": request.reason or "Alteração via API",
                        "version_display": version_display
                    },
                )
                config_id = config.config_id

            # Criar entrada de versão unificada
            unified_version = UnifiedVersionRepository.create_version(
                db=db,
                agent_type=request.agent_type,
                change_type=change_type,
                prompt_id=prompt_id,
                config_id=config_id,
                author=request.author or "API",
                reason=request.reason or "Alteração via API",
                description=f"Versão {version_display} - {change_type}",
                metadata={
                    "version_display": version_display,
                    "author": request.author or "API",
                    "reason": request.reason or "Alteração via API"
                },
            )

            result.update({
                "unified_version_number": unified_version.version_number,
                "version_display": version_display,
                "prompt_id": str(prompt_id) if prompt_id else None,
                "config_id": str(config_id) if config_id else None,
            })

            # Atualizar agentes se solicitado
            if request.update_agents:
                agents_results = {}
                
                # Atualizar agentes com prompt se foi alterado
                if has_prompt_changes:
                    prompt_agents_result = await system_prompt_service.update_all_agents_system_prompt(
                        new_prompt=request.prompt_content,
                        agent_type=request.agent_type,
                        tags=[request.agent_type],
                        db=db,
                        prompt_id=str(prompt_id),
                    )
                    agents_results.update(prompt_agents_result)

                # Atualizar agentes com configuração se foi alterada
                if has_config_changes:
                    config_values = {
                        "memory_blocks": clickup_cards_value,
                        "tools": tools_value,
                        "model_name": model_name_value,
                        "embedding_name": embedding_name_value,
                    }
                    
                    config_agents_result = await agent_config_service._update_all_agents(
                        new_cfg_values=config_values,
                        agent_type=request.agent_type,
                        tags=[request.agent_type],
                    )
                    
                    # Combinar resultados (se um agente falhou em qualquer atualização, marca como falso)
                    for agent_id, config_success in config_agents_result.items():
                        prompt_success = agents_results.get(agent_id, True)
                        agents_results[agent_id] = prompt_success and config_success

                result["agents_updated"] = agents_results

                # Verificar se todos os agentes foram atualizados com sucesso
                if agents_results and not all(agents_results.values()):
                    result["success"] = False
                    result["message"] = "Alterações salvas mas alguns agentes não foram atualizados"
                
                # Atualizar mensagem com estatísticas dos agentes
                if agents_results:
                    updated_count = sum(1 for success in agents_results.values() if success)
                    total_count = len(agents_results)
                    result["message"] += f", {updated_count}/{total_count} agentes foram atualizados"

            # Send Discord notification for production environment
            try:
                await discord_service.send_prompt_version_notification(
                    agent_type=request.agent_type,
                    version_number=version_number,
                    version_display=version_display,
                    author=request.author or "API",
                    reason=request.reason or "Alteração via API",
                    change_type=change_type,
                    prompt_content_preview=request.prompt_content[:200] if request.prompt_content else None,
                    clickup_cards=request.clickup_cards
                )
            except Exception as e:
                # Don't fail the main operation if Discord notification fails
                logger.error(f"Failed to send Discord notification: {str(e)}")

            return UnifiedSaveResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar alterações unificadas: {str(e)}",
        ) 