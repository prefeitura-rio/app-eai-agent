from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from loguru import logger

from src.core.security.dependencies import validar_token
from src.db import get_db_session
from src.repositories.unified_version_repository import UnifiedVersionRepository
from src.repositories.system_prompt_repository import SystemPromptRepository
from src.repositories.agent_config_repository import AgentConfigRepository
from src.models.system_prompt_model import SystemPrompt
from src.schemas.unified_delete_schema import UnifiedDeleteResponse

router = APIRouter(
    prefix="/unified-delete",
    tags=["Unified Delete"],
    dependencies=[Depends(validar_token)],
)


@router.delete("", response_model=UnifiedDeleteResponse)
async def delete_unified_version(
    agent_type: str = Query(..., description="Tipo do agente"),
    version_number: int = Query(..., description="Número da versão a ser excluída"),
):
    """
    Exclui uma versão específica do histórico unificado (prompt, config e versão).
    Remove em cascata: deployments → prompt → config → unified_version.

    Args:
        agent_type: Tipo do agente
        version_number: Número da versão a ser excluída

    Returns:
        UnifiedDeleteResponse: Resultado da operação de exclusão
    """
    try:
        if not agent_type or agent_type.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário especificar um tipo de agente válido",
            )

        if version_number <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário especificar um número de versão válido (maior que 0)",
            )

        result = {
            "success": True,
            "agent_type": agent_type,
            "version_number": version_number,
            "deployments_deleted": 0,
            "message": f"Versão {version_number} excluída com sucesso"
        }
        
        items_deleted = []

        with get_db_session() as db:
            # 1. Verificar se a versão existe na tabela unified_versions
            version = UnifiedVersionRepository.get_version_by_number(
                db, agent_type, version_number
            )
            
            # Se não existe na unified_versions, verificar se existe nas tabelas individuais
            if not version:
                # Buscar na tabela system_prompts
                prompt_by_version = (
                    db.query(SystemPrompt)
                    .filter(
                        SystemPrompt.agent_type == agent_type,
                        SystemPrompt.version == version_number
                    )
                    .first()
                )
                
                # Buscar na tabela agent_configs  
                from src.models.agent_config_model import AgentConfig
                config_by_version = (
                    db.query(AgentConfig)
                    .filter(
                        AgentConfig.agent_type == agent_type,
                        AgentConfig.version == version_number
                    )
                    .first()
                )
                
                # Se não existe em nenhuma tabela, erro
                if not prompt_by_version and not config_by_version:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Versão {version_number} não encontrada em nenhuma tabela para o tipo de agente {agent_type}",
                    )
                
                # Dados dos registros órfãos encontrados
                prompt_id = prompt_by_version.prompt_id if prompt_by_version else None
                config_id = config_by_version.config_id if config_by_version else None
                version_display = f"eai-ORPHAN-v{version_number}"
                
                logger.info(f"Encontrados registros órfãos para versão {version_number}: prompt_id={prompt_id}, config_id={config_id}")
            else:
                # Capturar dados da versão unificada
                prompt_id = version.prompt_id
                config_id = version.config_id
                version_display = version.version_metadata.get('version_display')

            result.update({
                "prompt_id": str(prompt_id) if prompt_id else None,
                "config_id": str(config_id) if config_id else None,
                "version_display": version_display,
            })

            # 2. Verificar se não é a única versão (proteção contra exclusão total)
            # Mas apenas se a versão existe na tabela unified_versions
            if version:  # Se existe versão unificada, verificar proteção
                all_versions = UnifiedVersionRepository.list_versions(db, agent_type, limit=2)
                if len(all_versions) <= 1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Não é possível excluir a única versão existente. Use o reset para recriar valores padrão.",
                    )
            else:
                logger.info(f"Limpando registros órfãos da versão {version_number}, sem verificação de proteção")

            # 3. ANTES de deletar, verificar se é a versão mais recente para prompt e config
            # Isso deve ser feito ANTES da deleção para garantir que encontramos as versões corretas
            is_latest_prompt = False
            is_latest_config = False
            previous_prompt = None
            previous_config = None
            
            if prompt_id:
                latest_prompt = SystemPromptRepository.get_latest_prompt(db, agent_type)
                if latest_prompt and latest_prompt.version == version_number:
                    is_latest_prompt = True
                    previous_prompt = SystemPromptRepository.get_previous_prompt(db, agent_type)
                    if previous_prompt:
                        logger.info(f"Prompt: versão {version_number} é a mais recente, versão {previous_prompt.version} será reativada")
                    else:
                        logger.warning("Prompt: não há versão anterior para reativar")
            
            if config_id:
                from src.models.agent_config_model import AgentConfig
                latest_config = AgentConfigRepository.get_latest_config(db, agent_type)
                if latest_config and latest_config.version == version_number:
                    is_latest_config = True
                    previous_config = AgentConfigRepository.get_previous_config(db, agent_type)
                    if previous_config:
                        logger.info(f"Config: versão {version_number} é a mais recente, versão {previous_config.version} será reativada")
                    else:
                        logger.warning("Config: não há versão anterior para reativar")

            # 4. Remover deployments de prompts primeiro (se existir prompt_id)
            if prompt_id:
                try:
                    deployments_deleted = SystemPromptRepository.delete_deployments_by_prompt_ids(
                        db, [str(prompt_id)]
                    )
                    result["deployments_deleted"] = deployments_deleted
                    db.commit()  # Commit após excluir deployments
                    logger.info(f"Deployments excluídos: {deployments_deleted}")
                    if deployments_deleted > 0:
                        items_deleted.append(f"{deployments_deleted} deployments")
                except Exception as e:
                    logger.warning(f"Erro ao excluir deployments do prompt {prompt_id}: {str(e)}")
                    db.rollback()

            # 5. Remover prompt e reativar anterior se necessário
            if prompt_id:
                try:
                    prompt_deleted = SystemPromptRepository.delete_prompt_by_id(db, str(prompt_id))
                    if prompt_deleted:
                        logger.info(f"Prompt {prompt_id} excluído com sucesso")
                        db.commit()  # Commit após excluir prompt
                        items_deleted.append("prompt")
                        
                        # Reativar prompt anterior se era o mais recente
                        if is_latest_prompt and previous_prompt:
                            db.query(SystemPrompt).filter(
                                SystemPrompt.prompt_id == previous_prompt.prompt_id
                            ).update({"is_active": True})
                            db.commit()
                            logger.info(f"Prompt anterior (versão {previous_prompt.version}) reativado com sucesso")
                            result["reactivated_version"] = previous_prompt.version
                            result["reactivated_prompt_id"] = str(previous_prompt.prompt_id)
                    else:
                        logger.warning(f"Prompt {prompt_id} não foi encontrado na tabela system_prompts")
                except Exception as e:
                    logger.warning(f"Erro ao excluir prompt {prompt_id}: {str(e)}")
                    db.rollback()

            # 6. Remover configuração e reativar anterior se necessário
            if config_id:
                try:
                    config_deleted = AgentConfigRepository.delete_config_by_id(db, str(config_id))
                    if config_deleted:
                        logger.info(f"Config {config_id} excluído com sucesso")
                        db.commit()  # Commit após excluir config
                        items_deleted.append("config")
                        
                        # Reativar config anterior se era o mais recente
                        if is_latest_config and previous_config:
                            from src.models.agent_config_model import AgentConfig
                            db.query(AgentConfig).filter(
                                AgentConfig.config_id == previous_config.config_id
                            ).update({"is_active": True})
                            db.commit()
                            logger.info(f"Config anterior (versão {previous_config.version}) reativado com sucesso")
                            result["reactivated_config_version"] = previous_config.version
                            result["reactivated_config_id"] = str(previous_config.config_id)
                    else:
                        logger.warning(f"Config {config_id} não foi encontrado na tabela agent_configs")
                except Exception as e:
                    logger.warning(f"Erro ao excluir config {config_id}: {str(e)}")
                    db.rollback()
            
            # 7. Remover entrada de versão unificada (se existir)
            if version:  # Só tenta deletar se existir
                version_deleted = UnifiedVersionRepository.delete_version_by_number(
                    db, agent_type, version_number
                )
                
                if not version_deleted:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Erro interno: não foi possível excluir a versão unificada",
                    )
                items_deleted.append("unified_version")
            else:
                logger.info(f"Versão {version_number} não existe na tabela unified_versions, pulando exclusão")

            # Força commit final da exclusão
            db.commit()
            
            # Atualizar mensagem com detalhes do que foi excluído
            if items_deleted:
                items_str = ", ".join(items_deleted)
                result["message"] = f"Versão {version_number} excluída com sucesso ({items_str})"
            else:
                result["message"] = f"Versão {version_number} excluída (apenas referência na tabela unified_versions)"

            return UnifiedDeleteResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir versão unificada: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir versão unificada: {str(e)}",
        )