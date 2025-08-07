import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.services.eai_gateway.api import EAIClient, CreateAgentRequest, EAIClientError
from pydantic import BaseModel
from typing import Dict, Any
from src.utils.log import logger


from typing import Dict, Any, Optional, List

# --- Pydantic Models ---


class ChatRequest(BaseModel):
    user_number: str
    message: str
    timeout: int = 180
    polling_interval: int = 2
    provider: str = "google_agent_engine"


class ChatResponse(BaseModel):
    response: Dict[str, Any]


# --- Router Setup ---

router = APIRouter(
    prefix="/eai-gateway",
    tags=["EAI Gateway"],
    dependencies=[Depends(validar_token)],
)


# --- Endpoints ---


@router.post("/chat", response_model=ChatResponse)
async def handle_chat(
    request: ChatRequest,
):
    """
    Handles a user chat message.
    - If `use_same_agent` is true, it retrieves the user's existing agent.
    - If no agent exists, or `use_same_agent` is false, it creates a new agent.
    - When creating an agent, it uses any provided optional parameters, falling back to defaults.
    """
    eai_client = EAIClient(
        timeout=180,
        polling_interval=2,
        provider=request.provider,
    )
    try:
        response = await eai_client.send_message_and_get_response(
            user_number=request.user_number,
            message=request.message,
        )
        return ChatResponse(response=response.model_dump())

    except EAIClientError as e:
        raise HTTPException(
            status_code=502, detail=f"Error communicating with EAI service: {e}"
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout waiting for EAI response.")
    except Exception as e:
        logger.exception("An unexpected error occurred in the chat endpoint.")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
