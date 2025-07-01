import os
import traceback
import logging
import asyncio
import httpx
from typing import List, Optional
from letta_client import Letta, AsyncLetta
from letta_client.types import MessageCreate, TextContent

import src.config.env as env
from src.services.letta.message_wrapper import process_stream_with_retry, process_stream_raw_with_retry

logger = logging.getLogger(__name__)


class LettaService:
    def __init__(self):
        """Inicializa o cliente Letta com as configurações do ambiente."""
        self.token = env.LETTA_API_TOKEN
        self.base_url = env.LETTA_API_URL
        self.client = Letta(token=self.token, base_url=self.base_url)
        self.client_async = AsyncLetta(token=self.token, base_url=self.base_url)
        
        # Configurar timeout aumentado no cliente HTTP interno
        self._configure_timeouts()

    def _configure_timeouts(self):
        """Configura timeouts aumentados no cliente HTTP do Letta"""
        try:
            # Configurar timeout para cliente síncrono
            if hasattr(self.client, '_client_wrapper') and hasattr(self.client._client_wrapper, 'httpx_client'):
                # Recriar o cliente com timeout personalizado
                timeout = httpx.Timeout(
                    connect=30.0,  # Timeout para conexão
                    read=env.LETTA_STREAM_TIMEOUT,  # Timeout para leitura (120s)
                    write=30.0,    # Timeout para escrita
                    pool=10.0      # Timeout para obter conexão do pool
                )
                
                # Atualizar o cliente interno com timeout personalizado
                old_client = self.client._client_wrapper.httpx_client
                self.client._client_wrapper.httpx_client = httpx.Client(
                    timeout=timeout,
                    limits=old_client.limits,
                    headers=old_client.headers,
                    base_url=old_client.base_url,
                    cookies=old_client.cookies,
                    proxies=old_client.proxies,
                    verify=old_client.verify,
                    cert=old_client.cert
                )
                logger.info(f"Timeout configurado no cliente síncrono: {timeout}")
                
            # Configurar timeout para cliente assíncrono  
            if hasattr(self.client_async, '_client_wrapper') and hasattr(self.client_async._client_wrapper, 'httpx_client'):
                timeout = httpx.Timeout(
                    connect=30.0,
                    read=env.LETTA_STREAM_TIMEOUT,
                    write=30.0,
                    pool=10.0
                )
                
                old_async_client = self.client_async._client_wrapper.httpx_client
                self.client_async._client_wrapper.httpx_client = httpx.AsyncClient(
                    timeout=timeout,
                    limits=old_async_client.limits,
                    headers=old_async_client.headers,
                    base_url=old_async_client.base_url,
                    cookies=old_async_client.cookies,
                    proxies=old_async_client.proxies,
                    verify=old_async_client.verify,
                    cert=old_async_client.cert
                )
                logger.info(f"Timeout configurado no cliente assíncrono: {timeout}")
                
        except Exception as e:
            logger.warning(f"Erro ao configurar timeouts no cliente Letta: {e}")

    async def _create_stream_with_retry(self, agent_id: str, messages: list):
        """Cria stream com retry para mitigar timeouts de conexão"""
        max_attempts = env.LETTA_STREAM_RETRY_ATTEMPTS
        base_delay = env.LETTA_STREAM_RETRY_DELAY
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"Tentativa {attempt + 1} de criar stream para agente {agent_id}")
                response = self.client_async.agents.messages.create_stream(
                    agent_id=agent_id, messages=messages
                )
                logger.info(f"Stream criado com sucesso na tentativa {attempt + 1}")
                return response
                
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.TimeoutException, ConnectionError) as e:
                if attempt == max_attempts - 1:  # Última tentativa
                    logger.error(f"Falha definitiva ao criar stream após {max_attempts} tentativas: {e}")
                    raise
                
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Tentativa {attempt + 1} falhou ao criar stream: {type(e).__name__}: {e}")
                logger.warning(f"Tentando novamente em {delay}s...")
                await asyncio.sleep(delay)
                
                # Reconfigurar timeouts após erro (caso o cliente tenha sido recriado)
                self._configure_timeouts()
                
            except Exception as e:
                # Para outros tipos de erro, não fazer retry
                logger.error(f"Erro não recuperável ao criar stream: {type(e).__name__}: {e}")
                raise

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
            logger.error(f"Erro ao obter tags: {error}")
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
        message_text = "[EVENTO] Este é um heartbeat automático temporizado (visível apenas para você). Use este evento para enviar uma mensagem, refletir e editar suas memórias, ou não fazer nada. Cabe a você! Considere, no entanto, que esta é uma oportunidade para você pensar por si mesmo - já que seu circuito não será ativado até o próximo heartbeat automático/temporizado ou evento de mensagem recebida."

        letta_message = MessageCreate(
            role="user", content=[TextContent(text=message_text)]
        )

        try:
            response = await self._create_stream_with_retry(agent_id, [letta_message])

            if response:
                agent_message_response = await process_stream_with_retry(response)
                return agent_message_response or ""

            return ""
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
        message_params = {
            "role": "user",
            "content": [TextContent(text=message_content)],
        }

        if name:
            message_params["name"] = name

        letta_message = MessageCreate(**message_params)

        try:
            response = await self._create_stream_with_retry(agent_id, [letta_message])

            if response:
                agent_message_response = await process_stream_with_retry(response)
                return agent_message_response or ""

            return ""
        except Exception as error:
            logger.error(f"Erro detalhado ao enviar mensagem: {error}")
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
        message_params = {
            "role": "user",
            "content": [TextContent(text=message_content)],
        }

        if name:
            message_params["name"] = name

        letta_message = MessageCreate(**message_params)

        try:
            response = await self._create_stream_with_retry(agent_id, [letta_message])

            if response:
                return await process_stream_raw_with_retry(response)

            return {
                "grouped": {
                    "system_messages": [],
                    "user_messages": [],
                    "reasoning_messages": [],
                    "tool_call_messages": [],
                    "tool_return_messages": [],
                    "assistant_messages": [],
                    "letta_usage_statistics": [],
                },
                "ordered": []
            }
        except Exception as error:
            logger.error(f"Erro ao enviar mensagem raw: {error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "error": str(error),
                "grouped": {
                    "system_messages": [],
                    "user_messages": [],
                    "reasoning_messages": [],
                    "tool_call_messages": [],
                    "tool_return_messages": [],
                    "assistant_messages": [],
                    "letta_usage_statistics": [],
                },
                "ordered": []
            }


letta_service = LettaService()
