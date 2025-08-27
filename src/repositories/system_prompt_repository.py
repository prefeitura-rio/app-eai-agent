from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from src.models.system_prompt_model import SystemPrompt, SystemPromptDeployment


class SystemPromptRepository:
    """
    Repositório para acesso aos system prompts no banco de dados.
    """

    @staticmethod
    def create_prompt(
        db: Session,
        agent_type: str,
        content: str,
        version: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SystemPrompt:
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
        
        Raises:
            Exception: Se houver conflito de versão (constraint unique violation)
        """
        from sqlalchemy.exc import IntegrityError
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Se a versão não foi fornecida, obter a versão mais recente e incrementar
                if version is None:
                    latest_prompt = SystemPromptRepository.get_latest_prompt(db, agent_type)
                    current_version = 1 if latest_prompt is None else latest_prompt.version + 1
                else:
                    current_version = version

                # Verifica se já existe um prompt com esta versão (prevenção extra)
                existing_prompt = db.query(SystemPrompt).filter(
                    SystemPrompt.agent_type == agent_type,
                    SystemPrompt.version == current_version
                ).first()
                
                if existing_prompt:
                    if version is not None:
                        # Se uma versão específica foi solicitada e já existe, lança erro
                        raise Exception(f"Já existe um prompt com agent_type '{agent_type}' e version {current_version}")
                    else:
                        # Se a versão foi auto-gerada, incrementa e tenta novamente
                        current_version = existing_prompt.version + 1

                # Desativa todos os prompts anteriores deste tipo de agente
                db.query(SystemPrompt).filter(
                    SystemPrompt.agent_type == agent_type, 
                    SystemPrompt.is_active == True
                ).update({"is_active": False})

                # Cria o novo prompt
                prompt = SystemPrompt(
                    agent_type=agent_type,
                    content=content,
                    version=current_version,
                    is_active=True,
                    prompt_metadata=metadata or {},
                )

                db.add(prompt)
                db.commit()
                db.refresh(prompt)

                return prompt
                
            except IntegrityError as e:
                db.rollback()
                retry_count += 1
                
                if "uix_agent_type_version" in str(e) and retry_count < max_retries:
                    # Se for erro de constraint única e ainda temos tentativas, 
                    # força recalculo da versão
                    version = None
                    continue
                else:
                    # Se não for erro de constraint ou esgotamos tentativas, re-raise
                    raise Exception(f"Erro ao criar prompt após {retry_count} tentativas: {str(e)}")
            
            except Exception as e:
                db.rollback()
                raise e
                
        raise Exception(f"Não foi possível criar o prompt após {max_retries} tentativas")

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
        return (
            db.query(SystemPrompt).filter(SystemPrompt.prompt_id == prompt_id).first()
        )

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
        return (
            db.query(SystemPrompt)
            .filter(SystemPrompt.agent_type == agent_type)
            .order_by(desc(SystemPrompt.version))
            .first()
        )

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
        return (
            db.query(SystemPrompt)
            .filter(
                SystemPrompt.agent_type == agent_type, SystemPrompt.is_active == True
            )
            .first()
        )

    @staticmethod
    def list_prompts(
        db: Session, agent_type: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[SystemPrompt]:
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

        return (
            query.order_by(SystemPrompt.agent_type, desc(SystemPrompt.version))
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_deployment(
        db: Session,
        prompt_id: str,
        agent_id: str,
        agent_type: str,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
    ) -> SystemPromptDeployment:
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
            details=details or {},
        )

        db.add(deployment)
        db.commit()
        db.refresh(deployment)

        return deployment

    @staticmethod
    def get_agent_deployments(
        db: Session, agent_id: str, limit: int = 10
    ) -> List[SystemPromptDeployment]:
        """
        Busca as implantações de system prompts para um agente específico.

        Args:
            db: Sessão do banco de dados
            agent_id: ID do agente
            limit: Limite de resultados

        Returns:
            List[SystemPromptDeployment]: Lista de implantações
        """
        return (
            db.query(SystemPromptDeployment)
            .filter(SystemPromptDeployment.agent_id == agent_id)
            .order_by(desc(SystemPromptDeployment.deployed_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_prompt_deployments(
        db: Session, prompt_id: str, limit: int = 100, offset: int = 0
    ) -> List[SystemPromptDeployment]:
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
        return (
            db.query(SystemPromptDeployment)
            .filter(SystemPromptDeployment.prompt_id == prompt_id)
            .order_by(desc(SystemPromptDeployment.deployed_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def delete_deployments_by_prompt_ids(db: Session, prompt_ids: List[str]) -> int:
        """
        Exclui todas as implantações associadas aos IDs de prompts fornecidos.

        Args:
            db: Sessão do banco de dados
            prompt_ids: Lista de IDs de prompts

        Returns:
            int: Número de registros excluídos
        """
        if not prompt_ids:
            return 0

        result = (
            db.query(SystemPromptDeployment)
            .filter(SystemPromptDeployment.prompt_id.in_(prompt_ids))
            .delete(synchronize_session=False)
        )

        return result

    @staticmethod
    def delete_prompts_by_agent_type(db: Session, agent_type: str) -> int:
        """
        Exclui todos os prompts de um tipo de agente específico.

        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente

        Returns:
            int: Número de registros excluídos
        """
        result = (
            db.query(SystemPrompt)
            .filter(SystemPrompt.agent_type == agent_type)
            .delete(synchronize_session=False)
        )

        return result

    @staticmethod
    def get_prompt_ids_by_agent_type(db: Session, agent_type: str) -> List[str]:
        """
        Obtém todos os IDs de prompts de um tipo de agente.

        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente

        Returns:
            List[str]: Lista de IDs de prompts
        """
        prompts = (
            db.query(SystemPrompt.prompt_id)
            .filter(SystemPrompt.agent_type == agent_type)
            .all()
        )

        return [p.prompt_id for p in prompts] if prompts else []

    @staticmethod
    def count_prompts_by_date_and_type(db: Session, agent_type: str, date) -> int:
        """
        Conta quantos prompts foram criados em uma data específica para um tipo de agente.

        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            date: Data para filtrar (datetime.date)

        Returns:
            int: Número de prompts criados na data
        """
        from sqlalchemy import func, cast, Date
        
        return (
            db.query(SystemPrompt)
            .filter(
                SystemPrompt.agent_type == agent_type,
                cast(SystemPrompt.created_at, Date) == date
            )
            .count()
        )
    
    @staticmethod
    def count_unified_changes_by_date_and_type(db: Session, agent_type: str, date) -> int:
        """
        Conta quantas alterações (prompts + configs) foram criadas em uma data específica 
        para um tipo de agente, permitindo versionamento unificado.
        
        Se não há registros para hoje, retorna a próxima versão baseada no maior número
        de versão existente entre prompts e configs.

        Args:
            db: Sessão do banco de dados
            agent_type: Tipo do agente
            date: Data para filtrar (datetime.date)

        Returns:
            int: Número total de alterações (prompts + configs) criadas na data
        """
        from sqlalchemy import func, cast, Date
        from src.models.agent_config_model import AgentConfig
        
        prompt_count = (
            db.query(SystemPrompt)
            .filter(
                SystemPrompt.agent_type == agent_type,
                cast(SystemPrompt.created_at, Date) == date
            )
            .count()
        )
        
        config_count = (
            db.query(AgentConfig)
            .filter(
                AgentConfig.agent_type == agent_type,
                cast(AgentConfig.created_at, Date) == date
            )
            .count()
        )
        
        total_today = prompt_count + config_count
        
        # Se não há alterações hoje, verificar a maior versão existente
        # para evitar conflitos de versionamento
        if total_today == 0:
            latest_prompt = SystemPromptRepository.get_latest_prompt(db, agent_type)
            latest_config = (
                db.query(AgentConfig)
                .filter(AgentConfig.agent_type == agent_type)
                .order_by(AgentConfig.version.desc())
                .first()
            )
            
            prompt_version = latest_prompt.version if latest_prompt else 0
            config_version = latest_config.version if latest_config else 0
            
            # Retorna a maior versão encontrada (será incrementada +1 no serviço)
            return max(prompt_version, config_version)
        
        return total_today

    @staticmethod
    def delete_prompt_by_id(db: Session, prompt_id: str) -> bool:
        """
        Exclui um prompt específico pelo ID.

        Args:
            db: Sessão do banco de dados
            prompt_id: ID do prompt a ser excluído

        Returns:
            bool: True se o prompt foi excluído, False se não encontrado
        """
        result = (
            db.query(SystemPrompt)
            .filter(SystemPrompt.prompt_id == prompt_id)
            .delete(synchronize_session=False)
        )

        return result > 0
