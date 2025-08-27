from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from src.models.unified_version_model import UnifiedVersion


class UnifiedVersionRepository:
    """Repositório para controle centralizado de versões."""

    @staticmethod
    def get_next_version_number(db: Session, agent_type: str) -> int:
        """
        Obtém o próximo número de versão para um tipo de agente.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            
        Returns:
            int: Próximo número de versão
        """
        latest_version = (
            db.query(func.max(UnifiedVersion.version_number))
            .filter(UnifiedVersion.agent_type == agent_type)
            .scalar()
        )
        
        return (latest_version or 0) + 1

    @staticmethod
    def create_version(
        db: Session,
        agent_type: str,
        change_type: str,
        prompt_id: Optional[str] = None,
        config_id: Optional[str] = None,
        author: Optional[str] = None,
        reason: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UnifiedVersion:
        """
        Cria uma nova versão no controle unificado.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            change_type: Tipo da alteração ('prompt', 'config', 'both')
            prompt_id: ID do prompt relacionado
            config_id: ID da configuração relacionada
            author: Autor da alteração
            reason: Motivo da alteração
            description: Descrição detalhada
            metadata: Metadados adicionais
            
        Returns:
            UnifiedVersion: Nova versão criada
        """
        version_number = UnifiedVersionRepository.get_next_version_number(db, agent_type)
        
        version = UnifiedVersion(
            agent_type=agent_type,
            version_number=version_number,
            change_type=change_type,
            prompt_id=prompt_id,
            config_id=config_id,
            author=author,
            reason=reason,
            description=description,
            version_metadata=metadata or {},
        )
        
        db.add(version)
        db.commit()
        db.refresh(version)
        
        return version

    @staticmethod
    def list_versions(
        db: Session,
        agent_type: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[UnifiedVersion]:
        """
        Lista versões por tipo de agente ordenadas por versão decrescente.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            limit: Limite de resultados
            offset: Deslocamento para paginação
            
        Returns:
            List[UnifiedVersion]: Lista de versões
        """
        return (
            db.query(UnifiedVersion)
            .filter(UnifiedVersion.agent_type == agent_type)
            .order_by(desc(UnifiedVersion.version_number))
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_version_by_number(
        db: Session,
        agent_type: str,
        version_number: int
    ) -> Optional[UnifiedVersion]:
        """
        Obtém uma versão específica pelo número.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            version_number: Número da versão
            
        Returns:
            Optional[UnifiedVersion]: Versão encontrada ou None
        """
        return (
            db.query(UnifiedVersion)
            .filter(
                UnifiedVersion.agent_type == agent_type,
                UnifiedVersion.version_number == version_number
            )
            .first()
        )

    @staticmethod
    def delete_versions_by_agent_type(db: Session, agent_type: str) -> int:
        """
        Remove todas as versões de um tipo de agente.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            
        Returns:
            int: Número de registros removidos
        """
        result = (
            db.query(UnifiedVersion)
            .filter(UnifiedVersion.agent_type == agent_type)
            .delete(synchronize_session=False)
        )
        
        return result

    @staticmethod
    def delete_version_by_number(
        db: Session,
        agent_type: str,
        version_number: int
    ) -> bool:
        """
        Remove uma versão específica do controle unificado.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            version_number: Número da versão a ser removida
            
        Returns:
            bool: True se a versão foi removida, False se não encontrada
        """
        result = (
            db.query(UnifiedVersion)
            .filter(
                UnifiedVersion.agent_type == agent_type,
                UnifiedVersion.version_number == version_number
            )
            .delete(synchronize_session=False)
        )
        
        return result > 0 