from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class MessageRequest(BaseModel):
    """Schema para requisição de envio de mensagem para o agente Letta."""

    agent_id: str = Field(
        ..., description="ID do agente para o qual a mensagem será enviada"
    )
    message: str = Field(..., description="Conteúdo da mensagem")
    name: Optional[str] = Field(None, description="Nome opcional do remetente")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agt_123456789",
                "message": "Olá, como posso ajudar?",
                "name": "Usuário",
            }
        }


class MessageResponse(BaseModel):
    """Schema para resposta do agente Letta."""

    response: str = Field(..., description="Resposta do agente Letta")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Olá! Sou o assistente Letta e estou aqui para ajudar."
            }
        }
