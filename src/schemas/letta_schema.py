from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


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


class RawMessageResponse(BaseModel):
    """Schema para resposta bruta do agente Letta, contendo todos os tipos de mensagens."""

    system_messages: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lista de mensagens do sistema"
    )
    user_messages: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lista de mensagens do usuário"
    )
    reasoning_messages: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lista de mensagens de raciocínio"
    )
    tool_call_messages: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lista de mensagens de chamada de ferramentas"
    )
    tool_return_messages: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lista de mensagens de retorno de ferramentas"
    )
    assistant_messages: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lista de mensagens do assistente"
    )
    letta_usage_statistics: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lista de estatísticas de uso do Letta"
    )
    ordered: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Lista ordenada de mensagens conforme recebidas, cada item contendo 'type' e 'message'"
    )
    error: Optional[str] = Field(None, description="Erro ocorrido durante o processamento, se houver")

    class Config:
        json_schema_extra = {
            "example": {
                "system_messages": [],
                "user_messages": [{"role": "user", "content": "Olá"}],
                "reasoning_messages": [],
                "tool_call_messages": [],
                "tool_return_messages": [],
                "assistant_messages": [{"role": "assistant", "content": "Olá! Como posso ajudar?"}],
                "letta_usage_statistics": [{"tokens": {"prompt": 10, "completion": 8}}],
                "ordered": [
                    {"type": "user_message", "message": {"role": "user", "content": "Olá"}},
                    {"type": "assistant_message", "message": {"role": "assistant", "content": "Olá! Como posso ajudar?"}}
                ]
            }
        }
