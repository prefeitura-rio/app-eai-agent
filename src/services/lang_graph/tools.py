from typing import Dict, Any, List, Optional
import logging
from langchain_core.tools import tool
from src.services.lang_graph.models import (
    MemoryType,
    MemoryCreateRequest,
    MemoryUpdateRequest,
    MemoryDeleteRequest,
    MemorySearchRequest,
    ToolOutput,
)
from src.services.lang_graph.memory import memory_manager

logger = logging.getLogger(__name__)


@tool
def get_memory_tool(
    mode: str = "semantic",
    query: Optional[str] = None,
    memory_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Recupera memórias do usuário.

    Args:
        mode: "semantic" para busca por similaridade ou "chronological" para ordem cronológica
        query: Texto para busca semântica (obrigatório se mode="semantic")
        memory_type: Tipo de memória para filtrar (opcional)

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # Validar parâmetros
        if mode not in ["semantic", "chronological"]:
            return {
                "success": False,
                "error": f"Mode inválido: {mode}. Use 'semantic' ou 'chronological'",
            }

        if mode == "semantic" and not query:
            return {
                "success": False,
                "error": "Query é obrigatória para busca semântica",
            }

        # Converter memory_type se fornecido
        memory_type_enum = None
        if memory_type:
            try:
                memory_type_enum = MemoryType(memory_type)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Memory type inválido: {memory_type}",
                }

        # PARÂMETROS SENSÍVEIS APLICADOS AUTOMATICAMENTE PELO SISTEMA
        # user_id, limit, min_relevance são injetados pelo grafo

        # Chamar memory manager
        result = memory_manager.get_memory(
            user_id="test_user_from_tool",  # Será sobrescrito pelo sistema
            mode=mode,
            query=query,
            memory_type=memory_type_enum,
            limit=20,  # Será sobrescrito pelo sistema
            min_relevance=0.6,  # Será sobrescrito pelo sistema
        )

        if result.success:
            return {
                "success": True,
                "memories": [memory.model_dump() for memory in result.memories],
                "count": len(result.memories),
            }
        else:
            return {"success": False, "error": result.error_message}

    except Exception as e:
        logger.error(f"Erro na ferramenta get_memory: {e}")
        return {"success": False, "error": f"Erro interno: {str(e)}"}


@tool
def save_memory_tool(content: str, memory_type: str) -> Dict[str, Any]:
    """
    Salva uma nova memória.

    Args:
        content: Conteúdo da memória
        memory_type: Tipo da memória (user_profile, preference, goal, constraint, critical_info)

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # Validar memory_type
        try:
            memory_type_enum = MemoryType(memory_type)
        except ValueError:
            return {"success": False, "error": f"Memory type inválido: {memory_type}"}

        # PARÂMETROS SENSÍVEIS APLICADOS AUTOMATICAMENTE PELO SISTEMA
        # user_id é injetado pelo grafo

        # Chamar memory manager diretamente
        result = memory_manager.save_memory(
            user_id="test_user_from_tool",  # Será sobrescrito pelo sistema
            content=content,
            memory_type=memory_type_enum,
        )

        if result.success:
            return {
                "success": True,
                "memory_id": result.memory_id,
                "message": "Memória salva com sucesso",
            }
        else:
            return {"success": False, "error": result.error_message}

    except Exception as e:
        logger.error(f"Erro na ferramenta save_memory: {e}")
        return {"success": False, "error": f"Erro interno: {str(e)}"}


@tool
def update_memory_tool(memory_id: str, new_content: str) -> Dict[str, Any]:
    """
    Atualiza uma memória existente.

    Args:
        memory_id: ID da memória a ser atualizada
        new_content: Novo conteúdo da memória

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # PARÂMETROS SENSÍVEIS APLICADOS AUTOMATICAMENTE PELO SISTEMA
        # user_id é injetado pelo grafo

        # Chamar memory manager diretamente
        result = memory_manager.update_memory(
            user_id="test_user_from_tool",  # Será sobrescrito pelo sistema
            memory_id=memory_id,
            new_content=new_content,
        )

        if result.success:
            return {"success": True, "message": "Memória atualizada com sucesso"}
        else:
            return {"success": False, "error": result.error_message}

    except Exception as e:
        logger.error(f"Erro na ferramenta update_memory: {e}")
        return {"success": False, "error": f"Erro interno: {str(e)}"}


@tool
def delete_memory_tool(memory_id: str) -> Dict[str, Any]:
    """
    Deleta uma memória.

    Args:
        memory_id: ID da memória a ser deletada

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # PARÂMETROS SENSÍVEIS APLICADOS AUTOMATICAMENTE PELO SISTEMA
        # user_id é injetado pelo grafo

        # Chamar memory manager diretamente
        result = memory_manager.delete_memory(
            user_id="test_user_from_tool",  # Será sobrescrito pelo sistema
            memory_id=memory_id,
        )

        if result.success:
            return {"success": True, "message": "Memória deletada com sucesso"}
        else:
            return {"success": False, "error": result.error_message}

    except Exception as e:
        logger.error(f"Erro na ferramenta delete_memory: {e}")
        return {"success": False, "error": f"Erro interno: {str(e)}"}


# Lista de ferramentas disponíveis
TOOLS = [
    get_memory_tool,
    save_memory_tool,
    update_memory_tool,
    delete_memory_tool,
]
