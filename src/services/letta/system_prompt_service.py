from typing import Dict, List, Optional, Any
import os
from pathlib import Path
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session

from loguru import logger

from src.db import get_db, get_db_session
from src.models.system_prompt_model import SystemPrompt, SystemPromptDeployment
from src.repositories.system_prompt_repository import SystemPromptRepository
from src.services.letta.letta_service import letta_service


class SystemPromptService:
    """
    Serviço para gerenciar system prompts dos agentes.
    Permite atualizar o system prompt e os agentes existentes.
    """
    
    def __init__(self):
        """
        Inicializa o serviço de system prompt.
        """
        pass
        
    async def get_current_system_prompt(self, agent_type: str = "agentic_search", db: Session = None) -> str:
        """
        Obtém o system prompt atual para o tipo de agente especificado.
        
        Args:
            agent_type: Tipo do agente
            db: Sessão do banco de dados
            
        Returns:
            str: Texto do system prompt atual
        """
        # Tenta obter o prompt do banco de dados
        if db:
            prompt = SystemPromptRepository.get_active_prompt(db, agent_type)
            if prompt:
                return prompt.content
        
        # Se não encontrar no banco ou não tiver conexão
        with get_db_session() as session:
            prompt = SystemPromptRepository.get_active_prompt(session, agent_type)
            if prompt:
                return prompt.content
                
        # Se não encontrar nenhum prompt
        raise ValueError(f"Nenhum system prompt encontrado para o tipo de agente: {agent_type}")
    
    def get_active_system_prompt_from_db(self, agent_type: str = "agentic_search") -> str:
        """
        Obtém o system prompt ativo do banco de dados de forma síncrona.
        Este método deve ser usado para criação de novos agentes.
        
        Args:
            agent_type: Tipo do agente
            
        Returns:
            str: Texto do system prompt ativo no banco de dados
        """
        try:
            # Abre uma sessão do banco de dados
            with get_db_session() as db:
                # Busca o prompt ativo no banco de dados
                prompt = SystemPromptRepository.get_active_prompt(db, agent_type)
                if prompt:
                    return prompt.content
                
            # Se não encontrar nenhum prompt
            raise ValueError(f"Nenhum system prompt encontrado para o tipo de agente: {agent_type}")
        except Exception as e:
            logger.error(f"Erro ao obter system prompt do banco: {str(e)}")
            raise
            
    async def update_all_agents_system_prompt(self, 
                                             new_prompt: str, 
                                             agent_type: str = "agentic_search",
                                             tags: Optional[List[str]] = None,
                                             db: Session = None,
                                             prompt_id: str = None) -> Dict[str, bool]:
        """
        Atualiza o system prompt de todos os agentes existentes do tipo especificado.
        
        Args:
            new_prompt: Novo texto para o system prompt
            agent_type: Tipo do agente
            tags: Filtrar agentes por tags específicas
            db: Sessão do banco de dados
            prompt_id: ID do prompt no banco de dados
            
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
                    
                    # Registra a implantação no banco de dados se disponível
                    if db and prompt_id:
                        SystemPromptRepository.create_deployment(
                            db=db,
                            prompt_id=prompt_id,
                            agent_id=agent.id,
                            agent_type=agent_type,
                            status="success",
                            details={"tags": agent.tags if hasattr(agent, "tags") else []}
                        )
                        
                except Exception as agent_error:
                    results[agent.id] = False
                    logger.error(f"Erro ao atualizar agente {agent.id}: {str(agent_error)}")
                    
                    # Registra a falha na implantação no banco de dados se disponível
                    if db and prompt_id:
                        SystemPromptRepository.create_deployment(
                            db=db,
                            prompt_id=prompt_id,
                            agent_id=agent.id,
                            agent_type=agent_type,
                            status="failed",
                            details={"error": str(agent_error), "tags": agent.tags if hasattr(agent, "tags") else []}
                        )
            
            return results
        
        except Exception as e:
            logger.error(f"Erro ao atualizar agents: {str(e)}")
            return results
    
    async def update_system_prompt(self, 
                                  new_prompt: str,
                                  agent_type: str = "agentic_search", 
                                  update_agents: bool = True,
                                  tags: Optional[List[str]] = None,
                                  metadata: Optional[Dict[str, Any]] = None,
                                  db: Session = None) -> Dict[str, any]:
        """
        Atualiza o system prompt no banco de dados e em todos os agentes existentes.
        
        Args:
            new_prompt: Novo texto para o system prompt
            agent_type: Tipo do agente
            update_agents: Se deve atualizar os agentes existentes
            tags: Filtrar agentes por tags específicas
            metadata: Metadados adicionais para armazenar com o prompt
            db: Sessão do banco de dados
            
        Returns:
            Dict: Resultado das operações
        """
        result = {
            "success": True,
            "prompt_id": None,
            "agents_updated": {}
        }
        
        # Usa gerenciador de contexto para sessão se db não for fornecido
        if db is None:
            with get_db_session() as session:
                db = session
        
        # Usa a sessão que foi fornecida ou criada
        return await self._perform_update(
            db, 
            new_prompt, 
            agent_type, 
            update_agents, 
            tags, 
            metadata, 
            result
        )
    
    async def _perform_update(self,
                             db: Session,
                             new_prompt: str,
                             agent_type: str,
                             update_agents: bool,
                             tags: Optional[List[str]],
                             metadata: Optional[Dict[str, Any]],
                             result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a atualização do system prompt com uma sessão de banco de dados.
        
        Args:
            db: Sessão do banco de dados
            new_prompt: Novo texto para o system prompt
            agent_type: Tipo do agente
            update_agents: Se deve atualizar os agentes existentes
            tags: Filtrar agentes por tags específicas
            metadata: Metadados adicionais para armazenar com o prompt
            result: Dicionário de resultado parcial
            
        Returns:
            Dict: Resultado das operações atualizado
        """
        # Salva o novo prompt no banco de dados
        prompt = SystemPromptRepository.create_prompt(
            db=db,
            agent_type=agent_type,
            content=new_prompt,
            metadata=metadata or {"source": "api"}
        )
        result["prompt_id"] = prompt.prompt_id
        
        # Atualiza os agentes existentes se solicitado
        if update_agents:
            agents_result = await self.update_all_agents_system_prompt(
                new_prompt=new_prompt, 
                agent_type=agent_type, 
                tags=tags,
                db=db,
                prompt_id=prompt.prompt_id
            )
            result["agents_updated"] = agents_result
            
            if agents_result and not all(agents_result.values()):
                result["success"] = False
        
        return result
    
    async def get_prompt_history(self, 
                                agent_type: str = "agentic_search",
                                limit: int = 10,
                                db: Session = None) -> List[Dict[str, Any]]:
        """
        Obtém o histórico de versões de um system prompt.
        
        Args:
            agent_type: Tipo do agente
            limit: Limite de resultados
            db: Sessão do banco de dados
            
        Returns:
            List[Dict[str, Any]]: Lista de prompts com informações resumidas
        """
        if db is None:
            with get_db_session() as session:
                return self._get_history(session, agent_type, limit)
        else:
            return self._get_history(db, agent_type, limit)
    
    def _get_history(self, 
                    db: Session, 
                    agent_type: str, 
                    limit: int) -> List[Dict[str, Any]]:
        """
        Implementação síncrona para obter o histórico de versões.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            limit: Limite de resultados
            
        Returns:
            List[Dict[str, Any]]: Lista de prompts formatada
        """
        prompts = SystemPromptRepository.list_prompts(
            db=db, 
            agent_type=agent_type, 
            limit=limit
        )
        
        # Formata os resultados
        formatted_prompts = []
        for p in prompts:
            # Resumo do conteúdo para preview
            content_preview = p.content[:100] + "..." if len(p.content) > 100 else p.content
            
            # Formata datas para string ISO
            created_at_str = p.created_at.isoformat() if p.created_at else None
            updated_at_str = p.updated_at.isoformat() if p.updated_at else None
            
            formatted_prompts.append({
                "prompt_id": p.prompt_id,
                "version": p.version,
                "is_active": p.is_active,
                "created_at": created_at_str,
                "updated_at": updated_at_str,
                "content": content_preview,
                "metadata": p.prompt_metadata
            })
            
        return formatted_prompts


# Instância do serviço
system_prompt_service = SystemPromptService() 