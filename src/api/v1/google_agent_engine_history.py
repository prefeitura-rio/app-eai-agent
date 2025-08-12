from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List

from src.core.security.dependencies import validar_token
from src.utils.log import logger
from src.config import env

from langchain_postgres import PostgresSaver
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage


async def get_checkpointer() -> PostgresSaver:
    # Conexão exclusivamente via Cloud SQL
    from langchain_google_cloud_sql_pg import PostgresEngine as GCPPostgresEngine  # type: ignore

    engine = await GCPPostgresEngine.afrom_instance(
        project_id=env.PROJECT_ID,
        region=env.LOCATION,
        instance=env.INSTANCE,
        database=env.DATABASE,
        user=env.DATABASE_USER,
        password=env.DATABASE_PASSWORD,
        engine_args={"pool_pre_ping": True, "pool_recycle": 300},
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

        # "aget" retorna o último checkpoint (estado mais recente) para o thread
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