import json
from typing import List, Dict, Any
from src.evaluations.core.eval.md_to_wpp import markdown_to_whatsapp


def parse_reasoning_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforma a lista de mensagens brutas da API em uma estrutura limpa e padronizada.
    """
    if not messages:
        return []

    parsed_list = []
    for msg in messages:
        message_type = msg.get("message_type")
        content = None

        if message_type == "assistant_message":
            content = msg.get("content")
            # content = markdown_to_whatsapp(content)
        elif message_type == "reasoning_message":
            content = msg.get("reasoning")
        elif message_type == "tool_return_message":
            tool_return = msg.get("tool_return", "{}")

            try:
                parsed_tool_return = json.loads(tool_return)
            except (json.JSONDecodeError, TypeError):
                parsed_tool_return = tool_return
            content = {"name": msg.get("name"), "tool_return": parsed_tool_return}

        elif message_type == "tool_call_message":
            tool_call = msg.get("tool_call", {})
            # Tenta fazer o parse dos argumentos, com fallback para string
            arguments = tool_call.get("arguments", "{}")
            try:
                parsed_args = json.loads(arguments)
            except (json.JSONDecodeError, TypeError):
                parsed_args = arguments
            content = {
                "name": tool_call.get("name"),
                "arguments": parsed_args,
            }
        elif message_type == "hidden_reasoning_message":
            content = msg.get("hidden_reasoning")
        elif message_type in ["system_message", "user_message"]:
            content = msg.get("content")
        elif message_type == "usage_statistics":
            content = {
                # "agent_name": msg.get("agent_name"),
                # "agent_id": msg.get("agent_id"),
                "user_number": msg.get("user_number"),
                "message_id": msg.get("message_id"),
                "processed_at": msg.get("processed_at"),
                "total_tokens": msg.get("total_tokens"),
                "prompt_tokens": msg.get("prompt_tokens"),
                "completion_tokens": msg.get("completion_tokens"),
                "step_count": msg.get("step_count"),
                "steps_messages": msg.get("steps_messages"),
                "run_ids": msg.get("run_ids"),
            }

        # Tenta fazer o parse do conteúdo se for uma string JSON, com fallback
        if isinstance(content, str):
            try:
                # Evita que strings simples como "Paris." sejam convertidas para JSON
                if content.strip().startswith(("{", "[")):
                    content = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                pass  # Mantém como string se o parse falhar

        if message_type:
            parsed_list.append({"message_type": message_type, "content": content})

    return parsed_list
