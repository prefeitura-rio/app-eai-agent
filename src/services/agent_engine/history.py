from typing import List, Dict
from datetime import datetime, timezone
import uuid
import asyncio

from src.utils.log import logger
from src.config import env

from langchain_google_cloud_sql_pg import PostgresSaver, PostgresEngine
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage


class GoogleAgentEngineHistory:
    def __init__(self):
        self._checkpointer = None

    async def get_checkpointer(self) -> PostgresSaver:
        if self._checkpointer is None:
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
            self._checkpointer = await PostgresSaver.create(engine=engine)

        return self._checkpointer

    def serialize_message(self, message: BaseMessage) -> dict:
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

    def now_utc(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00")

    def create_base_message(self, message_type: str, step_id: str, **kwargs) -> dict:
        base = {
            "id": f"message-{uuid.uuid4()}",
            "date": self.now_utc(),
            "name": kwargs.get("name"),
            "message_type": message_type,
            "otid": str(uuid.uuid4()),
            "sender_id": None,
            "step_id": step_id,
            "is_err": kwargs.get("is_err"),
        }
        base.update(kwargs)
        return base

    def message_formatter(self, messages: List[dict], agent_id: str) -> dict:
        """Método para formatação de mensagens no formato Letta"""
        serialized_messages = []
        current_step_id = f"step-{uuid.uuid4()}"

        for msg in messages:
            msg_type = msg.get("type")

            if msg_type == "human":
                serialized_messages.append(
                    self.create_base_message(
                        "user_message", current_step_id, content=msg.get("content", "")
                    )
                )

            elif msg_type == "ai":
                ai_messages = self._process_ai_message(msg, current_step_id)
                serialized_messages.extend(ai_messages)

            elif msg_type == "tool":
                serialized_messages.append(
                    self._create_tool_return_message(msg, current_step_id)
                )
                current_step_id = f"step-{uuid.uuid4()}"

        usage_stats = self._calculate_usage_stats(messages)
        usage_stats["step_count"] = len(
            {m.get("step_id") for m in serialized_messages if m.get("step_id")}
        )
        usage_stats.update(
            {
                "steps_messages": None,
                "run_ids": None,
            }
        )

        return {
            "status": "completed",
            "data": {
                "messages": serialized_messages,
                "usage": usage_stats,
                "agent_id": agent_id,
                "processed_at": self.now_utc(),
                "status": "done",
            },
        }

    def _create_reasoning_message(self, reasoning: str, step_id: str) -> dict:
        return self.create_base_message(
            "reasoning_message",
            step_id,
            source="reasoner_model",
            reasoning=reasoning,
            signature=None,
        )

    def _create_assistant_message(self, content: str, step_id: str) -> dict:
        return self.create_base_message("assistant_message", step_id, content=content)

    def _create_tool_call_message(self, tool_call: dict, step_id: str) -> dict:
        return self.create_base_message(
            "tool_call_message",
            step_id,
            tool_call={
                "name": tool_call.get("name", "unknown"),
                "arguments": str(tool_call.get("args", {})),
                "tool_call_id": tool_call.get("id", str(uuid.uuid4())),
            },
        )

    def _create_tool_return_message(self, msg: dict, step_id: str) -> dict:
        status = "error" if (msg.get("status") == "error") else "success"
        return self.create_base_message(
            "tool_return_message",
            step_id,
            name=(msg.get("name") or "unknown_tool"),
            is_err=status == "error",
            tool_return=msg.get("content", ""),
            status=status,
            tool_call_id=msg.get("tool_call_id", ""),
            stdout=None,
            stderr=msg.get("content", "") if status == "error" else None,
        )

    def _process_ai_message(self, msg: dict, step_id: str) -> List[dict]:
        serialized_messages = []
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls", [])
        usage_md = msg.get("usage_metadata") or {}
        output_details = usage_md.get("output_token_details") or {}
        reasoning_tokens = output_details.get("reasoning", 0) or 0

        if tool_calls:
            if reasoning_tokens > 0:
                reasoning = f"Processando chamada para ferramenta {tool_calls[0].get('name', 'unknown')}"
                serialized_messages.append(
                    self._create_reasoning_message(reasoning, step_id)
                )

            for tc in tool_calls:
                serialized_messages.append(self._create_tool_call_message(tc, step_id))

        elif content:
            if reasoning_tokens > 0:
                serialized_messages.append(
                    self._create_reasoning_message(
                        "Processando resposta para o usuário", step_id
                    )
                )
            serialized_messages.append(self._create_assistant_message(content, step_id))

        return serialized_messages

    def _calculate_usage_stats(self, messages: List[dict]) -> dict:
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0

        for msg in messages:
            usage_md = msg.get("usage_metadata") or {}
            input_tokens += int(usage_md.get("input_tokens", 0) or 0)
            output_tokens += int(usage_md.get("output_tokens", 0) or 0)
            total_tokens += int(usage_md.get("total_tokens", 0) or 0)

        return {
            "message_type": "usage_statistics",
            "completion_tokens": output_tokens,
            "prompt_tokens": input_tokens,
            "total_tokens": total_tokens or (input_tokens + output_tokens),
        }

    async def get_history(self, thread_id: str) -> dict:
        checkpointer = await self.get_checkpointer()
        config = RunnableConfig(configurable={"thread_id": thread_id})

        state = await checkpointer.aget(config=config)
        if not state:
            return {"thread_id": thread_id, "total_messages": 0, "messages": []}

        messages = state.get("channel_values", {}).get("messages", [])
        serialized = [self.serialize_message(msg) for msg in messages]

        return self.message_formatter(serialized, thread_id)

    async def _get_single_user_history(self, user_id: str) -> tuple[str, list]:
        """Método auxiliar para processar histórico de um único usuário"""
        checkpointer = await self.get_checkpointer()
        config = RunnableConfig(configurable={"thread_id": user_id})

        state = await checkpointer.aget(config=config)
        if not state:
            return user_id, []

        messages = state.get("channel_values", {}).get("messages", [])
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
            user_id, messages = item
            result[user_id] = messages

        return result


# Instância global para manter compatibilidade
_history_instance = GoogleAgentEngineHistory()


async def get_checkpointer() -> PostgresSaver:
    return await _history_instance.get_checkpointer()


async def get_google_agent_engine_history(thread_id: str):
    return await _history_instance.get_history(thread_id)


async def get_google_agent_engine_history_bulk(user_ids: List[str]) -> Dict[str, list]:
    return await _history_instance.get_history_bulk(user_ids)
