from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from loguru import logger

from src.core.security.dependencies import validar_token
from src.db import get_db_session
from src.repositories.unified_version_repository import UnifiedVersionRepository
from src.repositories.system_prompt_repository import SystemPromptRepository
from src.repositories.agent_config_repository import AgentConfigRepository
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

        with get_db_session() as db:
            # 1. Verificar se a versão existe
            version = UnifiedVersionRepository.get_version_by_number(
                db, agent_type, version_number
            )
            
            if not version:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Versão {version_number} não encontrada para o tipo de agente {agent_type}",
                )

            # Capturar dados antes da exclusão
            prompt_id = version.prompt_id
            config_id = version.config_id
            version_display = version.version_metadata.get('version_display')

            result.update({
                "prompt_id": str(prompt_id) if prompt_id else None,
                "config_id": str(config_id) if config_id else None,
                "version_display": version_display,
            })

            # 2. Verificar se não é a única versão (proteção contra exclusão total)
            all_versions = UnifiedVersionRepository.list_versions(db, agent_type, limit=2)
            if len(all_versions) <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não é possível excluir a única versão existente. Use o reset para recriar valores padrão.",
                )

            # 3. Remover deployments de prompts primeiro (se existir prompt_id)
            if prompt_id:
                deployments_deleted = SystemPromptRepository.delete_deployments_by_prompt_ids(
                    db, [str(prompt_id)]
                )
                result["deployments_deleted"] = deployments_deleted

            # 4. Remover prompt se existir
            if prompt_id:
                prompt_deleted = SystemPromptRepository.delete_prompt_by_id(db, str(prompt_id))
                if not prompt_deleted:
                    logger.warning(f"Prompt {prompt_id} não foi encontrado para exclusão")

            # 5. Remover configuração se existir
            if config_id:
                config_deleted = AgentConfigRepository.delete_config_by_id(db, str(config_id))
                if not config_deleted:
                    logger.warning(f"Config {config_id} não foi encontrado para exclusão")

            # 6. Remover entrada de versão unificada
            version_deleted = UnifiedVersionRepository.delete_version_by_number(
                db, agent_type, version_number
            )
            
            if not version_deleted:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro interno: não foi possível excluir a versão unificada",
                )

            # Força commit da exclusão
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