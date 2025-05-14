import typing
from letta_client.agents.messages.types.letta_streaming_response import LettaStreamingResponse


async def process_stream(response: typing.Iterator[LettaStreamingResponse]) -> str:
    """
    Processa o stream de resposta do agente Letta.
    
    Args:
        response: Stream de resposta do agente
        
    Returns:
        str: Conteúdo da mensagem do agente concatenado
    """
    agent_message_response = ''
    for chunk in response:
        if hasattr(chunk, 'content') and chunk.content:
            agent_message_response += chunk.content
    return agent_message_response
