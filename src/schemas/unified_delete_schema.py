from pydantic import BaseModel, Field
from typing import Optional


class UnifiedDeleteResponse(BaseModel):
    """Schema para resposta da exclusão de versão unificada."""

    success: bool = Field(..., description="Status geral da operação")
    agent_type: str = Field(..., description="Tipo do agente")
    version_number: int = Field(..., description="Número da versão excluída")
    version_display: Optional[str] = Field(None, description="Nome da versão no padrão eai-YYYY-MM-DD-vX")
    prompt_id: Optional[str] = Field(None, description="ID do prompt excluído")
    config_id: Optional[str] = Field(None, description="ID da configuração excluída")
    deployments_deleted: int = Field(default=0, description="Número de deployments excluídos")
    reactivated_version: Optional[int] = Field(None, description="Número da versão do prompt que foi reativada (se aplicável)")
    reactivated_prompt_id: Optional[str] = Field(None, description="ID do prompt que foi reativado (se aplicável)")
    reactivated_config_version: Optional[int] = Field(None, description="Número da versão do config que foi reativada (se aplicável)")
    reactivated_config_id: Optional[str] = Field(None, description="ID do config que foi reativado (se aplicável)")
    message: str = Field(..., description="Mensagem informativa sobre a operação")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "agent_type": "agentic_search",
                "version_number": 99,
                "version_display": "eai-2025-08-27-v99",
                "prompt_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "config_id": "a1b2c3d4-1234-5678-9abc-def0123456789",
                "deployments_deleted": 5,
                "message": "Versão 99 excluída com sucesso"
            }
        }