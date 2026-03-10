from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from loguru import logger

from src.db import get_db_session
from src.repositories.agent_config_repository import AgentConfigRepository
from src.repositories.unified_version_repository import UnifiedVersionRepository
from src.services.agent_settings.memory_blocks import (
    get_agentic_search_memory_blocks,
)
from src.config import env


class AgentConfigService:
    """Serviço para gerenciar configurações de agentes (memory blocks, tools, model, embedding) com controle de versão."""

    def __init__(self):
        pass

    def _default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão para um tipo de agente."""
        return {
            "memory_blocks": get_agentic_search_memory_blocks(),
            "tools": [
                "google_search",
                "public_services_grounded_search",
            ],
            "model_name": env.LLM_MODEL,
            "embedding_name": env.EMBEDDING_MODEL,
        }

    # ------------------------ Métodos de consulta ------------------------
    async def get_current_config(
        self, agent_type: str = "agentic_search", db: Session = None
    ) -> Dict[str, Any]:
        if db:
            cfg = AgentConfigRepository.get_active_config(db, agent_type)
            if cfg:
                return self._model_to_dict(cfg)

            # cria usando a mesma sessão fornecida
            logger.info(
                f"Nenhuma configuração encontrada para o tipo de agente: {agent_type}. Criando configuração padrão (sessão existente)..."
            )
            default_cfg = self._default_config()
            new_cfg = AgentConfigRepository.create_config(
                db=db,
                agent_type=agent_type,
                memory_blocks=default_cfg["memory_blocks"],
                tools=default_cfg["tools"],
                model_name=default_cfg["model_name"],
                embedding_name=default_cfg["embedding_name"],
                metadata={"author": "System", "reason": "Criada automaticamente"},
            )
            return self._model_to_dict(new_cfg)

    def get_active_config_from_db(self, agent_type: str = "agentic_search") -> Dict[str, Any]:
        try:
            with get_db_session() as db:
                cfg = AgentConfigRepository.get_active_config(db, agent_type)
                if cfg:
                    return self._model_to_dict(cfg)

                logger.info(
                    f"Nenhuma configuração encontrada para o tipo de agente: {agent_type}. Criando configuração padrão..."
                )
                default_cfg = self._default_config()
                new_cfg = AgentConfigRepository.create_config(
                    db=db,
                    agent_type=agent_type,
                    memory_blocks=default_cfg["memory_blocks"],
                    tools=default_cfg["tools"],
                    model_name=default_cfg["model_name"],
                    embedding_name=default_cfg["embedding_name"],
                    metadata={"author": "System", "reason": "Criada automaticamente"},
                )
                return self._model_to_dict(new_cfg)
        except Exception as e:
            logger.error(f"Erro ao obter/criar configuração do banco: {str(e)}")
            raise

    # ------------------------ Atualizações ------------------------
    async def update_agent_configs(
        self,
        new_cfg_values: Dict[str, Any],
        agent_type: str = "agentic_search",
        metadata: Optional[Dict[str, Any]] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """Atualiza configuração do agente."""
        result: Dict[str, Any] = {"success": True, "config_id": None}

        if db is None:
            with get_db_session() as session:
                db = session
        return await self._perform_update(db, new_cfg_values, agent_type, metadata, result)

    async def _perform_update(
        self,
        db: Session,
        new_cfg_values: Dict[str, Any],
        agent_type: str,
        metadata: Optional[Dict[str, Any]],
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Obter próximo número de versão do controle unificado
        version_number = UnifiedVersionRepository.get_next_version_number(db, agent_type)
        
        logger.info(f"Criando configuração para {agent_type} com versão unificada: {version_number}")
        
        cfg = AgentConfigRepository.create_config(
            db=db,
            agent_type=agent_type,
            memory_blocks=new_cfg_values.get("memory_blocks"),
            tools=new_cfg_values.get("tools"),
            model_name=new_cfg_values.get("model_name"),
            embedding_name=new_cfg_values.get("embedding_name"),
            version=version_number,
            metadata=metadata or {"source": "api"},
        )
        
        # Registrar no controle de versões unificado
        unified_version = UnifiedVersionRepository.create_version(
            db=db,
            agent_type=agent_type,
            change_type="config",
            version_number=version_number,
            config_id=cfg.config_id,
            author=metadata.get("author") if metadata else None,
            reason=metadata.get("reason") if metadata else None,
            metadata=metadata,
        )
        
        result["config_id"] = cfg.config_id
        result["unified_version"] = unified_version.version_number

        return result

    # ------------------------ Histórico ------------------------
    async def get_config_history(
        self, agent_type: str = "agentic_search", limit: int = 10, db: Session = None
    ) -> List[Dict[str, Any]]:
        if db is None:
            with get_db_session() as session:
                return self._get_history(session, agent_type, limit)
        else:
            return self._get_history(db, agent_type, limit)

    def _get_history(self, db: Session, agent_type: str, limit: int) -> List[Dict[str, Any]]:
        configs = AgentConfigRepository.list_configs(db=db, agent_type=agent_type, limit=limit)
        formatted: List[Dict[str, Any]] = []
        for c in configs:
            created_at_str = c.created_at.isoformat() if c.created_at else None
            updated_at_str = c.updated_at.isoformat() if c.updated_at else None
            formatted.append(
                {
                    "config_id": c.config_id,
                    "version": c.version,
                    "is_active": c.is_active,
                    "created_at": created_at_str,
                    "updated_at": updated_at_str,
                    "metadata": c.config_metadata,
                    # Previews
                    "tools": c.tools,
                    "model_name": c.model_name,
                    "embedding_name": c.embedding_name,
                }
            )
        return formatted

    # ------------------------ Util ------------------------
    def _model_to_dict(self, cfg):
        return {
            "config_id": cfg.config_id,
            "agent_type": cfg.agent_type,
            "memory_blocks": cfg.memory_blocks,
            "tools": cfg.tools,
            "model_name": cfg.model_name,
            "embedding_name": cfg.embedding_name,
            "version": cfg.version,
            "metadata": cfg.config_metadata,
        }

    # ------------------------ Reset ------------------------
    async def reset_agent_config(
        self, agent_type: str, db: Session = None
    ) -> Dict[str, Any]:
        """Reseta a configuração: remove histórico e recria padrão."""

        result: Dict[str, Any] = {"success": True}

        if db is None:
            with get_db_session() as session:
                db = session

        try:
            # Apaga histórico
            AgentConfigRepository.delete_configs_by_agent_type(db, agent_type)
            
            # Remover do controle de versões unificado também
            UnifiedVersionRepository.delete_versions_by_agent_type(db, agent_type)
            
            db.commit()

            default_cfg = self._default_config()
            # Para reset, sempre usar versão 1 já que deletamos todo o histórico
            new_cfg = AgentConfigRepository.create_config(
                db=db,
                agent_type=agent_type,
                memory_blocks=default_cfg["memory_blocks"],
                tools=default_cfg["tools"],
                model_name=default_cfg["model_name"],
                embedding_name=default_cfg["embedding_name"],
                version=1,
                metadata={"author": "System", "reason": "Resetado automaticamente"},
            )
            
            # Registrar no controle de versões unificado
            unified_version = UnifiedVersionRepository.create_version(
                db=db,
                agent_type=agent_type,
                change_type="config",
                version_number=1,
                config_id=new_cfg.config_id,
                author="System",
                reason="Resetado automaticamente",
                metadata={"author": "System", "reason": "Resetado automaticamente"},
            )
            
            result["unified_version"] = unified_version.version_number

            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao resetar configuração: {str(e)}")
            result["success"] = False
            return result


agent_config_service = AgentConfigService() 
