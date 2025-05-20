import httpx
import os
import json
import asyncio
import textwrap
from datetime import datetime

import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir.split("src")[0]
if project_root:  # Check if split found 'src'
    sys.path.append(project_root)

import pandas as pd

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


async def get_response_from_letta(query: str) -> dict:
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

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()

    if response_json.get("status") != "success":
        logging.warning(f"status is not success: {response_json}")
    elif "message" not in response_json:
        assert BaseException(f"No message in the response: {response_json}")
    else:
        return response_json["message"]


async def call_juges(eval_results: dict, judges: list) -> dict:
    model = Model(model="gemini-2.5-flash-preview-04-17", temperature=0.1)
    logging.info("Getting response from judges")
    judges_results = []
    for judge_name in judges:
        judges_result = model.judge(judge_name=judge_name, eval_results=eval_results)
        judges_results.append(judges_result)
    return judges_results


def explode_dataframe(dataframe: pd.DataFrame, explode_col: str) -> pd.DataFrame:
    s = dataframe[explode_col].explode()
    tmp = dataframe.drop(columns=explode_col)
    out = (
        pd.concat(
            [
                tmp,
                pd.json_normalize(s, sep="_")
                .set_axis(s.index)
                .dropna()
                .combine_first(tmp),
            ]
        )
        .drop_duplicates()
        .sort_index(kind="stable")
    )
    return out[out["judge"].notnull()]


def load_dataframe(final_results: list) -> pd.DataFrame:
    dataframe = pd.DataFrame(final_results)
    dataframe = explode_dataframe(dataframe=dataframe, explode_col="judges")


async def main():

    eval_dataset = [
        {
            "query": "Quero remover um sofa velho",
            "ideal_response": textwrap.dedent(
                """
                Para solicitar a remoção de móveis ou outros bens inservíveis pela Prefeitura do Rio, você deve entrar em contato com a Central 1746. A Comlurb é a responsável por este serviço gratuito.

                Você pode fazer a solicitação pelos seguintes canais:
                - *Portal 1746*: Acesse o site https://www.1746.rio/ e procure pelo serviço de \"Remoção de entulho e bens inservíveis\".
                - *Aplicativo 1746 Rio*: Disponível para smartphone.
                - *WhatsApp*: Salve o número (21) 3460-1746 e envie uma mensagem.
                - *Telefone*: Ligue para 1746 (dentro do município do Rio) ou (21) 3460-1746 (para outras localidades).

                O serviço atende a pedidos em todos os bairros do Rio. O prazo para atendimento pode ser de até 10 a 12 dias corridos ou úteis, dependendo da fonte da informação. O atendimento ocorre de segunda a sábado, das 7h às 22h.

                Há limites para a quantidade de bens inservíveis removidos gratuitamente por residência. Para bens de grande peso ou volume, como sofás, a remoção é limitada a dois itens por residência.

                _Informações e canais de contato podem mudar. Confira sempre os canais oficiais da Central 1746._
                """
            ),
        },
        {
            "query": "Quero vacinar meu gatinho",
            "ideal_response": textwrap.dedent(
                """
                Para vacinar seu gatinho, você pode solicitar o atendimento domiciliar para vacinação antirrábica se tiver dificuldade de locomoção ou possuir 10 ou mais animais. 🐱
                *Como solicitar*:
                - O serviço está disponível o ano todo, exceto durante a Campanha Anual de Vacinação Antirrábica (geralmente de agosto a novembro).
                - Após a solicitação, a equipe entrará em contato para agendar a data da vacinação.

                _Importante_: Fêmeas gestantes ou amamentando e filhotes menores de três meses não são vacinados. Os animais devem estar devidamente contidos na residência.

                Para mais informações e agendamento, acesse: https://www.1746.rio/hc/pt-br/articles/10769393994267-Atendimento-domiciliar-para-vacina%C3%A7%C3%A3o-antirr%C3%A1bica-animal

                Além disso, fique de olho na Campanha de Vacinação Antirrábica anual, que acontece em diversos postos pela cidade: https://www.1746.rio/hc/pt-br/articles/10769458450459-Campanha-de-vacina%C3%A7%C3%A3o-antirr%C3%A1bica-animal-2024 😉
                """
            ),
        },
    ]

    csv_save_path = f"{current_dir}/eval_results.csv"
    if os.path.exists(csv_save_path):
        os.remove(csv_save_path)

    judges = [
        "clarify",
        "location",
        "emergency",
        "feedback",
        "security",
        "whatsapp",
        "gold_standart",
    ]

    final_results = []
    for eval_results in eval_dataset:
        # datetime in str format
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datetime_dict = {"updated_at": now}
        eval_results = {**datetime_dict, **eval_results}

        logging.info("Getting response from letta api")
        letta_response = await get_response_from_letta(query=eval_results["query"])
        eval_results["letta_response"] = letta_response

        judges_results = await call_juges(eval_results=eval_results, judges=judges)
        eval_results["judges"] = judges_results

        final_results.append(eval_results)

        dataframe = pd.DataFrame([eval_results])
        dataframe.to_csv(
            csv_save_path,
            index=False,
            mode="a",
            sep=";",
            header=False if os.path.exists(csv_save_path) else True,
        )

    json.dump(
        json.loads(json.dumps(final_results)),
        open(f"{current_dir}/eval_results.json", "w"),
        indent=4,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    asyncio.run(main())
