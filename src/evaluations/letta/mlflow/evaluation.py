import requests
import os


import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir.split("src")[0])


from src.evaluations.letta.agents.final_response import (
    CLARITY_LLM_JUDGE_PROMPT,
    GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
    GROUNDEDNESS_LLM_JUDGE_PROMPT,
)


import logging

logging.basicConfig(level=logging.INFO)

for var in [
    "MLFLOW_TRACKIN_URL",
    "MLFLOW_TRACKING_USERNAME",
    "MLFLOW_TRACKING_PASSWORD",
    "AGENTIC_SEARCH_URL",
    "AGENTIC_SEARCH_TOKEN",
]:
    assert os.environ.get(var), f"Environment variable {var} is not set"


def get_response_from_agent(querry):
    url = os.getenv("AGENTIC_SEARCH_URL")
    payload = {
        "data": {
            "message": querry,
            "name": "João da Silva",
            "user_number": "5531999999999",
        },
        "metadata": {"origin": "sistema_externo", "timestamp": "2023-10-15T14:30:00Z"},
        "type": "message",
    }
    bearer_token = os.getenv("AGENTIC_SEARCH_TOKEN")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload)

    response.raise_for_status()

    response_json = response.json()

    if response_json.get("status") != "success":
        logging.warning(f"status is not success: {response_json}")
    elif "message" not in response_json:
        assert BaseException(f"No message in the response: {response_json}")
    else:
        return response_json.get("message")


if __name__ == "__main__":

    # querry = "Quero remover um sofa velho"
    # message = get_response_from_agent(querry=querry)
    # print(message)

    print(CLARITY_LLM_JUDGE_PROMPT)
