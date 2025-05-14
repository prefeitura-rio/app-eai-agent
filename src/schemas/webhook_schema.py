from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class WebhookEvent(BaseModel):
    """Schema para eventos recebidos via webhook."""
    type: str = Field(..., description="Tipo de evento recebido")
    data: Dict[str, Any] = Field(..., description="Dados do evento")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais do evento")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "message",
                "data": {
                    "user_number": "5531999999999",
                    "message": "Quero pagar meu IPTU!!",
                    "name": "João da Silva"
                },
                "metadata": {
                    "origin": "sistema_externo",
                    "timestamp": "2023-10-15T14:30:00Z"
                }
            }
        } 