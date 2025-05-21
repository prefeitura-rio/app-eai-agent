import typing
from letta_client.agents.messages.types.letta_streaming_response import (
    LettaStreamingResponse,
)
from letta_client.types.assistant_message import AssistantMessage


async def process_stream(response: typing.AsyncIterator[LettaStreamingResponse]) -> str:
    """
    Processa o stream de resposta do agente Letta, filtrando apenas mensagens do assistente.

    Args:
        response: Stream de resposta do agente

    Returns:
        str: Conteúdo da mensagem do assistente concatenado
    """
    agent_message_response = ""
    try:
        async for chunk in response:
            if (
                isinstance(chunk, AssistantMessage)
                and hasattr(chunk, "content")
                and chunk.content
            ):
                agent_message_response += chunk.content
            elif hasattr(chunk, "message") and isinstance(
                chunk.message, AssistantMessage
            ):
                if hasattr(chunk.message, "content") and chunk.message.content:
                    agent_message_response += chunk.message.content
            elif hasattr(chunk, "text") and chunk.text:
                agent_message_response += chunk.text
    except Exception as e:
        print(f"Erro ao processar stream: {e}")

    return agent_message_response

async def process_stream_raw(response: typing.AsyncIterator[LettaStreamingResponse]) -> typing.Dict[str, typing.List]:
    """
    Processa o stream de resposta do agente Letta, organizando todos os tipos de mensagens.

    Args:
        response: Stream de resposta do agente

    Returns:
        dict: Dicionário contendo listas de mensagens agrupadas por tipo
    """
    from letta_client.types.system_message import SystemMessage
    from letta_client.types.user_message import UserMessage
    from letta_client.types.reasoning_message import ReasoningMessage
    from letta_client.types.tool_call_message import ToolCallMessage
    from letta_client.types.tool_return_message import ToolReturnMessage
    from letta_client.types.letta_usage_statistics import LettaUsageStatistics
    
    # Inicializa o dicionário com uma lista vazia para cada tipo de mensagem
    result = {
        "system_messages": [],
        "user_messages": [],
        "reasoning_messages": [],
        "tool_call_messages": [],
        "tool_return_messages": [],
        "assistant_messages": [],
        "letta_usage_statistics": []
    }
    
    try:
        async for chunk in response:
            # Classifica cada chunk de acordo com seu tipo
            if isinstance(chunk, SystemMessage):
                result["system_messages"].append(chunk)
            elif isinstance(chunk, UserMessage):
                result["user_messages"].append(chunk)
            elif isinstance(chunk, ReasoningMessage):
                result["reasoning_messages"].append(chunk)
            elif isinstance(chunk, ToolCallMessage):
                result["tool_call_messages"].append(chunk)
            elif isinstance(chunk, ToolReturnMessage):
                result["tool_return_messages"].append(chunk)
            elif isinstance(chunk, AssistantMessage):
                result["assistant_messages"].append(chunk)
            elif isinstance(chunk, LettaUsageStatistics):
                result["letta_usage_statistics"].append(chunk)
    except Exception as e:
        print(f"Erro ao processar stream: {e}")

    return result