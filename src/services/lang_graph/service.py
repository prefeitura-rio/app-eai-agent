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
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from src.services.lang_graph.llms import EmbeddingService, ChatModelFactory
from src.services.lang_graph.repository import MemoryRepository
from src.db.database import get_db_session


# --- 1. Definição do Estado do Grafo ---
class ConversationState(TypedDict):
    user_id: str
    messages: List[BaseMessage]
    final_response: dict


# --- 2. Inicialização de Serviços Globais ---
embedding_service = EmbeddingService()

# --- 3. Nós do Grafo (Nodes) ---


def load_and_prepare_context_node(state: ConversationState, config: dict):
    user_id = state["user_id"]
    user_prompt = state["messages"][-1].content

    configurable = config.get("configurable", {})
    history_limit = configurable.get("history_limit", 4)
    embedding_limit = configurable.get("embedding_limit", 2)
    system_prompt = configurable.get(
        "system_prompt",
        "Você é a EAI, assistente virtual da Prefeitura do Rio de Janeiro.",
    )

    with get_db_session() as session:
        repo = MemoryRepository(session)
        query_embedding = embedding_service.get_embedding(user_prompt)
        memories = repo.get_unified_memory(
            user_id, query_embedding, history_limit, embedding_limit
        )

    history_mems = sorted(
        [m for m in memories if m["type"] == "history"], key=lambda x: x["created_at"]
    )
    embedding_mems = [m for m in memories if m["type"] == "embedding"]

    embedding_context = "\n".join(
        [
            f"{i+1}. {mem['content_type'].capitalize()}: {mem['content']}"
            for i, mem in enumerate(embedding_mems)
        ]
    )
    history_context = "\n".join(
        [
            f"{i+1}. {mem['content_type'].capitalize()}: {mem['content']}\n{i+1}. Eai: {mem['content']}"
            for i, mem in enumerate(history_mems)
        ]
    )

    context_message_content = f"## Informacoes contextuais\n{embedding_context}\n\n## Historico das ultimas {len(history_mems)} menssagens:\n{history_context}"

    system_message = SystemMessage(content=system_prompt)
    context_message = HumanMessage(content=context_message_content, name="context")
    user_message = HumanMessage(
        content=f"Com base nas informacoes contextuais e no historico responda a pergunta do usuario:\n\n{user_prompt}",
        name="user",
    )

    state["messages"] = [system_message, context_message, user_message]
    return state


def call_llm_node(state: ConversationState, config: dict):
    configurable = config.get("configurable", {})
    chat_model = configurable.get("chat_model")
    if not chat_model:
        raise ValueError("Instância do ChatModel não encontrada na configuração.")

    response = chat_model.invoke(state["messages"])
    state["messages"].append(response)
    return state


def save_memory_node(state: ConversationState, config: dict):
    user_id = state["user_id"]
    configurable = config.get("configurable", {})
    system_prompt = configurable.get(
        "system_prompt",
        "Você é a EAI, assistente virtual da Prefeitura do Rio de Janeiro.",
    )

    user_message_content = next(
        (
            m.content
            for m in state["messages"]
            if isinstance(m, HumanMessage) and m.name == "user"
        ),
        "",
    ).split("\n\n")[-1]
    eai_message = state["messages"][-1]
    eai_message_content = eai_message.content

    user_embedding = embedding_service.get_embedding(user_message_content)
    eai_embedding = embedding_service.get_embedding(eai_message_content)

    eai_message_raw = messages_to_dict([eai_message])

    with get_db_session() as session:
        repo = MemoryRepository(session)
        repo.add_message(user_id, user_message_content, "user", user_embedding)
        repo.add_message(
            user_id,
            eai_message_content,
            "eai",
            eai_embedding,
            content_raw=eai_message_raw[0],
        )

    system_msg_dict = {"type": "system", "data": {"content": system_prompt}}
    context_msg_dict = {
        "type": "context",
        "data": {
            "content": next(
                m.content
                for m in state["messages"]
                if isinstance(m, HumanMessage) and m.name == "context"
            )
        },
    }
    eai_msg_dict = {"type": "ai", "data": messages_to_dict([eai_message])[0]["data"]}

    state["final_response"] = [system_msg_dict, context_msg_dict, eai_msg_dict]
    return state


# --- 4. Construção do Grafo ---
workflow = StateGraph(ConversationState)
workflow.add_node("load_and_prepare_context", load_and_prepare_context_node)
workflow.add_node("call_llm", call_llm_node)
workflow.add_node("save_memory", save_memory_node)
workflow.set_entry_point("load_and_prepare_context")
workflow.add_edge("load_and_prepare_context", "call_llm")
workflow.add_edge("call_llm", "save_memory")
workflow.add_edge("save_memory", END)

# --- 5. Compilação do Grafo ---
memory = InMemorySaver()
app = workflow.compile(checkpointer=memory)


# --- 6. Função de Invocação ---
def run_chatbot(user_id: str, message: str, agent_config: Dict[str, Any]):
    chat_model_instance = ChatModelFactory.create(
        provider=agent_config.get("provider", "google"),
        model_name=agent_config.get("model_name"),
        temperature=agent_config.get("temperature"),
    )

    config = {
        "configurable": {
            "thread_id": f"user_{user_id}",
            "chat_model": chat_model_instance,
            "system_prompt": agent_config.get("system_prompt"),
            "history_limit": agent_config.get("history_limit"),
            "embedding_limit": agent_config.get("embedding_limit"),
        }
    }

    initial_state = {
        "user_id": user_id,
        "messages": [HumanMessage(content=message)],
        "final_response": {},
    }

    final_state = app.invoke(initial_state, config=config)
    return final_state.get("final_response", {})
