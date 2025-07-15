import typing
import traceback
import asyncio
import httpx
import json
import re
from loguru import logger
from letta_client.agents.messages.types.letta_streaming_response import (
    LettaStreamingResponse,
)
from letta_client.types.assistant_message import AssistantMessage
from letta_client.core.api_error import ApiError
import src.config.env as env


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
        if "peer closed connection" in str(e) or "incomplete chunked read" in str(e):
            logger.warning(f"Conexão fechada prematuramente durante o processamento do stream: {e}")
        else:
            logger.error(f"Erro ao processar stream: {e}")

    return agent_message_response

async def process_stream_raw(response: typing.AsyncIterator[LettaStreamingResponse]) -> typing.Dict[str, typing.List]:
    """
    Processa o stream de resposta do agente Letta, organizando todos os tipos de mensagens e preservando a ordem de chegada.

    Args:
        response: Stream de resposta do agente

    Returns:
        dict: Dicionário contendo listas de mensagens agrupadas por tipo e uma lista ordenada por chegada
    """
    from letta_client.types.system_message import SystemMessage
    from letta_client.types.user_message import UserMessage
    from letta_client.types.reasoning_message import ReasoningMessage
    from letta_client.types.tool_call_message import ToolCallMessage
    from letta_client.types.tool_return_message import ToolReturnMessage
    from letta_client.types.letta_usage_statistics import LettaUsageStatistics
    
    result = {
        "system_messages": [],
        "user_messages": [],
        "reasoning_messages": [],
        "tool_call_messages": [],
        "tool_return_messages": [],
        "assistant_messages": [],
        "letta_usage_statistics": [],
        "unclassified_messages": []
    }
    ordered_messages = []
    chunk_count = 0
    
    try:
        async for chunk in response:
            chunk_count += 1
            logger.debug(f"Processando raw chunk #{chunk_count} - Tipo: {type(chunk).__name__}")
            
            chunk_processed = False
            
            # Classificação por tipo específico
            if isinstance(chunk, SystemMessage):
                result["system_messages"].append(chunk)
                ordered_messages.append({"type": "system_message", "message": chunk})
                chunk_processed = True
            elif isinstance(chunk, UserMessage):
                result["user_messages"].append(chunk)
                ordered_messages.append({"type": "user_message", "message": chunk})
                chunk_processed = True
            elif isinstance(chunk, ReasoningMessage):
                result["reasoning_messages"].append(chunk)
                ordered_messages.append({"type": "reasoning_message", "message": chunk})
                chunk_processed = True
            elif isinstance(chunk, ToolCallMessage):
                result["tool_call_messages"].append(chunk)
                ordered_messages.append({"type": "tool_call_message", "message": chunk})
                chunk_processed = True
            elif isinstance(chunk, ToolReturnMessage):
                result["tool_return_messages"].append(chunk)
                ordered_messages.append({"type": "tool_return_message", "message": chunk})
                chunk_processed = True
            elif isinstance(chunk, AssistantMessage):
                result["assistant_messages"].append(chunk)
                ordered_messages.append({"type": "assistant_message", "message": chunk})
                chunk_processed = True
            elif isinstance(chunk, LettaUsageStatistics):
                result["letta_usage_statistics"].append(chunk)
                ordered_messages.append({"type": "letta_usage_statistics", "message": chunk})
                chunk_processed = True
            
            # Classificação por atributos se não foi processado
            if not chunk_processed and hasattr(chunk, "role"):
                if str(chunk.role).lower() == "assistant":
                    result["assistant_messages"].append(chunk)
                    ordered_messages.append({"type": "assistant_message", "message": chunk})
                    chunk_processed = True
                elif str(chunk.role).lower() == "user":
                    result["user_messages"].append(chunk)
                    ordered_messages.append({"type": "user_message", "message": chunk})
                    chunk_processed = True
                elif str(chunk.role).lower() == "system":
                    result["system_messages"].append(chunk)
                    ordered_messages.append({"type": "system_message", "message": chunk})
                    chunk_processed = True
            
            # Se ainda não foi processado, adicionar como não classificado
            if not chunk_processed:
                logger.debug(f"Chunk não classificado: {type(chunk).__name__}")
                result["unclassified_messages"].append(chunk)
                ordered_messages.append({"type": "unclassified_message", "message": chunk})
                    
    except Exception as e:
        logger.error(f"Erro ao processar stream raw: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

    logger.info(f"Stream raw processado: {chunk_count} chunks -> {len(ordered_messages)} mensagens classificadas")
    return {
        "grouped": result,
        "ordered": ordered_messages
    }