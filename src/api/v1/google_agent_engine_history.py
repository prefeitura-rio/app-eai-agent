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
            data = {
                "type": getattr(message, "type", None),
                "content": getattr(message, "content", None),
                "additional_kwargs": getattr(message, "additional_kwargs", {}),
                "id": getattr(message, "id", None),
            }
            tool_calls = getattr(message, "tool_calls", None)
            if tool_calls is not None:
                data["tool_calls"] = tool_calls
            return data

        messages = state.get("channel_values", {}).get("messages", [])
        serialized: List[dict] = [serialize_message(msg) for msg in messages]

        return {
            "thread_id": thread_id,
            "total_messages": len(serialized),
            "messages": serialized,
        }
    except Exception as e:
        logger.exception("Erro ao recuperar histórico do Google Agent Engine")
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar histórico: {e}")