from typing import Dict, Any, List, Optional
import logging
from langchain_core.tools import tool
from src.services.lang_graph.models import (
    MemoryType,
    MemoryTypeConfig,
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
    user_id: str,
    limit: int,
    min_relevance: float,
    memory_type: str,
    query: Optional[str] = None,
    mode: str = "semantic",
) -> Dict[str, Any]:
    """
    OBRIGATÓRIO: Use esta ferramenta sempre que o usuário pedir informações sobre si mesmo,
    perguntar sobre dados salvos anteriormente, ou quando você precisar buscar contexto
    para personalizar sua resposta.

    SITUAÇÕES DE USO OBRIGATÓRIO:
    - Usuário pergunta: "qual é o meu nome?", "quais são minhas preferências?", "lembra de mim?"
    - Usuário pede: "busque minhas informações", "mostre o que você sabe sobre mim"
    - Você precisa personalizar resposta baseada em dados do usuário
    - Usuário menciona algo que pode estar salvo (ex: "minha alergia", "minha profissão")

    Args:
        user_id: ID do usuário (injetado automaticamente)
        limit: Limite de resultados (injetado automaticamente)
        min_relevance: Relevância mínima (injetado automaticamente)
        memory_type: Tipo de memória para filtrar (user_profile, preference, goal, constraint, critical_info)
        query: Texto para busca semântica (obrigatório se mode="semantic")
        mode: "semantic" para busca por similaridade ou "chronological" para ordem cronológica

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

        # Se mode é semantic mas não há query, usar chronological
        if mode == "semantic" and not query:
            mode = "chronological"
            logger.info(
                "Modo alterado para 'chronological' pois não há query para busca semântica"
            )

        # Converter memory_type se fornecido
        memory_type_enum = None
        if memory_type:
            try:
                memory_type_enum = MemoryType(memory_type)
            except ValueError:
                # Obter lista de tipos válidos do enum
                valid_types = [t.value for t in MemoryType]
                return {
                    "success": False,
                    "error": f"Tipo de memória '{memory_type}' é inválido. Tente novamente com um dos tipos existentes: {', '.join(valid_types)}",
                }

        # Chamar memory manager
        result = memory_manager.get_memory(
            user_id=user_id,
            mode=mode,
            query=query,
            memory_type=memory_type_enum,
            limit=limit,
            min_relevance=min_relevance,
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
def save_memory_tool(user_id: str, content: str, memory_type: str) -> Dict[str, Any]:
    """
    OBRIGATÓRIO: Use esta ferramenta sempre que o usuário fornecer informações pessoais,
    preferências, objetivos, restrições ou informações críticas que devem ser lembradas.

    SITUAÇÕES DE USO OBRIGATÓRIO:
    - Usuário diz: "meu nome é João", "tenho 30 anos", "sou engenheiro"
    - Usuário menciona: "gosto de programar", "tenho alergia a frutos do mar"
    - Usuário informa: "quero aprender Python", "não posso comer glúten"
    - Usuário compartilha: "tenho um agendamento importante", "minha senha é..."
    - Qualquer informação pessoal que o usuário compartilha

    Args:
        user_id: ID do usuário (injetado automaticamente)
        content: Conteúdo da memória (informação a ser salva)
        memory_type: Tipo da memória - OBRIGATÓRIO escolher um dos seguintes:
            - user_profile: Dados pessoais (nome, idade, profissão, etc.)
            - preference: Preferências e gostos
            - goal: Objetivos e metas
            - constraint: Restrições e limitações
            - critical_info: Informações críticas (senhas, agendamentos, etc.)

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # Validar memory_type
        try:
            memory_type_enum = MemoryType(memory_type)
        except ValueError:
            # Obter lista de tipos válidos do enum
            valid_types = [t.value for t in MemoryType]
            return {
                "success": False,
                "error": f"Tipo de memória '{memory_type}' é inválido. Tente novamente com um dos tipos existentes: {', '.join(valid_types)}",
            }

        # Chamar memory manager diretamente
        result = memory_manager.save_memory(
            user_id=user_id,
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
def update_memory_tool(
    memory_id: str, new_content: str, user_id: str
) -> Dict[str, Any]:
    """
    OBRIGATÓRIO: Use esta ferramenta quando o usuário quiser atualizar ou corrigir
    informações que já foram salvas anteriormente.

    SITUAÇÕES DE USO OBRIGATÓRIO:
    - Usuário diz: "atualize minha idade para 31 anos"
    - Usuário pede: "corrija minha profissão para 'desenvolvedor'"
    - Usuário informa: "mude minha preferência de Java para Python"
    - Usuário quer atualizar qualquer informação já salva

    IMPORTANTE: Você precisa ter o memory_id correto. Se não tiver, use get_memory_tool
    primeiro para buscar a memória e obter o ID correto.

    Args:
        memory_id: ID da memória a ser atualizada (obtido via get_memory_tool)
        new_content: Novo conteúdo da memória
        user_id: ID do usuário (injetado automaticamente)

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # Chamar memory manager diretamente
        result = memory_manager.update_memory(
            user_id=user_id,
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
def delete_memory_tool(memory_id: str, user_id: str) -> Dict[str, Any]:
    """
    OBRIGATÓRIO: Use esta ferramenta quando o usuário quiser remover ou deletar
    informações que foram salvas anteriormente.

    SITUAÇÕES DE USO OBRIGATÓRIO:
    - Usuário diz: "delete a informação sobre minha alergia"
    - Usuário pede: "remova a memória sobre minha idade antiga"
    - Usuário quer: "apague essa informação que não é mais válida"
    - Usuário solicita deletar qualquer informação salva

    IMPORTANTE: Você precisa ter o memory_id correto. Se não tiver, use get_memory_tool
    primeiro para buscar a memória e obter o ID correto.

    Args:
        memory_id: ID da memória a ser deletada (obtido via get_memory_tool)
        user_id: ID do usuário (injetado automaticamente)

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # Chamar memory manager diretamente
        result = memory_manager.delete_memory(
            user_id=user_id,
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
