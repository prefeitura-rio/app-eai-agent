from fastapi import APIRouter, Depends, HTTPException

from src.core.security.dependencies import validar_token
from src.services.letta.letta_service import letta_service
from src.schemas.webhook_schema import WebhookEvent


router = APIRouter(prefix="/webhook", tags=["Webhook"], dependencies=[Depends(validar_token)])


async def processar_evento(evento: WebhookEvent):
    """
    Processa eventos recebidos de forma assíncrona.
    
    Args:
        evento: Dados do evento a ser processado
    """
    try:
        if evento.tipo == "message":
          try:
            if "user_number" in evento.data and "message" in evento.data:
              
                nome = evento.data.get("name")
                user_number = evento.data["user_number"]
                message = evento.data["message"]
                
                agent_id = letta_service.get_agent_id_by_tags([user_number])
                
                if not agent_id:
                  agent = letta_service.create_agent(agent_type="agentic_search", tags=[user_number])
                  agent_id = agent.id         
                
                response = await letta_service.send_message(
                    agent_id=agent_id,
                    message_content=message,
                    name=nome if nome else None
                )
                
                return {"status": "success", "message": response}
          except Exception as e:
            print(f"Erro ao processar evento: {str(e)}")
            return {"status": "error", "message": str(e)}
          
        elif evento.tipo == "timer":
          try:
            if "user_number" in evento.data:
              
                agent_id = letta_service.get_agent_id_by_tags([user_number])
                
                if not agent_id:
                  
                  agent = letta_service.create_agent(agent_type="agentic_search", tags=[user_number])
                  agent_id = agent.id
                  
                response = await letta_service.send_timer_message(agent_id=agent_id)
                
                return {"status": "success", "message": response}
          except Exception as e:
            print(f"Erro ao processar evento: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    except Exception as e:
        print(f"Erro ao processar evento: {str(e)}")


@router.post("/")
async def receber_webhook(evento: WebhookEvent):
    """
    Endpoint para receber eventos webhook.
    """
    tipos_validos = ["mensagem", "timer", "notificacao"]
    if evento.tipo not in tipos_validos:
        raise HTTPException(status_code=400, detail=f"Tipo de evento inválido. Valores aceitos: {', '.join(tipos_validos)}")
    
    response = await processar_evento(evento)
    
    return response
    
    
