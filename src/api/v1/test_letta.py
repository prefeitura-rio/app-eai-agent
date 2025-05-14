from fastapi import APIRouter, Depends, Body
from typing import Optional

from src.core.security.dependencies import validar_token
from src.services.letta.letta_service import letta_service
from src.schemas.letta import MessageRequest, MessageResponse

router = APIRouter(prefix="/letta", tags=["Letta"], dependencies=[Depends(validar_token)])

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
        agent_id=request.agent_id,
        message_content=request.message,
        name=request.name
    )
    
    return MessageResponse(response=response) 