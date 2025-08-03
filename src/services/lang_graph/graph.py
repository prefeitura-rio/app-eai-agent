from typing import Dict, Any, List, Optional, TypedDict, Annotated
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState
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
**FERRAMENTAS DISPONÍVEIS - USO OBRIGATÓRIO:**

**1. get_memory_tool - OBRIGATÓRIO usar quando:**
   - Usuário pergunta sobre si mesmo: "qual é o meu nome?", "lembra de mim?"
   - Usuário pede informações salvas: "busque minhas informações", "o que você sabe sobre mim?"
   - Você precisa personalizar resposta baseada em dados do usuário
   - Usuário menciona algo que pode estar salvo: "minha alergia", "minha profissão"
   - Qualquer pergunta sobre dados pessoais do usuário

**2. save_memory_tool - OBRIGATÓRIO usar quando:**
   - Usuário fornece informações pessoais: "meu nome é João", "tenho 30 anos"
   - Usuário menciona preferências: "gosto de programar", "tenho alergia a frutos do mar"
   - Usuário informa objetivos: "quero aprender Python", "não posso comer glúten"
   - Usuário compartilha informações críticas: "tenho um agendamento", "minha senha é..."
   - QUALQUER informação pessoal que o usuário compartilha deve ser salva

**3. update_memory_tool - OBRIGATÓRIO usar quando:**
   - Usuário quer atualizar informações: "atualize minha idade para 31 anos"
   - Usuário pede correções: "corrija minha profissão para 'desenvolvedor'"
   - Usuário quer mudar dados: "mude minha preferência de Java para Python"
   - IMPORTANTE: Use get_memory_tool primeiro para obter o memory_id correto

**4. delete_memory_tool - OBRIGATÓRIO usar quando:**
   - Usuário quer remover informações: "delete a informação sobre minha alergia"
   - Usuário pede para apagar dados: "remova a memória sobre minha idade antiga"
   - Usuário quer deletar informações: "apague essa informação que não é mais válida"
   - IMPORTANTE: Use get_memory_tool primeiro para obter o memory_id correto

**REGRAS OBRIGATÓRIAS:**
1. **SEMPRE use as ferramentas quando apropriado** - não ignore informações que devem ser salvas
2. **Para get_memory_tool:** Use sempre que precisar buscar informações do usuário
3. **Para save_memory_tool:** Use SEMPRE que o usuário compartilhar informações pessoais
4. **Para update_memory_tool:** Use quando o usuário quiser atualizar dados existentes
5. **Para delete_memory_tool:** Use quando o usuário quiser remover dados
6. **NUNCA ignore informações pessoais** - se o usuário compartilha algo sobre si, SALVE
7. **Use get_memory_tool primeiro** antes de update ou delete para obter memory_id correto

**EXEMPLOS DE USO OBRIGATÓRIO:**
- Usuário diz "meu nome é Pedro" → OBRIGATÓRIO usar save_memory_tool
- Usuário pergunta "qual é o meu nome?" → OBRIGATÓRIO usar get_memory_tool
- Usuário diz "atualize minha idade" → OBRIGATÓRIO usar get_memory_tool + update_memory_tool
- Usuário diz "delete minha alergia" → OBRIGATÓRIO usar get_memory_tool + delete_memory_tool

**TIPOS DE MEMÓRIA DISPONÍVEIS:**
- user_profile: Dados pessoais (nome, idade, profissão, etc.)
- preference: Preferências e gostos
- goal: Objetivos e metas  
- constraint: Restrições e limitações
- critical_info: Informações críticas (senhas, agendamentos, etc.)

**Diretrizes Importantes:**
1. **Use o Contexto da Conversa:** Você tem acesso ao histórico completo da conversa atual
2. **Combine Memórias:** Use tanto o contexto da conversa quanto as memórias de longo prazo
3. **Seja Proativo:** SEMPRE salve informações pessoais que o usuário compartilha
4. **Mantenha a Qualidade:** Atualize memórias erradas, delete irrelevantes
5. **Use Memórias Relevantes:** Utilize as memórias recuperadas para personalizar respostas
6. **OBRIGATÓRIO:** Use as ferramentas sempre que apropriado - não ignore informações importantes
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
            mode=config.memory_retrieval_mode,  # Usar o parâmetro da config
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


def tool_execution(state: CustomMessagesState) -> CustomMessagesState:
    """Nó para execução de ferramentas."""
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

        # Obter user_id do contexto
        config = state.get("config")
        user_id = config.user_id

        # Log para debug
        logger.info(f"Config encontrada: {config is not None}")
        if config:
            logger.info(f"User ID do config: {config.user_id}")
        logger.info(f"User ID final: {user_id}")

        # Obter parâmetros de configuração (APLICADOS AUTOMATICAMENTE)
        limit = config.memory_limit if config else 20
        min_relevance = config.memory_min_relevance if config else 0.6

        tool_outputs = state.get("tool_outputs", [])

        for tool_call in tool_calls:
            try:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})

                # APLICAR PARÂMETROS SENSÍVEIS AUTOMATICAMENTE (sem exposição ao agente)

                tool_args["user_id"] = user_id

                # Aplicar limit e min_relevance automaticamente para get_memory_tool
                if tool_name == "get_memory_tool":
                    if "limit" not in tool_args:
                        tool_args["limit"] = limit
                    if "min_relevance" not in tool_args:
                        tool_args["min_relevance"] = min_relevance

                logger.info(f"Executando ferramenta: {tool_name} com args: {tool_args}")

                # Encontrar a ferramenta correspondente
                tool_func = None
                for tool in TOOLS:
                    if tool.name == tool_name:
                        tool_func = tool
                        break

                if tool_func:
                    # Executar a ferramenta
                    result = tool_func.invoke(tool_args)

                    # Criar ToolOutput
                    tool_output = ToolOutput(
                        tool_name=tool_name,
                        success=result.get("success", False),
                        data=result,
                        error_message=(
                            result.get("error") if not result.get("success") else None
                        ),
                    )

                    tool_outputs.append(tool_output)
                    logger.info(
                        f"Ferramenta {tool_name} executada com sucesso: {result.get('success')}"
                    )
                else:
                    logger.error(f"Ferramenta {tool_name} não encontrada")

            except Exception as e:
                logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
                tool_output = ToolOutput(
                    tool_name=tool_name, success=False, data={}, error_message=str(e)
                )
                tool_outputs.append(tool_output)

        state["tool_outputs"] = tool_outputs
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

        # Pegar a última mensagem do assistente
        last_assistant_message = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                last_assistant_message = msg
                break

        if not last_assistant_message or not getattr(
            last_assistant_message, "tool_calls", []
        ):
            state["current_step"] = "complete"
            return state

        # Criar system prompt para resposta final
        system_prompt = create_system_prompt(
            config, state.get("retrieved_memories", [])
        )

        # Preparar mensagens incluindo os resultados das ferramentas
        langchain_messages = [SystemMessage(content=system_prompt)]

        # Adicionar histórico de mensagens
        langchain_messages.extend(messages)

        # Adicionar ToolMessages com os resultados das ferramentas
        from langchain_core.messages import ToolMessage

        for i, tool_output in enumerate(tool_outputs):
            if tool_output.success:
                # Encontrar o tool_call correspondente
                tool_calls = getattr(last_assistant_message, "tool_calls", [])
                if i < len(tool_calls):
                    tool_call = tool_calls[i]
                    tool_message = ToolMessage(
                        content=f"Ferramenta executada com sucesso: {tool_output.data}",
                        tool_call_id=tool_call.get("id", f"tool_call_{i}"),
                    )
                    langchain_messages.append(tool_message)

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


def create_graph() -> StateGraph:
    """Cria o grafo LangGraph com checkpointer para memória de curto prazo."""
    try:
        # Criar o grafo usando CustomMessagesState
        workflow = StateGraph(CustomMessagesState)

        # Adicionar nós
        workflow.add_node("proactive_memory_retrieval", proactive_memory_retrieval)
        workflow.add_node("agent_reasoning", agent_reasoning)
        workflow.add_node("tool_execution", tool_execution)
        workflow.add_node("final_response", final_response)

        # Adicionar arestas (fluxo com execução de ferramentas)
        workflow.add_edge("proactive_memory_retrieval", "agent_reasoning")
        workflow.add_edge("agent_reasoning", "tool_execution")
        workflow.add_edge("tool_execution", "final_response")
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
