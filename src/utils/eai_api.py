import httpx
import asyncio
import time
from typing import Optional, Dict, Any, List, Callable
from src.config import env


class EaiGatewayClient:
    """
    Um cliente assíncrono em Python para interagir com a API EAí Gateway.

    Esta classe fornece métodos para criar agentes, enviar mensagens e consultar
    respostas. Inclui um método de alto nível, `send_message_and_get_response`,
    que abstrai a lógica de espera pela resposta do agente.

    Args:
        base_url (str): A URL base da API do EAí Gateway.
        token (Optional[str]): O token de autenticação, se necessário.
    """

    def __init__(self, base_url: str, token: Optional[str] = None):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=headers)

    async def close(self):
        """Fecha a sessão do cliente httpx."""
        await self.client.aclose()

    async def create_agent(
        self,
        user_number: str,
        agent_type: str = "memgpt_v2_agent",
        name: str = "",
        tags: Optional[List[str]] = ["agentic_search"],
        system: str = "You are an AI assistant...",
        memory_blocks: Optional[List[Dict[str, Any]]] = None,
        tools: Optional[List[str]] = None,
        model: str = "google_ai/gemini-2.5-flash-lite-preview-06-17",
        embedding: str = "google_ai/text-embedding-004",
        context_window_limit: int = 1_000_000,
        include_base_tool_rules: bool = True,
        include_base_tools: bool = True,
        timezone: str = "America/Sao_Paulo",
    ) -> Dict[str, Any]:
        """
        Cria um novo agente.

        Returns:
            Dict[str, Any]: A resposta da API, que deve conter o 'agent_id'.
        """
        if tags is None:
            tags = ["agentic_search"]
        if memory_blocks is None:
            memory_blocks = [
                {"label": "human", "limit": 10000, "value": ""},
                {"label": "persona", "limit": 5000, "value": ""},
            ]
        if tools is None:
            tools = ["google_search", "web_search_surkai"]

        payload = {
            "user_number": user_number,
            "agent_type": agent_type,
            "name": name,
            "tags": tags,
            "system": system,
            "memory_blocks": memory_blocks,
            "tools": tools,
            "model": model,
            "embedding": embedding,
            "context_window_limit": context_window_limit,
            "include_base_tool_rules": include_base_tool_rules,
            "include_base_tools": include_base_tools,
            "timezone": timezone,
        }

        response = await self.client.post("/api/v1/agent/create", json=payload)
        response.raise_for_status()
        return response.json()

    async def send_message_and_get_response(
        self,
        agent_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        timeout: int = 60,
        polling_interval: int = 2,
        completion_check: Optional[Callable[[Dict], bool]] = None,
    ) -> Dict[str, Any]:
        """
        Envia uma mensagem para um agente e aguarda a resposta final.

        Este método de alto nível envia a mensagem, obtém o message_id e
        realiza o polling no endpoint de resposta até que a condição de
        conclusão seja atendida ou o timeout seja atingido.

        Args:
            agent_id (str): O ID do agente.
            message (str): A mensagem a ser enviada.
            metadata (Optional[Dict[str, Any]]): Metadados da mensagem.
            timeout (int): Tempo máximo em segundos para aguardar a resposta.
            polling_interval (int): Intervalo em segundos entre as tentativas de consulta.
            completion_check (Optional[Callable[[Dict], bool]]): Uma função que recebe
                a resposta da API e retorna True se a resposta for considerada final.
                Se None, o padrão é verificar se a resposta não está vazia e se
                o status é 'completed'.

        Returns:
            Dict[str, Any]: A resposta final do agente.

        Raises:
            ValueError: Se o message_id não for retornado pela API.
            asyncio.TimeoutError: Se a resposta não for recebida dentro do timeout.
        """
        # Define a função de verificação de conclusão padrão
        if completion_check is None:
            completion_check = lambda r: r and r.get("status") == "completed"

        # 1. Enviar a mensagem inicial para obter o message_id
        send_response = await self.send_message_to_agent(agent_id, message, metadata)
        message_id = send_response.get("message_id")

        if not message_id:
            raise ValueError(
                f"Não foi possível obter um message_id. Resposta da API: {send_response}"
            )

        # 2. Iniciar o polling para obter a resposta
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            try:
                response = await self.get_message_response(message_id)
                # 3. Verificar se a resposta é a final
                if completion_check(response):
                    return response
            except httpx.HTTPStatusError as e:
                # Ignora erros 404 temporários, que podem ocorrer se a resposta ainda não estiver na fila
                if e.response.status_code != 404:
                    raise e

            await asyncio.sleep(polling_interval)

        # 4. Lançar erro de timeout se o loop terminar
        raise asyncio.TimeoutError(
            f"A resposta para a mensagem {message_id} não foi recebida em {timeout} segundos."
        )

    async def send_message_to_agent(
        self, agent_id: str, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        (Baixo Nível) Envia uma mensagem para um agente específico.

        Returns:
            Dict[str, Any]: A resposta da API, que deve conter o 'message_id'.
        """
        payload = {"agent_id": agent_id, "message": message, "metadata": metadata or {}}
        response = await self.client.post("/api/v1/message/webhook/agent", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_message_response(self, message_id: str) -> Dict[str, Any]:
        """
        (Baixo Nível) Consulta a resposta de uma mensagem enviada.
        """
        params = {"message_id": message_id}
        response = await self.client.get("/api/v1/message/response", params=params)
        response.raise_for_status()
        return response.json()


### Exemplo de Uso Simplificado
import asyncio


async def main():
    """
    Função principal para demonstrar o uso simplificado do EaiGatewayClient.
    """
    # Substitua pela URL real da sua API
    BASE_URL = env.EAI_GATEWAY_API_URL
    api_client = EaiGatewayClient(base_url=BASE_URL, token=env.EAI_GATEWAY_API_TOKEN)

    try:
        # 1. Criar o agente
        print("Criando agente...")
        create_response = await api_client.create_agent(
            user_number="test-123",
            tools=["google_search"],
        )
        agent_id = create_response.get("agent_id")

        if not agent_id:
            print(f"Falha ao criar o agente. Resposta: {create_response}")
            return

        print(f"Agente criado com sucesso! agent_id: {agent_id}")

        # 2. Enviar mensagem e aguardar a resposta
        print("\nEnviando mensagem e aguardando a resposta do agente...")

        message_to_send = (
            "Olá, qual a capital da França e qual a sua população estimada?"
        )

        # O método agora lida com a espera internamente!
        final_response = await api_client.send_message_and_get_response(
            agent_id=agent_id,
            message=message_to_send,
            timeout=30,  # Aumente se o agente demorar mais para responder
        )

        print("\nResposta final recebida:")
        import json

        print(json.dumps(final_response, indent=4, ensure_ascii=False))

    except httpx.HTTPStatusError as e:
        print(f"Ocorreu um erro de HTTP: {e.response.status_code} - {e.response.text}")
    except asyncio.TimeoutError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        await api_client.close()
        print("\nConexão com a API fechada.")


if __name__ == "__main__":
    asyncio.run(main())
