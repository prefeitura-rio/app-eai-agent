from copy import deepcopy
from typing import Dict, Any, List, Optional, TypedDict, Annotated
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

from langchain_core.tools import tool
from src.services.lang_graph.models import (
    GraphState,
    SessionConfig,
    MemoryResponse,
    ToolOutput,
    MemoryType,
)
from src.services.lang_graph.llms import llm_config
from src.services.lang_graph.tools import TOOLS
from src.services.lang_graph.memory import memory_manager

logger = logging.getLogger(__name__)


class CustomMessagesState(MessagesState):
    """Estado customizado que estende MessagesState para incluir configurações."""

    retrieved_memories: Annotated[List[MemoryResponse], "Memórias recuperadas"]
    tool_outputs: Annotated[List[ToolOutput], "Saídas das ferramentas"]
    config: Annotated[SessionConfig, "Configuração da sessão"]
    current_step: Annotated[str, "Passo atual no fluxo"]


def create_system_prompt(
    config: SessionConfig, retrieved_memories: List[MemoryResponse] = None
) -> str:
    """Cria o system prompt dinâmico baseado na configuração."""
    base_prompt = config.system_prompt

    # Adicionar descrições dos tipos de memória
    memory_types_desc = """
**Tipos de Memória Disponíveis:**
"""
    for field_name, field in config.memory_types_config.model_fields.items():
        memory_types_desc += f"* **{field_name}:** {field.default}\n"

    # Adicionar instruções das ferramentas (SEM expor parâmetros sensíveis)
    tools_instructions = """
VOCÊ TEM 4 FERRAMENTAS DE MEMÓRIA DISPONÍVEIS:
1. get_memory_tool - buscar informações do usuário
2. save_memory_tool - salvar novas informações  
3. update_memory_tool - atualizar informações existentes
4. delete_memory_tool - deletar informações

USE SEMPRE que apropriado. Não ignore informações pessoais do usuário.

**Diretrizes Importantes:**
1. **Use o Contexto da Conversa:** Você tem acesso ao histórico completo da conversa atual
2. **Combine Memórias:** Use tanto o contexto da conversa quanto as memórias de longo prazo
3. **Seja Proativo:** SEMPRE salve informações pessoais que o usuário compartilha
4. **Mantenha a Qualidade:** Atualize memórias erradas, delete irrelevantes
5. **Use Memórias Relevantes:** Utilize as memórias recuperadas para personalizar respostas
6. **OBRIGATÓRIO:** Use as ferramentas sempre que apropriado - não ignore informações importantes
7. **EFICIÊNCIA:** Faça operações únicas quando possível, evite chamadas desnecessárias
8. **SEMPRE especifique memory_type** em get_memory_tool para evitar erros
"""

    # Adicionar contexto das memórias recuperadas
    memories_context = ""
    if retrieved_memories:
        memories_context = "\n**Memórias Relevantes Recuperadas:**\n"
        for i, memory in enumerate(retrieved_memories, 1):
            relevance = (
                f" (relevância: {memory.relevance_score:.2f})"
                if memory.relevance_score
                else ""
            )
            memories_context += (
                f"{i}. **{memory.memory_type.value}:** {memory.content}{relevance}\n"
            )

    return base_prompt + memory_types_desc + tools_instructions + memories_context


def proactive_memory_retrieval(state: CustomMessagesState) -> CustomMessagesState:
    """Nó para recuperação proativa de memórias."""
    try:
        # Verificar se temos as informações necessárias
        if "config" not in state:
            logger.warning(
                "Config não encontrada no estado, pulando recuperação de memórias"
            )
            return state

        config = state["config"]

        if not config.enable_proactive_memory_retrieval:
            return state

        # Pegar a última mensagem do usuário
        messages = state.get("messages", [])
        if not messages:
            return state

        last_message = messages[-1]
        if not isinstance(last_message, HumanMessage):
            return state

        user_content = last_message.content
        if not user_content.strip():
            return state

        # Buscar memórias relevantes
        result = memory_manager.get_memory(
            user_id=config.user_id,
            query=user_content,
            limit=config.memory_limit,
            min_relevance=config.memory_min_relevance,
        )

        if result.success and result.memories:
            state["retrieved_memories"] = result.memories
            logger.info(f"Recuperadas {len(result.memories)} memórias proativamente")
        else:
            state["retrieved_memories"] = []

        return state

    except Exception as e:
        logger.error(f"Erro na recuperação proativa de memórias: {e}")
        # Garantir que retrieved_memories existe
        state["retrieved_memories"] = []
        return state


def agent_reasoning(state: CustomMessagesState) -> CustomMessagesState:
    """Nó principal do agente para raciocínio e decisão."""
    try:
        config = state.get("config")
        if not config:
            logger.error("Config não encontrada no estado")
            return state

        messages = state.get("messages", [])
        retrieved_memories = state.get("retrieved_memories", [])

        # Criar system prompt dinâmico
        system_prompt = create_system_prompt(config, retrieved_memories)
        logger.info(
            f"System prompt criado com {len(retrieved_memories)} memórias recuperadas"
        )

        # Preparar mensagens para o LLM
        langchain_messages = [SystemMessage(content=system_prompt)]

        # Adicionar histórico de mensagens (já está no formato correto)
        # O MessagesState mantém automaticamente o histórico da conversa
        langchain_messages.extend(messages)

        # Obter modelo de chat com ferramentas
        chat_model = llm_config.get_chat_model(temperature=config.temperature)

        # Configurar modelo com ferramentas
        model_with_tools = chat_model.bind_tools(TOOLS)
        logger.info(
            f"Modelo configurado com {len(TOOLS)} ferramentas e temperatura {config.temperature}"
        )

        # Executar o modelo
        response = model_with_tools.invoke(langchain_messages)
        logger.info(f"Resposta do modelo: {response.content[:100]}...")

        # Verificar se há tool calls na resposta
        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.info(f"Ferramentas chamadas: {len(response.tool_calls)}")
            for tool_call in response.tool_calls:
                logger.info(f"Ferramenta: {tool_call['name']}")
            response.content = ""

        # Adicionar resposta ao estado (MessagesState gerencia automaticamente)
        state["messages"].append(response)

        state["current_step"] = "agent_reasoning_complete"

        return state

    except Exception as e:
        logger.error(f"Erro no raciocínio do agente: {e}")
        # Adicionar mensagem de erro
        error_message = AIMessage(
            content="Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
        )
        state["messages"].append(error_message)
        return state


# ===== VERSÃO SIMPLIFICADA COM TOOLNODE =====


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


# Criar ToolNode configurado com tratamento de erros personalizado
tool_node = ToolNode(
    TOOLS,
    # handle_tool_errors="Desculpe, ocorreu um erro ao executar a ferramenta. Tente novamente com diferentes parâmetros.",
)


def tool_execution_simplified(state: CustomMessagesState) -> CustomMessagesState:
    """Versão simplificada usando ToolNode do LangGraph."""
    try:
        messages = state.get("messages", [])
        if not messages:
            logger.info("Nenhuma mensagem encontrada no estado")
            return state

        last_message = messages[-1]
        if not isinstance(last_message, AIMessage):
            logger.info("Última mensagem não é do assistente")
            return state

        # Verificar se a resposta tem tool calls
        tool_calls = getattr(last_message, "tool_calls", [])
        logger.info(f"Tool calls encontrados: {len(tool_calls)}")

        # Se não há tool calls, retornar estado inalterado
        if not tool_calls:
            logger.info("Nenhum tool call encontrado, pulando execução")
            return state

        tools_to_execute = []
        for i, tool_call in enumerate(tool_calls):
            tool_name = tool_call.get("name", "unknown")
            tool_args = tool_call.get("args", {})
            tool_id = tool_call.get("id", f"call_{i}")

            # Log com informações detalhadas (sem expor dados sensíveis)
            safe_args = {k: v for k, v in tool_args.items() if k not in ["user_id"]}
            logger.info(f"Ferramenta #{i+1}: {tool_name}")
            logger.info(f"  - ID: {tool_id}")
            logger.info(f"  - Argumentos: {safe_args}")

            tools_to_execute.append(
                {"name": tool_name, "id": tool_id, "args": safe_args}
            )

        # INJEÇÃO AUTOMÁTICA DE PARÂMETROS
        # O ToolNode vai automaticamente injetar os parâmetros via RunnableConfig
        config = state.get("config")

        # Criar RunnableConfig com os parâmetros que serão injetados
        runnable_config = {
            "configurable": {
                "user_id": config.user_id,
                "memory_limit": config.memory_limit,
                "memory_min_relevance": config.memory_min_relevance,
            }
        }

        logger.info(
            f"Executando {len(tools_to_execute)} ferramenta(s) para user_id: {config.user_id}"
        )

        # Executar ToolNode - ele cuida de tudo automaticamente!
        result = tool_node.invoke(state, config=runnable_config)

        # ToolNode retorna o estado atualizado com ToolMessages
        # Adicionar as mensagens de ferramenta ao estado
        if "messages" in result:
            tool_messages = result["messages"]
            state["messages"].extend(tool_messages)

            # Log detalhado dos resultados
            logger.info("=== RESULTADOS DAS FERRAMENTAS ===")

            # Criar ToolOutput para compatibilidade (opcional)
            tool_outputs = []
            for i, msg in enumerate(tool_messages):
                tool_name = getattr(msg, "name", f"tool_{i}")
                tool_call_id = getattr(msg, "tool_call_id", f"call_{i}")
                is_error = hasattr(msg, "status") and msg.status == "error"

                # Função para converter enums e objetos problemáticos
                def safe_serialize(obj):
                    if isinstance(obj, dict):
                        return {k: safe_serialize(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [safe_serialize(item) for item in obj]
                    elif hasattr(obj, "value"):  # É um enum
                        return obj.value
                    elif hasattr(obj, "__dict__") and not isinstance(
                        obj, (str, int, float, bool)
                    ):
                        try:
                            return str(obj)
                        except:
                            return repr(obj)
                    else:
                        return obj

                if is_error:
                    logger.error(
                        f"Ferramenta {tool_name} (ID: {tool_call_id}) - ERRO: {msg.content}"
                    )
                    tool_output = ToolOutput(
                        tool_name=tool_name, success=False, data={"error": msg.content}
                    )
                else:
                    # Log do sucesso (truncar conteúdo longo)
                    content_preview = (
                        str(msg.content)[:200] + "..."
                        if len(str(msg.content)) > 200
                        else str(msg.content)
                    )
                    logger.info(
                        f"Ferramenta {tool_name} (ID: {tool_call_id}) - SUCESSO: {content_preview}"
                    )
                    try:
                        # Tentar fazer parse do JSON se for string
                        import json

                        if isinstance(
                            msg.content, str
                        ) and msg.content.strip().startswith("{"):
                            parsed_content = json.loads(msg.content)
                            safe_content = safe_serialize(parsed_content)
                        else:
                            safe_content = safe_serialize(msg.content)
                    except:
                        safe_content = str(msg.content)

                    tool_output = ToolOutput(
                        tool_name=tool_name, success=True, data={"result": safe_content}
                    )

                tool_outputs.append(tool_output)

            # Log resumo final
            successful_tools = [t for t in tool_outputs if t.success]
            failed_tools = [t for t in tool_outputs if not t.success]

            logger.info(f"=== RESUMO DE EXECUÇÃO ===")
            logger.info(f"Total de ferramentas: {len(tool_outputs)}")
            logger.info(f"Sucessos: {len(successful_tools)}")
            logger.info(f"Falhas: {len(failed_tools)}")

            if successful_tools:
                success_names = [t.tool_name for t in successful_tools]
                logger.info(
                    f"Ferramentas executadas com sucesso: {', '.join(success_names)}"
                )

            if failed_tools:
                fail_names = [t.tool_name for t in failed_tools]
                logger.warning(f"Ferramentas que falharam: {', '.join(fail_names)}")

            state["tool_outputs"] = tool_outputs

        return state

    except Exception as e:
        logger.error(f"Erro na execução de ferramentas: {e}")
        return state

    except Exception as e:
        logger.error(f"Erro na execução de ferramentas: {e}")
        return state


def final_response(state: CustomMessagesState) -> CustomMessagesState:
    """Nó final para preparar a resposta após execução de ferramentas."""
    try:
        messages = state.get("messages", [])
        tool_outputs = state.get("tool_outputs", [])
        config = state.get("config")

        # Se não há tool outputs, não precisamos gerar nova resposta
        if not tool_outputs:
            state["current_step"] = "complete"
            return state

        # Verificar se há ToolMessages nas mensagens
        has_tool_messages = any(
            hasattr(msg, "__class__") and "ToolMessage" in str(type(msg))
            for msg in messages
        )

        if not has_tool_messages:
            state["current_step"] = "complete"
            return state

        # Criar system prompt para resposta final
        system_prompt = create_system_prompt(
            config, state.get("retrieved_memories", [])
        )

        # Preparar mensagens incluindo os resultados das ferramentas
        langchain_messages = [SystemMessage(content=system_prompt)]

        # Adicionar histórico completo de mensagens (já inclui ToolMessages)
        langchain_messages.extend(messages)

        # Obter modelo de chat
        chat_model = llm_config.get_chat_model(temperature=config.temperature)

        # Executar o modelo para gerar resposta final
        try:
            response = chat_model.invoke(langchain_messages)
            logger.info(f"Resposta final gerada: {response.content[:100]}...")

            # Adicionar resposta final ao estado
            state["messages"].append(response)
        except Exception as e:
            logger.error(f"Erro ao gerar resposta final: {e}")
            # Adicionar mensagem de erro
            error_message = AIMessage(
                content="Desculpe, ocorreu um erro ao processar a resposta final. Tente novamente."
            )
            state["messages"].append(error_message)

        state["current_step"] = "complete"

        return state

    except Exception as e:
        logger.error(f"Erro na resposta final: {e}")
        # Adicionar mensagem de erro
        error_message = AIMessage(
            content="Desculpe, ocorreu um erro ao processar a resposta final. Tente novamente."
        )
        state["messages"].append(error_message)
        return state


def should_use_tools(state: CustomMessagesState) -> str:
    """Decide se deve executar ferramentas ou ir direto para resposta final."""
    messages = state.get("messages", [])
    if not messages:
        return "final_response"

    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_execution"
    else:
        return "final_response"


def create_graph() -> StateGraph:
    """Cria o grafo LangGraph com checkpointer para memória de curto prazo."""
    try:
        # Criar o grafo usando CustomMessagesState
        workflow = StateGraph(CustomMessagesState)

        # Adicionar nós
        workflow.add_node("proactive_memory_retrieval", proactive_memory_retrieval)

        workflow.add_node("agent_reasoning", agent_reasoning)
        # Usar a versão simplificada com ToolNode
        workflow.add_node("tool_execution", tool_execution_simplified)
        workflow.add_node("final_response", final_response)

        # Adicionar arestas (fluxo com execução de ferramentas)
        workflow.add_edge(START, "proactive_memory_retrieval")
        workflow.add_edge("proactive_memory_retrieval", "agent_reasoning")
        workflow.add_conditional_edges(
            "agent_reasoning",
            should_use_tools,
            {"tool_execution": "tool_execution", "final_response": "final_response"},
        )
        workflow.add_edge("tool_execution", "agent_reasoning")

        # workflow.add_edge("agent_reasoning", "tool_execution")
        # workflow.add_edge("tool_execution", "final_response")
        workflow.add_edge("final_response", END)

        # Configurar ponto de entrada
        workflow.set_entry_point("proactive_memory_retrieval")

        # Criar checkpointer para memória de curto prazo
        checkpointer = InMemorySaver()

        return workflow.compile(checkpointer=checkpointer)

    except Exception as e:
        logger.error(f"Erro ao criar grafo: {e}")
        raise


# Instância global do grafo
graph = create_graph()
