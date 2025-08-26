import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from src.db import Base


class UnifiedVersion(Base):
    """
    Modelo para controle centralizado de versões.
    Cada alteração (prompt ou config) gera uma nova versão sequencial.
    """

    __tablename__ = "unified_versions"

    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_type = Column(String(50), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, index=True)
    
    # Tipo de alteração: 'prompt', 'config', 'both'
    change_type = Column(String(20), nullable=False)
    
    # IDs das entidades relacionadas
    prompt_id = Column(UUID(as_uuid=True), nullable=True)
    config_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Metadados da versão
    author = Column(String(100), nullable=True)
    reason = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    # Controle temporal
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Metadados adicionais em JSON
    version_metadata = Column(JSON, default=dict)
    
    def __repr__(self):
        return f"<UnifiedVersion(agent_type='{self.agent_type}', version={self.version_number}, type='{self.change_type}')>" 