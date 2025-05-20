from fastapi import APIRouter, Depends, HTTPException

from src.core.security.dependencies import validar_token
from src.schemas.webhook_schema import WebhookEvent
from src.utils.webhook.processar_eventos_util import processar_evento

router = APIRouter(
    prefix="/webhook", tags=["Webhook"], dependencies=[Depends(validar_token)]
)


@router.post("/")
async def receber_webhook(evento: WebhookEvent):
    """
    Endpoint para receber eventos webhook.
    """
    tipos_validos = ["message", "timer"]
    if evento.type not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de evento inválido. Valores aceitos: {', '.join(tipos_validos)}",
        )

    response = await processar_evento(evento)

    return response
