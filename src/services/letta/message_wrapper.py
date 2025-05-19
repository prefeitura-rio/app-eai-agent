import typing
from letta_client.agents.messages.types.letta_streaming_response import LettaStreamingResponse
from letta_client.types.assistant_message import AssistantMessage


async def process_stream(response: typing.AsyncIterator[LettaStreamingResponse]) -> str:
    """
    Processa o stream de resposta do agente Letta, filtrando apenas mensagens do assistente.
    
    Args:
        response: Stream de resposta do agente
        
    Returns:
        str: Conteúdo da mensagem do assistente concatenado
    """
    agent_message_response = ''
    try:
        async for chunk in response:
            # Verifica se é uma mensagem do assistente diretamente
            if isinstance(chunk, AssistantMessage) and hasattr(chunk, 'content') and chunk.content:
                agent_message_response += chunk.content
            # Verifica se é um container que contém uma mensagem do assistente
            elif hasattr(chunk, 'message') and isinstance(chunk.message, AssistantMessage):
                if hasattr(chunk.message, 'content') and chunk.message.content:
                    agent_message_response += chunk.message.content
            # Verifica se é um objeto com campo de texto
            elif hasattr(chunk, 'text') and chunk.text:
                agent_message_response += chunk.text
            # Debug - pode ser removido depois
            elif hasattr(chunk, '__dict__'):
                print(f"Chunk recebido: {chunk.__dict__}")
    except Exception as e:
        print(f"Erro ao processar stream: {e}")
    
    return agent_message_response
