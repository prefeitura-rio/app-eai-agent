from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.db import get_db_session
from src.repositories.unified_version_repository import UnifiedVersionRepository
from src.repositories.system_prompt_repository import SystemPromptRepository
from src.repositories.agent_config_repository import AgentConfigRepository
from src.services.letta.system_prompt_service import system_prompt_service
from src.services.letta.agent_config_service import agent_config_service
from src.schemas.unified_reset_schema import UnifiedResetResponse

router = APIRouter(
    prefix="/unified-reset",
    tags=["Unified Reset"],
    dependencies=[Depends(validar_token)],
)


@router.delete("", response_model=UnifiedResetResponse)
async def unified_reset(
    agent_type: str = Query(..., description="Tipo do agente para resetar"),
    update_agents: bool = Query(False, description="Atualizar também os agentes existentes"),
):
    """
    Reset completo e unificado: remove todo o histórico (prompts, configs e versões)
    e recria valores padrão com versionamento limpo.

    Args:
        agent_type: Tipo do agente para resetar
        update_agents: Se deve atualizar os agentes existentes

    Returns:
        UnifiedResetResponse: Resultado da operação
    """
    try:
        if not agent_type or agent_type.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário especificar um tipo de agente válido",
            )

        result = {
            "success": True,
            "agent_type": agent_type,
            "agents_updated": {},
            "message": "Reset unificado concluído com sucesso"
        }

        with get_db_session() as db:
            # 1. Remover deployments de prompts primeiro (referências externas)
            prompt_ids = SystemPromptRepository.get_prompt_ids_by_agent_type(db, agent_type)
            if prompt_ids:
                SystemPromptRepository.delete_deployments_by_prompt_ids(db, prompt_ids)

            # 2. Remover todos os registros do banco (ordem é importante)
            SystemPromptRepository.delete_prompts_by_agent_type(db, agent_type)
            AgentConfigRepository.delete_configs_by_agent_type(db, agent_type)
            UnifiedVersionRepository.delete_versions_by_agent_type(db, agent_type)

            # Força commit da deleção antes de criar novos registros
            db.commit()

            # 3. Criar prompt padrão (versão 1)
            default_prompt = system_prompt_service._get_default_prompt(agent_type)
            new_prompt = SystemPromptRepository.create_prompt(
                db=db,
                agent_type=agent_type,
                content=default_prompt,
                version=1,
                metadata={"author": "System", "reason": "Reset unificado automaticamente"},
            )

            # 4. Criar configuração padrão (versão 1)  
            default_config = agent_config_service._default_config(agent_type)
            new_config = AgentConfigRepository.create_config(
                db=db,
                agent_type=agent_type,
                memory_blocks=default_config["memory_blocks"],
                tools=default_config["tools"],
                model_name=default_config["model_name"],
                embedding_name=default_config["embedding_name"],
                version=1,
                metadata={"author": "System", "reason": "Reset unificado automaticamente"},
            )

            # 5. Criar entrada de versão unificada (versão 1)
            unified_version = UnifiedVersionRepository.create_version(
                db=db,
                agent_type=agent_type,
                change_type="both",
                prompt_id=new_prompt.prompt_id,
                config_id=new_config.config_id,
                author="System",
                reason="Reset unificado automaticamente",
                description="Reset completo do sistema - prompt e configuração recriados",
                metadata={"author": "System", "reason": "Reset unificado automaticamente"},
            )

            result["unified_version"] = unified_version.version_number
            result["prompt_id"] = new_prompt.prompt_id
            result["config_id"] = new_config.config_id

            # 6. Atualizar agentes se solicitado
            if update_agents:
                # Atualizar agentes com novo prompt
                prompt_agents_result = await system_prompt_service.update_all_agents_system_prompt(
                    new_prompt=default_prompt,
                    agent_type=agent_type,
                    tags=[agent_type],
                    db=db,
                    prompt_id=new_prompt.prompt_id,
                )

                # Atualizar agentes com nova configuração
                config_agents_result = await agent_config_service._update_all_agents(
                    new_cfg_values=default_config,
                    agent_type=agent_type,
                    tags=[agent_type],
                )

                # Combinar resultados dos agentes
                all_agent_ids = set(prompt_agents_result.keys()) | set(config_agents_result.keys())
                combined_agents_result = {}
                
                for agent_id in all_agent_ids:
                    prompt_success = prompt_agents_result.get(agent_id, True)
                    config_success = config_agents_result.get(agent_id, True)
                    combined_agents_result[agent_id] = prompt_success and config_success

                result["agents_updated"] = combined_agents_result

                # Verificar se todos os agentes foram atualizados com sucesso
                if combined_agents_result and not all(combined_agents_result.values()):
                    result["success"] = False
                    result["message"] = "Reset concluído mas alguns agentes não foram atualizados"

                # Atualizar mensagem com estatísticas dos agentes
                if combined_agents_result:
                    updated_count = sum(1 for success in combined_agents_result.values() if success)
                    total_count = len(combined_agents_result)
                    result["message"] += f", {updated_count}/{total_count} agentes foram atualizados"

            return UnifiedResetResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar reset unificado: {str(e)}",
        ) 