from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from src.services.lang_graph.service import run_chatbot

router = APIRouter(tags=["LangGraph ChatBot"])


class AgentConfig(BaseModel):
    provider: str = Field(default="google", description="Provedor do modelo de IA.")
    temperature: float = Field(
        default=0.7, description="Temperatura para a geração do modelo."
    )
    model_name: str = Field(
        default="gemini-1.5-flash-latest",
        description="Nome do modelo de IA a ser usado.",
    )
    system_prompt: str = Field(
        default="Você é a EAI, assistente virtual da Prefeitura do Rio de Janeiro.",
        description="Prompt de sistema para definir a persona do chatbot.",
    )
    history_limit: int = Field(
        default=4, description="Número de mensagens do histórico a serem consideradas."
    )
    embedding_limit: int = Field(
        default=2, description="Número de documentos de embedding a serem considerados."
    )


class ChatRequest(BaseModel):
    user_id: str
    prompt: str
    agent_config: Optional[AgentConfig] = Field(default_factory=AgentConfig)


@router.post("/chat", summary="Inicia uma conversa com o chatbot EAI.")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint para interagir com o chatbot EAI.

    Recebe uma solicitação com o ID do usuário, o prompt e uma configuração opcional do agente.
    Se a configuração não for fornecida, valores padrão serão utilizados.

    Retorna a resposta estruturada do chatbot, incluindo o contexto utilizado.
    """
    # O endpoint é async para não bloquear o event loop, mas a chamada subjacente
    # ao LangGraph é síncrona.
    response = run_chatbot(
        user_id=request.user_id,
        message=request.prompt,
        agent_config=request.agent_config.dict(),
    )
    return response
