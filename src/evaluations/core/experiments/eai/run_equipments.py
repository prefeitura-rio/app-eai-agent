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

from src.evaluations.core.experiments.eai.evaluators import (
    GoldenEquipmentLLMGuidedConversation,
    EquipmentsCorrectnessEvaluator,
    EquipmentsSpeedEvaluator,
    EquipmentsToolsEvaluator,
    EquipmentsCategoriesEvaluator,
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
        source="https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=1216607284#gid=1216607284",  # golden equipments
        # number_rows=3,
        id_col="id",
        prompt_col="initial_message",
        dataset_name="Golden Equipment Test",
        dataset_description="Dataset de avaliacao de equipamentos",
        metadata_cols=[
            "context",
            "golden_equipment",
            "golden_equipment_type",
            "extra_info",
        ],
        # upload_to_bq=False,
    )
    logger.info(
        f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    # --- 3. Definição da Suíte de Avaliação ---
    judge_client = AzureOpenAIClient(model_name="gpt-4o")
    # judge_client = GeminiAIClient(model_name="gemini-1.5-flash-latest")

    # Instancia os avaliadores que serão executados
    evaluators_to_run = [
        GoldenEquipmentLLMGuidedConversation(judge_client),
        EquipmentsCategoriesEvaluator(judge_client),
        EquipmentsCorrectnessEvaluator(judge_client),
        EquipmentsSpeedEvaluator(judge_client),
        EquipmentsToolsEvaluator(judge_client),
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
        experiment_description="gemini-2.5-flash",
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        # upload_to_bq=False,
        output_dir=EXPERIMENT_DATA_PATH,
        rate_limit_requests_per_minute=10000,
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
