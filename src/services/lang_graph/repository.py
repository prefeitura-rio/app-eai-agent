from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.services.lang_graph.database import db_manager, LongTermMemory
from src.services.lang_graph.models import (
    MemoryResponse,
    MemoryType,
    MemoryCreateRequest,
    MemoryUpdateRequest,
)
from src.services.lang_graph.llms import llm_config

logger = logging.getLogger(__name__)


class MemoryRepository:
    """Repositório para operações de memória usando SQLAlchemy."""

    def __init__(self):
        self.db_manager = db_manager
        self.llm_config = llm_config

    def create_memory(
        self, user_id: str, content: str, memory_type: MemoryType
    ) -> Optional[str]:
        try:
            # Gerar embedding
            embedding = self.llm_config.generate_embedding(content)

            # Criar objeto SQLAlchemy
            memory = LongTermMemory(
                user_id=user_id,
                content=content,
                memory_type=memory_type.value,
                embedding=embedding,  # pgvector.Vector aceita lista diretamente
            )

            # Salvar no banco
            session = self.db_manager.get_session()
            try:
                session.add(memory)
                session.commit()
                session.refresh(memory)
                logger.info(f"Memória criada com sucesso: {memory.memory_id}")
                return str(memory.memory_id)
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Erro ao criar memória: {e}")
            raise

    def get_memories_semantic(
        self,
        user_id: str,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 20,
        min_relevance: float = 0.6,
    ) -> List[MemoryResponse]:
        try:
            # Gerar embedding da query
            query_embedding = self.llm_config.generate_embedding(query)
            # Converter numpy.ndarray para lista
            query_embedding_list = (
                query_embedding.tolist()
                if hasattr(query_embedding, "tolist")
                else list(query_embedding)
            )

            session = self.db_manager.get_session()
            try:
                # Usar SQLAlchemy ORM com pgvector conforme documentação
                from sqlalchemy import select
                from src.services.lang_graph.database import LongTermMemory

                # Construir query base usando a sintaxe correta do pgvector
                query_obj = session.query(
                    LongTermMemory,
                    LongTermMemory.embedding.cosine_distance(
                        query_embedding_list
                    ).label("distance"),
                ).filter(LongTermMemory.user_id == user_id)

                # Adicionar filtro de memory_type se fornecido
                if memory_type:
                    query_obj = query_obj.filter(
                        LongTermMemory.memory_type == memory_type.value
                    )

                # Adicionar filtro de relevância usando cosine_distance
                similarity_threshold = min_relevance
                query_obj = query_obj.filter(
                    LongTermMemory.embedding.cosine_distance(query_embedding_list)
                    < similarity_threshold
                )

                # Ordenar por similaridade (menor distância = mais similar)
                query_obj = query_obj.order_by("distance").limit(limit)

                # Executar query
                results = query_obj.all()

                # Converter para objetos MemoryResponse
                memories = []
                for memory_db, distance in results:
                    # Calcular score de relevância
                    relevance_score = 1 - distance  # cosine_distance já é 0-1

                    memory = MemoryResponse(
                        memory_id=str(memory_db.memory_id),
                        content=memory_db.content,
                        memory_type=MemoryType(memory_db.memory_type),
                        creation_datetime=memory_db.creation_datetime,
                        last_accessed=memory_db.last_accessed,
                        relevance_score=relevance_score,
                    )
                    memories.append(memory)

                # Atualizar last_accessed
                if memories:
                    memory_ids = [m.memory_id for m in memories]
                    self._update_last_accessed(memory_ids)

                logger.info(
                    f"Encontradas {len(memories)} memórias semânticas para query: {query}"
                )
                return memories

            finally:
                session.close()

        except Exception as e:
            import traceback

            logger.error(f"Erro ao buscar memórias semânticas: {e}")
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            # Fallback para busca cronológica em caso de erro
            logger.info(f"Usando fallback cronológico para query: {query}")
            return self.get_memories_chronological(user_id, memory_type, limit)

    def get_memories_chronological(
        self, user_id: str, memory_type: Optional[MemoryType] = None, limit: int = 20
    ) -> List[MemoryResponse]:
        try:
            session = self.db_manager.get_session()
            try:
                query = session.query(LongTermMemory).filter(
                    LongTermMemory.user_id == user_id
                )

                if memory_type:
                    query = query.filter(
                        LongTermMemory.memory_type == memory_type.value
                    )

                memories_db = (
                    query.order_by(LongTermMemory.creation_datetime.desc())
                    .limit(limit)
                    .all()
                )

                # Converter para objetos MemoryResponse
                memories = []
                for memory_db in memories_db:
                    memory = MemoryResponse(
                        memory_id=str(memory_db.memory_id),
                        content=memory_db.content,
                        memory_type=MemoryType(memory_db.memory_type),
                        creation_datetime=memory_db.creation_datetime,
                        last_accessed=memory_db.last_accessed,
                    )
                    memories.append(memory)

                # Atualizar last_accessed
                if memories:
                    memory_ids = [m.memory_id for m in memories]
                    self._update_last_accessed(memory_ids)

                logger.info(f"Encontradas {len(memories)} memórias cronológicas")
                return memories
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Erro ao buscar memórias cronológicas: {e}")
            raise

    def update_memory(self, memory_id: str, user_id: str, new_content: str) -> bool:
        try:
            session = self.db_manager.get_session()
            try:
                # Buscar memória
                memory = (
                    session.query(LongTermMemory)
                    .filter(
                        LongTermMemory.memory_id == memory_id,
                        LongTermMemory.user_id == user_id,
                    )
                    .first()
                )

                if not memory:
                    logger.warning(
                        f"Memória {memory_id} não encontrada ou não pertence ao usuário {user_id}"
                    )
                    return False

                # Gerar novo embedding
                new_embedding = self.llm_config.generate_embedding(new_content)

                # Atualizar memória
                memory.content = new_content
                memory.embedding = (
                    new_embedding  # pgvector.Vector aceita lista diretamente
                )
                memory.last_accessed = datetime.utcnow()

                session.commit()
                logger.info(f"Memória {memory_id} atualizada com sucesso")
                return True
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Erro ao atualizar memória: {e}")
            raise

    def delete_memory(self, memory_id: str, user_id: str) -> bool:
        try:
            session = self.db_manager.get_session()
            try:
                # Buscar memória
                memory = (
                    session.query(LongTermMemory)
                    .filter(
                        LongTermMemory.memory_id == memory_id,
                        LongTermMemory.user_id == user_id,
                    )
                    .first()
                )

                if not memory:
                    logger.warning(
                        f"Memória {memory_id} não encontrada ou não pertence ao usuário {user_id}"
                    )
                    return False

                # Deletar memória
                session.delete(memory)
                session.commit()

                logger.info(f"Memória {memory_id} deletada com sucesso")
                return True
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Erro ao deletar memória: {e}")
            raise

    def _update_last_accessed(self, memory_ids: List[str]) -> None:
        """Atualiza o campo last_accessed para uma lista de memórias."""
        if not memory_ids:
            return

        try:
            session = self.db_manager.get_session()
            try:
                session.query(LongTermMemory).filter(
                    LongTermMemory.memory_id.in_(memory_ids)
                ).update(
                    {LongTermMemory.last_accessed: datetime.utcnow()},
                    synchronize_session=False,
                )
                session.commit()
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Erro ao atualizar last_accessed: {e}")
            # Não levantar exceção para não interromper o fluxo principal

    def get_memory_by_id(
        self, memory_id: str, user_id: str
    ) -> Optional[MemoryResponse]:
        try:
            session = self.db_manager.get_session()
            try:
                memory_db = (
                    session.query(LongTermMemory)
                    .filter(
                        LongTermMemory.memory_id == memory_id,
                        LongTermMemory.user_id == user_id,
                    )
                    .first()
                )

                if memory_db:
                    memory = MemoryResponse(
                        memory_id=str(memory_db.memory_id),
                        content=memory_db.content,
                        memory_type=MemoryType(memory_db.memory_type),
                        creation_datetime=memory_db.creation_datetime,
                        last_accessed=memory_db.last_accessed,
                    )
                    return memory

                return None
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Erro ao buscar memória por ID: {e}")
            raise


# Instância global para uso em todo o módulo
memory_repository = MemoryRepository()
