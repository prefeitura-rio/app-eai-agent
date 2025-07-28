import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.security.dependencies import validar_token
from src.db.database import get_db
from src.repositories.user_agent_repository import UserAgentRepository
from src.services.eai_gateway.api import EAIClient, CreateAgentRequest, EAIClientError
from pydantic import BaseModel
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

from typing import Dict, Any, Optional, List

# --- Pydantic Models ---


class ChatRequest(CreateAgentRequest):
    message: str
    use_same_agent: bool = True
    timeout: int = 180
    polling_interval: int = 2


class ChatResponse(BaseModel):
    response: Dict[str, Any]


# --- Router Setup ---

router = APIRouter(
    prefix="/eai-gateway",
    tags=["EAI Gateway"],
    dependencies=[Depends(validar_token)],
)
eai_client = EAIClient()

# --- Event Handlers ---


@router.on_event("shutdown")
async def shutdown_event():
    await eai_client.close()


# --- Endpoints ---


@router.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Handles a user chat message.
    - If `use_same_agent` is true, it retrieves the user's existing agent.
    - If no agent exists, or `use_same_agent` is false, it creates a new agent.
    - When creating an agent, it uses any provided optional parameters, falling back to defaults.
    """
    try:
        agent_id = None
        if request.use_same_agent:
            logger.info(f"Checking for existing agent for user {request.user_number}")
            agent_id = UserAgentRepository.get_agent_id(
                db=db, user_number=request.user_number
            )

        if not agent_id:
            logger.info(
                f"No agent found for user {request.user_number}, creating a new one."
            )
            create_req = CreateAgentRequest(
                user_number=request.user_number,
                agent_type=request.agent_type,
                name=request.name,
                tags=request.tags,
                system=request.system,
                memory_blocks=request.memory_blocks,
                tools=request.tools,
                model=request.model,
                embedding=request.embedding,
                context_window_limit=request.context_window_limit,
                include_base_tool_rules=request.include_base_tool_rules,
                include_base_tools=request.include_base_tools,
                timezone=request.timezone,
            )
            create_resp = await eai_client.create_agent(create_req)
            agent_id = create_resp.get("agent_id")
            if not agent_id:
                raise HTTPException(
                    status_code=500, detail="Failed to get agent_id from EAI API."
                )

            if request.use_same_agent:
                UserAgentRepository.store_agent_id(
                    db=db, user_number=request.user_number, agent_id=agent_id
                )
                logger.info(
                    f"Saved ID {agent_id} for user {request.user_number} in the database."
                )
        # Send the message and get the response
        response = await eai_client.send_message_and_get_response(
            agent_id=agent_id,
            message=request.message,
            timeout=request.timeout,
            polling_interval=request.polling_interval,
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


@router.get("/agent/{user_number}", response_model=Dict[str, str | None])
def get_agent(user_number: str, db: Session = Depends(get_db)):
    """Returns the agent_id associated with a user_number, if it exists."""
    agent_id = UserAgentRepository.get_agent_id(db=db, user_number=user_number)
    return {"agent_id": agent_id}


@router.delete("/agent/{user_number}", status_code=204)
def delete_agent_association(user_number: str, db: Session = Depends(get_db)):
    """Deletes the association between a user_number and agent_id."""
    success = UserAgentRepository.delete_agent_id(db=db, user_number=user_number)
    if not success:
        raise HTTPException(
            status_code=404, detail="No association found for this user."
        )
    return None
