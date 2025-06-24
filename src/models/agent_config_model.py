from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

from src.db import Base


class AgentConfig(Base):
    """Modelo para armazenar configurações de agente (memory blocks, tools, model, embedding) com controle de versão."""

    __tablename__ = "agent_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(
        String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True
    )
    agent_type = Column(String(50), nullable=False, index=True)

    # Campos configuráveis
    memory_blocks = Column(JSONB, nullable=True)
    tools = Column(JSONB, nullable=True)
    model_name = Column(String(100), nullable=True)
    embedding_name = Column(String(100), nullable=True)

    # Controle de versão e metadados
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    config_metadata = Column(JSONB, nullable=True)

    __table_args__ = (
        UniqueConstraint("agent_type", "version", name="uix_agent_cfg_agent_type_version"),
    )

    def __repr__(self):
        return f"<AgentConfig(id={self.id}, agent_type='{self.agent_type}', version={self.version})>" 