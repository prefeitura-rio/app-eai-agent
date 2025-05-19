import typing
import logging
import traceback
import json
from letta_client.agents.messages.types.letta_streaming_response import LettaStreamingResponse
from letta_client.types.assistant_message import AssistantMessage

# Configurar logger
logger = logging.getLogger(__name__)

async def process_stream_basic(response):
    """
    Versão simplificada de processamento de stream para diagnóstico.
    """
    logger.info("Iniciando processamento básico do stream")
    resultado = ""
    contador = 0
    
    try:
        async for chunk in response:
            contador += 1
            logger.info(f"Recebido chunk {contador}: {type(chunk)}")
            # Simplesmente converte o objeto para string para logs
            chunk_str = str(chunk)
            logger.info(f"Conteúdo do chunk: {chunk_str[:200]}")
            # Tenta extrair algum conteúdo útil
            if hasattr(chunk, 'content'):
                resultado += str(chunk.content)
            elif hasattr(chunk, 'text'):
                resultado += str(chunk.text)
        
        logger.info(f"Stream básico concluído. Processados {contador} chunks.")
        return resultado
    except Exception as e:
        logger.error(f"Erro no stream básico: {e}")
        logger.error(traceback.format_exc())
        return ""

async def process_stream(response: typing.AsyncIterator[LettaStreamingResponse]) -> str:
    """
    Processa o stream de resposta do agente Letta, filtrando apenas mensagens do assistente.
    
    Args:
        response: Stream de resposta do agente
        
    Returns:
        str: Conteúdo da mensagem do assistente concatenado
    """
    # Tenta usar a versão simplificada primeiro para diagnóstico
    try:
        logger.info("Tentando usar processamento básico para diagnóstico")
        return await process_stream_basic(response)
    except Exception as e:
        logger.error(f"Falha no processamento básico, tentando método regular: {e}")
    
    logger.info("Iniciando processamento do stream")
    agent_message_response = ''
    chunks_processados = 0
    
    try:
        logger.info("Iniciando iteração no stream")
        async for chunk in response:
            chunks_processados += 1
            logger.info(f"Processando chunk {chunks_processados}: tipo={type(chunk)}")
            
            # Verifica se é uma mensagem do assistente diretamente
            if isinstance(chunk, AssistantMessage) and hasattr(chunk, 'content') and chunk.content:
                logger.info(f"Chunk é AssistantMessage com conteúdo: {chunk.content[:100]}...")
                agent_message_response += chunk.content
            # Verifica se é um container que contém uma mensagem do assistente
            elif hasattr(chunk, 'message') and isinstance(chunk.message, AssistantMessage):
                if hasattr(chunk.message, 'content') and chunk.message.content:
                    logger.info(f"Chunk contém AssistantMessage com conteúdo: {chunk.message.content[:100]}...")
                    agent_message_response += chunk.message.content
            # Verifica se é um objeto com campo de texto
            elif hasattr(chunk, 'text') and chunk.text:
                logger.info(f"Chunk tem campo text: {chunk.text[:100]}...")
                agent_message_response += chunk.text
            # Log detalhado do objeto recebido
            logger.info(f"Atributos do chunk: {dir(chunk)}")
            if hasattr(chunk, '__dict__'):
                logger.info(f"Chunk __dict__: {chunk.__dict__}")
                
        logger.info(f"Processamento de stream concluído. Processados {chunks_processados} chunks.")
    except StopAsyncIteration:
        logger.info("StopAsyncIteration recebido - fim do stream")
    except Exception as e:
        logger.error(f"Erro ao processar stream: {e}")
        logger.error(traceback.format_exc())
    
    if agent_message_response:
        logger.info(f"Resposta final obtida: {len(agent_message_response)} caracteres")
    else:
        logger.warning("Nenhuma resposta obtida do stream")
        
    return agent_message_response
