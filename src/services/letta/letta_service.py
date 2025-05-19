import os
from typing import List
from letta_client import Letta, AsyncLetta

import src.config.env as env
from src.services.letta.message_wrapper import process_stream

class LettaService:
    def __init__(self):
        """Inicializa o cliente Letta com as configurações do ambiente."""
        self.token = env.LETTA_API_TOKEN
        self.base_url = env.LETTA_API_URL
        self.client = Letta(token=self.token, base_url=self.base_url)
        self.client_async = AsyncLetta(token=self.token, base_url=self.base_url)
            
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
      
    async def create_agent(self, agent_type: str, tags: List[str] = None, name: str = None):
      """Cria um novo agente de acordo com o tipo de agente passado."""
      if agent_type == "agentic_search":
          from src.services.letta.agents.agentic_search_agent import create_agentic_search_agent
          return await create_agentic_search_agent(tags=tags, name=name)
      else:
          raise ValueError(f"Tipo de agente não suportado: {agent_type}")
      
    async def send_timer_message(self,agent_id: str) -> str:
        """
        Envia uma mensagem de timer para o agente.
        
        Returns:
            str: Resposta do agente
        """
        client = self.client_async
            
        letta_message = {
            "role": "user",
            "content": '[EVENTO] Este é um heartbeat automático temporizado (visível apenas para você). Use este evento para enviar uma mensagem, refletir e editar suas memórias, ou não fazer nada. Cabe a você! Considere, no entanto, que esta é uma oportunidade para você pensar por si mesmo - já que seu circuito não será ativado até o próximo heartbeat automático/temporizado ou evento de mensagem recebida.'
        }
        
        try:
            response = await client.agents.messages.create_stream(agent_id=agent_id, messages=[letta_message])
            
            if response:
                agent_message_response = await process_stream(response)
                return agent_message_response or ""
            
            return ""
        except Exception as error:
            print(f"Erro: {error}")
            return 'Ocorreu um erro ao enviar a mensagem para o agente. Por favor, tente novamente mais tarde.'


    async def send_message(self, agent_id: str, message_content: str, name: str = None) -> str:
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
        
        content = message_content
        
        letta_message = {
            "role": "user",
            "content": content
        }
        
        if name:
            letta_message["name"] = name
        
        try:
            response = await client.agents.messages.create_stream(agent_id=agent_id, messages=[letta_message])
            
            if response:
                agent_message_response = await process_stream(response)
                return agent_message_response or ""
            
            return ""
        except Exception as error:
            print(f"Erro: {error}")
            return 'Ocorreu um erro ao enviar a mensagem para o agente. Por favor, tente novamente mais tarde.'

letta_service = LettaService()
