import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime

from src.evaluations.core.eval import (
    DataLoader,
    AzureOpenAIClient,
    GeminiAIClient,
    AsyncExperimentRunner,
)
from src.utils.log import logger

# Importa os novos avaliadores de desastres
from src.evaluations.core.experiments.eai.evaluators import (
    ToolUsageEvaluator,
    CivilDefenseDisasterResponseEvaluator,
    ResponseQualityEvaluator,
)
from src.evaluations.core.experiments.eai.evaluators.prompts import (
    prompt_data,
)


EXPERIMENT_DATA_PATH = Path(__file__).parent / "data"


async def run_experiment():
    """
    Experimento focado em avaliação de respostas sobre desastres hidrológicos.
    Avalia: uso de ferramentas, qualidade de resposta, e conhecimentos de defesa civil.
    """
    logger.info("--- Configurando Experimento de Avaliação de Desastres ---")

    # --- 1. Configuração do Dataset ---
    loader = DataLoader(
        source=str(EXPERIMENT_DATA_PATH / "disaster_questions.csv"),  # Dataset local de perguntas sobre desastres
        # number_rows=10,  # Descomente para testar com menos linhas
        id_col="id",
        prompt_col="mensagem_whatsapp_simulada",
        dataset_name="Disaster Response Questions",
        dataset_description="Dataset de avaliação de respostas sobre desastres hidrológicos com tools de COR e equipamentos",
        metadata_cols=[
            "golden_answer",
            "golden_tool",
            "equipment_category",
        ],
    )
    logger.info(
        f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    # --- 2. Configuração do Judge (LLM para avaliação) ---
    judge_client = AzureOpenAIClient(model_name="gpt-4o")
    # judge_client = GeminiAIClient(model_name="gemini-1.5-flash-latest")

    # --- 3. Definição dos Avaliadores ---
    evaluators_to_run = [
        ToolUsageEvaluator(judge_client),
        CivilDefenseDisasterResponseEvaluator(judge_client),
        ResponseQualityEvaluator(judge_client),
    ]

    evaluator_names = [e.name for e in evaluators_to_run]
    logger.info(f"✅ Avaliadores configurados: {evaluator_names}")

    # --- 4. Metadados do Experimento ---
    # Coleta os prompts de cada avaliador para documentação
    judges_prompts = {
        evaluator.name: evaluator.PROMPT_TEMPLATE
        for evaluator in evaluators_to_run
        if hasattr(evaluator, "PROMPT_TEMPLATE")
    }

    metadata = {
        "system_prompt": prompt_data["prompt"],
        "judge_model": judge_client.model_name,
        "judges_prompts": judges_prompts,
        "experiment_focus": "Disaster Response Evaluation (Tool Usage, Civil Defense, Quality)",
    }

    # --- 5. Configuração e Execução do Runner ---
    MAX_CONCURRENCY = int(os.getenv("EAI_MAX_CONCURRENCY", "12"))
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(
        os.getenv("EAI_RATE_LIMIT_RPM", "1200")
    )
    MIN_SECONDS_BETWEEN_REQUESTS = float(
        os.getenv("DISASTER_EVAL_MIN_SECONDS_BETWEEN_REQUESTS", "3.0")
    )
    logger.info(
        "Configuração de execução: %s concurrency, %s req/min, %.2fs entre requisições",
        MAX_CONCURRENCY,
        RATE_LIMIT_REQUESTS_PER_MINUTE,
        MIN_SECONDS_BETWEEN_REQUESTS,
    )

    runner = AsyncExperimentRunner(
        experiment_name=f"disaster-eval-{datetime.now().strftime('%Y-%m-%d')}-{prompt_data['version']}",
        experiment_description="Avaliação de respostas sobre desastres hidrológicos com foco em defesa civil",
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        output_dir=EXPERIMENT_DATA_PATH,
        timeout=180,
        polling_interval=5,
        rate_limit_requests_per_minute=RATE_LIMIT_REQUESTS_PER_MINUTE,
    )
    logger.info(f"✅ Runner pronto para o experimento: '{runner.experiment_name}'")

    # Executa o experimento
    await runner.run(loader)
    logger.info("✅ Experimento concluído!")


if __name__ == "__main__":
    try:
        asyncio.run(run_experiment())
    except Exception as e:
        logging.getLogger(__name__).error(
            f"Ocorreu um erro fatal durante a execução do experimento: {e}",
            exc_info=True,
        )