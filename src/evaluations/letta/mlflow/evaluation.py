import requests
import os
import json

import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir.split("src")[0])

from src.evaluations.letta.mlflow.model import Model


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


def get_response_from_agent(query):
    url = os.getenv("AGENTIC_SEARCH_URL")
    payload = {
        "data": {
            "message": query,
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
    query = "Quero remover um sofa velho"
    ideal_response = """
Para solicitar a remoção de móveis ou outros bens inservíveis pela Prefeitura do Rio, você deve entrar em contato com a Central 1746. A Comlurb é a responsável por este serviço gratuito.

Você pode fazer a solicitação pelos seguintes canais:
- *Portal 1746*: Acesse o site https://www.1746.rio/ e procure pelo serviço de \"Remoção de entulho e bens inservíveis\".
- *Aplicativo 1746 Rio*: Disponível para smartphone.
- *WhatsApp*: Salve o número (21) 3460-1746 e envie uma mensagem.
- *Telefone*: Ligue para 1746 (dentro do município do Rio) ou (21) 3460-1746 (para outras localidades).

O serviço atende a pedidos em todos os bairros do Rio. O prazo para atendimento pode ser de até 10 a 12 dias corridos ou úteis, dependendo da fonte da informação. O atendimento ocorre de segunda a sábado, das 7h às 22h.

Há limites para a quantidade de bens inservíveis removidos gratuitamente por residência. Para bens de grande peso ou volume, como sofás, a remoção é limitada a dois itens por residência.

_Informações e canais podem mudar. Confira sempre os canais oficiais da Central 1746._
"""

    logging.info("Getting response from letta api")
    letta_response = get_response_from_agent(query=query)

    eval_results = {
        "query": query,
        "letta_response": letta_response,
        "ideal_response": ideal_response,
    }

    model = Model()
    logging.info("Getting response from judges")
    judges = [
        "clarify",
        "location",
        "emergency",
        "feedback",
        "security",
        "whatsapp",
        "gold_standart",
    ]
    for judge_name in judges:
        eval_results = model.judge(judge_name=judge_name, eval_results=eval_results)

    json.dump(
        eval_results,
        open(f"{current_dir}/eval_results.json", "w"),
        indent=4,
        ensure_ascii=False,
    )
