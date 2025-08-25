from typing import List, Dict, Optional
import asyncio

from src.utils.log import logger
from src.config import env
from src.services.agent_engine.message_formatter import to_gateway_format

from langchain_google_cloud_sql_pg import PostgresSaver, PostgresEngine, PostgresLoader
from langchain_core.runnables import RunnableConfig


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

    async def _get_single_user_history(
        self,
        user_id: str,
        session_timeout_seconds: Optional[int] = 3600,
        use_whatsapp_format: bool = True,
    ) -> tuple[str, list]:
        """Método auxiliar para processar histórico de um único usuário"""
        config = RunnableConfig(configurable={"thread_id": user_id})

        state = await self._checkpointer.aget(config=config)
        if not state:
            return user_id, []

        messages = state.get("channel_values", {}).get("messages", [])
        # logger.info(messages)

        letta_payload = to_gateway_format(
            messages=messages,
            thread_id=user_id,
            session_timeout_seconds=session_timeout_seconds,
            use_whatsapp_format=use_whatsapp_format,
        )

        return user_id, letta_payload.get("data", {}).get("messages", [])

    async def get_history_bulk(
        self,
        user_ids: List[str],
        session_timeout_seconds: Optional[int] = 3600,
        use_whatsapp_format: bool = True,
    ) -> Dict[str, list]:
        """Método otimizado com async concorrente para buscar histórico de múltiplos usuários"""
        tasks = [
            self._get_single_user_history(
                user_id=user_id,
                session_timeout_seconds=session_timeout_seconds,
                use_whatsapp_format=use_whatsapp_format,
            )
            for user_id in user_ids
        ]
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

    async def get_history_bulk_from_last_update(self, last_update: str = "2025-07-25"):
        """
        CREATE VIEW "public"."thread_ids" AS (
                    WITH tb AS (
                    SELECT
                        thread_id,
                        encode(checkpoint, 'hex') as checkpoint_hex
                    FROM "public"."checkpoints"
                    ),
                    extracted_hex AS (
                    SELECT
                        thread_id,
                        (regexp_matches(
                        checkpoint_hex,
                        '((3[0-9]){4}2d(3[0-9]){2}2d(3[0-9]){2}54(3[0-9]){2}3a(3[0-9]){2}3a(3[0-9]){2}2e(3[0-9])+(2b|2d)(3[0-9]){2}3a(3[0-9]){2})'
                        ))[1] AS timestamp_hex
                    FROM tb
                    ),
                    final_tb AS (
                    SELECT DISTINCT
                    thread_id,
                    (convert_from(decode(timestamp_hex, 'hex'), 'UTF8'))::timestamptz AS checkpoint_ts
                    FROM extracted_hex
                    WHERE timestamp_hex IS NOT NULL
                    )

                    SELECT DISTINCT ON (thread_id)
                    thread_id,
                    checkpoint_ts
                    FROM final_tb
                    ORDER BY thread_id, checkpoint_ts DESC
        );
        """

        query = f"""
            SELECT 
                thread_id,
                checkpoint_ts::text
            FROM "public"."thread_ids_2"
        """

        engine = self._checkpointer._engine
        loader = await PostgresLoader.create(engine=engine, query=query)
        docs = await loader.aload()
        logger.info(docs)
        user_ids_infos = [
            {
                "user_id": doc.page_content,
                "last_update": doc.metadata["checkpoint_ts"][:19].replace(" ", "T"),
            }
            for doc in docs
        ]
        logger.info(f"Loaded {len(user_ids_infos)} users")
        user_ids = [info["user_id"] for info in user_ids_infos]
        history_to_save = await self.get_history_bulk(
            user_ids=user_ids, session_timeout_seconds=10, use_whatsapp_format=True
        )

        return history_to_save
