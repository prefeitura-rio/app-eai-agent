from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


class SystemPromptUpdateRequest(BaseModel):
    """Schema para requisição de atualização de system prompt."""

    new_prompt: str = Field(..., description="Novo texto para o system prompt")
    agent_type: str = Field(
        "agentic_search", description="Tipo de agente a ser atualizado"
    )
    update_agents: bool = Field(
        True, description="Se deve atualizar os agentes existentes"
    )
    tags: Optional[List[str]] = Field(
        None, description="Tags para filtrar os agentes a serem atualizados"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Metadados adicionais para armazenar com o prompt"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "new_prompt": "Novo conteúdo do system prompt...",
                "agent_type": "agentic_search",
                "update_agents": True,
                "tags": ["agentic_search", "user_123456"],
                "metadata": {
                    "author": "admin",
                    "reason": "Melhoria na resposta de emergência",
                },
            }
        }


class AgentUpdateResult(BaseModel):
    """Resultado da atualização de um agente."""

    agent_id: str = Field(..., description="ID do agente")
    success: bool = Field(..., description="Status da atualização")


class SystemPromptUpdateResponse(BaseModel):
    """Schema para resposta da atualização de system prompt."""

    success: bool = Field(..., description="Status geral da operação")
    prompt_id: Optional[str] = Field(
        None, description="ID do prompt criado no banco de dados"
    )
    agents_updated: Dict[str, bool] = Field(
        ..., description="Status da atualização dos agentes"
    )
    message: str = Field("", description="Mensagem adicional sobre a operação")
    version: Optional[int] = Field(None, description="Versão do prompt")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "prompt_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "agents_updated": {"agt_123456789": True, "agt_987654321": True},
                "message": "System prompt atualizado com sucesso para 2 agentes.",
                "version": 1,
            }
        }


class SystemPromptGetResponse(BaseModel):
    """Schema para resposta da obtenção do system prompt atual."""

    prompt: str = Field(..., description="Texto do system prompt atual")
    agent_type: str = Field(..., description="Tipo de agente")
    version: Optional[int] = Field(None, description="Versão do prompt")
    prompt_id: Optional[str] = Field(None, description="ID do prompt no banco de dados")
    created_at: Optional[datetime] = Field(
        None, description="Data de criação do prompt"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Conteúdo atual do system prompt...",
                "agent_type": "agentic_search",
                "version": 3,
                "prompt_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "created_at": "2023-05-16T14:30:15.123456",
            }
        }


class SystemPromptHistoryItem(BaseModel):
    """Item do histórico de system prompts."""

    prompt_id: str = Field(..., description="ID do prompt")
    version: int = Field(..., description="Versão do prompt")
    is_active: bool = Field(..., description="Se o prompt está ativo")
    created_at: str = Field(
        ..., description="Data de criação formatada como string ISO"
    )
    updated_at: str = Field(
        ..., description="Data de atualização formatada como string ISO"
    )
    content: str = Field(..., description="Conteúdo resumido do prompt")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados do prompt")


class SystemPromptHistoryResponse(BaseModel):
    """Schema para resposta da obtenção do histórico de system prompts."""

    agent_type: str = Field(..., description="Tipo de agente")
    prompts: List[SystemPromptHistoryItem] = Field(..., description="Lista de prompts")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "agentic_search",
                "prompts": [
                    {
                        "prompt_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                        "version": 3,
                        "is_active": True,
                        "created_at": "2023-05-16T14:30:15.123456",
                        "updated_at": "2023-05-16T14:30:15.123456",
                        "content": "Fundamental Identity: You are EAí, the official...",
                        "metadata": {
                            "author": "admin",
                            "reason": "Melhoria na resposta de emergência",
                        },
                    },
                    {
                        "prompt_id": "a1b2c3d4-1234-5678-9abc-def0123456789",
                        "version": 2,
                        "is_active": False,
                        "created_at": "2023-05-10T09:15:30.123456",
                        "updated_at": "2023-05-10T09:15:30.123456",
                        "content": "Fundamental Identity: You are EAí, the official...",
                        "metadata": {"author": "admin", "reason": "Ajuste inicial"},
                    },
                ],
            }
        }


class SystemPromptResetResponse(BaseModel):
    """Schema para resposta do reset de system prompt."""

    success: bool = Field(..., description="Status geral da operação")
    agent_type: str = Field(..., description="Tipo de agente que foi resetado")
    agents_updated: Dict[str, bool] = Field(
        ..., description="Status da atualização dos agentes"
    )
    message: str = Field("", description="Mensagem adicional sobre a operação")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "agent_type": "agentic_search",
                "agents_updated": {"agt_123456789": True, "agt_987654321": True},
                "message": "System prompt resetado com sucesso para 2 agentes.",
            }
        }


class SystemPromptDeleteResponse(BaseModel):
    """Schema para resposta da deleção do último system prompt."""

    success: bool = Field(..., description="Status geral da operação")
    agent_type: str = Field(..., description="Tipo de agente")
    deleted_version: Optional[int] = Field(
        None, description="Versão do prompt que foi deletado"
    )
    active_version: Optional[int] = Field(
        None, description="Versão do prompt que ficou ativo"
    )
    previous_prompt_id: Optional[str] = Field(
        None, description="ID do prompt que foi reativado"
    )
    agents_updated: Dict[str, bool] = Field(
        default_factory=dict, description="Status da atualização dos agentes"
    )
    message: str = Field("", description="Mensagem adicional sobre a operação")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "agent_type": "agentic_search",
                "deleted_version": 5,
                "active_version": 4,
                "previous_prompt_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "agents_updated": {"agt_123456789": True, "agt_987654321": True},
                "message": "Última versão do system prompt deletada com sucesso.",
            }
        }
