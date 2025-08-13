from typing import List, Optional
from datetime import datetime, timezone
import uuid
import json
import hashlib
from src.utils.md_to_wpp import markdown_to_whatsapp


def to_gateway_format(
    messages: List[dict],
    thread_id: str | None = None,
    session_timeout_seconds: Optional[int] = None,
    use_whatsapp_format: bool = True,
) -> dict:
    """
    Converte uma lista de mensagens para o formato Gateway.

    Args:
        messages: Lista de mensagens serializadas
        thread_id: ID do thread/agente (opcional)
        session_timeout_seconds: Tempo limite em segundos para nova sessão (padrão: 3600 = 1 hora)
                                Se for None, todos os session_id serão None (para uso em API)
        use_whatsapp_format: Define se deve usar o markdown_to_whatsapp (opcional)

    Returns:
        Dict no formato Gateway com status, data, mensagens e estatísticas de uso
    """
    serialized_messages: List[dict] = []
    current_step_id = f"step-{uuid.uuid4()}"

    # Mapeamento de tool_call_id para nome da ferramenta
    tool_call_to_name = {}

    # Controle de sessão - baseado na primeira mensagem de cada sessão
    current_session_id = None
    current_session_start_time = None
    last_message_timestamp = None

    def generate_deterministic_session_id(timestamp_str, thread_id=None):
        """Gera um session_id determinístico baseado no timestamp e thread_id"""
        # Usar timestamp + thread_id como base para o hash
        base_string = f"{timestamp_str}_{thread_id}"
        hash_object = hashlib.md5(base_string.encode())
        hash_hex = hash_object.hexdigest()
        # Usar os primeiros 8 caracteres para formar um ID mais curto
        return f"{hash_hex[:16]}"

    def should_create_new_session(time_since_last_message, timeout_seconds):
        """Determina se deve criar uma nova sessão baseado no tempo desde a última mensagem"""
        if time_since_last_message is None or timeout_seconds is None:
            return False

        return time_since_last_message > timeout_seconds

    def now_utc():
        return datetime.now(timezone.utc).isoformat()

    def parse_timestamp(timestamp_str):
        """Converte string de timestamp para datetime object"""
        if not timestamp_str:
            return None
        try:
            # Remove 'Z' se presente e substitui por '+00:00'
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1] + "+00:00"
            return datetime.fromisoformat(timestamp_str)
        except:
            return None

    for msg in messages:
        # Extrair dados do formato dumpd do langchain
        kwargs = msg.get("kwargs", {})
        msg_type = kwargs.get("type")
        original_id = kwargs.get("id").replace("run--", "")

        # Extrair timestamp do additional_kwargs se disponível
        additional_kwargs = kwargs.get("additional_kwargs", {})
        message_timestamp = additional_kwargs.get("timestamp", None)

        # Calcular tempo entre mensagens em segundos
        time_since_last_message = None
        if message_timestamp and last_message_timestamp:
            current_dt = parse_timestamp(message_timestamp)
            last_dt = parse_timestamp(last_message_timestamp)
            if current_dt and last_dt:
                time_since_last_message = (current_dt - last_dt).total_seconds()

        # Verificar se deve gerar session_id (só se timeout não for None)
        if session_timeout_seconds is None:
            # Para API: session_id sempre None
            current_session_id = None
        else:
            # Para histórico completo: verificar se deve criar nova sessão
            if current_session_id is None or should_create_new_session(
                time_since_last_message, session_timeout_seconds
            ):
                # Nova sessão: usar o timestamp atual como base para gerar o ID determinístico
                current_session_start_time = message_timestamp
                current_session_id = generate_deterministic_session_id(
                    current_session_start_time, thread_id
                )

        # Atualizar o último timestamp de mensagem
        if message_timestamp:
            last_message_timestamp = message_timestamp

        # Determinar metadados baseado no tipo de mensagem
        response_metadata = kwargs.get("response_metadata", {})
        usage_md = response_metadata.get("usage_metadata", {})

        if msg_type in ["human", "tool"]:
            # user_message e tool_return_message: campos null
            model_name = None
            finish_reason = None
            avg_logprobs = None
            usage_metadata = None
        else:
            # assistant_message e tool_call_message: campos com dados
            model_name = response_metadata.get("model_name", "")
            finish_reason = response_metadata.get("finish_reason", "")
            avg_logprobs = response_metadata.get("avg_logprobs")
            usage_metadata = {
                "prompt_token_count": usage_md.get("prompt_token_count", 0),
                "candidates_token_count": usage_md.get("candidates_token_count", 0),
                "total_token_count": usage_md.get("total_token_count", 0),
                "thoughts_token_count": usage_md.get("thoughts_token_count", 0),
                "cached_content_token_count": usage_md.get(
                    "cached_content_token_count", 0
                ),
            }

        if msg_type == "human":
            serialized_messages.append(
                {
                    "id": original_id or f"message-{uuid.uuid4()}",
                    "date": message_timestamp,
                    "session_id": current_session_id,
                    "time_since_last_message": time_since_last_message,
                    "name": None,
                    "message_type": "user_message",
                    "otid": str(uuid.uuid4()),
                    "sender_id": None,
                    "step_id": current_step_id,
                    "is_err": None,
                    "content": kwargs.get("content", ""),
                    "model_name": model_name,
                    "finish_reason": finish_reason,
                    "avg_logprobs": avg_logprobs,
                    "usage_metadata": usage_metadata,
                }
            )
        elif msg_type == "ai":
            content = kwargs.get("content", "")
            tool_calls = kwargs.get("tool_calls", [])
            usage_md = response_metadata.get("usage_metadata", {})
            output_details = usage_md.get("output_token_details") or {}
            reasoning_tokens = output_details.get("reasoning", 0) or 0

            if tool_calls:
                # Construir mapeamento de tool_call_id para nome da ferramenta
                for tc in tool_calls:
                    tool_call_id = tc.get("id")
                    tool_name = tc.get("name", "unknown")
                    if tool_call_id:
                        tool_call_to_name[tool_call_id] = tool_name

                if reasoning_tokens > 0:
                    serialized_messages.append(
                        {
                            "id": original_id or f"{uuid.uuid4()}",
                            "date": message_timestamp,
                            "session_id": current_session_id,
                            "time_since_last_message": time_since_last_message,
                            "name": None,
                            "message_type": "reasoning_message",
                            "otid": str(uuid.uuid4()),
                            "sender_id": None,
                            "step_id": current_step_id,
                            "is_err": None,
                            "source": "reasoner_model",
                            "reasoning": f"Processando chamada para ferramenta {tool_calls[0].get('name', 'unknown')}",
                            "signature": None,
                            "model_name": model_name,
                            "finish_reason": finish_reason,
                            "avg_logprobs": avg_logprobs,
                            "usage_metadata": usage_metadata,
                        }
                    )
                for tc in tool_calls:
                    tool_call_id = tc.get("id", str(uuid.uuid4()))

                    # Tentar parsear arguments como JSON
                    args = tc.get("args", {})
                    try:
                        if isinstance(args, str):
                            parsed_args = json.loads(args)
                        else:
                            parsed_args = args
                    except (json.JSONDecodeError, TypeError):
                        parsed_args = str(args)

                    serialized_messages.append(
                        {
                            "id": f"{tool_call_id}",
                            "date": message_timestamp,
                            "session_id": current_session_id,
                            "time_since_last_message": time_since_last_message,
                            "name": None,
                            "message_type": "tool_call_message",
                            "otid": str(uuid.uuid4()),
                            "sender_id": None,
                            "step_id": current_step_id,
                            "is_err": None,
                            "tool_call": {
                                "name": tc.get("name", "unknown"),
                                "arguments": parsed_args,
                                "tool_call_id": tool_call_id,
                            },
                            "model_name": model_name,
                            "finish_reason": finish_reason,
                            "avg_logprobs": avg_logprobs,
                            "usage_metadata": usage_metadata,
                        }
                    )
            elif content:
                if reasoning_tokens > 0:
                    serialized_messages.append(
                        {
                            "id": f"{original_id or uuid.uuid4()}",
                            "date": message_timestamp,
                            "session_id": current_session_id,
                            "time_since_last_message": time_since_last_message,
                            "name": None,
                            "message_type": "reasoning_message",
                            "otid": str(uuid.uuid4()),
                            "sender_id": None,
                            "step_id": current_step_id,
                            "is_err": None,
                            "source": "reasoner_model",
                            "reasoning": "Processando resposta para o usuário",
                            "signature": None,
                            "model_name": model_name,
                            "finish_reason": finish_reason,
                            "avg_logprobs": avg_logprobs,
                            "usage_metadata": usage_metadata,
                        }
                    )
                serialized_messages.append(
                    {
                        "id": original_id or f"{uuid.uuid4()}",
                        "date": message_timestamp,
                        "session_id": current_session_id,
                        "time_since_last_message": time_since_last_message,
                        "name": None,
                        "message_type": "assistant_message",
                        "otid": str(uuid.uuid4()),
                        "sender_id": None,
                        "step_id": current_step_id,
                        "is_err": None,
                        "content": (
                            markdown_to_whatsapp(content)
                            if use_whatsapp_format
                            else content
                        ),
                        "model_name": model_name,
                        "finish_reason": finish_reason,
                        "avg_logprobs": avg_logprobs,
                        "usage_metadata": usage_metadata,
                    }
                )
        elif msg_type == "tool":
            status = "error" if (kwargs.get("status") == "error") else "success"
            tool_call_id = kwargs.get("tool_call_id", "")

            # Usar o mapeamento para obter o nome da ferramenta, ou usar o nome direto da mensagem
            tool_name = (
                tool_call_to_name.get(tool_call_id)
                or kwargs.get("name")
                or "unknown_tool"
            )

            # Tentar parsear tool_return como JSON
            tool_content = kwargs.get("content", "")
            try:
                if isinstance(tool_content, str) and tool_content.strip().startswith(
                    ("{", "[")
                ):
                    parsed_tool_return = json.loads(tool_content)
                else:
                    parsed_tool_return = tool_content
            except (json.JSONDecodeError, TypeError):
                parsed_tool_return = tool_content

            serialized_messages.append(
                {
                    "id": original_id or f"tool-return-{tool_call_id}",
                    "date": message_timestamp,
                    "session_id": current_session_id,
                    "time_since_last_message": time_since_last_message,
                    "name": tool_name,
                    "message_type": "tool_return_message",
                    "otid": str(uuid.uuid4()),
                    "sender_id": None,
                    "step_id": current_step_id,
                    "is_err": status == "error",
                    "tool_return": parsed_tool_return,
                    "status": status,
                    "tool_call_id": tool_call_id,
                    "stdout": None,
                    "stderr": parsed_tool_return if status == "error" else None,
                    "model_name": model_name,
                    "finish_reason": finish_reason,
                    "avg_logprobs": avg_logprobs,
                    "usage_metadata": usage_metadata,
                }
            )
            current_step_id = f"step-{uuid.uuid4()}"

    # Calcular estatísticas de uso agregadas e coletar model_names
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    model_names = set()

    for msg in messages:
        kwargs = msg.get("kwargs", {})
        response_metadata = kwargs.get("response_metadata", {})
        usage_md = response_metadata.get("usage_metadata", {})

        # Mapear campos corretos do Google AI
        input_tokens += int(usage_md.get("prompt_token_count", 0) or 0)
        output_tokens += int(usage_md.get("candidates_token_count", 0) or 0)
        total_tokens += int(usage_md.get("total_token_count", 0) or 0)

        # Coletar model_names
        model_name = response_metadata.get("model_name")
        if model_name:
            model_names.add(model_name)

    serialized_messages.append(
        {
            "message_type": "usage_statistics",
            "completion_tokens": output_tokens,
            "prompt_tokens": input_tokens,
            "total_tokens": total_tokens or (input_tokens + output_tokens),
            "step_count": len(
                {m.get("step_id") for m in serialized_messages if m.get("step_id")}
            ),
            "steps_messages": None,
            "run_ids": None,
            "agent_id": thread_id,
            "processed_at": now_utc(),
            "status": "done",
            "model_names": list(model_names),
        }
    )

    return {
        "status": "completed",
        "data": {
            "messages": serialized_messages,
        },
    }
