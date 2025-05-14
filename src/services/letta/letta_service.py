import os
from typing import List
from letta_client import Letta

import src.config.env as env

class LettaService:
    def __init__(self):
        """Inicializa o cliente Letta com as configurações do ambiente."""
        self.token = env.LETTA_API_TOKEN
        self.base_url = env.LETTA_API_URL
        self.client = Letta(token=self.token, base_url=self.base_url)
            
    def get_client(self):
        """Retorna a instância do cliente Letta."""
        return self.client
    
    def get_agent_id_by_tags(self, tags: List[str]):
        """Retorna o ID do agente que possui as tags especificadas."""
        return self.client.agents.list(tags=tags).agents[0].id

letta_service = LettaService()
