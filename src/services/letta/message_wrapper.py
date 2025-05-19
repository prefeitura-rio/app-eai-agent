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
    async for chunk in response:
        if isinstance(chunk, AssistantMessage) and hasattr(chunk, 'content') and chunk.content:
            agent_message_response += chunk.content
    return agent_message_response
