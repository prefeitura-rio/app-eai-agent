from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from loguru import logger

from src.db import get_db_session
from src.repositories.system_prompt_repository import SystemPromptRepository
from src.repositories.unified_version_repository import UnifiedVersionRepository
from src.services.letta.letta_service import letta_service
from src.models.system_prompt_model import SystemPrompt, SystemPromptDeployment


class SystemPromptService:
    """
    Serviço para gerenciar system prompts dos agentes.
    Permite atualizar o system prompt e os agentes existentes.
    """

    def __init__(self):
        """
        Inicializa o serviço de system prompt.
        """
        pass

    async def get_current_system_prompt(
        self, agent_type: str = "agentic_search", db: Session = None
    ) -> str:
        """
        Obtém o system prompt atual para o tipo de agente especificado.

        Args:
            agent_type: Tipo do agente
            db: Sessão do banco de dados

        Returns:
            str: Texto do system prompt atual
        """
        if db:
            prompt = SystemPromptRepository.get_active_prompt(db, agent_type)
            if prompt:
                return prompt.content

        with get_db_session() as session:
            prompt = SystemPromptRepository.get_active_prompt(session, agent_type)
            if prompt:
                return prompt.content

        raise ValueError(
            f"Nenhum system prompt encontrado para o tipo de agente: {agent_type}"
        )

    def get_active_system_prompt_from_db(
        self, agent_type: str = "agentic_search"
    ) -> str:
        """
        Obtém o system prompt ativo do banco de dados de forma síncrona.
        Este método deve ser usado para criação de novos agentes.
        Se não existir um prompt para o tipo de agente fornecido, cria automaticamente um padrão.

        Args:
            agent_type: Tipo do agente

        Returns:
            str: Texto do system prompt ativo no banco de dados
        """
        try:
            with get_db_session() as db:
                prompt = SystemPromptRepository.get_active_prompt(db, agent_type)
                if prompt:
                    return prompt.content

                # Se não existe um prompt ativo, tenta criar um padrão
                logger.info(
                    f"Nenhum system prompt encontrado para o tipo de agente: {agent_type}. Criando um padrão..."
                )
                default_prompt = self._get_default_prompt(agent_type)
                new_prompt = SystemPromptRepository.create_prompt(
                    db=db,
                    agent_type=agent_type,
                    content=default_prompt,
                    version=1,
                    metadata={"author": "System", "reason": "Criado automaticamente"},
                )
                return new_prompt.content
        except Exception as e:
            logger.error(f"Erro ao obter/criar system prompt do banco: {str(e)}")
            raise

    async def update_all_agents_system_prompt(
        self,
        new_prompt: str,
        agent_type: str = "agentic_search",
        tags: Optional[List[str]] = None,
        db: Session = None,
        prompt_id: str = None,
    ) -> Dict[str, bool]:
        """
        Atualiza o system prompt de todos os agentes existentes do tipo especificado.

        Args:
            new_prompt: Novo texto para o system prompt
            agent_type: Tipo do agente
            tags: Filtrar agentes por tags específicas
            db: Sessão do banco de dados
            prompt_id: ID do prompt no banco de dados

        Returns:
            Dict[str, bool]: Dicionário com agent_id: status da atualização
        """
        client = letta_service.get_client_async()
        results = {}

        try:
            filter_tags = (
                tags
                if tags
                else (["agentic_search"] if agent_type == "agentic_search" else [])
            )
            agents = await client.agents.list(tags=filter_tags)

            if not agents:
                logger.info(f"Nenhum agente encontrado com as tags: {filter_tags}")
                return results

            for agent in agents:
                try:
                    await client.agents.modify(agent_id=agent.id, system=new_prompt)
                    results[agent.id] = True
                    logger.info(f"System prompt atualizado para o agente: {agent.id}")

                    if db and prompt_id:
                        SystemPromptRepository.create_deployment(
                            db=db,
                            prompt_id=prompt_id,
                            agent_id=agent.id,
                            agent_type=agent_type,
                            status="success",
                            details={
                                "tags": agent.tags if hasattr(agent, "tags") else []
                            },
                        )

                except Exception as agent_error:
                    results[agent.id] = False
                    logger.error(
                        f"Erro ao atualizar agente {agent.id}: {str(agent_error)}"
                    )

                    if db and prompt_id:
                        SystemPromptRepository.create_deployment(
                            db=db,
                            prompt_id=prompt_id,
                            agent_id=agent.id,
                            agent_type=agent_type,
                            status="failed",
                            details={
                                "error": str(agent_error),
                                "tags": agent.tags if hasattr(agent, "tags") else [],
                            },
                        )

            return results

        except Exception as e:
            logger.error(f"Erro ao atualizar agents: {str(e)}")
            return results

    async def update_system_prompt(
        self,
        new_prompt: str,
        agent_type: str = "agentic_search",
        update_agents: bool = True,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db: Session = None,
    ) -> Dict[str, any]:
        """
        Atualiza o system prompt no banco de dados e em todos os agentes existentes.

        Args:
            new_prompt: Novo texto para o system prompt
            agent_type: Tipo do agente
            update_agents: Se deve atualizar os agentes existentes
            tags: Filtrar agentes por tags específicas
            metadata: Metadados adicionais para armazenar com o prompt
            db: Sessão do banco de dados

        Returns:
            Dict: Resultado das operações
        """
        result = {"success": True, "prompt_id": None, "agents_updated": {}}

        if db is None:
            with get_db_session() as session:
                db = session

        return await self._perform_update(
            db, new_prompt, agent_type, update_agents, tags, metadata, result
        )

    async def _perform_update(
        self,
        db: Session,
        new_prompt: str,
        agent_type: str,
        update_agents: bool,
        tags: Optional[List[str]],
        metadata: Optional[Dict[str, Any]],
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executa a atualização do system prompt com uma sessão de banco de dados.

        Args:
            db: Sessão do banco de dados
            new_prompt: Novo texto para o system prompt
            agent_type: Tipo do agente
            update_agents: Se deve atualizar os agentes existentes
            tags: Filtrar agentes por tags específicas
            metadata: Metadados adicionais para armazenar com o prompt
            result: Dicionário de resultado parcial

        Returns:
            Dict: Resultado das operações atualizado
        """
        # Obter próximo número de versão do controle unificado
        version_number = UnifiedVersionRepository.get_next_version_number(db, agent_type)
        
        logger.info(f"Criando system prompt para {agent_type} com versão unificada: {version_number}")
        
        try:
            prompt = SystemPromptRepository.create_prompt(
                db=db,
                agent_type=agent_type,
                content=new_prompt,
                version=version_number,
                metadata=metadata or {"source": "api"},
            )
            
            # Registrar no controle de versões unificado
            unified_version = UnifiedVersionRepository.create_version(
                db=db,
                agent_type=agent_type,
                change_type="prompt",
                prompt_id=prompt.prompt_id,
                author=metadata.get("author") if metadata else None,
                reason=metadata.get("reason") if metadata else None,
                metadata=metadata,
            )
            
            result["prompt_id"] = prompt.prompt_id
            result["unified_version"] = unified_version.version_number
            
        except Exception as e:
            logger.error(f"Erro ao criar prompt com versão {version_number}: {str(e)}")
            raise

        if update_agents:
            agents_result = await self.update_all_agents_system_prompt(
                new_prompt=new_prompt,
                agent_type=agent_type,
                tags=tags,
                db=db,
                prompt_id=prompt.prompt_id,
            )
            result["agents_updated"] = agents_result

            if agents_result and not all(agents_result.values()):
                result["success"] = False

        return result

    async def get_prompt_history(
        self, agent_type: str = "agentic_search", limit: int = 10, db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém o histórico de versões de um system prompt.

        Args:
            agent_type: Tipo do agente
            limit: Limite de resultados
            db: Sessão do banco de dados

        Returns:
            List[Dict[str, Any]]: Lista de prompts com informações resumidas
        """
        if db is None:
            with get_db_session() as session:
                return self._get_history(session, agent_type, limit)
        else:
            return self._get_history(db, agent_type, limit)

    def _get_history(
        self, db: Session, agent_type: str, limit: int
    ) -> List[Dict[str, Any]]:
        """
        Implementação síncrona para obter o histórico de versões.

        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            limit: Limite de resultados

        Returns:
            List[Dict[str, Any]]: Lista de prompts formatada
        """
        prompts = SystemPromptRepository.list_prompts(
            db=db, agent_type=agent_type, limit=limit
        )

        formatted_prompts = []
        for p in prompts:
            content_preview = (
                p.content[:100] + "..." if len(p.content) > 100 else p.content
            )

            created_at_str = p.created_at.isoformat() if p.created_at else None
            updated_at_str = p.updated_at.isoformat() if p.updated_at else None

            formatted_prompts.append(
                {
                    "prompt_id": p.prompt_id,
                    "version": p.version,
                    "is_active": p.is_active,
                    "created_at": created_at_str,
                    "updated_at": updated_at_str,
                    "content": content_preview,
                    "metadata": p.prompt_metadata,
                }
            )

        return formatted_prompts

    async def delete_last_system_prompt(
        self, agent_type: str, update_agents: bool = False, db: Session = None
    ) -> Dict[str, Any]:
        """
        Deleta apenas o último system prompt do histórico e reativa o anterior.

        Args:
            agent_type: Tipo do agente
            update_agents: Se deve atualizar os agentes existentes com o prompt anterior
            db: Sessão do banco de dados

        Returns:
            Dict: Resultado da operação incluindo versões deletada e ativa
        """
        result = {
            "success": True,
            "agents_updated": {},
            "deleted_version": None,
            "active_version": None,
            "previous_prompt_id": None,
        }

        if db is None:
            with get_db_session() as session:
                db = session

        try:
            # Obter o prompt mais recente (último)
            latest_prompt = SystemPromptRepository.get_latest_prompt(db, agent_type)

            if not latest_prompt:
                raise ValueError(
                    f"Nenhum system prompt encontrado para o tipo de agente: {agent_type}"
                )

            # Obter o penúltimo prompt
            previous_prompt = SystemPromptRepository.get_previous_prompt(db, agent_type)

            if not previous_prompt:
                raise ValueError(
                    f"Não é possível deletar o único system prompt existente para o tipo de agente: {agent_type}. "
                    f"Use o endpoint de reset se deseja resetar para o padrão."
                )

            # Armazenar informações antes de deletar
            deleted_version = latest_prompt.version
            latest_prompt_id = latest_prompt.prompt_id

            # Deletar deployments relacionados ao último prompt
            prompt_ids = [latest_prompt_id]
            SystemPromptRepository.delete_deployments_by_prompt_ids(db, prompt_ids)

            # Deletar o último prompt
            SystemPromptRepository.delete_prompt_by_id(db, latest_prompt_id)

            # Deletar a versão do controle unificado
            UnifiedVersionRepository.delete_version_by_number(
                db, agent_type, deleted_version
            )

            # Reativar o prompt anterior
            db.query(SystemPrompt).filter(
                SystemPrompt.prompt_id == previous_prompt.prompt_id
            ).update({"is_active": True})

            db.commit()
            db.refresh(previous_prompt)

            # Atualizar resultado
            result["deleted_version"] = deleted_version
            result["active_version"] = previous_prompt.version
            result["previous_prompt_id"] = previous_prompt.prompt_id

            # Atualizar agentes se solicitado
            if update_agents:
                agents_result = await self.update_all_agents_system_prompt(
                    new_prompt=previous_prompt.content,
                    agent_type=agent_type,
                    tags=[agent_type],
                    db=db,
                    prompt_id=previous_prompt.prompt_id,
                )
                result["agents_updated"] = agents_result

                if agents_result and not all(agents_result.values()):
                    result["success"] = False

            return result

        except ValueError as ve:
            # Re-raise ValueError para ser tratado no controller
            raise ve
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao deletar último system prompt: {str(e)}")
            result["success"] = False
            raise Exception(f"Erro ao deletar último system prompt: {str(e)}")

    async def reset_system_prompt(
        self, agent_type: str, update_agents: bool = False, db: Session = None
    ) -> Dict[str, Any]:
        """
        Reseta o system prompt para o tipo de agente, removendo todo o histórico
        e criando um novo prompt padrão.

        Args:
            agent_type: Tipo do agente para resetar
            update_agents: Se deve atualizar os agentes existentes
            db: Sessão do banco de dados

        Returns:
            Dict: Resultado da operação
        """
        result = {"success": True, "agents_updated": {}}

        if db is None:
            with get_db_session() as session:
                db = session

        try:
            prompt_ids = SystemPromptRepository.get_prompt_ids_by_agent_type(
                db, agent_type
            )

            if prompt_ids:
                SystemPromptRepository.delete_deployments_by_prompt_ids(db, prompt_ids)

            SystemPromptRepository.delete_prompts_by_agent_type(db, agent_type)
            
            # Remover do controle de versões unificado também
            UnifiedVersionRepository.delete_versions_by_agent_type(db, agent_type)

            # Força commit da deleção antes de criar o novo prompt
            db.commit()

            default_prompt = self._get_default_prompt(agent_type)

            # Para reset, sempre usar versão 1 - começamos do zero
            new_prompt = SystemPromptRepository.create_prompt(
                db=db,
                agent_type=agent_type,
                content=default_prompt,
                version=1,
                metadata={"author": "System", "reason": "Resetado automaticamente"},
            )
            
            # Registrar no controle de versões unificado
            unified_version = UnifiedVersionRepository.create_version(
                db=db,
                agent_type=agent_type,
                change_type="prompt",
                prompt_id=new_prompt.prompt_id,
                author="System",
                reason="Resetado automaticamente",
                metadata={"author": "System", "reason": "Resetado automaticamente"},
            )
            
            result["unified_version"] = unified_version.version_number

            if update_agents:
                agents_result = await self.update_all_agents_system_prompt(
                    new_prompt=default_prompt,
                    agent_type=agent_type,
                    tags=[agent_type],
                    db=db,
                    prompt_id=new_prompt.prompt_id,
                )
                result["agents_updated"] = agents_result

                if agents_result and not all(agents_result.values()):
                    result["success"] = False

            return result

        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao resetar system prompt: {str(e)}")
            result["success"] = False
            return result

    def _get_default_prompt(self, agent_type: str) -> str:
        """
        Retorna o conteúdo padrão para um system prompt de acordo com o tipo de agente.

        Args:
            agent_type: Tipo do agente

        Returns:
            str: Texto padrão do system prompt
        """
        return f"""You are an AI assistant for the {agent_type} role.
Follow these guidelines:
1. Answer concisely but accurately
2. Use tools when necessary
3. Focus on providing factual information
4. Be helpful, harmless, and honest"""


system_prompt_service = SystemPromptService()
