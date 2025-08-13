from typing import List, Dict
import asyncio

from src.utils.log import logger
from src.config import env
from src.utils.letta_format_messages import to_letta

from langchain_google_cloud_sql_pg import PostgresSaver, PostgresEngine
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage
from langchain_core.load.dump import dumpd


class GoogleAgentEngineHistory:
    def __init__(self, checkpointer: PostgresSaver):
        self._checkpointer = checkpointer

    @classmethod
    async def create(cls) -> "GoogleAgentEngineHistory":
        """Factory method para criar uma instância com checkpointer inicializado"""
        url = env.PG_URI
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        connect_args = {}
        if env.DB_SSL.lower() in ("false", "0", "no"):
            connect_args = {"ssl": False}

        engine = PostgresEngine.from_engine_args(
            url=url,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args=connect_args,
        )
        checkpointer = await PostgresSaver.create(engine=engine)
        logger.info("Checkpointer inicializado")
        return cls(checkpointer)

    async def get_checkpointer(self) -> PostgresSaver:
        return self._checkpointer

    def serialize_message(self, message: BaseMessage) -> dict:
        """Serializa mensagem usando dumpd do langchain para preservar todas as informações"""
        raw = dumpd(message)

        # Adicionar usage_metadata se existir no response_metadata
        response_metadata = getattr(message, "response_metadata", None)
        if response_metadata and "usage_metadata" in response_metadata:
            raw["usage_metadata"] = response_metadata["usage_metadata"]

        return raw

    def message_formatter(self, messages: List[dict], agent_id: str) -> dict:
        """Método para formatação de mensagens no formato Letta"""
        return to_letta(messages, agent_id)

    async def _get_single_user_history(self, user_id: str) -> tuple[str, list]:
        """Método auxiliar para processar histórico de um único usuário"""
        config = RunnableConfig(configurable={"thread_id": user_id})

        state = await self._checkpointer.aget(config=config)
        if not state:
            return user_id, []

        messages = state.get("channel_values", {}).get("messages", [])
        # logger.info(messages)

        serialized = [self.serialize_message(msg) for msg in messages]

        letta_payload = self.message_formatter(serialized, user_id)

        return user_id, letta_payload.get("data", {}).get("messages", [])

    async def get_history_bulk(self, user_ids: List[str]) -> Dict[str, list]:
        """Método otimizado com async concorrente para buscar histórico de múltiplos usuários"""
        tasks = [self._get_single_user_history(user_id) for user_id in user_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        result = {}
        for item in results:
            if isinstance(item, Exception):
                logger.error(f"Erro ao processar histórico: {item}")
                continue
            if isinstance(item, tuple) and len(item) == 2:
                user_id, messages = item
                result[user_id] = messages

        return result
