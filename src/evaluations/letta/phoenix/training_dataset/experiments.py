import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from src.config import env
from src.evaluations.letta.phoenix.training_dataset.evaluators import *
from src.evaluations.letta.phoenix.llm_models.genai_model import GenAIModel
from src.services.letta.agents.memory_blocks.agentic_search_mb import get_agentic_search_memory_blocks

os.environ["PHOENIX_HOST"] = env.PHOENIX_HOST
os.environ["PHOENIX_PORT"] = env.PHOENIX_PORT
os.environ["PHOENIX_ENDPOINT"] = env.PHOENIX_ENDPOINT

import pandas as pd
import httpx
import phoenix as px
import nest_asyncio
nest_asyncio.apply()
import asyncio
from src.services.llm.gemini_service import GeminiService

from phoenix.evals import llm_classify
from phoenix.evals.models import OpenAIModel
from phoenix.experiments.types import Example
from phoenix.experiments import run_experiment
import pprint


phoenix_client = px.Client(endpoint=env.PHOENIX_ENDPOINT)

GEMINI_COMPLETO = GeminiService()

EVAL_MODEL = GenAIModel(model=env.GEMINI_EVAL_MODEL, api_key=env.GEMINI_API_KEY, temperature=0, max_tokens=100000)
# EVAL_MODEL = OpenAIModel(api_key=env.OPENAI_API_KEY, azure_endpoint=env.OPENAI_URL, api_version="2024-02-15-preview", model="gpt-4.1")

async def get_response_from_letta(example: Example) -> dict:  
    url = f"{env.EAI_AGENT_URL}letta/test-message-raw"
    payload = {
        "agent_id": "agent-8a86f0e0-0d78-4646-9c8a-9de5af4ac83b",
        "message": example.input.get("pergunta"),
        "name": "Usuário Teste",
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {env.EAI_AGENT_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=300) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise RuntimeError("Resposta vazia do agente.")
            return data
        
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"Erro na chamada para Letta: {exc.response.status_code} - {exc.response.text}") from exc

async def get_response_from_gpt(example: Example) -> dict:
    headers = {
        "Content-Type": "application/json",
        "api-key": env.OPENAI_API_KEY
    }
    
    payload = {
        "messages": [
            {
                "role": "user", 
                "content": example.input.get("pergunta"),
            }
        ],
        "temperature": 0.8,
        "max_tokens": 256
    }

    url = f"{env.OPENAI_URL}openai/deployments/gpt-4.1/chat/completions?api-version=2024-02-15-preview"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]



async def get_response_from_gemini(example: Example) -> str:
    # genai.configure(api_key=env.GEMINI_API_KEY)


    # model = genai.GenerativeModel("models/gemini-2.5-pro-preview-06-05")
    # loop = asyncio.get_event_loop()

    # def _run_blocking():
    #     response = model.generate_content(example.input.get("pergunta"))
    #     return response.text

    response = await GEMINI_COMPLETO.generate_content(
            str(example.input.get("pergunta")),
            model="gemini-2.5-pro-preview-06-05",
            use_google_search=True,
            response_format="text_only",
        )
    return response.get("texto")


def final_response(agent_stream: dict) -> dict:
    if not agent_stream or "assistant_messages" not in agent_stream:
        return {}
    
    return agent_stream["assistant_messages"][-1]


def tool_returns(agent_stream: dict) -> str:
    if not agent_stream:
        return ""
     
    returns = [
        f"Tool Return {i + 1}:\n"
        f"Tool Name: {msg.get('name', 'Unknown')}\n"
        f"Tool Result: {msg.get('tool_return', '').strip()}\n"
        for i, msg in enumerate(agent_stream.get("tool_return_messages", []))
    ]
    
    return "\n".join(returns)


def search_tool_returns_summary(agent_stream: dict) -> list[dict]:
    if not agent_stream:
        return []
    
    search_tool_returns = [
        {
            "title": msg.get('tool_return', {}).get('title', ''),
            "summary": msg.get('tool_return', {}).get('summary', '')
        }
        for msg in agent_stream.get("tool_return_messages", [])
        if msg.get('name') == 'search_tool'
    ]

    return search_tool_returns


def empty_agent_core_memory():
    core_memory = [f"{mb['label']}: {mb['value']}" for mb in get_agentic_search_memory_blocks()]

    return "\n".join(core_memory)


async def experiment_eval(input, output, prompt, rails, expected=None, **kwargs) -> tuple| bool:
    if not output:
        return False
    
    df = pd.DataFrame({
        "query": [input.get("pergunta")], 
        "model_response": [final_response(output).get("content", "")],
        # "model_response": [output], # Gemini e GPT
    })
    
    if expected:
        df["ideal_response"] = [expected.get("resposta_ideal")]

    for k, val in kwargs.items():
        if isinstance(val, str):
            df[k] = [val]
        elif isinstance(val, list):
            df[k] = [", ".join(val)]
        else:
            df[k] = [val]

    response = llm_classify(
        data=df,
        template=prompt,
        rails=rails,
        model=EVAL_MODEL,
        provide_explanation=True
    )

    eval = response.get('label') == rails[0]
    explanation = response.get("explanation")

    # print(f"Query: {input.get('pergunta')}")
    # print(f"Model Response: {response}")
    # print(f"Label: {response.get('label')}")
    # pd.set_option('display.max_colwidth', None)
    # # print the explanation, no matter the length
    # print(f"Explanation: {explanation}")
    # print("---"*20)

    return (eval, explanation)
    

async def main():
    print("Iniciando a execução do script...")

    # dataset_name = "Typesense_IA_Dataset-2025-05-29"
    dataset_name = "GPT_Dataset-2025-06-12"
    dataset = phoenix_client.get_dataset(name=dataset_name)

    experiment = run_experiment(
        dataset,
        get_response_from_letta,
        evaluators=[
            experiment_eval_answer_completeness,
            # experiment_eval_gold_standard_similarity,
            # experiment_eval_clarity,
            experiment_eval_groundedness,
            # experiment_eval_entity_presence,
            # experiment_eval_feedback_handling_compliance,
            # experiment_eval_emergency_handling_compliance,
            # experiment_eval_location_policy_compliance,
            # experiment_eval_security_privacy_compliance,
            experiment_eval_whatsapp_formatting_compliance,
            experiment_eval_search_result_coverage,
            # experiment_eval_tool_calling,
            # experiment_eval_search_query_effectiveness,
            experiment_eval_good_response_standards,
            ],
        experiment_name="Letta - Prompts fixed", 
        experiment_description="Evaluating final response of the agent with various evaluators.",
        dry_run=False,
        concurrency=dataset.as_dataframe().shape[0],
    )
    
if __name__ == "__main__":
    asyncio.run(main())
