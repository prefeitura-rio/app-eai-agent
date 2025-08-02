from langchain_mcp_adapters.tools import load_mcp_tools
from src.config import env
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio


async def get_mcp_tools():
    """
    Inicializa o cliente MCP e busca as ferramentas disponíveis de forma assíncrona.
    """
    client = MultiServerMCPClient(
        {
            "rio_mcp": {
                "transport": "streamable_http",
                "url": env.MCP_SERVER_URL,
                "headers": {
                    "Authorization": f"Bearer {env.MCP_API_TOKEN}",
                },
            },
        }
    )
    tools = await client.get_tools()
    return tools
