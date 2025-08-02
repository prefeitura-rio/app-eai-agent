import os
import json
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    messages_to_dict,
)
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from src.services.lang_graph.llms import EmbeddingService, ChatModelFactory
from src.services.lang_graph.repository import MemoryRepository
from src.db.database import get_db_session
from src.services.lang_graph.tools import get_mcp_tools


# --- 1. Definição do Estado do Grafo (Minimalista) ---
class ConversationState(TypedDict):
    user_id: str
    messages: List[BaseMessage]
    final_response: dict


# --- 2. Inicialização de Serviços Globais ---
embedding_service = EmbeddingService()

# Variável global para armazenar ferramentas (evita serialização)
GLOBAL_TOOLS = []


# --- 3. Função auxiliar para executar ferramentas ---
async def execute_tool_call(tool_name: str, tool_args: dict) -> str:
    """Executa uma ferramenta específica e retorna o resultado como string"""
    global GLOBAL_TOOLS

    for tool in GLOBAL_TOOLS:
        if tool.name == tool_name:
            try:
                if hasattr(tool, "ainvoke"):
                    result = await tool.ainvoke(tool_args)
                else:
                    result = tool.invoke(tool_args)
                return str(result)
            except Exception as e:
                return f"Erro ao executar {tool_name}: {str(e)}"

    return f"Ferramenta '{tool_name}' não encontrada"


# --- 4. Nós do Grafo ---
def load_and_prepare_context_node(state: ConversationState, config: dict):
    user_id = state["user_id"]

    # Pega a mensagem original do usuário
    original_user_message = None
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            original_user_message = msg
            break

    if not original_user_message or not original_user_message.content.strip():
        raise ValueError("Mensagem do usuário não encontrada ou está vazia")

    user_prompt = original_user_message.content.strip()

    configurable = config.get("configurable", {})
    history_limit = configurable.get("history_limit", 4)
    embedding_limit = configurable.get("embedding_limit", 2)
    system_prompt = configurable.get(
        "system_prompt",
        "Você é a EAI, assistente virtual da Prefeitura do Rio de Janeiro.",
    )

    try:
        with get_db_session() as session:
            repo = MemoryRepository(session)
            query_embedding = embedding_service.get_embedding(user_prompt)
            memories = repo.get_unified_memory(
                user_id, query_embedding, history_limit, embedding_limit
            )
    except Exception as e:
        print(f"Erro ao carregar memórias: {e}")
        memories = []

    # Processa as memórias
    history_mems = sorted(
        [m for m in memories if m["type"] == "history"], key=lambda x: x["created_at"]
    )
    embedding_mems = [m for m in memories if m["type"] == "embedding"]

    # Constrói o contexto
    context_parts = []

    if embedding_mems:
        embedding_context = "\n".join(
            [
                f"- {mem.get('content_type', 'informação').capitalize()}: {mem.get('content', '')}"
                for mem in embedding_mems
                if mem.get("content")
            ]
        )
        if embedding_context:
            context_parts.append(f"## Informações contextuais\n{embedding_context}")

    if history_mems:
        history_context = "\n".join(
            [
                f"- {mem.get('content_type', 'mensagem').capitalize()}: {mem.get('content', '')}"
                for mem in history_mems
                if mem.get("content")
            ]
        )
        if history_context:
            context_parts.append(f"## Histórico recente\n{history_context}")

    # Constrói o prompt final
    if context_parts:
        context_message_content = "\n\n".join(context_parts)
        full_user_prompt = (
            f"{context_message_content}\n\n"
            f"---\n\n"
            f"Pergunta do usuário: {user_prompt}"
        )
    else:
        full_user_prompt = user_prompt

    # Constrói as mensagens
    messages = []
    if system_prompt and system_prompt.strip():
        messages.append(SystemMessage(content=system_prompt.strip()))
    messages.append(HumanMessage(content=full_user_prompt.strip()))

    state["messages"] = messages
    return state


async def call_llm_node(state: ConversationState, config: dict):
    configurable = config.get("configurable", {})
    chat_model = configurable.get("chat_model")

    if not chat_model:
        raise ValueError("Instância do ChatModel não encontrada na configuração.")

    # Filtra apenas mensagens válidas
    valid_messages = []
    for msg in state["messages"]:
        if (
            isinstance(msg, (SystemMessage, HumanMessage, AIMessage))
            and msg.content
            and msg.content.strip()
        ):
            valid_messages.append(msg)

    if not valid_messages:
        raise ValueError("Nenhuma mensagem válida encontrada")

    print(f"Enviando {len(valid_messages)} mensagens para o modelo:")
    for i, msg in enumerate(valid_messages):
        print(f"  {i+1}. {type(msg).__name__}: {msg.content[:100]}...")

    try:
        response = chat_model.invoke(valid_messages)
        state["messages"].append(response)

        # Verifica se o modelo retornou tool_calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            print(f"Modelo solicitou {len(response.tool_calls)} ferramenta(s)")

            # Executa cada ferramenta
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})
                print(f"Executando ferramenta: {tool_name} com args: {tool_args}")

                result = await execute_tool_call(tool_name, tool_args)
                tool_results.append(f"Resultado da ferramenta '{tool_name}':\n{result}")

            # Adiciona os resultados como nova mensagem
            if tool_results:
                combined_results = "\n\n".join(tool_results)
                tool_message = HumanMessage(
                    content=f"Resultados das ferramentas executadas:\n\n{combined_results}"
                )
                state["messages"].append(tool_message)

                # Chama o modelo novamente para processar os resultados
                print(
                    "Chamando modelo novamente para processar resultados das ferramentas..."
                )
                final_response = chat_model.invoke(state["messages"])
                state["messages"].append(final_response)

        return state
    except Exception as e:
        print(f"Erro ao chamar o modelo: {e}")
        import traceback

        traceback.print_exc()
        raise


def save_memory_node(state: ConversationState, config: dict):
    user_id = state["user_id"]

    try:
        # Encontra mensagens do usuário e da IA
        user_message_content = ""
        ai_message_content = ""

        # Pega a última mensagem da IA (resposta final)
        for msg in reversed(state["messages"]):
            if isinstance(msg, AIMessage):
                ai_message_content = msg.content
                break

        # Pega a pergunta original do usuário
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage) and not msg.content.startswith(
                "Resultados das ferramentas"
            ):
                content = msg.content
                if "Pergunta do usuário:" in content:
                    user_message_content = content.split("Pergunta do usuário:")[
                        -1
                    ].strip()
                else:
                    user_message_content = content
                break

        # Salva na memória
        if user_message_content.strip() and ai_message_content.strip():
            try:
                user_embedding = embedding_service.get_embedding(user_message_content)
                ai_embedding = embedding_service.get_embedding(ai_message_content)

                with get_db_session() as session:
                    repo = MemoryRepository(session)
                    repo.add_message(
                        user_id, user_message_content, "user", user_embedding
                    )
                    repo.add_message(user_id, ai_message_content, "eai", ai_embedding)

                print(
                    f"Salvou memórias - User: {user_message_content[:50]}... | AI: {ai_message_content[:50]}..."
                )
            except Exception as e:
                print(f"Erro ao salvar memórias: {e}")

        # Prepara resposta final (filtra mensagens internas)
        response_messages = []
        for msg in state["messages"]:
            if not (
                isinstance(msg, HumanMessage)
                and msg.content.startswith("Resultados das ferramentas")
            ):
                response_messages.append(msg)

        state["final_response"] = messages_to_dict(response_messages)

    except Exception as e:
        print(f"Erro no save_memory_node: {e}")
        import traceback

        traceback.print_exc()
        state["final_response"] = {"error": str(e)}

    return state


# --- 5. Construção do Grafo ---
def create_simple_graph():
    """Cria um grafo simples e linear."""
    workflow = StateGraph(ConversationState)

    # Adiciona os nós
    workflow.add_node("load_and_prepare_context", load_and_prepare_context_node)
    workflow.add_node("call_llm", call_llm_node)
    workflow.add_node("save_memory", save_memory_node)

    # Define o fluxo linear
    workflow.set_entry_point("load_and_prepare_context")
    workflow.add_edge("load_and_prepare_context", "call_llm")
    workflow.add_edge("call_llm", "save_memory")
    workflow.add_edge("save_memory", END)

    # Compila o grafo
    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)


# --- 6. Função de Invocação ---
async def run_chatbot(user_id: str, message: str, agent_config: Dict[str, Any]):
    """
    Executa o chatbot de forma simplificada para Gemini.
    """
    global GLOBAL_TOOLS

    if not user_id or not message or not message.strip():
        raise ValueError("user_id e message são obrigatórios e não podem estar vazios")

    try:
        # Carrega as ferramentas globalmente (evita serialização)
        GLOBAL_TOOLS = await get_mcp_tools()
        print(f"Carregadas {len(GLOBAL_TOOLS)} ferramentas MCP")
    except Exception as e:
        print(f"Erro ao carregar ferramentas MCP: {e}")
        GLOBAL_TOOLS = []

    try:
        # Cria a instância do modelo de chat com as ferramentas
        chat_model_instance = ChatModelFactory.create(
            provider=agent_config.get("provider", "google"),
            model_name=agent_config.get("model_name"),
            temperature=agent_config.get("temperature"),
            tools=GLOBAL_TOOLS if GLOBAL_TOOLS else None,
        )
    except Exception as e:
        print(f"Erro ao criar modelo de chat: {e}")
        raise ValueError(f"Falha ao inicializar o modelo de chat: {e}")

    # Cria o grafo simples
    app = create_simple_graph()

    config = {
        "configurable": {
            "thread_id": f"user_{user_id}",
            "chat_model": chat_model_instance,
            "system_prompt": agent_config.get(
                "system_prompt", "Você é um assistente útil."
            ),
            "history_limit": agent_config.get("history_limit", 4),
            "embedding_limit": agent_config.get("embedding_limit", 2),
        }
    }

    initial_state = {
        "user_id": user_id,
        "messages": [HumanMessage(content=message.strip())],
        "final_response": {},
    }

    try:
        # Invoca o grafo
        final_state = await app.ainvoke(initial_state, config=config)
        return final_state.get("final_response", {})
    except Exception as e:
        print(f"Erro durante a execução do chatbot: {e}")
        import traceback

        traceback.print_exc()
        return {"error": f"Erro interno: {str(e)}"}
