import asyncio
import json
from typing import Optional
from abc import ABC, abstractmethod
from src.config import env

from google import genai
from google.genai import types

from openai import AsyncAzureOpenAI

from src.services.eai_gateway.api import (
    EAIClient,
    CreateAgentRequest,
    EAIClientError,
)
from src.evaluations.core.eval.utils import parse_reasoning_messages
from src.evaluations.core.eval.schemas import AgentResponse, ReasoningStep

from src.evaluations.core.eval.log import logger


class EAIConversationManager:
    """
    Gerencia o ciclo de vida de uma única conversa com um agente,
    garantindo que o mesmo agent_id seja usado em todas as interações.
    """

    def __init__(
        self,
        # agent_config: CreateAgentRequest,
        eai_client: EAIClient = EAIClient(),
        timeout: int = 180,
        polling_interval: int = 2,
    ):
        self.user_number: Optional[str] = None
        self.timeout = timeout
        self.polling_interval = polling_interval
        self.eai_client = eai_client
        # self.agent_config = agent_config
        # self.agent_id: Optional[str] = None

    # async def initialize(self):
    #     """
    #     Cria o agente UMA VEZ e armazena seu ID.
    #     Deve ser chamado antes de enviar qualquer mensagem.
    #     """
    #     if self.agent_id:
    #         return

    #     try:
    #         logger.info("Inicializando agente via API...")
    #         create_resp = await self.eai_client.create_agent(self.agent_config)
    #         self.agent_id = create_resp.get("agent_id")
    #         if not self.agent_id:
    #             # Se o agent_id não for retornado, mesmo com status 200.
    #             raise EAIClientError(
    #                 "Falha ao obter o agent_id na resposta da API, embora a chamada tenha sido bem-sucedida."
    #             )
    #         logger.info(f"Agente inicializado com sucesso. ID: {self.agent_id}")
    #     except EAIClientError as e:
    #         # Apenas loga e relança a exceção já contextualizada de api.py
    #         logger.error(f"Erro de cliente EAI ao inicializar o agente: {e}")
    #         raise
    #     except Exception as e:
    #         logger.error(f"Erro inesperado ao inicializar o agente: {e}", exc_info=True)
    #         # Encapsula exceções inesperadas na nossa exceção customizada para consistência
    #         raise EAIClientError(f"Erro inesperado ao inicializar o agente: {e}") from e
    async def initialize(self):
        import uuid

        if self.user_number:
            return
        self.user_number = str(uuid.uuid4())
        logger.info(f"User number inicializado com sucesso: {self.user_number}")

    async def send_message(
        self,
        message: str,
    ) -> AgentResponse:
        """
        Envia uma mensagem para o agente existente e retorna a resposta com o
        reasoning já parseado e as estatísticas de uso incluídas.
        """
        # if not self.agent_id:
        #     raise RuntimeError(
        #         "O gerenciador de conversa não foi inicializado. Chame initialize() primeiro."
        #     )

        try:
            logger.info(
                f"Enviando mensagem para o numero ({self.eai_client.provider}) {self.user_number}..."
            )
            response = await self.eai_client.send_message_and_get_response(
                # agent_id=self.agent_id,
                user_number=self.user_number,
                message=message,
            )
            logger.info(f"Resposta recebida do numero: {self.user_number}.")
            response_dict = response.model_dump(exclude_none=True)

            if "data" in response_dict and "messages" in response_dict["data"]:
                # Adiciona as estatísticas de uso à lista de mensagens para serem parseadas
                usage_stats = response_dict["data"].get("usage", {})
                usage_stats.update(
                    {
                        # "agent_id": response_dict["data"].get("agent_id"),
                        # "agent_name": self.agent_config.name,
                        "user_number": self.user_number,
                        "message_id": response_dict.get("message_id"),
                        "processed_at": response_dict["data"].get("processed_at"),
                        "message_type": "usage_statistics",  # Garante que o parser identifique o tipo
                    }
                )
                raw_messages = response_dict["data"]["messages"]
                raw_messages.append(usage_stats)

                # Parseia a lista completa de mensagens
                parsed_messages = parse_reasoning_messages(raw_messages)

                # Extrai o output da mensagem do assistente
                output_content = None
                for msg in parsed_messages:
                    if msg.get("message_type") == "assistant_message":
                        output_content = msg.get("content")
                        break
                if not output_content:
                    logger.warning(
                        "A resposta do agente não continha uma 'assistant_message'."
                    )

                # Converte a lista de dicionários para uma lista de objetos Pydantic
                reasoning_steps = [ReasoningStep(**msg) for msg in parsed_messages]
                return AgentResponse(
                    message=output_content, reasoning_trace=reasoning_steps
                )

            return AgentResponse(message=None, reasoning_trace=[])

        except EAIClientError as e:
            # Apenas loga e relança a exceção já contextualizada
            logger.error(e)
            raise
        except Exception as e:
            logger.error(
                f"Erro inesperado ao enviar mensagem para o agente: {e}", exc_info=True
            )
            # Encapsula exceções inesperadas na nossa exceção customizada
            raise EAIClientError(
                message=f"Erro inesperado na comunicação com o agente: {e}",
                agent_id=self.user_number,
            ) from e

    async def close(self):
        """
        Encerra o agente ou limpa os recursos.
        """
        logger.info(
            f"Encerrando conversa do user number ({self.eai_client.provider}): {self.user_number}."
        )
        self.user_number = None
        # No futuro, poderia chamar uma API para deletar o agente


class BaseJudgeClient(ABC):
    """
    Define a interface para um cliente de LLM que atua como juiz,
    garantindo que qualquer cliente (Azure, Gemini, etc.) tenha um método `execute`.
    """

    @abstractmethod
    async def execute(self, prompt: str) -> str:
        """
        Executa um prompt e retorna a resposta em texto.

        Args:
            prompt (str): O prompt a ser enviado para o LLM.

        Returns:
            str: A resposta do LLM.
        """
        pass


class AzureOpenAIClient(BaseJudgeClient):
    """
    Cliente para Azure OpenAI.
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


class GeminiAIClient(BaseJudgeClient):
    """
    Cliente para a API Gemini do Google.
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
    # Exemplo de uso do novo EAIConversationManager
    agent_config = CreateAgentRequest(
        model="google_ai/gemini-2.5-flash-lite-preview-06-17",
        system="voce é o batman",
        tools=["google_search"],
        user_number="evaluation_user",
        name="Evaluation Agent",
        tags=["batman"],
    )

    manager = EAIConversationManager(agent_config=agent_config)

    try:
        # Inicia a conversa (cria o agente)
        await manager.initialize()
        print(f"Agente criado com ID: {manager.agent_id}")

        # Envia a primeira mensagem
        prompt1 = "Quem é voce?"
        print(f"\nEnviando: {prompt1}")
        response1 = await manager.send_message(prompt1)
        print(json.dumps(response1.model_dump(), ensure_ascii=False, indent=2))

        # # Envia a segunda mensagem na mesma conversa
        # prompt2 = "E qual a sua missão?"
        # print(f"\nEnviando: {prompt2}")
        # response2 = await manager.send_message(prompt2)
        # print(json.dumps(response2.model_dump(), ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        # Encerra a conversa
        await manager.close()
        print("\nConversa encerrada.")


if __name__ == "__main__":
    asyncio.run(main())
