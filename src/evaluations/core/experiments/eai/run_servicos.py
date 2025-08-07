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

# Importa os avaliadores modulares
from src.evaluations.core.experiments.eai.evaluators import (
    GoldenLinkInAnswerEvaluator,
    GoldenLinkInToolCallingEvaluator,
    AnswerCompletenessEvaluator,
    AnswerAddressingEvaluator,
    ClarityEvaluator,
    ActivateSearchEvaluator,
    WhatsAppFormatEvaluator,
)
from src.evaluations.core.experiments.eai.evaluators.prompts import (
    SYSTEM_PROMPT,
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
        dataset_name="Golden Dataset 10 samples",
        dataset_description="Dataset de avaliacao de servicos",
        metadata_cols=[
            "golden_links_list",
            "golden_answer",
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
        GoldenLinkInAnswerEvaluator(judge_client),
        GoldenLinkInToolCallingEvaluator(judge_client),
        AnswerCompletenessEvaluator(judge_client),
        AnswerAddressingEvaluator(judge_client),
        ClarityEvaluator(judge_client),
        ActivateSearchEvaluator(judge_client),
        WhatsAppFormatEvaluator(judge_client),
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
        # "agent_config": agent_config.model_dump(exclude_none=True),
        "system_prompt": SYSTEM_PROMPT,
        "judge_model": judge_client.model_name,
        "judges_prompts": judges_prompts,
    }

    # --- 5. Configuração e Execução do Runner ---
    MAX_CONCURRENCY = 10

    runner = AsyncExperimentRunner(
        experiment_name="eai-2025-08-07-v59",
        experiment_description="Test",
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        # precomputed_responses=precomputed_responses_dict,
        # upload_to_bq=False,
        output_dir=EXPERIMENT_DATA_PATH,
        timeout=180,
        polling_interval=5,
        rate_limit_requests_per_minute=10,
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
