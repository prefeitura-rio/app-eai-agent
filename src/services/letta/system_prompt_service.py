from typing import Dict, List, Optional
import os
import json
from pathlib import Path
from datetime import datetime

from loguru import logger

from src.services.letta.letta_service import letta_service


class SystemPromptService:
    """
    Serviço para gerenciar system prompts dos agentes.
    Permite atualizar o system prompt do template e de todos os agentes existentes.
    """
    
    def __init__(self, cache_dir: str = "src/services/letta/agents/system_prompts/cache"):
        """
        Inicializa o serviço de system prompt.
        
        Args:
            cache_dir: Diretório para cache dos system prompts
        """
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
    async def get_current_system_prompt(self, agent_type: str = "agentic_search") -> str:
        """
        Obtém o system prompt atual para o tipo de agente especificado.
        
        Args:
            agent_type: Tipo do agente
            
        Returns:
            str: Texto do system prompt atual
        """
        if agent_type == "agentic_search":
            from src.services.letta.agents.system_prompts.agentic_search_sp import get_agentic_search_system_prompt_text
            return get_agentic_search_system_prompt_text()
        else:
            raise ValueError(f"Tipo de agente não suportado: {agent_type}")
    
    async def update_template_system_prompt(self, new_prompt: str, agent_type: str = "agentic_search") -> bool:
        """
        Atualiza o system prompt no arquivo de template.
        
        Args:
            new_prompt: Novo texto para o system prompt
            agent_type: Tipo do agente
            
        Returns:
            bool: True se a atualização foi bem-sucedida
        """
        try:
            await self._create_backup(agent_type)
            
            if agent_type == "agentic_search":
                template_path = Path("src/services/letta/agents/system_prompts/agentic_search_sp.py")
                
                if not template_path.exists():
                    logger.error(f"Arquivo de template não encontrado: {template_path}")
                    return False
                
                new_content = 'def get_agentic_search_system_prompt_text():\n  return """\\\n'
                new_content += new_prompt
                new_content += '\n"""'
                
                template_path.write_text(new_content)
                
                return True
            else:
                logger.error(f"Tipo de agente não suportado: {agent_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar template do system prompt: {str(e)}")
            return False
    
    async def update_all_agents_system_prompt(self, 
                                             new_prompt: str, 
                                             agent_type: str = "agentic_search",
                                             tags: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Atualiza o system prompt de todos os agentes existentes do tipo especificado.
        
        Args:
            new_prompt: Novo texto para o system prompt
            agent_type: Tipo do agente
            tags: Filtrar agentes por tags específicas
            
        Returns:
            Dict[str, bool]: Dicionário com agent_id: status da atualização
        """
        client = letta_service.get_client_async()
        results = {}
        
        try:
            filter_tags = tags if tags else ["agentic_search"] if agent_type == "agentic_search" else []
            agents = await client.agents.list(tags=filter_tags)
            
            if not agents:
                logger.info(f"Nenhum agente encontrado com as tags: {filter_tags}")
                return results
            
            for agent in agents:
                try:
                    await client.agents.modify(
                        agent_id=agent.id,
                        system=new_prompt
                    )
                    results[agent.id] = True
                    logger.info(f"System prompt atualizado para o agente: {agent.id}")
                except Exception as agent_error:
                    results[agent.id] = False
                    logger.error(f"Erro ao atualizar agente {agent.id}: {str(agent_error)}")
            
            return results
        
        except Exception as e:
            logger.error(f"Erro ao atualizar agents: {str(e)}")
            return results
    
    async def update_system_prompt(self, 
                                  new_prompt: str,
                                  agent_type: str = "agentic_search", 
                                  update_template: bool = True,
                                  update_agents: bool = True,
                                  tags: Optional[List[str]] = None) -> Dict[str, any]:
        """
        Atualiza o system prompt no template e em todos os agentes existentes.
        
        Args:
            new_prompt: Novo texto para o system prompt
            agent_type: Tipo do agente
            update_template: Se deve atualizar o template
            update_agents: Se deve atualizar os agentes existentes
            tags: Filtrar agentes por tags específicas
            
        Returns:
            Dict: Resultado das operações
        """
        result = {
            "success": True,
            "template_updated": False,
            "agents_updated": {}
        }
        
        if update_template:
            template_result = await self.update_template_system_prompt(new_prompt, agent_type)
            result["template_updated"] = template_result
            
            if not template_result:
                result["success"] = False
        
        if update_agents:
            agents_result = await self.update_all_agents_system_prompt(new_prompt, agent_type, tags)
            result["agents_updated"] = agents_result
            
            if agents_result and not all(agents_result.values()):
                result["success"] = False
        
        return result
    
    async def _create_backup(self, agent_type: str = "agentic_search") -> bool:
        """
        Cria um backup do system prompt atual.
        
        Args:
            agent_type: Tipo do agente
            
        Returns:
            bool: True se o backup foi criado com sucesso
        """
        try:
            current_prompt = await self.get_current_system_prompt(agent_type)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = Path(self.cache_dir) / f"{agent_type}_prompt_{timestamp}.json"
            
            backup_data = {
                "agent_type": agent_type,
                "timestamp": timestamp,
                "prompt": current_prompt
            }
            
            with open(backup_file, "w") as f:
                json.dump(backup_data, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar backup do system prompt: {str(e)}")
            return False

system_prompt_service = SystemPromptService() 