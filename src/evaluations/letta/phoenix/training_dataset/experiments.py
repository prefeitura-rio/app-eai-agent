import os
import re
import pandas as pd
import phoenix as px
import requests
import httpx
import asyncio
import nest_asyncio # Import nest_asyncio

nest_asyncio.apply() # Apply the patch

import json

# Configurar variáveis de ambiente para Phoenix
os.environ["PHOENIX_HOST"] = "34.60.92.205"
os.environ["PHOENIX_PORT"] = "6006"
os.environ["PHOENIX_ENDPOINT"] = "http://34.60.92.205:6006"

from phoenix.evals import llm_classify
from phoenix.experiments.types import Example
from phoenix.experiments import run_experiment, evaluate_experiment
from phoenix.experiments.evaluators import create_evaluator

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
    GROUNDEDNESS_LLM_JUDGE_PROMPT,
    EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
    FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
    SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
    WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
)

from src.evaluations.letta.agents.router import (
    SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
    TOOL_CALLING_LLM_JUDGE_PROMPT,
)

from src.evaluations.letta.agents.search_tools import (
    SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT
)

from src.evaluations.letta.phoenix.llm_models.genai_model import GenAIModel
from src.services.letta.agents.memory_blocks.agentic_search_mb import get_agentic_search_memory_blocks
from src.evaluations.letta.phoenix.utils import (
    get_system_prompt,
    extrair_query,
)

EVAL_MODEL = GenAIModel(model="gemini-2.5-flash-preview-04-17", api_key=env.GEMINI_API_KEY)
api_key = env.GEMINI_API_KEY
phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")

def get_response_from_letta(example: Example) -> dict:
    url = env.EAI_AGENT_URL + "api/v1/letta/test-message-raw"
    payload = {
        "agent_id": "agent-45d877fa-4f50-4935-a18f-8a481291c950",
        "message": example.input.get("pergunta"),
        "name": "Usuário Teste",
    }
    bearer_token = env.EAI_AGENT_TOKEN
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=300) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    print("Pergunta enviada:", example.input.get("pergunta"))
    #print([key for key in response.json().keys()])
    print(json.dumps(response.json()["tool_call_messages"], indent=4, ensure_ascii=False))
    print("--" * 50)
    return response.json()

def final_response(agent_stream: dict) -> dict:
    return agent_stream["assistant_messages"][-1]

def tool_returns(agent_stream: dict) -> str:
    total_tool_return = []
    for i, message in enumerate(agent_stream["tool_return_messages"]):
        tool_name = message.get('name', 'Unknown')
        tool_result = message.get('tool_return', '').replace('\n', '').replace('\r', '').strip()
        total_tool_return.append(
            f"Tool Return {i + 1}:\n"
            f"Tool Name: {tool_name}\n"
            f"Tool Result: {tool_result}\n"
        )
    return "\n".join(total_tool_return)

def tool_calls(agent_stream: dict) -> dict:
    tool_calls = []
    for i, message in enumerate(agent_stream["tool_calls_messages"]):
        tool_name = message.get('name', 'Unknown')
        tool_result = message.get('tool_return', '').replace('\n', '').replace('\r', '').strip()
        tool_calls.append(
            {)
        )
    return 

def search_tool_returns_summary(agent_stream: dict) -> list[dict]:
    search_tool_returns = []
    for message in agent_stream["tool_return_messages"]:
        if message.get('name') == 'search_tool':
            search_tool_returns.append({
                "title": message.get('tool_return', {}).get('title', ''),
                "summary": message.get('tool_return', {}).get('summary', '')
            })
    return search_tool_returns

def empty_agent_core_memory():
    core_memory = []
    for mb in get_agentic_search_memory_blocks():
        core_memory.append(f"{mb['label']}: {mb['value']}")
    return "\n".join(core_memory)

def experiment_eval(input, output, prompt, rails, expected=None, **kwargs) -> bool | dict:
    if output is None:
        return False
    df = pd.DataFrame({"query": [input.get("pergunta")], 
                       "model_response": [final_response(output).get("content", "")]})
    
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

    if expected:
        return response

    return response['label'] == rails[0]

@create_evaluator(name="Answer Completeness", kind="LLM")
def experiment_eval_answer_completeness(input, output, expected) -> bool:
    rails_answer_completeness = ["complete", "incomplete"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
        rails=rails_answer_completeness
    )
    if isinstance(response, dict):
        return response.get('label') == rails_answer_completeness[0]
    return response

@create_evaluator(name="Clarity", kind="LLM")
def experiment_eval_clarity(input, output, expected) -> bool:
    rails_clarity = ["clear", "unclear"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=CLARITY_LLM_JUDGE_PROMPT,
        rails=rails_clarity
    )
    if isinstance(response, dict):
        return response.get('label') == rails_clarity[0]
    return response

@create_evaluator(name="Similaridade Resposta Ideal", kind="LLM")
def experiment_eval_gold_standart_similarity(input, output, expected) -> float | bool:
    rails_gold_standart_similarity = ["equivalent", "similar", "different"]
    gold_standart_similarity_mapping = {
        "equivalent": 1,
        "similar": 0.5,
        "different": 0
    }
    response = experiment_eval(
        input=input,
        output=output,
        prompt=GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
        rails=rails_gold_standart_similarity,
        expected=expected
    )
    if not isinstance(response, bool):
        label = response.get('label')
        if isinstance(label, str) and label in gold_standart_similarity_mapping:
            return gold_standart_similarity_mapping[label]
        return False
    return False

@create_evaluator(name="Emergency Handling", kind="LLM")
def experiment_eval_emergency_handling_compliance(input, output, expected) -> bool:
    rails_emergency_handling_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_emergency_handling_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_emergency_handling_compliance[0]
    return response

@create_evaluator(name="Entity Presence", kind="LLM")
def experiment_eval_entity_presence(input, output, expected) -> bool:
    rails_entity_presence = ["entities_present", "entities_missing"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
        rails=rails_entity_presence
    )
    if isinstance(response, dict):
        return response.get('label') == rails_entity_presence[0]
    return response    

@create_evaluator(name="Feedback Handling", kind="LLM")
def experiment_eval_feedback_handling_compliance(input, output, expected) -> bool:
    rails_feedback_handling_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_feedback_handling_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_feedback_handling_compliance[0]
    return response

@create_evaluator(name="Location Policy", kind="LLM")
def experiment_eval_location_policy_compliance(input, output, expected) -> bool:
    rails_location_policy_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_location_policy_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_location_policy_compliance[0]
    return response

@create_evaluator(name="Security and Privacy", kind="LLM")
def experiment_eval_security_privacy_compliance(input, output, expected) -> bool:
    rails_security_privacy_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_security_privacy_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_security_privacy_compliance[0]
    return response

@create_evaluator(name="Whatsapp Format", kind="LLM")
def experiment_eval_whatsapp_formatting_compliance(input, output, expected) -> bool:
    rails_whatsapp_formatting_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_whatsapp_formatting_compliance
    )
    if isinstance(response, dict):
        return response.get('label') == rails_whatsapp_formatting_compliance[0]
    return response

@create_evaluator(name="Groundness", kind="LLM")
def experiment_eval_groundedness(input, output, expected) -> bool:
    rails_groundedness = ["based", "unfounded"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=GROUNDEDNESS_LLM_JUDGE_PROMPT,
        rails=rails_groundedness,
        core_memory=empty_agent_core_memory(),
        search_tool_results=tool_returns(output),
    )
    if isinstance(response, dict):
        return response.get('label') == rails_groundedness[0]
    return response

@create_evaluator(name="Search Result Coverage", kind="LLM")
def experiment_eval_search_result_coverage(input, output, expected) -> bool:
    rails_search_result_coverage = ["covers", "uncovers"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT,
        rails=rails_search_result_coverage,
        search_tool_results=tool_returns(output),
    )
    if isinstance(response, dict):
        return response.get('label') == rails_search_result_coverage[0]
    return response

@create_evaluator(name="Tool Calling", kind="LLM")
def experiment_eval_tool_calling(input, output, expected) -> float | bool:
    tool_definitions = get_system_prompt()
    tool_definitions = tool_definitions[tool_definitions.find("Available tools:\n") :]
    rails_tool_calling = ["correct", "incorrect"]

    results = []
    for tool_call in output["tool_calls_messages"]:
        if tool_call.get('name') in ('typesense_search', 'google_search'):
            response = experiment_eval(
                input=input,
                output=output,
                prompt=TOOL_CALLING_LLM_JUDGE_PROMPT.replace("{tool_definitions}", tool_definitions),
                rails=rails_tool_calling,
                tool_call=tool_call,
            )
            if isinstance(response, dict):
                result = int(response.get('label') == rails_tool_calling[0])
            else:
                result = int(response)
            results.append(result)
    if results:
        return sum(results) / len(results)
    return False

def main():
    print("Iniciando a execução do script...")
    dataset = phoenix_client.get_dataset(name="Typesense_IA_Dataset-2025-05-29")
    experiment = run_experiment(dataset,
                            get_response_from_letta,
                            evaluators=[experiment_eval_answer_completeness,
                                        experiment_eval_gold_standart_similarity,
                                        experiment_eval_clarity,
                                        experiment_eval_groundedness,
                                        experiment_eval_entity_presence,
                                        experiment_eval_feedback_handling_compliance,
                                        experiment_eval_emergency_handling_compliance,
                                        experiment_eval_location_policy_compliance,
                                        experiment_eval_security_privacy_compliance,
                                        experiment_eval_whatsapp_formatting_compliance],
                            experiment_name="Overall Final Response Experiment",
                            experiment_description="Evaluating the final response of the agent with various evaluators.",
                            dry_run=True,
                            )
    
if __name__ == "__main__":
    main()
