from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union


class SystemPromptUpdateRequest(BaseModel):
    """Schema para requisição de atualização de system prompt."""
    new_prompt: str = Field(..., description="Novo texto para o system prompt")
    agent_type: str = Field("agentic_search", description="Tipo de agente a ser atualizado")
    update_template: bool = Field(True, description="Se deve atualizar o template do system prompt")
    update_agents: bool = Field(True, description="Se deve atualizar os agentes existentes")
    tags: Optional[List[str]] = Field(None, description="Tags para filtrar os agentes a serem atualizados")

    class Config:
        json_schema_extra = {
            "example": {
                "new_prompt": "Novo conteúdo do system prompt...",
                "agent_type": "agentic_search",
                "update_template": True,
                "update_agents": True,
                "tags": ["agentic_search", "user_123456"]
            }
        }


class AgentUpdateResult(BaseModel):
    """Resultado da atualização de um agente."""
    agent_id: str = Field(..., description="ID do agente")
    success: bool = Field(..., description="Status da atualização")


class SystemPromptUpdateResponse(BaseModel):
    """Schema para resposta da atualização de system prompt."""
    success: bool = Field(..., description="Status geral da operação")
    template_updated: bool = Field(..., description="Status da atualização do template")
    agents_updated: Dict[str, bool] = Field(..., description="Status da atualização dos agentes")
    message: str = Field("", description="Mensagem adicional sobre a operação")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "template_updated": True,
                "agents_updated": {
                    "agt_123456789": True,
                    "agt_987654321": True
                },
                "message": "System prompt atualizado com sucesso para 2 agentes."
            }
        }


class SystemPromptGetResponse(BaseModel):
    """Schema para resposta da obtenção do system prompt atual."""
    prompt: str = Field(..., description="Texto do system prompt atual")
    agent_type: str = Field(..., description="Tipo de agente")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Conteúdo atual do system prompt...",
                "agent_type": "agentic_search"
            }
        } 