import os
import re
import pandas as pd
import phoenix as px
import requests
import httpx
import asyncio
import json

# from phoenix.evals import llm_classify
# from phoenix.trace.dsl import SpanQuery
# from llm_models.genai_model import GenAIModel
# from google.oauth2 import service_account
# from phoenix.trace import SpanEvaluations

# from openinference.instrumentation import suppress_tracing

# from src.evaluations.letta.agents.final_response import CLARITY_LLM_JUDGE_PROMPT


import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
)
from src.config import env

api_key = env.GEMINI_API_KEY

async def get_response_from_letta(query: str) -> dict:
    url = env.EAI_AGENT_URL + "api/v1/letta/test-message-raw"
    payload = {
        "agent_id": "agent-45d877fa-4f50-4935-a18f-8a481291c950",
        "message": query,
        "name": "Usuário Teste",
    }
    print(f"URL: {url}")
    bearer_token = env.EAI_AGENT_TOKEN
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    print(f"Headers: {headers}")

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    return response.json()


async def main():
    print("Iniciando a execução do script...")
    response = await get_response_from_letta(query="qual o serviço para reparo de luminária?")
    # print response as a formatted JSON
    print(json.dumps(response, indent=4, ensure_ascii=False))
    # print(response)


if __name__ == "__main__":
    asyncio.run(main())
