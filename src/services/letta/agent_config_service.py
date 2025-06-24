from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from loguru import logger

from src.db import get_db_session
from src.repositories.agent_config_repository import AgentConfigRepository
from src.services.letta.letta_service import letta_service
from src.services.letta.agents.memory_blocks.agentic_search_mb import (
    get_agentic_search_memory_blocks,
)
from src.config import env


class AgentConfigService:
    """Serviço para gerenciar configurações de agentes (memory blocks, tools, model, embedding) com controle de versão."""

    def __init__(self):
        pass

    def _default_config(self, agent_type: str) -> Dict[str, Any]:
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
            default_cfg = self._default_config(agent_type)
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
                default_cfg = self._default_config(agent_type)
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
        update_agents: bool = True,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """Atualiza configuração e opcionalmente propaga para agentes."""
        result: Dict[str, Any] = {"success": True, "config_id": None, "agents_updated": {}}

        if db is None:
            with get_db_session() as session:
                db = session
        return await self._perform_update(db, new_cfg_values, agent_type, update_agents, tags, metadata, result)

    async def _perform_update(
        self,
        db: Session,
        new_cfg_values: Dict[str, Any],
        agent_type: str,
        update_agents: bool,
        tags: Optional[List[str]],
        metadata: Optional[Dict[str, Any]],
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        cfg = AgentConfigRepository.create_config(
            db=db,
            agent_type=agent_type,
            memory_blocks=new_cfg_values.get("memory_blocks"),
            tools=new_cfg_values.get("tools"),
            model_name=new_cfg_values.get("model_name"),
            embedding_name=new_cfg_values.get("embedding_name"),
            metadata=metadata or {"source": "api"},
        )
        result["config_id"] = cfg.config_id

        if update_agents:
            agents_result = await self._update_all_agents(
                new_cfg_values=new_cfg_values,
                agent_type=agent_type,
                tags=tags,
            )
            result["agents_updated"] = agents_result
            if agents_result and not all(agents_result.values()):
                result["success"] = False
        return result

    async def _update_all_agents(
        self,
        new_cfg_values: Dict[str, Any],
        agent_type: str,
        tags: Optional[List[str]],
    ) -> Dict[str, bool]:
        client = letta_service.get_client_async()
        results: Dict[str, bool] = {}
        filter_tags = tags if tags else ([agent_type] if agent_type else [])
        agents = await client.agents.list(tags=filter_tags)
        if not agents:
            logger.info(f"Nenhum agente encontrado com as tags: {filter_tags}")
            return results

        # Obter IDs das ferramentas
        available_tools = await client.tools.list()
        tool_ids = [tool.id for tool in available_tools if tool.name in (new_cfg_values.get("tools") or [])]

        for agent in agents:
            try:
                memory_blocks = await client.blocks.list(agent_id=agent.id)
                memory_blocks_ids = [block.id for block in memory_blocks if block.name in new_cfg_values.get("memory_blocks")]
                
                for memory_block_id in memory_blocks_ids:
                    await client.blocks.delete(memory_block_id)
                
                new_memory_blocks_ids = []
                
                for memory_block in new_cfg_values.get("memory_blocks"):
                  memory_block = await client.blocks.create(
                    agent_id=agent.id,
                    name=memory_block["label"],
                    value=memory_block["value"],
                    limit=memory_block["limit"],
                  )
                  new_memory_blocks_ids.append(memory_block.id)
                
                await client.agents.modify(
                    agent_id=agent.id,
                    block_ids=new_memory_blocks_ids,
                    tool_ids=tool_ids,
                    model=new_cfg_values.get("model_name"),
                    embedding=new_cfg_values.get("embedding_name"),
                )
                results[agent.id] = True
            except Exception as agent_error:
                results[agent.id] = False
                logger.error(f"Erro ao atualizar agente {agent.id}: {str(agent_error)}")
        return results

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
        self, agent_type: str, update_agents: bool = False, db: Session = None
    ) -> Dict[str, Any]:
        """Reseta a configuração: remove histórico e recria padrão."""

        result: Dict[str, Any] = {"success": True, "agents_updated": {}}

        if db is None:
            with get_db_session() as session:
                db = session

        try:
            # Apaga histórico
            AgentConfigRepository.delete_configs_by_agent_type(db, agent_type)
            db.commit()

            default_cfg = self._default_config(agent_type)
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

            if update_agents:
                agents_result = await self._update_all_agents(
                    new_cfg_values=default_cfg,
                    agent_type=agent_type,
                    tags=[agent_type],
                )
                result["agents_updated"] = agents_result
                if agents_result and not all(agents_result.values()):
                    result["success"] = False

            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao resetar configuração: {str(e)}")
            result["success"] = False
            return result


agent_config_service = AgentConfigService() 