import httpx
import asyncio
import time
from typing import Optional, Dict, Any, List, Callable
from src.config import env
from pydantic import BaseModel, Field

# --- Pydantic Models for API Interaction ---


class CreateAgentRequest(BaseModel):
    # Optional agent override parameters
    user_number: str
    agent_type: Optional[str] = "memgpt_v2_agent"
    name: Optional[str] = "test_agent"
    tags: Optional[List[str]] = ["agentic_search"]
    system: Optional[str] = "You are an AI assistant..."
    memory_blocks: Optional[List[Dict[str, Any]]] = []
    # memory_blocks: Optional[List[Dict[str, Any]]] =[
    #     {"label": "human", "limit": 10000, "value": ""},
    #     {"label": "persona", "limit": 5000, "value": ""},
    # ]
    tools: Optional[List[str]] = [
        "google_search",
        "equipments_instructions",
        # "equipments_by_address",
    ]
    model: Optional[str] = "google_ai/gemini-2.5-flash-lite-preview-06-17"
    embedding: Optional[str] = "google_ai/text-embedding-004"
    context_window_limit: Optional[int] = 1_000_000
    include_base_tool_rules: Optional[bool] = True
    include_base_tools: Optional[bool] = True
    timezone: Optional[str] = "America/Sao_Paulo"


class AgentWebhookRequest(BaseModel):
    agent_id: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class AgentWebhookResponse(BaseModel):
    message_id: str


class MessageResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    # Adicione outros campos conforme a estrutura da resposta da API


# --- Custom Exception ---


class EAIClientError(Exception):
    """Custom exception for EAI client errors."""

    pass


# --- EAI Client ---


class EAIClient:
    def __init__(self):
        self.base_url = env.EAI_GATEWAY_API_URL
        headers = (
            {"Authorization": f"Bearer {env.EAI_GATEWAY_API_TOKEN}"}
            if env.EAI_GATEWAY_API_TOKEN
            else {}
        )
        self._client = httpx.AsyncClient(
            base_url=self.base_url, headers=headers, timeout=120.0
        )

    async def create_agent(self, request: CreateAgentRequest) -> Dict[str, Any]:
        """Creates a new agent."""
        try:
            response = await self._client.post(
                "/api/v1/agent/create", json=request.model_dump()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise EAIClientError(
                f"API Error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise EAIClientError(f"An unexpected error occurred: {e}") from e

    async def send_message_to_agent(
        self, request: AgentWebhookRequest
    ) -> AgentWebhookResponse:
        """(Low-level) Sends a message to a specific agent."""
        try:
            response = await self._client.post(
                "/api/v1/message/webhook/agent", json=request.model_dump()
            )
            response.raise_for_status()
            return AgentWebhookResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise EAIClientError(
                f"API Error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise EAIClientError(f"An unexpected error occurred: {e}") from e

    async def get_message_response(self, message_id: str) -> MessageResponse:
        """(Low-level) Polls for the response of a sent message."""
        try:
            params = {"message_id": message_id}
            response = await self._client.get("/api/v1/message/response", params=params)
            response.raise_for_status()

            # Log the raw response from the API
            raw_response = response.json()
            return MessageResponse(**raw_response)
        except httpx.HTTPStatusError as e:
            raise EAIClientError(
                f"API Error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise EAIClientError(f"An unexpected error occurred: {e}") from e

    async def send_message_and_get_response(
        self, agent_id: str, message: str, timeout: int = 180, polling_interval: int = 2
    ) -> MessageResponse:
        """
        High-level method to send a message and poll for the final response.
        """
        send_req = AgentWebhookRequest(agent_id=agent_id, message=message)
        send_resp = await self.send_message_to_agent(send_req)

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = await self.get_message_response(send_resp.message_id)
                if response.status == "completed":
                    return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 404:
                    raise EAIClientError(
                        f"API Error during polling: {e.response.status_code}"
                    ) from e

            await asyncio.sleep(polling_interval)

        raise asyncio.TimeoutError("Timeout waiting for agent response.")

    async def close(self):
        await self._client.aclose()
