from src.config import env
from loguru import logger
import httpx
import asyncio


async def get_agent_config_from_api(agent_type: str = "agentic_search") -> dict:
    """Obtém a configuração do agente via API"""
    try:
        base_url = getattr(env, "EAI_AGENT_URL", "http://localhost:8000")
        api_url = f"{base_url}api/v1/agent-config?agent_type={agent_type}"

        bearer_token = getattr(env, "EAI_AGENT_TOKEN", "")

        headers = {}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            logger.info(
                f"Agent config obtida via API. Status: {response.status_code}"
            )
            return data

    except Exception as e:
        logger.warning(
            f"Erro ao obter agent config via API: {str(e)}. Usando fallback."
        )
        # Fallback para configuração padrão
        default_config = {}
        return {
            "config": default_config,
            "version": "FallBack",
        }


agent_config_data = asyncio.run(get_agent_config_from_api())
