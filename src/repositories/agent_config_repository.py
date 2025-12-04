from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.agent_config_model import AgentConfig


class AgentConfigRepository:
    """Repositório para manipular AgentConfig no banco de dados."""

    @staticmethod
    def create_config(
        db: Session,
        agent_type: str,
        memory_blocks: Optional[List[Dict[str, Any]]] = None,
        tools: Optional[List[str]] = None,
        model_name: Optional[str] = None,
        embedding_name: Optional[str] = None,
        version: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentConfig:
        """Cria uma nova configuração de agente.

        Se version não for fornecida, incrementa automaticamente em relação à última ativa.
        Todos os registros ativos anteriores serão desativados.
        """
        if version is None:
            latest_cfg = AgentConfigRepository.get_latest_config(db, agent_type)
            version = 1 if latest_cfg is None else latest_cfg.version + 1

        # Desativa configs anteriores
        if version > 1:
            db.query(AgentConfig).filter(
                AgentConfig.agent_type == agent_type, AgentConfig.is_active == True
            ).update({"is_active": False})

        cfg = AgentConfig(
            agent_type=agent_type,
            memory_blocks=memory_blocks or [],
            tools=tools or [],
            model_name=model_name,
            embedding_name=embedding_name,
            version=version,
            is_active=True,
            config_metadata=metadata or {},
        )

        db.add(cfg)
        db.commit()
        db.refresh(cfg)
        return cfg

    @staticmethod
    def get_active_config(db: Session, agent_type: str) -> Optional[AgentConfig]:
        return (
            db.query(AgentConfig)
            .filter(AgentConfig.agent_type == agent_type, AgentConfig.is_active == True)
            .first()
        )

    @staticmethod
    def get_latest_config(db: Session, agent_type: str) -> Optional[AgentConfig]:
        return (
            db.query(AgentConfig)
            .filter(AgentConfig.agent_type == agent_type)
            .order_by(desc(AgentConfig.version))
            .first()
        )

    @staticmethod
    def get_previous_config(db: Session, agent_type: str) -> Optional[AgentConfig]:
        """Busca a penúltima configuração (segunda mais recente) para um tipo de agente.
        Útil para reativar após deletar a última config.
        """
        configs = (
            db.query(AgentConfig)
            .filter(AgentConfig.agent_type == agent_type)
            .order_by(desc(AgentConfig.version))
            .limit(2)
            .all()
        )
        
        # Retorna a segunda config se existirem pelo menos 2
        return configs[1] if len(configs) >= 2 else None

    @staticmethod
    def list_configs(
        db: Session, agent_type: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[AgentConfig]:
        query = db.query(AgentConfig)
        if agent_type:
            query = query.filter(AgentConfig.agent_type == agent_type)
        return (
            query.order_by(AgentConfig.agent_type, desc(AgentConfig.version))
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def delete_configs_by_agent_type(db: Session, agent_type: str) -> int:
        return (
            db.query(AgentConfig)
            .filter(AgentConfig.agent_type == agent_type)
            .delete(synchronize_session=False)
        )

    @staticmethod
    def get_config_ids_by_agent_type(db: Session, agent_type: str) -> List[str]:
        ids = (
            db.query(AgentConfig.config_id)
            .filter(AgentConfig.agent_type == agent_type)
            .all()
        )
        return [i[0] for i in ids]

    @staticmethod
    def get_config_by_id(db: Session, config_id: str) -> Optional[AgentConfig]:
        return db.query(AgentConfig).filter(AgentConfig.config_id == config_id).first()

    @staticmethod
    def count_configs_by_date_and_type(db: Session, agent_type: str, date) -> int:
        """
        Conta quantas configurações foram criadas em uma data específica para um tipo de agente.

        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            date: Data para filtrar (datetime.date)

        Returns:
            int: Número de configurações criadas na data
        """
        from sqlalchemy import func, cast, Date
        
        return (
            db.query(AgentConfig)
            .filter(
                AgentConfig.agent_type == agent_type,
                cast(AgentConfig.created_at, Date) == date
            )
            .count()
        )

    @staticmethod
    def delete_config_by_id(db: Session, config_id: str) -> bool:
        """
        Exclui uma configuração específica pelo ID.

        Args:
            db: Sessão do banco de dados
            config_id: ID da configuração a ser excluída

        Returns:
            bool: True se a configuração foi excluída, False se não encontrada
        """
        result = (
            db.query(AgentConfig)
            .filter(AgentConfig.config_id == config_id)
            .delete(synchronize_session=False)
        )

        return result > 0 