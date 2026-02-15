#!/usr/bin/env python3
"""
Evaluation script for Defesa Civil LLM dataset.
Tests the agent's ability to provide emergency response information for Rio de Janeiro.
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime

from src.evaluations.core.eval import (
    DataLoader,
    AzureOpenAIClient,
    AsyncExperimentRunner,
)
from src.utils.log import logger

# Import evaluators (to be created)
from src.evaluations.core.experiments.defesa_civil.evaluators import (
    DefesaCivilSemanticCorrectnessEvaluator,
    DefesaCivilCompletenessEvaluator,
    DefesaCivilCrisisResponseEvaluator,
)
from src.evaluations.core.experiments.eai.evaluators.prompts import (
    prompt_data,
)

EXPERIMENT_DATA_PATH = Path(__file__).parent / "data"


async def run_experiment():
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    """
    logger.info("--- Configurando o Experimento Defesa Civil (Emergency Response) ---")

    # Configure DataLoader for the local CSV dataset
    dataset_path = (
        Path(__file__).parent.parent.parent.parent.parent / "dataset_avaliacao_llm.csv"
    )

    loader = DataLoader(
        source=dataset_path,
        number_rows=2,  # Testing with 2 rows first
        id_col=None,  # Will auto-generate IDs
        prompt_col="pergunta",
        dataset_name="Defesa Civil Emergency Response Dataset",
        dataset_description="Dataset para avaliação de respostas de emergências hidrológicas.",
        metadata_cols=[
            "resposta_esperada",
            "complexidade",
            "urgencia",
            "contexto",
            "tools",
            "criterios_avaliados",
        ],
        upload_to_bq=False,  # Set to False for local development
    )
    logger.info(
        f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    # --- Judge Client Configuration ---
    judge_client = AzureOpenAIClient(model_name="gpt-4o")

    # Instancia os avaliadores que serão executados
    evaluators_to_run = [
        DefesaCivilSemanticCorrectnessEvaluator(judge_client),
        DefesaCivilCompletenessEvaluator(judge_client),
        DefesaCivilCrisisResponseEvaluator(judge_client),
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
        "system_prompt": prompt_data["prompt"],
        "system_prompt_version": prompt_data["version"],
        "judge_model": judge_client.model_name,
        "judges_prompts": judges_prompts,
        "dataset_path": str(dataset_path),
    }

    # --- Configuração e Execução do Runner ---
    MAX_CONCURRENCY = 10  # Lower for emergency response evaluation

    runner = AsyncExperimentRunner(
        experiment_name=f"defesa-civil-{datetime.now().strftime('%Y-%m-%d')}-v{prompt_data['version']}",
        experiment_description="Avaliação de respostas de emergências hidrológicas.",
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        # upload_to_bq=False,  # Set to False for local development
        output_dir=EXPERIMENT_DATA_PATH,
        rate_limit_requests_per_minute=1000,
    )
    logger.info(f"✅ Runner pronto para o experimento: '{runner.experiment_name}'")

    # Run the experiment once
    await runner.run(loader)


if __name__ == "__main__":
    try:
        asyncio.run(run_experiment())
    except Exception as e:
        logging.getLogger(__name__).error(
            f"Ocorreu um erro fatal durante a execução do experimento: {e}",
            exc_info=True,
        )
