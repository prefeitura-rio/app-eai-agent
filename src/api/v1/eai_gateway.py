import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.services.eai_gateway.api import EAIClient, CreateAgentRequest, EAIClientError
from src.services.agent_engine.history import GoogleAgentEngineHistory
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from src.utils.log import logger

# --- Pydantic Models ---


class ChatRequest(BaseModel):
    user_number: str
    message: str
    timeout: int = 300
    polling_interval: int = 2
    provider: str = "google_agent_engine"
    reasoning_engine_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: Dict[str, Any]


class HistoryRequest(BaseModel):
    user_id: str
    session_timeout_seconds: int = 3600
    use_whatsapp_format: bool = False


class BulkHistoryRequest(BaseModel):
    user_ids: List[str]
    session_timeout_seconds: int = 3600
    use_whatsapp_format: bool = False


class HistoryResponse(BaseModel):
    data: List[Dict[str, Any]]


class BulkHistoryResponse(BaseModel):
    data: Dict[str, List[Dict[str, Any]]]


class DeleteHistoryRequest(BaseModel):
    user_id: str


class DeleteHistoryResponse(BaseModel):
    thread_id: str
    overall_result: str
    tables: Dict[str, Dict[str, Any]]


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
        timeout=300,
        polling_interval=2,
        provider=request.provider,
    )
    try:
        response = await eai_client.send_message_and_get_response(
            user_number=request.user_number,
            reasoning_engine_id=request.reasoning_engine_id,
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


@router.post("/history", response_model=HistoryResponse)
async def get_user_history(
    request: HistoryRequest,
):
    """
    Retrieves the conversation history for a single user.

    Args:
        request: Contains user_id and optional session_timeout_seconds (default: 3600)

    Returns:
        HistoryResponse: List of formatted messages for the user
    """
    try:
        # Initialize the history service using context manager
        async with GoogleAgentEngineHistory.create() as history_service:
            # Get the history for the single user
            _, messages = await history_service._get_single_user_history(
                user_id=request.user_id,
                session_timeout_seconds=request.session_timeout_seconds,
                use_whatsapp_format=request.use_whatsapp_format,
            )

            return HistoryResponse(data=messages)

    except Exception as e:
        logger.exception(f"Error retrieving history for user {request.user_id}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.post("/history/bulk", response_model=BulkHistoryResponse)
async def get_bulk_user_history(
    request: BulkHistoryRequest,
):
    """
    Retrieves the conversation history for multiple users in bulk.

    Args:
        request: Contains user_ids list and optional session_timeout_seconds (default: 3600)

    Returns:
        BulkHistoryResponse: Dictionary mapping user_id to their message history
    """
    try:
        # Initialize the history service using context manager
        async with GoogleAgentEngineHistory.create() as history_service:
            # Get the history for multiple users
            bulk_history = await history_service.get_history_bulk(
                user_ids=request.user_ids,
                session_timeout_seconds=request.session_timeout_seconds,
                use_whatsapp_format=request.use_whatsapp_format,
            )

            return BulkHistoryResponse(data=bulk_history)

    except Exception as e:
        logger.exception(f"Error retrieving bulk history for users {request.user_ids}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.delete("/history", response_model=DeleteHistoryResponse)
async def delete_user_history(
    request: DeleteHistoryRequest,
):
    """
    Deletes the conversation history for a specific user from both checkpoint tables.

    Args:
        request: Contains user_id to delete

    Returns:
        DeleteHistoryResponse: Results of the deletion operation for both tables
    """
    try:
        # Initialize the history service using context manager
        async with GoogleAgentEngineHistory.create() as history_service:
            # Delete user history from both tables
            result = await history_service.delete_user_history(user_id=request.user_id)

            return DeleteHistoryResponse(**result)

    except Exception as e:
        logger.exception(f"Error deleting history for user {request.user_id}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
