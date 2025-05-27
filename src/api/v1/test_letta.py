from fastapi import APIRouter, Depends, Body
from typing import Optional

from src.core.security.dependencies import validar_token
from src.services.letta.letta_service import letta_service
from src.schemas.letta_schema import MessageRequest, MessageResponse, RawMessageResponse

router = APIRouter(
    prefix="/letta", tags=["Letta"], dependencies=[Depends(validar_token)]
)


@router.post("/test-message", response_model=MessageResponse)
async def test_send_message(
    request: MessageRequest = Body(...),
):
    """
    Endpoint para testar o envio de mensagens para o agente Letta.

    Parâmetros:
    - agent_id: ID do agente para o qual a mensagem será enviada
    - message: Conteúdo da mensagem
    - name: Nome opcional do remetente

    Retorna:
    - response: Resposta do agente
    """
    response = await letta_service.send_message(
        agent_id=request.agent_id, message_content=request.message, name=request.name
    )

    return MessageResponse(response=response)


@router.post("/test-message-raw", response_model=RawMessageResponse)
async def test_send_message_raw(
    request: MessageRequest = Body(...),
):
    """
    Endpoint para testar o envio de mensagens para o agente Letta e receber todos os tipos de mensagens.
    Útil para fins de debug e análise detalhada das respostas do agente.

    Parâmetros:
    - agent_id: ID do agente para o qual a mensagem será enviada
    - message: Conteúdo da mensagem
    - name: Nome opcional do remetente

    Retorna:
    - Dicionário contendo todas as mensagens do stream organizadas por tipo:
        - system_messages: Mensagens do sistema
        - user_messages: Mensagens do usuário
        - reasoning_messages: Mensagens de raciocínio
        - tool_call_messages: Mensagens de chamada de ferramentas
        - tool_return_messages: Mensagens de retorno de ferramentas
        - assistant_messages: Mensagens do assistente
        - letta_usage_statistics: Estatísticas de uso do Letta
        - error: Erro ocorrido durante o processamento, se houver
    """
    response = await letta_service.send_message_raw(
        agent_id=request.agent_id, message_content=request.message, name=request.name
    )
    
    formatted_response = {}
    
    if "error" in response:
        formatted_response["error"] = response["error"]
    
    for key in [
        "system_messages", 
        "user_messages", 
        "reasoning_messages", 
        "tool_call_messages", 
        "tool_return_messages", 
        "assistant_messages", 
        "letta_usage_statistics"
    ]:
        formatted_response[key] = [
            message.dict() if hasattr(message, "dict") else message
            for message in response.get(key, [])
        ]
    
    return RawMessageResponse(**formatted_response)
