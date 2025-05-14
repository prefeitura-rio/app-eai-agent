import typing
from letta_client.agents.messages.types.letta_streaming_response import LettaStreamingResponse

from src.services.letta.letta_service import letta_service


async def process_stream(response: typing.Iterator[LettaStreamingResponse]) -> str:
    """
    Processa o stream de resposta do agente Letta.
    
    Args:
        response: Stream de resposta do agente
        
    Returns:
        str: Conteúdo da mensagem do agente concatenado
    """
    agent_message_response = ''
    async for chunk in response:
        if hasattr(chunk, 'content') and chunk.content:
            agent_message_response += chunk.content
    return agent_message_response


async def send_timer_message(agent_id: str) -> str:
    """
    Envia uma mensagem de timer para o agente.
    
    Returns:
        str: Resposta do agente
    """
    client = letta_service.get_client()
        
    letta_message = {
        "role": "user",
        "content": '[EVENTO] Este é um heartbeat automático temporizado (visível apenas para você). Use este evento para enviar uma mensagem, refletir e editar suas memórias, ou não fazer nada. Cabe a você! Considere, no entanto, que esta é uma oportunidade para você pensar por si mesmo - já que seu circuito não será ativado até o próximo heartbeat automático/temporizado ou evento de mensagem recebida.'
    }
    
    try:
        response = await client.agents.messages.create_stream(agent_id, {
            "messages": [letta_message]
        })
        
        if response:
            agent_message_response = await process_stream(response)
            return agent_message_response or ""
        
        return ""
    except Exception as error:
        print(f"Erro: {error}")
        return 'Ocorreu um erro ao enviar a mensagem para o agente. Por favor, tente novamente mais tarde.'


async def send_message(agent_id: str, message_content: str, name: str = None) -> str:
    """
    Envia uma mensagem para o agente e recebe a resposta.
    
    Args:
        sender_info: Informações sobre o remetente
        message_content: Conteúdo da mensagem
        message_type: Tipo da mensagem
        
    Returns:
        str: Resposta do agente
    """
    client = letta_service.get_client()
    
    content = message_content
    
    letta_message = {
        "role": "user",
        "content": content
    }
    
    if name:
        letta_message["name"] = name
    
    try:
        response = await client.agents.messages.create_stream(agent_id, {
            "messages": [letta_message]
        })
        
        if response:
            agent_message_response = await process_stream(response)
            return agent_message_response or ""
        
        return ""
    except Exception as error:
        print(f"Erro: {error}")
        return 'Ocorreu um erro ao enviar a mensagem para o agente. Por favor, tente novamente mais tarde.'
