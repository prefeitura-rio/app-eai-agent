from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

from src.db import Base


class SystemPrompt(Base):
    """Modelo para armazenar system prompts."""
    __tablename__ = "system_prompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    agent_type = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    prompt_metadata = Column(JSONB, nullable=True)

    __table_args__ = (
        UniqueConstraint('agent_type', 'version', name='uix_agent_type_version'),
    )

    def __repr__(self):
        return f"<SystemPrompt(id={self.id}, agent_type='{self.agent_type}', version={self.version})>"


class SystemPromptDeployment(Base):
    """Modelo para armazenar informações de implantação de system prompts em agentes."""
    __tablename__ = "system_prompt_deployments"

    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    prompt_id = Column(String(36), nullable=False, index=True)
    agent_id = Column(String(50), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="success")  # success, failed
    deployed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    details = Column(JSONB, nullable=True)

    def __repr__(self):
        return f"<SystemPromptDeployment(id={self.id}, agent_id='{self.agent_id}', status='{self.status}')>" 