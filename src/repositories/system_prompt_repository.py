from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from src.models.system_prompt_model import SystemPrompt, SystemPromptDeployment


class SystemPromptRepository:
    """
    Repositório para acesso aos system prompts no banco de dados.
    """
    
    @staticmethod
    def create_prompt(db: Session, 
                      agent_type: str, 
                      content: str, 
                      version: Optional[int] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> SystemPrompt:
        """
        Cria um novo system prompt.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            content: Conteúdo do system prompt
            version: Versão do prompt (se None, será incrementado automaticamente)
            metadata: Metadados adicionais
            
        Returns:
            SystemPrompt: Novo system prompt criado
        """
        # Se a versão não foi fornecida, obter a versão mais recente e incrementar
        if version is None:
            latest_prompt = SystemPromptRepository.get_latest_prompt(db, agent_type)
            version = 1 if latest_prompt is None else latest_prompt.version + 1
            
        # Desativa todos os prompts anteriores deste tipo de agente
        if version > 1:
            db.query(SystemPrompt).filter(
                SystemPrompt.agent_type == agent_type,
                SystemPrompt.is_active == True
            ).update({"is_active": False})
        
        # Cria o novo prompt
        prompt = SystemPrompt(
            agent_type=agent_type,
            content=content,
            version=version,
            is_active=True,
            metadata=metadata or {}
        )
        
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        return prompt
    
    @staticmethod
    def get_prompt_by_id(db: Session, prompt_id: str) -> Optional[SystemPrompt]:
        """
        Busca um system prompt pelo ID.
        
        Args:
            db: Sessão do banco de dados
            prompt_id: ID do prompt
            
        Returns:
            Optional[SystemPrompt]: System prompt encontrado ou None
        """
        return db.query(SystemPrompt).filter(SystemPrompt.prompt_id == prompt_id).first()
    
    @staticmethod
    def get_latest_prompt(db: Session, agent_type: str) -> Optional[SystemPrompt]:
        """
        Busca o system prompt mais recente para um tipo de agente.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            
        Returns:
            Optional[SystemPrompt]: System prompt mais recente ou None
        """
        return db.query(SystemPrompt).filter(
            SystemPrompt.agent_type == agent_type
        ).order_by(desc(SystemPrompt.version)).first()
    
    @staticmethod
    def get_active_prompt(db: Session, agent_type: str) -> Optional[SystemPrompt]:
        """
        Busca o system prompt ativo para um tipo de agente.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            
        Returns:
            Optional[SystemPrompt]: System prompt ativo ou None
        """
        return db.query(SystemPrompt).filter(
            SystemPrompt.agent_type == agent_type,
            SystemPrompt.is_active == True
        ).first()
    
    @staticmethod
    def list_prompts(db: Session, 
                    agent_type: Optional[str] = None, 
                    limit: int = 100, 
                    offset: int = 0) -> List[SystemPrompt]:
        """
        Lista system prompts com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente para filtrar
            limit: Limite de resultados
            offset: Deslocamento para paginação
            
        Returns:
            List[SystemPrompt]: Lista de system prompts
        """
        query = db.query(SystemPrompt)
        
        if agent_type:
            query = query.filter(SystemPrompt.agent_type == agent_type)
            
        return query.order_by(
            SystemPrompt.agent_type, 
            desc(SystemPrompt.version)
        ).offset(offset).limit(limit).all()
    
    @staticmethod
    def create_deployment(db: Session,
                         prompt_id: str,
                         agent_id: str,
                         agent_type: str,
                         status: str = "success",
                         details: Optional[Dict[str, Any]] = None) -> SystemPromptDeployment:
        """
        Registra uma implantação de system prompt em um agente.
        
        Args:
            db: Sessão do banco de dados
            prompt_id: ID do prompt implantado
            agent_id: ID do agente
            agent_type: Tipo do agente
            status: Status da implantação
            details: Detalhes adicionais
            
        Returns:
            SystemPromptDeployment: Registro de implantação criado
        """
        deployment = SystemPromptDeployment(
            prompt_id=prompt_id,
            agent_id=agent_id,
            agent_type=agent_type,
            status=status,
            details=details or {}
        )
        
        db.add(deployment)
        db.commit()
        db.refresh(deployment)
        
        return deployment
    
    @staticmethod
    def get_agent_deployments(db: Session, 
                             agent_id: str, 
                             limit: int = 10) -> List[SystemPromptDeployment]:
        """
        Busca as implantações de system prompts para um agente específico.
        
        Args:
            db: Sessão do banco de dados
            agent_id: ID do agente
            limit: Limite de resultados
            
        Returns:
            List[SystemPromptDeployment]: Lista de implantações
        """
        return db.query(SystemPromptDeployment).filter(
            SystemPromptDeployment.agent_id == agent_id
        ).order_by(desc(SystemPromptDeployment.deployed_at)).limit(limit).all()
    
    @staticmethod
    def get_prompt_deployments(db: Session, 
                              prompt_id: str, 
                              limit: int = 100,
                              offset: int = 0) -> List[SystemPromptDeployment]:
        """
        Busca as implantações de um system prompt específico.
        
        Args:
            db: Sessão do banco de dados
            prompt_id: ID do prompt
            limit: Limite de resultados
            offset: Deslocamento para paginação
            
        Returns:
            List[SystemPromptDeployment]: Lista de implantações
        """
        return db.query(SystemPromptDeployment).filter(
            SystemPromptDeployment.prompt_id == prompt_id
        ).order_by(desc(SystemPromptDeployment.deployed_at)).offset(offset).limit(limit).all() 