import os
import traceback
import logging
from typing import List, Optional
import httpx
from letta_client import Letta, AsyncLetta
from letta_client.types import MessageCreate, TextContent

import src.config.env as env
from src.services.letta.message_wrapper import (
    process_stream,
    process_stream_raw,
)

logger = logging.getLogger(__name__)


class LettaService:
    def __init__(self):
        """Inicializa o cliente Letta com as configurações do ambiente."""
        self.token = env.LETTA_API_TOKEN
        self.base_url = env.LETTA_API_URL

        # Configurar timeout personalizado para o cliente HTTP
        timeout_config = httpx.Timeout(
            connect=120.0,  # Timeout para conectar
            read=120.0,  # Timeout para ler a resposta
            write=120.0,  # Timeout para escrever
            pool=120.0,  # Timeout para pool de conexões
        )

        # Configurar cliente HTTP personalizado
        httpx_client = httpx.Client(timeout=timeout_config)
        httpx_async_client = httpx.AsyncClient(timeout=timeout_config)

        # Inicializar clientes Letta com configurações personalizadas
        self.client = Letta(
            token=self.token, base_url=self.base_url, httpx_client=httpx_client
        )
        self.client_async = AsyncLetta(
            token=self.token, base_url=self.base_url, httpx_client=httpx_async_client
        )

    def get_client(self):
        """Retorna a instância do cliente Letta."""
        return self.client

    def get_client_async(self):
        """Retorna a instância do cliente Letta assíncrono."""
        return self.client_async

    async def get_agent_id_by_tags(self, tags: List[str]):
        """Retorna o ID do agente que possui as tags especificadas."""
        agents = await self.client_async.agents.list(tags=tags)
        if agents and len(agents) > 0:
            return agents[0].id
        return None

    async def get_agentic_tags(self) -> List[str]:
        """
        Retorna uma lista de tags que contenham 'agentic' em seu conteúdo.

        Returns:
            List[str]: Lista de tags filtradas
        """
        try:
            agents = await self.client_async.agents.list()
            all_tags = set()
            for agent in agents:
                if hasattr(agent, "tags") and agent.tags:
                    all_tags.update(agent.tags)
            agentic_tags = [tag for tag in all_tags if "agentic" in tag.lower()]
            return agentic_tags
        except Exception as error:
            print(f"Erro ao obter tags: {error}")
            return []

    async def create_agent(
        self,
        agent_type: str,
        tags: List[str] = None,
        name: str = None,
        tools: list = None,
        model_name: str = None,
        system_prompt: str = None,
        temperature: float = 0.7,
    ):
        """Cria um novo agente de acordo com o tipo de agente passado."""
        if agent_type == "agentic_search":
            from src.services.letta.agents.agentic_search_agent import (
                create_agentic_search_agent,
            )

            return await create_agentic_search_agent(
                tags=tags,
                username=name,
                tools=tools,
                model_name=model_name,
                system_prompt=system_prompt,
                temperature=temperature,
            )
        else:
            raise ValueError(f"Tipo de agente não suportado: {agent_type}")

    async def delete_agent(self, agent_id: str):
        """Deleta um agente de acordo com o ID passado."""
        if agent_id:
            return await self.client_async.agents.delete(agent_id)
        else:
            raise ValueError(f"ID do agente não suportado: {agent_id}")

    async def deletar_agentes_teste(self):
        """Deleta todos os agentes de teste."""
        agents = await self.client_async.agents.list()
        for agent in agents:
            if hasattr(agent, "tags") and agent.tags:
                if any("test" in tag.lower() for tag in agent.tags):
                    await self.client_async.agents.delete(agent.id)

    async def send_timer_message(self, agent_id: str) -> str:
        """
        Envia uma mensagem de timer para o agente.

        Returns:
            str: Resposta do agente
        """
        client = self.client_async

        message_text = "[EVENTO] Este é um heartbeat automático temporizado (visível apenas para você). Use este evento para enviar uma mensagem, refletir e editar suas memórias, ou não fazer nada. Cabe a você! Considere, no entanto, que esta é uma oportunidade para você pensar por si mesmo - já que seu circuito não será ativado até o próximo heartbeat automático/temporizado ou evento de mensagem recebida."

        letta_message = MessageCreate(
            role="user", content=[TextContent(text=message_text)]
        )

        try:

            def create_response():
                return client.agents.messages.create_stream(
                    agent_id=agent_id, messages=[letta_message]
                )

            agent_message_response = await process_stream(create_response())
            return agent_message_response or ""

        except Exception as error:
            logger.error(f"Erro detalhado ao enviar timer message: {error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "Ocorreu um erro ao enviar a mensagem para o agente. Por favor, tente novamente mais tarde."

    async def send_message(
        self, agent_id: str, message_content: str, name: str = None
    ) -> str:
        """
        Envia uma mensagem para o agente e recebe a resposta.

        Args:
            agent_id: ID do agente
            message_content: Conteúdo da mensagem
            name: Nome do remetente

        Returns:
            str: Resposta do agente
        """
        client = self.client_async

        message_params = {
            "role": "user",
            "content": [TextContent(text=message_content)],
        }

        if name:
            message_params["name"] = name

        letta_message = MessageCreate(**message_params)

        try:
            return await client.agents.messages.create(
                agent_id=agent_id, messages=[letta_message]
            )

        except Exception as error:
            logger.error(f"Erro detalhado ao enviar message: {error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "Ocorreu um erro ao enviar a mensagem para o agente. Por favor, tente novamente mais tarde."

    async def send_message_raw(
        self, agent_id: str, message_content: str, name: str = None
    ) -> dict:
        """
        Envia uma mensagem para o agente e recebe a resposta em formato bruto,
        organizada por tipos de mensagens.

        Args:
            agent_id: ID do agente
            message_content: Conteúdo da mensagem
            name: Nome do remetente

        Returns:
            dict: Dicionário contendo todas as mensagens do stream organizadas por tipo
        """
        client = self.client_async

        message_params = {
            "role": "user",
            "content": [TextContent(text=message_content)],
        }

        if name:
            message_params["name"] = name

        letta_message = MessageCreate(**message_params)

        try:

            def create_response():
                return client.agents.messages.create_stream(
                    agent_id=agent_id, messages=[letta_message]
                )

            return await process_stream_raw(create_response())
        except Exception as error:
            logger.error(f"Erro ao enviar mensagem: {error}")
            return {
                "error": str(error),
                "system_messages": [],
                "user_messages": [],
                "reasoning_messages": [],
                "tool_call_messages": [],
                "tool_return_messages": [],
                "assistant_messages": [],
                "letta_usage_statistics": [],
            }


letta_service = LettaService()
