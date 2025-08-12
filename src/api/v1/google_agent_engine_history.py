from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List

from src.core.security.dependencies import validar_token
from src.utils.log import logger
from src.config import env

from langchain_google_cloud_sql_pg import PostgresSaver, PostgresEngine
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage


async def get_checkpointer() -> PostgresSaver:
    if env.PG_URI_GOOGLE_AGENT_ENGINE:
        url = env.PG_URI_GOOGLE_AGENT_ENGINE
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        url = (
            f"postgresql+asyncpg://{env.DATABASE_USER}:{env.DATABASE_PASSWORD}"
            f"@{env.DB_HOST}:{env.DB_PORT}/{env.DATABASE}"
        )
    connect_args = {}
    if env.DB_SSL.lower() in ("false", "0", "no"):
        connect_args = {"ssl": False}

    engine = PostgresEngine.from_engine_args(
        url=url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args=connect_args,
    )
    return await PostgresSaver.create(engine=engine)


router = APIRouter(
    prefix="/google-agent-engine", tags=["Google Agent Engine History"], dependencies=[Depends(validar_token)]
)


@router.get("/history")
async def get_google_agent_engine_history(
    thread_id: str = Query(..., description="Thread ID do usuário (ex.: número/UUID)"),
):
    """
    Retorna o histórico completo de mensagens do LangGraph/LangChain para um `thread_id`.
    """
    try:
        checkpointer = await get_checkpointer()
        config = RunnableConfig(configurable={"thread_id": thread_id})

        state = await checkpointer.aget(config=config)
        if not state:
            return {"thread_id": thread_id, "total_messages": 0, "messages": []}

        def serialize_message(message: BaseMessage) -> dict:
            raw = {
                "type": getattr(message, "type", None),
                "content": getattr(message, "content", None),
                "additional_kwargs": getattr(message, "additional_kwargs", {}),
                "id": getattr(message, "id", None),
            }
            tool_calls = getattr(message, "tool_calls", None)
            if tool_calls is not None:
                raw["tool_calls"] = tool_calls
            response_metadata = getattr(message, "response_metadata", None)
            if response_metadata:
                raw["usage_metadata"] = response_metadata.get("usage_metadata") or {}
            return raw

        messages = state.get("channel_values", {}).get("messages", [])
        serialized: List[dict] = [serialize_message(msg) for msg in messages]

        from datetime import datetime, timezone
        import uuid

        def to_letta(messages: List[dict]) -> dict:
            serialized_messages: List[dict] = []
            current_step_id = f"step-{uuid.uuid4()}"

            def now_utc():
                return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00")

            for msg in messages:
                msg_type = msg.get("type")
                if msg_type == "human":
                    serialized_messages.append({
                        "id": f"message-{uuid.uuid4()}",
                        "date": now_utc(),
                        "name": None,
                        "message_type": "user_message",
                        "otid": str(uuid.uuid4()),
                        "sender_id": None,
                        "step_id": current_step_id,
                        "is_err": None,
                        "content": msg.get("content", ""),
                    })
                elif msg_type == "ai":
                    content = msg.get("content", "")
                    tool_calls = msg.get("tool_calls", [])
                    usage_md = msg.get("usage_metadata") or {}
                    output_details = usage_md.get("output_token_details") or {}
                    reasoning_tokens = output_details.get("reasoning", 0) or 0

                    if tool_calls:
                        if reasoning_tokens > 0:
                            serialized_messages.append({
                                "id": f"message-{uuid.uuid4()}",
                                "date": now_utc(),
                                "name": None,
                                "message_type": "reasoning_message",
                                "otid": str(uuid.uuid4()),
                                "sender_id": None,
                                "step_id": current_step_id,
                                "is_err": None,
                                "source": "reasoner_model",
                                "reasoning": f"Processando chamada para ferramenta {tool_calls[0].get('name', 'unknown')}",
                                "signature": None,
                            })
                        for tc in tool_calls:
                            serialized_messages.append({
                                "id": f"message-{uuid.uuid4()}",
                                "date": now_utc(),
                                "name": None,
                                "message_type": "tool_call_message",
                                "otid": str(uuid.uuid4()),
                                "sender_id": None,
                                "step_id": current_step_id,
                                "is_err": None,
                                "tool_call": {
                                    "name": tc.get("name", "unknown"),
                                    "arguments": str(tc.get("args", {})),
                                    "tool_call_id": tc.get("id", str(uuid.uuid4())),
                                },
                            })
                    elif content:
                        if reasoning_tokens > 0:
                            serialized_messages.append({
                                "id": f"message-{uuid.uuid4()}",
                                "date": now_utc(),
                                "name": None,
                                "message_type": "reasoning_message",
                                "otid": str(uuid.uuid4()),
                                "sender_id": None,
                                "step_id": current_step_id,
                                "is_err": None,
                                "source": "reasoner_model",
                                "reasoning": "Processando resposta para o usuário",
                                "signature": None,
                            })
                        serialized_messages.append({
                            "id": f"message-{uuid.uuid4()}",
                            "date": now_utc(),
                            "name": None,
                            "message_type": "assistant_message",
                            "otid": str(uuid.uuid4()),
                            "sender_id": None,
                            "step_id": current_step_id,
                            "is_err": None,
                            "content": content,
                        })
                elif msg_type == "tool":
                    status = "error" if (msg.get("status") == "error") else "success"
                    serialized_messages.append({
                        "id": f"message-{uuid.uuid4()}",
                        "date": now_utc(),
                        "name": (msg.get("name") or "unknown_tool"),
                        "message_type": "tool_return_message",
                        "otid": str(uuid.uuid4()),
                        "sender_id": None,
                        "step_id": current_step_id,
                        "is_err": status == "error",
                        "tool_return": msg.get("content", ""),
                        "status": status,
                        "tool_call_id": msg.get("tool_call_id", ""),
                        "stdout": None,
                        "stderr": msg.get("content", "") if status == "error" else None,
                    })
                    current_step_id = f"step-{uuid.uuid4()}"

            # usage agregado
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0
            for msg in messages:
                usage_md = msg.get("usage_metadata") or {}
                input_tokens += int(usage_md.get("input_tokens", 0) or 0)
                output_tokens += int(usage_md.get("output_tokens", 0) or 0)
                total_tokens += int(usage_md.get("total_tokens", 0) or 0)

            letta_usage = {
                "message_type": "usage_statistics",
                "completion_tokens": output_tokens,
                "prompt_tokens": input_tokens,
                "total_tokens": total_tokens or (input_tokens + output_tokens),
                "step_count": len({m.get("step_id") for m in serialized_messages if m.get("step_id")}),
                "steps_messages": None,
                "run_ids": None,
            }

            return {
                "status": "completed",
                "data": {
                    "messages": serialized_messages,
                    "usage": letta_usage,
                    "agent_id": thread_id,
                    "processed_at": now_utc(),
                    "status": "done",
                },
            }

        letta_payload = to_letta(serialized)
        return letta_payload
    except Exception as e:
        logger.exception("Erro ao recuperar histórico do Google Agent Engine")
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar histórico: {e}")