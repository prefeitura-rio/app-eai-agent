import os
import re
import pandas as pd
import phoenix as px
import requests
import httpx
import asyncio
import json

from phoenix.evals import llm_classify

import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
)
from src.config import env

from src.evaluations.letta.agents.final_response import (
    ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
    CLARITY_LLM_JUDGE_PROMPT,
    GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
    EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
    FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
    SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
    WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
)
from llm_models.genai_model import GenAIModel

EVAL_MODEL = GenAIModel(model="gemini-2.5-flash-preview-04-17", api_key=env.GEMINI_API_KEY)
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

    async with httpx.AsyncClient(timeout=60) as client:

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    return response.json()

def final_response(agent_stream: dict) -> dict:
    return agent_stream["assistant_messages"][-1]

async def experiment_eval(input, output, prompt, rails, expected=None) -> bool | dict:
    if output is None:
        return False
    df = pd.DataFrame({"query": [input.get("pergunta")], 
                       "model_response": [final_response(output).get("content", "")]})
    
    if expected:
        df["ideal_response"] = [expected.get("resposta_ideal")]

    response = llm_classify(
        data=df,
        template=prompt,
        rails=rails,
        model=EVAL_MODEL,
        provide_explanation=True
    )

    if expected:
        return response

    return response['label'] == rails[0]

async def experiment_eval_answer_completeness(input, output, expected) -> bool:
    rails_answer_completeness = ["complete", "incomplete"]
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
        rails=rails_answer_completeness
    )
    if isinstance(response, dict):
        return response.get('label') == rails_answer_completeness[0]
    return response

async def experiment_eval_clarity(input, output, expected) -> bool:
    rails_clarity = ["clear", "unclear"]
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=CLARITY_LLM_JUDGE_PROMPT,
        rails=rails_clarity
    )
    if isinstance(response, dict):
        return response.get('label') == rails_clarity[0]
    return response

async def experiment_eval_gold_standart_similarity(input, output, expected) -> float:
    rails_gold_standart_similarity = ["equivalent", "similar", "different"]
    gold_standart_similarity_mapping = {
        "equivalent": 1,
        "similar": 0.5,
        "different": 0
    }
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
        rails=rails_gold_standart_similarity,
        expected=expected
    )
    if isinstance(response, dict):
        label = response.get('label')
        if isinstance(label, str) and label in gold_standart_similarity_mapping:
            return gold_standart_similarity_mapping[label]
        return 0.0
    return response

async def experiment_eval_emergency_handling_compliance(input, output, expected) -> bool:
    rails_emergency_handling_compliance = ["compliant", "non_compliant"]
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_emergency_handling_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_emergency_handling_compliance[0]
    return response

async def experiment_eval_entity_presence(input, output, expected) -> bool:
    rails_entity_presence = ["entities_present", "entities_missing"]
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
        rails=rails_entity_presence
    )
    if isinstance(response, dict):
        return response.get('label') == rails_entity_presence[0]
    return response    

async def experiment_eval_feedback_handling_compliance(input, output, expected) -> bool:
    rails_feedback_handling_compliance = ["compliant", "non_compliant"]
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_feedback_handling_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_feedback_handling_compliance[0]
    return response

async def experiment_eval_location_policy_compliance(input, output, expected) -> bool:
    rails_location_policy_compliance = ["compliant", "non_compliant"]
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_location_policy_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_location_policy_compliance[0]
    return response

async def experiment_eval_security_privacy_compliance(input, output, expected) -> bool:
    rails_security_privacy_compliance = ["compliant", "non_compliant"]
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_security_privacy_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_security_privacy_compliance[0]
    return response

async def experiment_eval_whatsapp_formatting_compliance(input, output, expected) -> bool:
    rails_whatsapp_formatting_compliance = ["compliant", "non_compliant"]
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_whatsapp_formatting_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_whatsapp_formatting_compliance[0]
    return response

async def main():
    print("Iniciando a execução do script...")
    response = await get_response_from_letta(query="Como faço para pagar o iptu?")
    # print response as a formatted JSON
    print(json.dumps(response["assistant_messages"], indent=4, ensure_ascii=False))
    # print(response)


if __name__ == "__main__":
    asyncio.run(main())
