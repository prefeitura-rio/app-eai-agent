import asyncio
import uuid
import pandas as pd
import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path

from src.evaluations.core.eval import (
    DataLoader,
    AzureOpenAIClient,
    GeminiAIClient,
    AsyncExperimentRunner,
)
from src.services.eai_gateway.api import CreateAgentRequest
from src.evaluations.core.experiments.batman.data.test_data import UNIFIED_TEST_DATA
from src.utils.log import logger
from datetime import datetime

# Importa os avaliadores modulares
from src.evaluations.core.experiments.eai.evaluators import (
    # GoldenLinkInAnswerEvaluator,
    # GoldenLinkInToolCallingEvaluator,
    AnswerCompletenessEvaluator,
    AnswerAddressingEvaluator,
    ClarityEvaluator,
    ActivateSearchEvaluator,
    WhatsAppFormatEvaluator,
    ProactivityEvaluator,
    MessageLengthEvaluator,
    HasLinkEvaluator,
    LinkCompletenessEvaluator,
    ToolCallingLinkCompletenessEvaluator,
)
from src.evaluations.core.experiments.eai.evaluators.prompts import (
    prompt_data,
)

from src.evaluations.core.experiments.eai.evaluators.agent_config import (
    agent_config_data,
)

EXPERIMENT_DATA_PATH = Path(__file__).parent / "data"


async def run_experiment():
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    """
    logger.info("--- Configurando o Experimento Unificado (Arquitetura Refatorada) ---")

    loader = DataLoader(
        source="https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=370781785",  # golden dataset
        # number_rows=10,
        id_col="id",
        prompt_col="mensagem_whatsapp_simulada",
        dataset_name="Golden Dataset samples",
        dataset_description="Dataset de avaliacao de servicos",
        metadata_cols=[
            "golden_links_list",
            "golden_answer",
            "golden_answer_criteria",
        ],
    )
    logger.info(
        f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    # --- 3. Definição da Suíte de Avaliação ---
    judge_client = AzureOpenAIClient(model_name="gpt-4o")
    # judge_client = GeminiAIClient(model_name="gemini-1.5-flash-latest")

    # Instancia os avaliadores que serão executados
    evaluators_to_run = [
        # GoldenLinkInAnswerEvaluator(judge_client),
        # GoldenLinkInToolCallingEvaluator(judge_client),
        AnswerCompletenessEvaluator(judge_client),
        AnswerAddressingEvaluator(judge_client),
        ClarityEvaluator(judge_client),
        ActivateSearchEvaluator(judge_client),
        WhatsAppFormatEvaluator(judge_client),
        ProactivityEvaluator(judge_client),
        MessageLengthEvaluator(judge_client),
        HasLinkEvaluator(judge_client),
        LinkCompletenessEvaluator(judge_client),
        ToolCallingLinkCompletenessEvaluator(judge_client),
    ]

    evaluator_names = [e.name for e in evaluators_to_run]
    logger.info(f"✅ Suíte de avaliações configurada para rodar: {evaluator_names}")

    # Coleta os prompts de cada avaliador para os metadados
    judges_prompts = {
        evaluator.name: evaluator.PROMPT_TEMPLATE
        for evaluator in evaluators_to_run
        if hasattr(evaluator, "PROMPT_TEMPLATE")
    }

    metadata = {
        # "agent_config": agent_config_data,
        "system_prompt": prompt_data["prompt"],
        "judge_model": judge_client.model_name,
        "judges_prompts": judges_prompts,
    }

    # --- 5. Configuração e Execução do Runner ---
    MAX_CONCURRENCY = 20

    runner = AsyncExperimentRunner(
        experiment_name=f"eai-{datetime.now().strftime('%Y-%m-%d')}-v{prompt_data['version']}",
        # experiment_name=f"eai-surkai-{datetime.now().strftime('%Y-%m-%d')}-v{prompt_data['version']}",
        # experiment_name=f"dharma-{datetime.now().strftime('%Y-%m-%d')}-v0.3",
        experiment_description="gemini-2.5-flash",
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        # precomputed_responses=precomputed_responses_dict,
        # upload_to_bq=False,
        output_dir=EXPERIMENT_DATA_PATH,
        timeout=180,
        polling_interval=5,
        rate_limit_requests_per_minute=1000,
        # reasoning_engine_id="3875545391445311488", #DHARMA_REASONING_ENGINE_ID
    )
    logger.info(f"✅ Runner pronto para o experimento: '{runner.experiment_name}'")
    for i in range(1):
        await runner.run(loader)


if __name__ == "__main__":
    try:
        asyncio.run(run_experiment())
    except Exception as e:
        logging.getLogger(__name__).error(
            f"Ocorreu um erro fatal durante a execução do experimento: {e}",
            exc_info=True,
        )
