import asyncio
import json
from typing import Dict, Any, Union
from src.config import env

from google import genai
from google.genai import types

from openai import AzureOpenAI

from src.services.eai_gateway.api import (
    EAIClient,
    CreateAgentRequest,
    EAIClientError,
)


class EvaluatedLLMClient:
    """
    Classe base para clientes de LLM que serão avaliados.
    Esta classe deve ser estendida por clientes específicos de LLM.
    """

    def __init__(self, agent_config: CreateAgentRequest):
        self.agent_config = agent_config
        self.client = EAIClient()

    async def execute(
        self, message: str, timeout: int = 180, polling_interval: int = 2
    ) -> Dict[str, Any]:

        try:
            create_resp = await self.client.create_agent(self.agent_config)
            agent_id = create_resp.get("agent_id")

            if not agent_id:
                raise BaseException("Failed to create agent or retrieve agent ID.")

            response = await self.client.send_message_and_get_response(
                agent_id=agent_id,
                message=message,
                timeout=timeout,
                polling_interval=polling_interval,
            )
            response_dict = response.model_dump()

            if "data" in response_dict:
                for message in response_dict["data"]["messages"]:
                    if message.get("message_type") == "assistant_message":
                        response_dict["output"] = message.get("content")
                    else:
                        raise BaseException(
                            "Expected assistant message type in response, but found another type."
                        )

            return response_dict

        except EAIClientError as e:
            raise BaseException(f"Error communicating with EAI service: {e}")
        except asyncio.TimeoutError:
            raise BaseException("Timeout waiting for EAI response.")
        except Exception as e:
            raise BaseException(f"Internal server error: {e}")


class AzureOpenAIClient:
    """
    Cliente para Azure OpenAI, que herda de BaseLLMClient.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = AzureOpenAI(
            azure_endpoint=env.OPENAI_AZURE_URL,
            api_key=env.OPENAI_AZURE_API_KEY,
            api_version=env.OPENAI_AZURE_API_VERSION,
        )

    async def execute(
        self,
        prompt: str,
    ) -> str:
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "text"},
        )
        if completion.choices[0].message.content:
            return completion.choices[0].message.content
        else:
            raise BaseException("No text response received from Azure OpenAI.")


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
        if response.text:
            return response.text
        else:
            raise BaseException("No text response received from Gemini AI.")


async def main():
    # Exemplo de uso do cliente Azure OpenAI
    # agent_config = CreateAgentRequest(
    #     model="google_ai/gemini-2.5-flash-lite-preview-06-17",
    #     system="voce é o batman",
    #     tools=["google_search", "equipments_instructions", "equipments_by_address"],
    #     user_number="evaluation_user",
    #     name="Evaluation Agent",
    # )
    # client = EvaluatedLLMClient(agent_config=agent_config)

    # client = GeminiAIClient(model_name="gemini-2.5-flash-lite-preview-06-17")

    client = AzureOpenAIClient(model_name="gpt-4o")

    prompt = "Quem é voce?"
    # Executa a chamada ao modelo
    response = await client.execute(prompt)

    # Imprime a resposta
    print(json.dumps(response, ensure_ascii=False, indent=2))  # Formata a saída JSON


if __name__ == "__main__":
    asyncio.run(main())
