from copy import deepcopy
from typing import Dict, Any, List, Optional
import logging
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from src.services.lang_graph.models import (
    MemoryType,
    MemoryTypeConfig,
    MemoryCreateRequest,
    MemoryUpdateRequest,
    MemoryDeleteRequest,
    MemorySearchRequest,
    ToolOutput,
    GetMemoryToolInput,
    SaveMemoryToolInput,
    UpdateMemoryToolInput,
    DeleteMemoryToolInput,
    GetMemoryToolOutput,
    SaveMemoryToolOutput,
    UpdateMemoryToolOutput,
    DeleteMemoryToolOutput,
    ToolSuccessResponse,
    ToolErrorResponse,
)
from src.services.lang_graph.memory import memory_manager


from src.config import env
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

logger = logging.getLogger(__name__)


async def get_mcp_tools():
    """
    Inicializa o cliente MCP e busca as ferramentas disponíveis de forma assíncrona.
    """
    client = MultiServerMCPClient(
        {
            "rio_mcp": {
                "transport": "streamable_http",
                "url": env.MCP_SERVER_URL,
                "headers": {
                    "Authorization": f"Bearer {env.MCP_API_TOKEN}",
                },
            },
        }
    )
    tools = await client.get_tools()
    return tools


def safe_serialize_memory(memory_data: dict) -> dict:
    """Serializa dados de memória de forma segura."""
    try:
        # Clonar para não modificar original
        safe_data = deepcopy(memory_data)

        # Tratar memory_type
        memory_type = safe_data.get("memory_type")
        if memory_type is not None:
            if hasattr(memory_type, "value"):
                safe_data["memory_type"] = memory_type.value
            elif isinstance(memory_type, int):
                # Se é int, converter usando enum
                try:
                    safe_data["memory_type"] = MemoryType(memory_type).value
                except ValueError:
                    safe_data["memory_type"] = str(memory_type)
            else:
                safe_data["memory_type"] = str(memory_type)

        # Tratar datetime
        creation_datetime = safe_data.get("creation_datetime")
        if creation_datetime and hasattr(creation_datetime, "isoformat"):
            safe_data["creation_datetime"] = creation_datetime.isoformat()

        return safe_data

    except Exception as e:
        logger.error(f"Erro ao serializar memória: {e}")
        return {"error": "Erro de serialização"}


@tool
def get_memory_tool(
    memory_type: str,
    query: str,
    config: RunnableConfig = None,
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
        memory_type: Tipo de memória para filtrar (user_profile, preference, goal, constraint, critical_info)
        query: Texto para busca semântica (obrigatório!!)
        config: Configuração injetada automaticamente pelo LangGraph

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # Validar input usando o modelo
        input_data = GetMemoryToolInput(memory_type=memory_type, query=query)

        # Extrair parâmetros injetados da configuração
        configurable = config.get("configurable", {}) if config else {}
        user_id = configurable.get("user_id")
        limit = configurable.get("memory_limit", 20)
        min_relevance = configurable.get("memory_min_relevance", 0.6)

        if not user_id:
            error_response = ToolErrorResponse(
                success=False, error="user_id não fornecido na configuração"
            )
            return error_response.model_dump()

        # Converter memory_type se fornecido
        memory_type_enum = None
        if input_data.memory_type:
            try:
                memory_type_enum = MemoryType(input_data.memory_type)
            except ValueError:
                # Obter lista de tipos válidos do enum
                valid_types = [t.value for t in MemoryType]
                error_response = ToolErrorResponse(
                    success=False,
                    error=f"Tipo de memória '{input_data.memory_type}' é inválido. Tente novamente com um dos tipos existentes: {', '.join(valid_types)}",
                )
                return error_response.model_dump()

        logger.info(f"=== GET_MEMORY_TOOL EXECUTADA ===")
        logger.info(
            f"Parâmetros: user_id={user_id}, memory_type={input_data.memory_type}, query='{input_data.query}', limit={limit}, min_relevance={min_relevance}"
        )

        # Chamar memory manager
        result = memory_manager.get_memory(
            user_id=user_id,
            query=input_data.query,
            memory_type=memory_type_enum,
            limit=limit,
            min_relevance=min_relevance,
        )

        if result.success:
            logger.info(
                f"get_memory_tool - SUCESSO: Encontradas {len(result.memories)} memórias"
            )

            # Usar em get_memory_tool:
            memories_data = []
            for memory in result.memories:
                try:
                    memory_dict = memory.model_dump()
                    safe_memory = safe_serialize_memory(memory_dict)
                    memories_data.append(safe_memory)
                except Exception as e:
                    logger.error(f"Erro ao processar memória {memory.memory_id}: {e}")
                    continue

            success_response = GetMemoryToolOutput(
                success=True,
                memories=result.memories,
                count=len(result.memories),
                message=f"Encontradas {len(result.memories)} memórias",
            )
            return success_response.model_dump()
        else:
            logger.warning(f"get_memory_tool - FALHA: {result.error_message}")
            error_response = GetMemoryToolOutput(
                success=False,
                error=result.error_message or "Erro desconhecido ao buscar memórias",
            )
            return error_response.model_dump()

    except Exception as e:
        logger.error(f"Erro inesperado em get_memory_tool: {e}")
        error_response = GetMemoryToolOutput(
            success=False, error=f"Erro inesperado: {str(e)}"
        )
        return error_response.model_dump()


@tool
def save_memory_tool(
    content: str,
    memory_type: str,
    config: RunnableConfig = None,
) -> Dict[str, Any]:
    """
    OBRIGATÓRIO: Use esta ferramenta sempre que o usuário fornecer informações pessoais,
    preferências, objetivos, restrições ou informações críticas que devem ser lembradas.

    SITUAÇÕES DE USO OBRIGATÓRIO:
    - Usuário fornece dados pessoais: "meu nome é João", "tenho 30 anos"
    - Usuário menciona preferências: "gosto de programar", "tenho alergia a frutos do mar"
    - Usuário informa objetivos: "quero aprender Python", "não posso comer glúten"
    - Usuário compartilha informações críticas: "tenho um agendamento", "minha senha é..."
    - QUALQUER informação pessoal que o usuário compartilha deve ser salva

    Args:
        content: Conteúdo da memória a ser salva
        memory_type: Tipo de memória (user_profile, preference, goal, constraint, critical_info)
        config: Configuração injetada automaticamente pelo LangGraph

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # Validar input usando o modelo
        input_data = SaveMemoryToolInput(content=content, memory_type=memory_type)

        # Extrair parâmetros injetados da configuração
        configurable = config.get("configurable", {}) if config else {}
        user_id = configurable.get("user_id")

        if not user_id:
            error_response = ToolErrorResponse(
                success=False, error="user_id não fornecido na configuração"
            )
            return error_response.model_dump()

        # Validar memory_type
        try:
            memory_type_enum = MemoryType(input_data.memory_type)
        except ValueError:
            # Obter lista de tipos válidos do enum
            valid_types = [t.value for t in MemoryType]
            error_response = ToolErrorResponse(
                success=False,
                error=f"Tipo de memória '{input_data.memory_type}' é inválido. Tente novamente com um dos tipos existentes: {', '.join(valid_types)}",
            )
            return error_response.model_dump()

        logger.info(f"=== SAVE_MEMORY_TOOL EXECUTADA ===")
        logger.info(
            f"Parâmetros: user_id={user_id}, memory_type={input_data.memory_type}"
        )
        logger.info(
            f"Conteúdo: {input_data.content[:100]}..."
            if len(input_data.content) > 100
            else f"Conteúdo: {input_data.content}"
        )

        # Chamar memory manager
        result = memory_manager.save_memory(
            user_id=user_id,
            content=input_data.content,
            memory_type=memory_type_enum,
        )

        if result.success:
            logger.info(
                f"save_memory_tool - SUCESSO: Memória salva com ID {result.memory_id}"
            )

            success_response = SaveMemoryToolOutput(
                success=True,
                memory_id=result.memory_id,
                message="Memória salva com sucesso",
            )
            return success_response.model_dump()
        else:
            logger.warning(f"save_memory_tool - FALHA: {result.error_message}")
            error_response = SaveMemoryToolOutput(
                success=False,
                error=result.error_message or "Erro desconhecido ao salvar memória",
            )
            return error_response.model_dump()

    except Exception as e:
        logger.error(f"Erro inesperado em save_memory_tool: {e}")
        error_response = SaveMemoryToolOutput(
            success=False, error=f"Erro inesperado: {str(e)}"
        )
        return error_response.model_dump()


@tool
def update_memory_tool(
    memory_id: str,
    new_content: str,
    config: RunnableConfig = None,
) -> Dict[str, Any]:
    """
    OBRIGATÓRIO: Use esta ferramenta quando o usuário quiser atualizar ou corrigir
    informações que já foram salvas anteriormente.

    SITUAÇÕES DE USO OBRIGATÓRIO:
    - Usuário quer atualizar informações: "atualize minha idade para 31 anos"
    - Usuário pede correções: "corrija minha profissão para 'desenvolvedor'"
    - Usuário quer mudar dados: "mude minha preferência de Java para Python"
    - Usuário quer atualizar qualquer informação já salva

    IMPORTANTE: Você precisa ter o memory_id correto. Se não tiver, use get_memory_tool
    primeiro para buscar a memória e obter o ID correto.

    Args:
        memory_id: ID da memória a ser atualizada
        new_content: Novo conteúdo da memória
        config: Configuração injetada automaticamente pelo LangGraph

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # Validar input usando o modelo
        input_data = UpdateMemoryToolInput(memory_id=memory_id, new_content=new_content)

        # Extrair parâmetros injetados da configuração
        configurable = config.get("configurable", {}) if config else {}
        user_id = configurable.get("user_id")

        if not user_id:
            error_response = ToolErrorResponse(
                success=False, error="user_id não fornecido na configuração"
            )
            return error_response.model_dump()

        logger.info(f"=== UPDATE_MEMORY_TOOL EXECUTADA ===")
        logger.info(f"Parâmetros: user_id={user_id}, memory_id={input_data.memory_id}")
        logger.info(
            f"Novo conteúdo: {input_data.new_content[:100]}..."
            if len(input_data.new_content) > 100
            else f"Novo conteúdo: {input_data.new_content}"
        )

        # Chamar memory manager
        result = memory_manager.update_memory(
            user_id=user_id,
            memory_id=input_data.memory_id,
            new_content=input_data.new_content,
        )

        if result.success:
            logger.info(
                f"update_memory_tool - SUCESSO: Memória {input_data.memory_id} atualizada"
            )
            success_response = UpdateMemoryToolOutput(
                success=True, message="Memória atualizada com sucesso"
            )
            return success_response.model_dump()
        else:
            logger.warning(f"update_memory_tool - FALHA: {result.error_message}")
            error_response = UpdateMemoryToolOutput(
                success=False,
                error=result.error_message or "Erro desconhecido ao atualizar memória",
            )
            return error_response.model_dump()

    except Exception as e:
        logger.error(f"Erro inesperado em update_memory_tool: {e}")
        error_response = UpdateMemoryToolOutput(
            success=False, error=f"Erro inesperado: {str(e)}"
        )
        return error_response.model_dump()


@tool
def delete_memory_tool(
    memory_id: str,
    config: RunnableConfig = None,
) -> Dict[str, Any]:
    """
    OBRIGATÓRIO: Use esta ferramenta quando o usuário quiser remover ou deletar
    informações que foram salvas anteriormente.

    SITUAÇÕES DE USO OBRIGATÓRIO:
    - Usuário quer remover informações: "delete a informação sobre minha alergia"
    - Usuário pede para apagar dados: "remova a memória sobre minha idade antiga"
    - Usuário quer deletar informações: "apague essa informação que não é mais válida"
    - Usuário solicita deletar qualquer informação salva

    IMPORTANTE: Você precisa ter o memory_id correto. Se não tiver, use get_memory_tool
    primeiro para buscar a memória e obter o ID correto.

    Args:
        memory_id: ID da memória a ser deletada
        config: Configuração injetada automaticamente pelo LangGraph

    Returns:
        Dicionário com resultado da operação
    """
    try:
        # Validar input usando o modelo
        input_data = DeleteMemoryToolInput(memory_id=memory_id)

        # Extrair parâmetros injetados da configuração
        configurable = config.get("configurable", {}) if config else {}
        user_id = configurable.get("user_id")

        if not user_id:
            error_response = ToolErrorResponse(
                success=False, error="user_id não fornecido na configuração"
            )
            return error_response.model_dump()

        logger.info(f"=== DELETE_MEMORY_TOOL EXECUTADA ===")
        logger.info(f"Parâmetros: user_id={user_id}, memory_id={input_data.memory_id}")

        # Chamar memory manager
        result = memory_manager.delete_memory(
            user_id=user_id,
            memory_id=input_data.memory_id,
        )

        if result.success:
            logger.info(
                f"delete_memory_tool - SUCESSO: Memória {input_data.memory_id} deletada"
            )
            success_response = DeleteMemoryToolOutput(
                success=True, message="Memória deletada com sucesso"
            )
            return success_response.model_dump()
        else:
            logger.warning(f"delete_memory_tool - FALHA: {result.error_message}")
            error_response = DeleteMemoryToolOutput(
                success=False,
                error=result.error_message or "Erro desconhecido ao deletar memória",
            )
            return error_response.model_dump()

    except Exception as e:
        logger.error(f"Erro inesperado em delete_memory_tool: {e}")
        error_response = DeleteMemoryToolOutput(
            success=False, error=f"Erro inesperado: {str(e)}"
        )
        return error_response.model_dump()


# Lista de ferramentas disponíveis
mcp_tools = asyncio.run(get_mcp_tools())
TOOLS = [
    get_memory_tool,
    save_memory_tool,
    update_memory_tool,
    delete_memory_tool,
    *mcp_tools,
]
