import sys
import os
import asyncio

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
)
from src.config import env
from src.evaluations.letta.phoenix.training_dataset.evaluators import *
from src.evaluations.letta.phoenix.training_dataset.utils import coletar_todas_respostas
from src.evaluations.letta.phoenix.training_dataset.prompts import (
    SYSTEM_PROMPT_BASELINE_O4,
    SYSTEM_PROMPT_BASELINE_GEMINI,
    SYSTEM_PROMPT_EAI,
)

os.environ["PHOENIX_HOST"] = env.PHOENIX_HOST
os.environ["PHOENIX_PORT"] = env.PHOENIX_PORT
os.environ["PHOENIX_ENDPOINT"] = env.PHOENIX_ENDPOINT


import phoenix as px
import nest_asyncio


from phoenix.experiments.types import Example
from phoenix.experiments import run_experiment
import logging


## NOTE: MANDEI A IA COMENTAR O CÓDIGO PARA QUALQUER UM ENTENDA O QUE ESTÁ ACONTECENDO AQUI.
## NOTE: MANDEI A IA COMENTAR O CÓDIGO PARA QUALQUER UM ENTENDA O QUE ESTÁ ACONTECENDO AQUI.
## NOTE: ----------------------------------------------------------------------------------
## NOTE: PARA RODAR O CÓDIGO, TEM UMA PECULIARIDADE EM QUE É PRECISO ALTERAR UM ITEM DA CRIAÇÃO DO AGENTE, QUALQUER DÚVIDA ME CHAMA (FRED) QUE EU EXPLICO O QUE FAZER.
## NOTE: PARA RODAR O CÓDIGO, TEM UMA PECULIARIDADE EM QUE É PRECISO ALTERAR UM ITEM DA CRIAÇÃO DO AGENTE, QUALQUER DÚVIDA ME CHAMA (FRED) QUE EU EXPLICO O QUE FAZER.

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

phoenix_client = px.Client(endpoint=env.PHOENIX_ENDPOINT)


async def executar_avaliacao_phoenix(
    dataset: str, respostas_coletadas: dict, experiment_name: str, evaluators: list
):
    """
    Executa a avaliação Phoenix usando as respostas já coletadas.

    Args:
        dataset: Dataset do Phoenix
        respostas_coletadas: Dicionário com as respostas já coletadas
    """
    logger.info(
        f"Iniciando avaliação Phoenix com as respostas coletadas: {experiment_name}"
    )

    async def get_cached_responses(example: Example) -> dict:
        return {
            "agent_output": respostas_coletadas.get(example.id, {}),
            "metadata": example.metadata,
        }

    experiment = run_experiment(
        dataset,
        get_cached_responses,
        evaluators=evaluators,
        experiment_name=experiment_name,
        experiment_description="Evaluating final response of the agent with various evaluators.",
        dry_run=False,
        concurrency=10,
    )

    logger.info("Avaliação Phoenix concluída")
    return experiment


async def main():
    """Função principal que executa todo o processo"""
    ##TODO: ALTERAR AQUI O DATASET QUE SERÁ AVALIADO

    evaluators = [
        # experiment_eval_answer_completeness,
        # experiment_eval_groundedness,
        # experiment_eval_whatsapp_formatting_compliance,
        # experiment_eval_search_result_coverage,
        # experiment_eval_good_response_standards,
        golden_link_in_tool_calling,
        golden_link_in_answer,
        activate_search,
        # answer_similarity,
    ]
    experiments_configs = [
        # {
        #     "dataset_name": "golden_dataset_v3",
        #     "experiment_name": "baseline-o4-2025-06-27-v12",
        #     "evaluators": evaluators,
        #     "tools": ["gpt_search"],
        #     "model_name": "google_ai/gemini-2.5-flash-lite-preview-06-17",
        #     "system_prompt": system_prompt_baseline_o4,
        # },
        # {
        #     "dataset_name": "golden_dataset_v3",
        #     "experiment_name": "baseline-gemini-2.5-flash-2025-06-27-v12",
        #     "evaluators": evaluators,
        #     "tools": ["google_search"],
        #     "model_name": "google_ai/gemini-2.5-flash-lite-preview-06-17",
        #     "system_prompt": system_prompt_baseline_gemini,
        # },
        {
            "dataset_name": "golden_dataset_small_sample_v3",
            "experiment_name": "eai-2025-06-27-v12",
            "evaluators": evaluators,
            "tools": ["google_search"],
            "model_name": "google_ai/gemini-2.5-flash-lite-preview-06-17",
            "batch_size": 15,
            "system_prompt": SYSTEM_PROMPT_EAI,
        },
    ]

    for experiment_index, experiment_config in enumerate(experiments_configs):
        dataset_name = experiment_config["dataset_name"]
        tools = experiment_config.get("tools", None)
        model_name = experiment_config.get("model_name", None)
        experiment_name = experiment_config["experiment_name"]
        evaluators = experiment_config["evaluators"]
        batch_size = experiment_config.get("batch_size", 10)
        system_prompt = experiment_config.get("system_prompt", 10)

        logger.info(f"{'='*100}")
        percentage = 100 * (experiment_index + 1) / len(experiments_configs)
        logger.info(
            f"Experimento {experiment_index + 1} de {len(experiments_configs)} | {percentage:.2f}%"
        )
        logger.info(f"Iniciando Experimento : {experiment_name}")

        logger.info(f"Carregando dataset: {dataset_name}")
        dataset = phoenix_client.get_dataset(name=dataset_name)

        # Etapa 1: Coletar todas as respostas em batches
        logger.info("Iniciando coleta de respostas em batches")
        respostas = await coletar_todas_respostas(
            dataset=dataset,
            tools=tools,
            model_name=model_name,
            batch_size=batch_size,
            system_prompt=system_prompt,
        )

        # Etapa 2: Executar avaliação Phoenix
        logger.info("Iniciando avaliação Phoenix")
        await executar_avaliacao_phoenix(
            dataset=dataset,
            respostas_coletadas=respostas,
            experiment_name=experiment_name,
            evaluators=evaluators,
        )

        logger.info(f"Processo completo: {experiment_name}\n")
        logger.info(f"{'='*100}\n\n")


if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
