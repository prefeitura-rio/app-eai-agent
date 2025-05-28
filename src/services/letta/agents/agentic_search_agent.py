from typing import List

from src.services.letta.agents.memory_blocks.agentic_search_mb import (
    get_agentic_search_memory_blocks,
)
from src.services.letta.system_prompt_service import system_prompt_service
from src.services.letta.letta_service import letta_service
import uuid
from loguru import logger

from letta_client import ContinueToolRule
from src.config import env


async def create_agentic_search_agent(tags: List[str] = None, username: str = None):
    """Cria um novo agentic_search agent"""
    try:
        client = letta_service.get_client_async()

        system_prompt = system_prompt_service.get_active_system_prompt_from_db(
            agent_type="agentic_search"
        )

        agent = await client.agents.create(
            agent_type="memgpt_agent",
            name=f"agentic_search_{tags[0] if tags[0] != None else str(uuid.uuid4())}_{username.replace(' ', '') if username else str(uuid.uuid4())}",
            description="Agente pessoal de cada cidadão do Rio de Janeiro, que busca informações sobre os serviços públicos da Prefeitura do Rio de Janeiro.",
            context_window_limit=20000,
            include_base_tools=True,
            include_base_tool_rules=False,
            tools=[
                "google_search",
                "typesense_search",
            ],
            tool_rules=[
                ContinueToolRule(tool_name="conversation_search"),
                ContinueToolRule(tool_name="core_memory_append"),
                ContinueToolRule(tool_name="core_memory_replace"),
                ContinueToolRule(tool_name="archival_memory_search"),
                ContinueToolRule(tool_name="archival_memory_insert"),
                ContinueToolRule(tool_name="google_search"),
                ContinueToolRule(tool_name="typesense_search"),
            ],
            tags=["agentic_search"] + (tags if tags else []),
            model=env.LLM_MODEL,
            embedding=env.EMBEDDING_MODEL,
            system=system_prompt,
            memory_blocks=get_agentic_search_memory_blocks(),
        )
        return agent
    except Exception as e:
        logger.error(f"Erro ao criar agente agentic_search: {str(e)}")
        raise
