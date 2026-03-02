from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class AgentConfigUpdateRequest(BaseModel):
    agent_type: str = Field("agentic_search", description="Tipo do agente")
    memory_blocks: Optional[List[Dict[str, Any]]] = Field(None, description="Memory blocks personalizados")
    tools: Optional[List[str]] = Field(None, description="Lista de ferramentas")
    model_name: Optional[str] = Field(None, description="Nome do modelo LLM")
    embedding_name: Optional[str] = Field(None, description="Nome do modelo de embedding")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais (autor, motivo, etc.)")


class AgentConfigUpdateResponse(BaseModel):
    success: bool
    config_id: Optional[str]
    message: str


class AgentConfigGetResponse(BaseModel):
    config_id: Optional[str]
    agent_type: str
    version: Optional[int]
    memory_blocks: Optional[List[Dict[str, Any]]]
    tools: Optional[List[str]]
    model_name: Optional[str]
    embedding_name: Optional[str]
    created_at: Optional[str]


class AgentConfigHistoryItem(BaseModel):
    config_id: str
    version: int
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]
    metadata: Optional[Dict[str, Any]]
    tools: Optional[List[str]]
    model_name: Optional[str]
    embedding_name: Optional[str]


class AgentConfigHistoryResponse(BaseModel):
    agent_type: str
    configs: List[AgentConfigHistoryItem]


class AgentConfigResetResponse(BaseModel):
    success: bool
    agent_type: str
    message: str
