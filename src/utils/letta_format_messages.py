from typing import List
from datetime import datetime, timezone
import uuid
import json
from src.utils.md_to_wpp import markdown_to_whatsapp


def to_letta(messages: List[dict], thread_id: str | None = None) -> dict:
    """
    Converte uma lista de mensagens para o formato Letta.

    Args:
        messages: Lista de mensagens serializadas
        thread_id: ID do thread/agente (opcional)

    Returns:
        Dict no formato Letta com status, data, mensagens e estatísticas de uso
    """
    serialized_messages: List[dict] = []
    current_step_id = f"step-{uuid.uuid4()}"

    # Mapeamento de tool_call_id para nome da ferramenta
    tool_call_to_name = {}

    def now_utc():
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00")

    for msg in messages:
        # Extrair dados do formato dumpd do langchain
        kwargs = msg.get("kwargs", {})
        msg_type = kwargs.get("type")
        original_id = kwargs.get("id").replace("run--", "")

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
                "cached_content_token_count": usage_md.get("cached_content_token_count", 0)
            }

        if msg_type == "human":
            serialized_messages.append(
                {
                    "id": original_id or f"message-{uuid.uuid4()}",
                    "date": now_utc(),
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
                            "date": now_utc(),
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
                            "model_name": model_name,
                            "finish_reason": finish_reason,
                            "avg_logprobs": avg_logprobs,
                            "usage_metadata": usage_metadata,
                        }
                    )
                serialized_messages.append(
                    {
                        "id": original_id or f"{uuid.uuid4()}",
                        "date": now_utc(),
                        "name": None,
                        "message_type": "assistant_message",
                        "otid": str(uuid.uuid4()),
                        "sender_id": None,
                        "step_id": current_step_id,
                        "is_err": None,
                        "content": markdown_to_whatsapp(text=content),
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
                if isinstance(tool_content, str) and tool_content.strip().startswith(('{', '[')):
                    parsed_tool_return = json.loads(tool_content)
                else:
                    parsed_tool_return = tool_content
            except (json.JSONDecodeError, TypeError):
                parsed_tool_return = tool_content

            serialized_messages.append(
                {
                    "id": original_id or f"tool-return-{tool_call_id}",
                    "date": now_utc(),
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
