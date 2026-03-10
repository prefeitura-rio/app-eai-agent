from pydantic import BaseModel, Field
from typing import Optional


class UnifiedResetResponse(BaseModel):
    """Schema para resposta do reset unificado."""

    success: bool = Field(..., description="Status geral da operação")
    agent_type: str = Field(..., description="Tipo do agente resetado")
    unified_version: Optional[int] = Field(None, description="Número da versão unificada criada")
    version_display: Optional[str] = Field(None, description="Nome da versão no padrão eai-YYYY-MM-DD-vX")
    prompt_id: Optional[str] = Field(None, description="ID do prompt padrão criado")
    config_id: Optional[str] = Field(None, description="ID da configuração padrão criada")
    message: str = Field(..., description="Mensagem informativa sobre a operação")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "agent_type": "agentic_search",
                "unified_version": 1,
                "version_display": "eai-2025-06-26-v1",
                "prompt_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "config_id": "a1b2c3d4-1234-5678-9abc-def0123456789",
                "message": "Reset unificado concluído com sucesso"
            }
        }
