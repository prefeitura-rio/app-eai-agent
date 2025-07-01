import typing
import traceback
import asyncio
import httpx
from loguru import logger
from letta_client.agents.messages.types.letta_streaming_response import (
    LettaStreamingResponse,
)
from letta_client.types.assistant_message import AssistantMessage
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
    except ConnectionError as e:
        logger.error(f"Erro de conexão ao processar stream: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    except TimeoutError as e:
        logger.error(f"Timeout ao processar stream: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    except ValueError as e:
        logger.error(f"Erro de valor/formato ao processar stream: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar stream: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

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
    except ConnectionError as e:
        logger.error(f"Erro de conexão ao processar stream raw: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    except TimeoutError as e:
        logger.error(f"Timeout ao processar stream raw: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    except ValueError as e:
        logger.error(f"Erro de valor/formato ao processar stream raw: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar stream raw: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

    return {
        "grouped": result,
        "ordered": ordered_messages
    }

async def process_stream_with_retry(
    response_func, max_retries: int = None, retry_delay: float = None
) -> str:
    """
    Wrapper para process_stream com retry automático em caso de timeout.
    
    Args:
        response_func: Função que retorna o stream de resposta
        max_retries: Número máximo de tentativas (default: LETTA_STREAM_RETRY_ATTEMPTS)
        retry_delay: Delay entre tentativas em segundos (default: LETTA_STREAM_RETRY_DELAY)
    
    Returns:
        str: Resposta processada do stream
    """
    if max_retries is None:
        max_retries = env.LETTA_STREAM_RETRY_ATTEMPTS
    if retry_delay is None:
        retry_delay = env.LETTA_STREAM_RETRY_DELAY
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            response = response_func()
            return await process_stream(response)
        except (httpx.ReadTimeout, TimeoutError, ConnectionError) as e:
            last_exception = e
            if attempt < max_retries:
                delay = retry_delay * (2 ** attempt)  # Backoff exponencial
                logger.warning(f"Timeout na tentativa {attempt + 1}: {type(e).__name__}: {e}. Tentando novamente em {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Todas as {max_retries + 1} tentativas falharam com timeout. Último erro: {e}")
        except Exception as e:
            last_exception = e
            # Para outros tipos de erro, não tenta novamente
            logger.error(f"Erro não relacionado a timeout na tentativa {attempt + 1}: {type(e).__name__}: {e}")
            break
    
    # Se chegou aqui, todas as tentativas falharam
    raise last_exception if last_exception else Exception("Falha desconhecida no retry")


async def process_stream_raw_with_retry(
    response_func, max_retries: int = None, retry_delay: float = None
) -> typing.Dict[str, typing.List]:
    """
    Wrapper para process_stream_raw com retry automático em caso de timeout.
    
    Args:
        response_func: Função que retorna o stream de resposta
        max_retries: Número máximo de tentativas (default: LETTA_STREAM_RETRY_ATTEMPTS)
        retry_delay: Delay entre tentativas em segundos (default: LETTA_STREAM_RETRY_DELAY)
    
    Returns:
        dict: Resposta processada do stream em formato raw
    """
    if max_retries is None:
        max_retries = env.LETTA_STREAM_RETRY_ATTEMPTS
    if retry_delay is None:
        retry_delay = env.LETTA_STREAM_RETRY_DELAY
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            response = response_func()
            return await process_stream_raw(response)
        except (httpx.ReadTimeout, TimeoutError, ConnectionError) as e:
            last_exception = e
            if attempt < max_retries:
                delay = retry_delay * (2 ** attempt)  # Backoff exponencial
                logger.warning(f"Timeout na tentativa {attempt + 1}: {type(e).__name__}: {e}. Tentando novamente em {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Todas as {max_retries + 1} tentativas falharam com timeout. Último erro: {e}")
        except Exception as e:
            last_exception = e
            # Para outros tipos de erro, não tenta novamente
            logger.error(f"Erro não relacionado a timeout na tentativa {attempt + 1}: {type(e).__name__}: {e}")
            break
    
    # Se chegou aqui, todas as tentativas falharam
    raise last_exception if last_exception else Exception("Falha desconhecida no retry")