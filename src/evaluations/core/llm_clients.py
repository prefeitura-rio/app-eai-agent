import asyncio
import json
from typing import Dict, Any, Union
from src.config import env

from google import genai
from google.genai import types

from openai import AsyncAzureOpenAI

from src.services.eai_gateway.api import (
    EAIClient,
    CreateAgentRequest,
    EAIClientError,
)
from src.evaluations.core.utils import parse_reasoning_messages

from src.utils.log import logger


class AgentConversationManager:
    """
    Gerencia o ciclo de vida de uma única conversa com um agente,
    garantindo que o mesmo agent_id seja usado em todas as interações.
    """

    def __init__(self, agent_config: CreateAgentRequest):
        self.agent_config = agent_config
        self.client = EAIClient()
        self.agent_id: str | None = None

    async def initialize(self):
        """
        Cria o agente UMA VEZ e armazena seu ID.
        Deve ser chamado antes de enviar qualquer mensagem.
        """
        if self.agent_id:
            return

        try:
            logger.info("Inicializando agente via API...")
            create_resp = await self.client.create_agent(self.agent_config)
            self.agent_id = create_resp.get("agent_id")
            if not self.agent_id:
                logger.error("Falha ao obter o agent_id na resposta da API.")
                raise ConnectionError("Falha ao criar o agente ou obter o agent_id.")
            logger.info(f"Agente inicializado com sucesso. ID: {self.agent_id}")
        except EAIClientError as e:
            logger.error(f"Erro de cliente EAI ao inicializar o agente: {e}")
            raise ConnectionError(f"Erro ao inicializar o agente: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado ao inicializar o agente: {e}", exc_info=True)
            raise

    async def send_message(
        self, message: str, timeout: int = 180, polling_interval: int = 2
    ) -> Dict[str, Any]:
        """
        Envia uma mensagem para o agente existente e retorna a resposta com o
        reasoning já parseado.
        """
        if not self.agent_id:
            raise RuntimeError(
                "O gerenciador de conversa não foi inicializado. Chame initialize() primeiro."
            )

        try:
            logger.info(f"Enviando mensagem para o agente {self.agent_id}...")
            response = await self.client.send_message_and_get_response(
                agent_id=self.agent_id,
                message=message,
                timeout=timeout,
                polling_interval=polling_interval,
            )

            logger.info(f"Resposta recebida do agente {self.agent_id}.")
            response_dict = response.model_dump(exclude_none=True)

            if "data" in response_dict and "messages" in response_dict["data"]:
                # Transforma a lista de mensagens brutas na estrutura limpa
                raw_messages = response_dict["data"]["messages"]
                response_dict["data"]["messages"] = parse_reasoning_messages(
                    raw_messages
                )

                # Extrai o 'output' para conveniência, mantendo a resposta completa
                for msg in response_dict["data"]["messages"]:
                    if msg.get("message_type") == "assistant_message":
                        response_dict["data"]["output"] = msg.get("content")
                        break

                if "output" not in response_dict["data"]:
                    logger.warning(
                        "A resposta do agente não continha uma 'assistant_message'."
                    )

            return response_dict.get("data", {})

        except EAIClientError as e:
            logger.error(
                f"Erro de cliente EAI ao comunicar com o agente {self.agent_id}: {e}"
            )
            raise ConnectionError(f"Error communicating with EAI service: {e}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout esperando pela resposta do agente {self.agent_id}.")
            raise ConnectionError("Timeout waiting for EAI response.")
        except Exception as e:
            logger.error(
                f"Erro inesperado ao enviar mensagem para o agente: {e}", exc_info=True
            )
            raise

    async def close(self):
        """
        Encerra o agente ou limpa os recursos.
        """
        logger.info(f"Encerrando conversa com o agente {self.agent_id}.")
        self.agent_id = None
        # No futuro, poderia chamar uma API para deletar o agente


class AzureOpenAIClient:
    """
    Cliente para Azure OpenAI, que herda de BaseLLMClient.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = AsyncAzureOpenAI(
            azure_endpoint=env.OPENAI_AZURE_URL,
            api_key=env.OPENAI_AZURE_API_KEY,
            api_version=env.OPENAI_AZURE_API_VERSION,
        )

    async def execute(
        self,
        prompt: str,
    ) -> str:
        logger.info(f"Executando prompt do juiz com o modelo {self.model_name}...")
        try:
            completion = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "text"},
            )
            logger.info("Resposta do juiz recebida com sucesso.")
            if completion.choices[0].message.content:
                return completion.choices[0].message.content
            else:
                logger.error("Resposta do juiz (Azure OpenAI) está vazia.")
                raise BaseException("No text response received from Azure OpenAI.")
        except Exception as e:
            logger.error(
                f"Erro ao executar o prompt do juiz (Azure OpenAI): {e}", exc_info=True
            )
            raise


class GeminiAIClient:
    """
    Cliente para Azure OpenAI, que herda de BaseLLMClient.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = genai.Client(
            api_key=env.GEMINI_API_KEY,
        )

    async def execute(
        self,
        prompt: str,
    ) -> str:
        logger.info(f"Executando prompt do juiz com o modelo {self.model_name}...")
        try:
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=-1,
                ),
            )
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
                config=generate_content_config,
            )
            logger.info("Resposta do juiz recebida com sucesso.")
            if response.text:
                return response.text
            else:
                logger.error("Resposta do juiz (Gemini AI) está vazia.")
                raise BaseException("No text response received from Gemini AI.")
        except Exception as e:
            logger.error(
                f"Erro ao executar o prompt do juiz (Gemini AI): {e}", exc_info=True
            )
            raise


async def main():
    # Exemplo de uso do novo AgentConversationManager
    agent_config = CreateAgentRequest(
        model="google_ai/gemini-2.5-flash-lite-preview-06-17",
        system="voce é o batman",
        tools=["google_search"],
        user_number="evaluation_user",
        name="Evaluation Agent",
        tags=["batman"],
    )

    manager = AgentConversationManager(agent_config=agent_config)

    try:
        # Inicia a conversa (cria o agente)
        await manager.initialize()
        print(f"Agente criado com ID: {manager.agent_id}")

        # Envia a primeira mensagem
        prompt1 = "Quem é voce?"
        print(f"\nEnviando: {prompt1}")
        response1 = await manager.send_message(prompt1)
        print(json.dumps(response1, ensure_ascii=False, indent=2))

        # Envia a segunda mensagem na mesma conversa
        prompt2 = "E qual a sua missão?"
        print(f"\nEnviando: {prompt2}")
        response2 = await manager.send_message(prompt2)
        print(json.dumps(response2, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        # Encerra a conversa
        await manager.close()
        print("\nConversa encerrada.")


if __name__ == "__main__":
    asyncio.run(main())
