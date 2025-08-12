from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class PromptInfo(BaseModel):
    """Informações do system prompt em uma versão."""
    prompt_id: str = Field(..., description="ID do prompt")
    content: Optional[str] = Field(None, description="Conteúdo completo do prompt")
    content_preview: Optional[str] = Field(None, description="Preview do conteúdo")
    is_active: bool = Field(..., description="Se o prompt está ativo")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados do prompt")
    created_at: Optional[str] = Field(None, description="Data de criação do prompt")
    updated_at: Optional[str] = Field(None, description="Data de atualização do prompt")


class ConfigInfo(BaseModel):
    """Informações da configuração em uma versão."""
    config_id: str = Field(..., description="ID da configuração")
    memory_blocks: List[Dict[str, Any]] = Field(default_factory=list, description="Blocos de memória")
    tools: List[str] = Field(default_factory=list, description="Ferramentas")
    model_name: Optional[str] = Field(None, description="Nome do modelo")
    embedding_name: Optional[str] = Field(None, description="Nome do embedding")
    is_active: bool = Field(..., description="Se a configuração está ativa")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados da configuração")
    created_at: Optional[str] = Field(None, description="Data de criação da configuração")
    updated_at: Optional[str] = Field(None, description="Data de atualização da configuração")


class UnifiedHistoryItem(BaseModel):
    """Item do histórico unificado."""
    version_id: str = Field(..., description="ID único da versão")
    version_number: int = Field(..., description="Número sequencial da versão")
    change_type: str = Field(..., description="Tipo da alteração: 'prompt', 'config', 'both'")
    created_at: Optional[str] = Field(None, description="Data de criação da versão")
    author: Optional[str] = Field(None, description="Autor da alteração")
    reason: Optional[str] = Field(None, description="Motivo da alteração")
    description: Optional[str] = Field(None, description="Descrição detalhada")
    preview: str = Field(..., description="Preview unificado da alteração")
    is_active: bool = Field(False, description="Se esta versão está atualmente ativa")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados da versão")
    
    # Informações opcionais dos componentes
    prompt: Optional[PromptInfo] = Field(None, description="Informações do prompt se aplicável")
    config: Optional[ConfigInfo] = Field(None, description="Informações da config se aplicável")


class UnifiedHistoryResponse(BaseModel):
    """Resposta do histórico unificado."""
    agent_type: str = Field(..., description="Tipo do agente")
    total_items: int = Field(..., description="Total de itens retornados")
    items: List[UnifiedHistoryItem] = Field(..., description="Lista de itens do histórico")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "agentic_search",
                "total_items": 3,
                "items": [
                    {
                        "version_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                        "version_number": 3,
                        "change_type": "both",
                        "created_at": "2023-05-16T14:30:15.123456",
                        "author": "admin",
                        "reason": "Melhoria completa do sistema",
                        "preview": "System Prompt: Você é EAí, assistente oficial... | Config: Tools: google_search, public_services...",
                        "is_active": True,
                        "metadata": {"author": "admin", "reason": "Melhoria completa"},
                        "prompt": {
                            "prompt_id": "abc123",
                            "content_preview": "Você é EAí, assistente oficial...",
                            "is_active": True,
                            "metadata": {}
                        },
                        "config": {
                            "config_id": "def456",
                            "tools": ["google_search", "public_services"],
                            "model_name": "gpt-4",
                            "is_active": True,
                            "metadata": {}
                        }
                    }
                ]
            }
        }


class UnifiedVersionDetailsResponse(BaseModel):
    """Detalhes completos de uma versão específica."""
    version_id: str = Field(..., description="ID único da versão")
    version_number: int = Field(..., description="Número sequencial da versão")
    change_type: str = Field(..., description="Tipo da alteração")
    created_at: Optional[str] = Field(None, description="Data de criação")
    author: Optional[str] = Field(None, description="Autor da alteração")
    reason: Optional[str] = Field(None, description="Motivo da alteração")
    description: Optional[str] = Field(None, description="Descrição detalhada")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados da versão")
    
    # Dados completos dos componentes
    prompt: Optional[PromptInfo] = Field(None, description="Dados completos do prompt")
    config: Optional[ConfigInfo] = Field(None, description="Dados completos da configuração")

    class Config:
        json_schema_extra = {
            "example": {
                "version_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "version_number": 3,
                "change_type": "both",
                "created_at": "2023-05-16T14:30:15.123456",
                "author": "admin",
                "reason": "Melhoria completa do sistema",
                "description": "Atualização que incluiu melhorias no prompt e novas ferramentas",
                "metadata": {"author": "admin", "reason": "Melhoria completa"},
                "prompt": {
                    "prompt_id": "abc123",
                    "content": "Você é EAí, o assistente oficial da Prefeitura do Rio de Janeiro...",
                    "is_active": True,
                    "created_at": "2023-05-16T14:30:15.123456",
                    "metadata": {"author": "admin"}
                },
                "config": {
                    "config_id": "def456",
                    "memory_blocks": [{"label": "core_memory", "value": "..."}],
                    "tools": ["google_search", "public_services"],
                    "model_name": "gpt-4",
                    "embedding_name": "text-embedding-ada-002",
                    "is_active": True,
                    "created_at": "2023-05-16T14:30:15.123456",
                    "metadata": {"author": "admin"}
                }
            }
        } 