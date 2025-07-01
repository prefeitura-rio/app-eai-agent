from typing import List
import httpx
import uuid
from loguru import logger

from src.services.letta.agents.memory_blocks.agentic_search_mb import (
    get_agentic_search_memory_blocks,
)
from src.services.letta.letta_service import letta_service
from letta_client import ContinueToolRule
from src.config import env


async def _get_system_prompt_from_api(agent_type: str = "agentic_search") -> str:
    """Obtém o system prompt via API"""
    try:
        base_url = getattr(env, "EAI_AGENT_URL", "http://localhost:8000")
        api_url = f"{base_url}system-prompt?agent_type={agent_type}"

        bearer_token = getattr(env, "EAI_AGENT_TOKEN", "")

        headers = {}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            logger.info(f"System prompt obtido via API para agent_type: {agent_type}")
            return data.get("prompt", "")

    except Exception as e:
        logger.warning(
            f"Erro ao obter system prompt via API: {str(e)}. Usando fallback."
        )
        # Fallback para prompt padrão
        return f"""You are an AI assistant for the {agent_type} role.
Follow these guidelines:
1. Answer concisely but accurately
2. Use tools when necessary
3. Focus on providing factual information
4. Be helpful, harmless, and honest"""


async def _get_agent_config_from_api(agent_type: str = "agentic_search") -> dict:
    """Obtém a configuração do agente via API"""
    try:
        base_url = getattr(env, "EAI_AGENT_URL", "http://localhost:8000")
        api_url = f"{base_url}agent-config?agent_type={agent_type}"

        bearer_token = getattr(env, "EAI_AGENT_TOKEN", "")

        headers = {}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            logger.info(
                f"Configuração do agente obtida via API para agent_type: {agent_type}"
            )
            return data

    except Exception as e:
        logger.warning(
            f"Erro ao obter configuração via API: {str(e)}. Usando fallback."
        )
        # Fallback para configuração padrão
        return {
            "memory_blocks": get_agentic_search_memory_blocks(),
            "tools": ["google_search", "public_services_grounded_search"],
            "model_name": env.LLM_MODEL,
            "embedding_name": env.EMBEDDING_MODEL,
        }


async def create_agentic_search_agent(
    tags: List[str] = None,
    username: str = None,
    tools: list = None,
    model_name: str = None,
):
    """Cria um novo agentic_search agent"""
    try:
        client = letta_service.get_client_async()

        # Obtém system prompt e configuração ativa via API
        system_prompt = await _get_system_prompt_from_api(agent_type="agentic_search")
        agent_cfg = await _get_agent_config_from_api(agent_type="agentic_search")

        # Extrai valores com fallback já incluído nas funções API
        memory_blocks = agent_cfg.get(
            "memory_blocks", get_agentic_search_memory_blocks()
        )

        if tools is None:
            tools = agent_cfg.get(
                "tools", ["google_search", "public_services_grounded_search"]
            )

        if model_name is None:
            model_name = agent_cfg.get("model_name", env.LLM_MODEL)

        logger.info(f"Model name: {model_name} | Tools: {tools}")

        embedding_name = agent_cfg.get("embedding_name", env.EMBEDDING_MODEL)

        agent = await client.agents.create(
            agent_type="memgpt_agent",
            name=f"agentic_search_{tags[0] if tags[0] != None else str(uuid.uuid4())}_{username.replace(' ', '') if username else str(uuid.uuid4())}",
            description="Agente pessoal de cada cidadão do Rio de Janeiro, que busca informações sobre os serviços públicos da Prefeitura do Rio de Janeiro.",
            context_window_limit=20000,
            include_base_tools=True,
            include_base_tool_rules=False,
            tools=tools,
            tool_rules=[
                ContinueToolRule(tool_name="conversation_search"),
                ContinueToolRule(tool_name="core_memory_append"),
                ContinueToolRule(tool_name="core_memory_replace"),
                ContinueToolRule(tool_name="archival_memory_search"),
                ContinueToolRule(tool_name="archival_memory_insert"),
                ContinueToolRule(tool_name="google_search"),
                ContinueToolRule(tool_name="public_services_grounded_search"),
                ContinueToolRule(tool_name="gpt_search"),
            ],
            tags=["agentic_search"] + (tags if tags else []),
            model=model_name,
            embedding=embedding_name,
            system=system_prompt,
            memory_blocks=memory_blocks,
        )
        return agent
    except Exception as e:
        logger.error(f"Erro ao criar agente agentic_search: {str(e)}")
        raise
