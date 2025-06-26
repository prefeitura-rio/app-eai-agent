from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from loguru import logger

from src.db import get_db_session
from src.repositories.unified_version_repository import UnifiedVersionRepository
from src.repositories.system_prompt_repository import SystemPromptRepository
from src.repositories.agent_config_repository import AgentConfigRepository


class UnifiedHistoryService:
    """Serviço para fornecer histórico unificado de alterações."""

    def __init__(self):
        pass

    async def get_unified_history(
        self, agent_type: str = "agentic_search", limit: int = 50, db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém o histórico unificado de alterações para um tipo de agente.

        Args:
            agent_type: Tipo do agente
            limit: Limite de resultados
            db: Sessão do banco de dados

        Returns:
            List[Dict[str, Any]]: Lista do histórico unificado
        """
        if db is None:
            with get_db_session() as session:
                return self._get_unified_history(session, agent_type, limit)
        else:
            return self._get_unified_history(db, agent_type, limit)

    def _get_unified_history(
        self, db: Session, agent_type: str, limit: int
    ) -> List[Dict[str, Any]]:
        """
        Implementação síncrona para obter o histórico unificado.

        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            limit: Limite de resultados

        Returns:
            List[Dict[str, Any]]: Lista do histórico formatada
        """
        # Buscar versões unificadas
        versions = UnifiedVersionRepository.list_versions(
            db=db, agent_type=agent_type, limit=limit
        )

        unified_history = []
        
        for version in versions:
            # Dados básicos da versão
            item = {
                "version_id": str(version.version_id),
                "version_number": version.version_number,
                "change_type": version.change_type,
                "created_at": version.created_at.isoformat() if version.created_at else None,
                "author": version.author,
                "reason": version.reason,
                "description": version.description,
                "metadata": version.version_metadata,
            }

            # Buscar dados do prompt se existir
            if version.prompt_id:
                prompt = SystemPromptRepository.get_prompt_by_id(db, str(version.prompt_id))
                if prompt:
                    item["prompt"] = {
                        "prompt_id": str(prompt.prompt_id),
                        "content": prompt.content,
                        "content_preview": (
                            prompt.content[:100] + "..." 
                            if len(prompt.content) > 100 
                            else prompt.content
                        ),
                        "is_active": prompt.is_active,
                        "metadata": prompt.prompt_metadata,
                    }

            # Buscar dados da configuração se existir
            if version.config_id:
                config = AgentConfigRepository.get_config_by_id(db, str(version.config_id))
                if config:
                    item["config"] = {
                        "config_id": str(config.config_id),
                        "memory_blocks": config.memory_blocks,
                        "tools": config.tools,
                        "model_name": config.model_name,
                        "embedding_name": config.embedding_name,
                        "is_active": config.is_active,
                        "metadata": config.config_metadata,
                    }

            # Criar preview unificado
            preview_parts = []
            if version.change_type == "prompt" and "prompt" in item:
                preview_parts.append(f"System Prompt: {item['prompt']['content_preview']}")
            elif version.change_type == "config" and "config" in item:
                tools_preview = ", ".join(item["config"]["tools"][:3])
                if len(item["config"]["tools"]) > 3:
                    tools_preview += "..."
                preview_parts.append(f"Config: Tools: {tools_preview}")
            elif version.change_type == "both":
                if "prompt" in item:
                    preview_parts.append(f"Prompt: {item['prompt']['content_preview']}")
                if "config" in item:
                    tools_preview = ", ".join(item["config"]["tools"][:3])
                    if len(item["config"]["tools"]) > 3:
                        tools_preview += "..."
                    preview_parts.append(f"Config: {tools_preview}")

            item["preview"] = " | ".join(preview_parts) if preview_parts else "Alteração registrada"

            # Informações sobre status ativo
            item["is_active"] = False
            if "prompt" in item and item["prompt"]["is_active"]:
                item["is_active"] = True
            if "config" in item and item["config"]["is_active"]:
                item["is_active"] = True

            unified_history.append(item)

        logger.info(f"Histórico unificado carregado: {len(unified_history)} itens para {agent_type}")
        return unified_history

    async def get_version_details(
        self, agent_type: str, version_number: int, db: Session = None
    ) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes completos de uma versão específica.

        Args:
            agent_type: Tipo do agente
            version_number: Número da versão
            db: Sessão do banco de dados

        Returns:
            Optional[Dict[str, Any]]: Detalhes da versão ou None se não encontrada
        """
        if db is None:
            with get_db_session() as session:
                return self._get_version_details(session, agent_type, version_number)
        else:
            return self._get_version_details(db, agent_type, version_number)

    def _get_version_details(
        self, db: Session, agent_type: str, version_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Implementação síncrona para obter detalhes de uma versão.

        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            version_number: Número da versão

        Returns:
            Optional[Dict[str, Any]]: Detalhes da versão
        """
        version = UnifiedVersionRepository.get_version_by_number(
            db, agent_type, version_number
        )
        
        if not version:
            return None

        details = {
            "version_id": str(version.version_id),
            "version_number": version.version_number,
            "change_type": version.change_type,
            "created_at": version.created_at.isoformat() if version.created_at else None,
            "author": version.author,
            "reason": version.reason,
            "description": version.description,
            "metadata": version.version_metadata,
        }

        # Adicionar dados completos do prompt se existir
        if version.prompt_id:
            prompt = SystemPromptRepository.get_prompt_by_id(db, str(version.prompt_id))
            if prompt:
                details["prompt"] = {
                    "prompt_id": str(prompt.prompt_id),
                    "content": prompt.content,
                    "is_active": prompt.is_active,
                    "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
                    "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None,
                    "metadata": prompt.prompt_metadata,
                }

        # Adicionar dados completos da configuração se existir
        if version.config_id:
            config = AgentConfigRepository.get_config_by_id(db, str(version.config_id))
            if config:
                details["config"] = {
                    "config_id": str(config.config_id),
                    "memory_blocks": config.memory_blocks,
                    "tools": config.tools,
                    "model_name": config.model_name,
                    "embedding_name": config.embedding_name,
                    "is_active": config.is_active,
                    "created_at": config.created_at.isoformat() if config.created_at else None,
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None,
                    "metadata": config.config_metadata,
                }

        return details


unified_history_service = UnifiedHistoryService() 