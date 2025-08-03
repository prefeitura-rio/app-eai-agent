from typing import List, Optional, Dict, Any
import logging
from src.services.lang_graph.repository import memory_repository
from src.services.lang_graph.models import (
    MemoryResponse,
    MemoryType,
    MemoryOperationResult,
    MemorySearchRequest,
    MemoryCreateRequest,
    MemoryUpdateRequest,
)

logger = logging.getLogger(__name__)


class MemoryManager:
    """Gerenciador de memória que integra com o repositório."""

    def __init__(self):
        self.repository = memory_repository

    def get_memory(
        self,
        user_id: str,
        mode: str,
        query: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 20,
        min_relevance: float = 0.6,
    ) -> MemoryOperationResult:
        """Recupera memórias baseado no modo especificado."""
        try:
            if mode == "semantic":
                if not query:
                    return MemoryOperationResult(
                        success=False,
                        error_message="Query é obrigatória para busca semântica",
                    )

                memories = self.repository.get_memories_semantic(
                    user_id=user_id,
                    query=query,
                    memory_type=memory_type,
                    limit=limit,
                    min_relevance=min_relevance,
                )

            elif mode == "chronological":
                memories = self.repository.get_memories_chronological(
                    user_id=user_id, memory_type=memory_type, limit=limit
                )

            else:
                return MemoryOperationResult(
                    success=False,
                    error_message=f"Modo '{mode}' não suportado. Use 'semantic' ou 'chronological'",
                )

            return MemoryOperationResult(success=True, memories=memories)

        except Exception as e:
            logger.error(f"Erro ao recuperar memórias: {e}")
            return MemoryOperationResult(success=False, error_message=str(e))

    def save_memory(
        self, user_id: str, content: str, memory_type: MemoryType
    ) -> MemoryOperationResult:
        """Salva uma nova memória."""
        try:
            # Validar entrada
            if not content.strip():
                return MemoryOperationResult(
                    success=False,
                    error_message="Conteúdo da memória não pode estar vazio",
                )

            # Criar memória no repositório
            memory_id = self.repository.create_memory(
                user_id=user_id, content=content.strip(), memory_type=memory_type
            )

            if memory_id:
                return MemoryOperationResult(
                    success=True,
                    memory_id=memory_id,
                    content=content,
                    memory_type=memory_type,
                )
            else:
                return MemoryOperationResult(
                    success=False,
                    error_message="Falha ao criar memória no banco de dados",
                )

        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")
            return MemoryOperationResult(success=False, error_message=str(e))

    def update_memory(
        self, user_id: str, memory_id: str, new_content: str
    ) -> MemoryOperationResult:
        """Atualiza uma memória existente."""
        try:
            # Validar entrada
            if not new_content.strip():
                return MemoryOperationResult(
                    success=False,
                    error_message="Novo conteúdo da memória não pode estar vazio",
                )

            # Obter memória atual para retornar conteúdo antigo
            current_memory = self.repository.get_memory_by_id(memory_id, user_id)
            if not current_memory:
                return MemoryOperationResult(
                    success=False,
                    error_message="Memória não encontrada ou não pertence ao usuário",
                )

            # Atualizar memória
            success = self.repository.update_memory(
                memory_id=memory_id, user_id=user_id, new_content=new_content.strip()
            )

            if success:
                return MemoryOperationResult(
                    success=True,
                    memory_id=memory_id,
                    content=new_content,
                    memory_type=current_memory.memory_type,
                )
            else:
                return MemoryOperationResult(
                    success=False, error_message="Falha ao atualizar memória"
                )

        except Exception as e:
            logger.error(f"Erro ao atualizar memória: {e}")
            return MemoryOperationResult(success=False, error_message=str(e))

    def delete_memory(self, user_id: str, memory_id: str) -> MemoryOperationResult:
        """Deleta uma memória."""
        try:
            # Obter memória antes de deletar para retornar informações
            memory = self.repository.get_memory_by_id(memory_id, user_id)
            if not memory:
                return MemoryOperationResult(
                    success=False,
                    error_message="Memória não encontrada ou não pertence ao usuário",
                )

            # Deletar memória
            success = self.repository.delete_memory(
                memory_id=memory_id, user_id=user_id
            )

            if success:
                return MemoryOperationResult(
                    success=True,
                    memory_id=memory_id,
                    content=memory.content,
                    memory_type=memory.memory_type,
                )
            else:
                return MemoryOperationResult(
                    success=False, error_message="Falha ao deletar memória"
                )

        except Exception as e:
            logger.error(f"Erro ao deletar memória: {e}")
            return MemoryOperationResult(success=False, error_message=str(e))

    def get_memory_by_id(self, user_id: str, memory_id: str) -> MemoryOperationResult:
        """Obtém uma memória específica por ID."""
        try:
            memory = self.repository.get_memory_by_id(memory_id, user_id)

            if memory:
                return MemoryOperationResult(
                    success=True,
                    memory_id=memory.memory_id,
                    content=memory.content,
                    memory_type=memory.memory_type,
                )
            else:
                return MemoryOperationResult(
                    success=False,
                    error_message="Memória não encontrada ou não pertence ao usuário",
                )

        except Exception as e:
            logger.error(f"Erro ao buscar memória por ID: {e}")
            return MemoryOperationResult(success=False, error_message=str(e))

    def search_memories(
        self, user_id: str, search_request: MemorySearchRequest
    ) -> MemoryOperationResult:
        """Busca memórias usando um objeto de requisição."""
        return self.get_memory(
            user_id=user_id,
            mode=search_request.mode,
            query=search_request.query,
            memory_type=search_request.memory_type,
        )

    def create_memory_from_request(
        self, user_id: str, request: MemoryCreateRequest
    ) -> MemoryOperationResult:
        """Cria memória usando um objeto de requisição."""
        return self.save_memory(
            user_id=user_id, content=request.content, memory_type=request.memory_type
        )

    def update_memory_from_request(
        self, user_id: str, request: MemoryUpdateRequest
    ) -> MemoryOperationResult:
        """Atualiza memória usando um objeto de requisição."""
        return self.update_memory(
            user_id=user_id,
            memory_id=request.memory_id,
            new_content=request.new_content,
        )


# Instância global para uso em todo o módulo
memory_manager = MemoryManager()
