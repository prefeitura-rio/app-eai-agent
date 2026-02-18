from typing import List, Dict, Optional
import asyncio

from src.utils.log import logger
from src.config import env
from src.services.agent_engine.message_formatter import to_gateway_format

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


class GoogleAgentEngineHistory:
    def __init__(self, checkpointer: AsyncPostgresSaver):
        self._checkpointer = checkpointer

    @classmethod
    async def create(cls) -> "GoogleAgentEngineHistory":
        """Factory method para criar uma instância com checkpointer inicializado"""
        # Build connection string from PG_URI or individual env vars
        if hasattr(env, 'PG_URI') and env.PG_URI:
            conn_string = env.PG_URI
        else:
            # Fallback to building from individual components (like in the script)
            user = getattr(env, 'DATABASE_USER', 'postgres')
            password = getattr(env, 'DATABASE_PASSWORD', '')
            host = getattr(env, 'DATABASE_HOST', 'localhost')
            port = getattr(env, 'DATABASE_PORT', '5432')
            database = getattr(env, 'DATABASE', 'postgres')
            conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        # Use AsyncPostgresSaver (same as the working script)
        checkpointer = AsyncPostgresSaver.from_conn_string(conn_string)
        await checkpointer.setup()
        logger.info("AsyncPostgresSaver inicializado com sucesso")
        return cls(checkpointer)

    async def get_checkpointer(self) -> AsyncPostgresSaver:
        return self._checkpointer

    async def _get_single_user_history(
        self,
        user_id: str,
        session_timeout_seconds: Optional[int] = 3600,
        use_whatsapp_format: bool = True,
    ) -> tuple[str, list]:
        """Método auxiliar para processar histórico de um único usuário"""
        config = {"configurable": {"thread_id": user_id}}

        # Use aget_tuple (same as the working script)
        checkpoint_tuple = await self._checkpointer.aget_tuple(config)
        
        if not checkpoint_tuple:
            return user_id, []
        
        checkpoint = checkpoint_tuple.checkpoint
        messages = checkpoint.get("channel_values", {}).get("messages", [])
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
        import asyncpg

        try:
            # Build connection string
            if hasattr(env, 'PG_URI') and env.PG_URI:
                conn_string = env.PG_URI
            else:
                user = getattr(env, 'DATABASE_USER', 'postgres')
                password = getattr(env, 'DATABASE_PASSWORD', '')
                host = getattr(env, 'DATABASE_HOST', 'localhost')
                port = getattr(env, 'DATABASE_PORT', '5432')
                database = getattr(env, 'DATABASE', 'postgres')
                conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            
            query = f"""
                DELETE 
                FROM "public"."{table_id}" 
                WHERE thread_id = $1
            """
            
            conn = await asyncpg.connect(conn_string)
            try:
                result = await conn.execute(query, user_id)
                # Extract number of deleted rows from result string like "DELETE 5"
                deleted_count = int(result.split()[-1]) if result.split()[-1].isdigit() else 0
                logger.info(f"Linhas deletadas de {table_id}: {deleted_count}")
            finally:
                await conn.close()
            
            return {
                "result": "success",
                "deleted_rows": deleted_count,
            }
        except Exception as e:
            logger.error(f"Erro ao deletar histórico de {table_id}: {e}")
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
        import asyncpg

        query = """
            SELECT 
                thread_id,
                checkpoint_ts::text
            FROM "public"."thread_ids_2"
        """

        # Use direct asyncpg connection to execute the query
        if hasattr(env, 'PG_URI') and env.PG_URI:
            conn_string = env.PG_URI
        else:
            user = getattr(env, 'DATABASE_USER', 'postgres')
            password = getattr(env, 'DATABASE_PASSWORD', '')
            host = getattr(env, 'DATABASE_HOST', 'localhost')
            port = getattr(env, 'DATABASE_PORT', '5432')
            database = getattr(env, 'DATABASE', 'postgres')
            conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        conn = await asyncpg.connect(conn_string)
        try:
            rows = await conn.fetch(query)
            user_ids_infos = [
                {
                    "user_id": row["thread_id"],
                    "last_update": row["checkpoint_ts"][:19].replace(" ", "T"),
                }
                for row in rows
            ]
        finally:
            await conn.close()
        
        logger.info(f"Loaded {len(user_ids_infos)} users")
        user_ids = [info["user_id"] for info in user_ids_infos]
        history_to_save = await self.get_history_bulk(
            user_ids=user_ids, session_timeout_seconds=10, use_whatsapp_format=True
        )

        return history_to_save
