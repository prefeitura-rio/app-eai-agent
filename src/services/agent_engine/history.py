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
        checkpointer = await PostgresSaver.create(engine=engine, use_jsonb=True)
        logger.info("Checkpointer inicializado com suporte a JSONB")
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

    async def _delete_user_history(self, user_id: str, table_id: str = "checkpoints"):
        """Deleta o histórico de um usuário específico"""
        from sqlalchemy import text

        # Definir a função que será executada com a conexão
        async def execute_delete():
            query = f"""
                DELETE 
                FROM "public"."{table_id}" 
                WHERE thread_id = '{user_id}'
            """
            query_line = " ".join([line.strip() for line in query.split("\n")])
            pool = self._checkpointer._engine._pool
            async with pool.connect() as conn:
                result = await conn.execute(text(query_line))
                await conn.commit()
                deleted_count = result.rowcount
                logger.info(f"Linhas deletadas: {deleted_count}")
            return deleted_count

        try:
            # Criar uma coroutine wrapper que chama a função
            coro = execute_delete()
            deleted_count = await self._checkpointer._engine._run_as_async(coro)
            return {
                "result": "success",
                "deleted_rows": deleted_count,
            }
        except Exception as e:
            return {
                "result": "error",
                "error": str(e),
            }

    async def delete_user_history(self, user_id: str):
        """Interface pública para deletar histórico de um usuário específico de ambas as tabelas"""
        import asyncio

        # Executa ambas as operações em paralelo
        results = await asyncio.gather(
            self._delete_user_history(user_id=user_id, table_id="checkpoints"),
            self._delete_user_history(user_id=user_id, table_id="checkpoints_writes"),
            return_exceptions=True,
        )

        checkpoints_result, checkpoints_writes_result = results

        # Estruturar o retorno de forma mais clara
        return {
            "thread_id": user_id,
            "overall_result": (
                "success"
                if all(
                    isinstance(r, dict) and r.get("result") == "success"
                    for r in results
                )
                else "partial_failure"
            ),
            "tables": {
                "checkpoints": checkpoints_result,
                "checkpoints_writes": checkpoints_writes_result,
            },
        }

    async def get_history_bulk_from_last_update(self, last_update: str = "2025-07-25"):
        """
        CREATE VIEW "public"."thread_ids" AS (
            SELECT DISTINCT ON (thread_id)
                thread_id,
                (checkpoint->>'ts')::timestamptz AS checkpoint_ts
            FROM "public"."checkpoints"
            WHERE checkpoint->>'ts' IS NOT NULL
            ORDER BY thread_id, (checkpoint->>'ts')::timestamptz DESC
        );
        
        Note: This view now works with JSONB checkpoint column.
        It extracts the 'ts' field from the checkpoint JSONB object.
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
