from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from loguru import logger

from src.core.security.dependencies import validar_token
from src.db import get_db_session
from src.repositories.unified_version_repository import UnifiedVersionRepository
from src.repositories.system_prompt_repository import SystemPromptRepository
from src.repositories.agent_config_repository import AgentConfigRepository
from src.models.unified_version_model import UnifiedVersion
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
    Exclui uma versão específica do histórico unificado.
    Remove a entrada unificada e só remove prompt/config quando não houver
    outras versões unificadas referenciando os mesmos IDs.

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
            # 1. Lock pessimista por agent_type para serializar deleções concorrentes.
            locked_versions = (
                db.query(UnifiedVersion)
                .filter(UnifiedVersion.agent_type == agent_type)
                .with_for_update()
                .all()
            )
            version = next(
                (v for v in locked_versions if v.version_number == version_number),
                None,
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
                version_display = (
                    version.version_metadata.get("version_display")
                    if version.version_metadata
                    else None
                )

            result.update({
                "prompt_id": str(prompt_id) if prompt_id else None,
                "config_id": str(config_id) if config_id else None,
                "version_display": version_display,
            })

            # 2. Verificar se não é a única versão (proteção contra exclusão total)
            if version:
                if len(locked_versions) <= 1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Não é possível excluir a única versão existente. Use o reset para recriar valores padrão.",
                    )
            else:
                logger.info(f"Limpando registros órfãos da versão {version_number}, sem verificação de proteção")

            # 3. Remover entrada de versão unificada (se existir)
            if version:
                version_deleted = UnifiedVersionRepository.delete_version_by_number(
                    db, agent_type, version_number
                )

                if not version_deleted:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Erro interno: não foi possível excluir a versão unificada",
                    )
                items_deleted.append("unified_version")
                db.flush()
            else:
                logger.info(f"Versão {version_number} não existe na tabela unified_versions, pulando exclusão")

            # 4. Limpeza de prompt/config somente se não houver outras versões referenciando.
            if prompt_id:
                prompt_refs = (
                    db.query(UnifiedVersion)
                    .filter(
                        UnifiedVersion.agent_type == agent_type,
                        UnifiedVersion.prompt_id == prompt_id,
                    )
                    .count()
                )

                if prompt_refs == 0:
                    try:
                        deployments_deleted = SystemPromptRepository.delete_deployments_by_prompt_ids(
                            db, [str(prompt_id)]
                        )
                        result["deployments_deleted"] = deployments_deleted
                        if deployments_deleted > 0:
                            items_deleted.append(f"{deployments_deleted} deployments")

                        prompt_deleted = SystemPromptRepository.delete_prompt_by_id(db, str(prompt_id))
                        if prompt_deleted:
                            items_deleted.append("prompt")
                            logger.info(f"Prompt {prompt_id} excluído com sucesso")
                        db.commit()
                    except Exception as e:
                        logger.warning(f"Erro ao excluir prompt/deployments {prompt_id}: {str(e)}")
                        db.rollback()
                else:
                    logger.info(
                        f"Prompt {prompt_id} mantido: ainda referenciado por {prompt_refs} versão(ões)"
                    )

            if config_id:
                config_refs = (
                    db.query(UnifiedVersion)
                    .filter(
                        UnifiedVersion.agent_type == agent_type,
                        UnifiedVersion.config_id == config_id,
                    )
                    .count()
                )

                if config_refs == 0:
                    try:
                        config_deleted = AgentConfigRepository.delete_config_by_id(db, str(config_id))
                        if config_deleted:
                            items_deleted.append("config")
                            logger.info(f"Config {config_id} excluído com sucesso")
                        db.commit()
                    except Exception as e:
                        logger.warning(f"Erro ao excluir config {config_id}: {str(e)}")
                        db.rollback()
                else:
                    logger.info(
                        f"Config {config_id} mantido: ainda referenciado por {config_refs} versão(ões)"
                    )

            # 5. A versão ativa é sempre a mais recente remanescente.
            latest_versions = UnifiedVersionRepository.list_versions(db, agent_type, limit=1)
            result["active_version"] = (
                latest_versions[0].version_number if latest_versions else None
            )

            # Atualizar mensagem com detalhes do que foi excluído
            if items_deleted:
                items_str = ", ".join(items_deleted)
                result["message"] = f"Versão {version_number} excluída com sucesso ({items_str})"
            else:
                result["message"] = f"Versão {version_number} excluída (apenas referência na tabela unified_versions)"

            db.commit()
            return UnifiedDeleteResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir versão unificada: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir versão unificada: {str(e)}",
        )
