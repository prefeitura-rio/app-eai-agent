import typing
import traceback
import asyncio
from loguru import logger
from letta_client.agents.messages.types.letta_streaming_response import (
    LettaStreamingResponse,
)
from letta_client.types.assistant_message import AssistantMessage
import src.config.env as env


async def process_stream_with_retry(response: typing.AsyncIterator[LettaStreamingResponse]) -> str:
    """
    Wrapper com retry para process_stream.
    
    Args:
        response: Stream de resposta do agente

    Returns:
        str: Conteúdo da mensagem do assistente concatenado
    """
    max_attempts = env.LETTA_STREAM_RETRY_ATTEMPTS
    base_delay = env.LETTA_STREAM_RETRY_DELAY
    
    for attempt in range(max_attempts):
        try:
            return await process_stream(response)
        except (ConnectionError, TimeoutError, ValueError) as e:
            if attempt == max_attempts - 1:  # Última tentativa
                logger.error(f"Falha definitiva após {max_attempts} tentativas: {e}")
                raise
            
            delay = base_delay * (2 ** attempt)  # Exponential backoff
            logger.warning(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente em {delay}s...")
            await asyncio.sleep(delay)
            
    return ""


async def process_stream_raw_with_retry(response: typing.AsyncIterator[LettaStreamingResponse]) -> typing.Dict[str, typing.List]:
    """
    Wrapper com retry para process_stream_raw.
    
    Args:
        response: Stream de resposta do agente

    Returns:
        dict: Dicionário contendo listas de mensagens agrupadas por tipo e uma lista ordenada por chegada
    """
    max_attempts = env.LETTA_STREAM_RETRY_ATTEMPTS
    base_delay = env.LETTA_STREAM_RETRY_DELAY
    
    for attempt in range(max_attempts):
        try:
            return await process_stream_raw(response)
        except (ConnectionError, TimeoutError, ValueError) as e:
            if attempt == max_attempts - 1:  # Última tentativa
                logger.error(f"Falha definitiva após {max_attempts} tentativas: {e}")
                raise
            
            delay = base_delay * (2 ** attempt)  # Exponential backoff
            logger.warning(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente em {delay}s...")
            await asyncio.sleep(delay)
            
    return {
        "grouped": {
            "system_messages": [],
            "user_messages": [],
            "reasoning_messages": [],
            "tool_call_messages": [],
            "tool_return_messages": [],
            "assistant_messages": [],
            "letta_usage_statistics": []
        },
        "ordered": []
    }


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
        # Timeout para o processamento do stream completo
        async def process_chunks():
            nonlocal agent_message_response
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
                    
        await asyncio.wait_for(process_chunks(), timeout=env.LETTA_STREAM_TIMEOUT)
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout de {env.LETTA_STREAM_TIMEOUT}s ao processar stream")
        raise TimeoutError(f"Stream processing timed out after {env.LETTA_STREAM_TIMEOUT} seconds")
    except ConnectionError as e:
        logger.error(f"Erro de conexão ao processar stream: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    except ValueError as e:
        logger.error(f"Erro de valor/formato ao processar stream: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao processar stream: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

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
        "letta_usage_statistics": []
    }
    ordered_messages = []
    
    try:
        # Timeout para o processamento do stream completo
        async def process_chunks():
            nonlocal result, ordered_messages
            async for chunk in response:
                if isinstance(chunk, SystemMessage):
                    result["system_messages"].append(chunk)
                    ordered_messages.append({"type": "system_message", "message": chunk})
                elif isinstance(chunk, UserMessage):
                    result["user_messages"].append(chunk)
                    ordered_messages.append({"type": "user_message", "message": chunk})
                elif isinstance(chunk, ReasoningMessage):
                    result["reasoning_messages"].append(chunk)
                    ordered_messages.append({"type": "reasoning_message", "message": chunk})
                elif isinstance(chunk, ToolCallMessage):
                    result["tool_call_messages"].append(chunk)
                    ordered_messages.append({"type": "tool_call_message", "message": chunk})
                elif isinstance(chunk, ToolReturnMessage):
                    result["tool_return_messages"].append(chunk)
                    ordered_messages.append({"type": "tool_return_message", "message": chunk})
                elif isinstance(chunk, AssistantMessage):
                    result["assistant_messages"].append(chunk)
                    ordered_messages.append({"type": "assistant_message", "message": chunk})
                elif isinstance(chunk, LettaUsageStatistics):
                    result["letta_usage_statistics"].append(chunk)
                    ordered_messages.append({"type": "letta_usage_statistics", "message": chunk})
                    
        await asyncio.wait_for(process_chunks(), timeout=env.LETTA_STREAM_TIMEOUT)
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout de {env.LETTA_STREAM_TIMEOUT}s ao processar stream raw")
        raise TimeoutError(f"Stream processing timed out after {env.LETTA_STREAM_TIMEOUT} seconds")
    except ConnectionError as e:
        logger.error(f"Erro de conexão ao processar stream raw: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    except ValueError as e:
        logger.error(f"Erro de valor/formato ao processar stream raw: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao processar stream raw: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

    return {
        "grouped": result,
        "ordered": ordered_messages
    }