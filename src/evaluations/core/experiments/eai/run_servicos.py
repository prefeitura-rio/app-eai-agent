import asyncio
import logging
from pathlib import Path
from datetime import datetime

from src.evaluations.core.eval import (
    DataLoader,
    AzureOpenAIClient,
    GeminiAIClient,
    AsyncExperimentRunner,
)
from src.utils.log import logger

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
    AnswerCompletenessOldEvaluator,
)
from src.evaluations.core.experiments.eai.evaluators.prompts import (
    prompt_data,
)


EXPERIMENT_DATA_PATH = Path(__file__).parent / "data"


async def run_experiment():
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    """
    logger.info("--- Configurando o Experimento Unificado (Arquitetura Refatorada) ---")

    loader = DataLoader(
        source="https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=370781785",  # golden dataset
        # number_rows=20,
        id_col="id",
        prompt_col="mensagem_whatsapp_simulada",
        dataset_name="Rio: Comparação de Modelos - 2026.1",
        dataset_description="Dataset de comparação de modelos Rio Fast 2.5, Rio Nano 3.0 e Rio 3.0 Preview, todos utilizando o Google Search como ferramenta de busca.",
        metadata_cols=[
            "golden_documents_list",
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
        AnswerCompletenessOldEvaluator(judge_client),
        AnswerAddressingEvaluator(judge_client),
        ClarityEvaluator(judge_client),
        ActivateSearchEvaluator(judge_client),
        WhatsAppFormatEvaluator(judge_client),
        ProactivityEvaluator(judge_client),
        MessageLengthEvaluator(judge_client),
        # HasLinkEvaluator(judge_client),
        # LinkCompletenessEvaluator(judge_client),
        # ToolCallingLinkCompletenessEvaluator(judge_client),
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
        experiment_name=f"eai-{datetime.now().strftime('%Y-%m-%d-%H%M')}-v{prompt_data['version']}",
        # experiment_name=f"Rio-Preview-3.0_{datetime.now().strftime('%Y-%m-%d-%Hh%Mm')}",
        experiment_description="Eai Gemini 2.5 flash",
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        # precomputed_responses=precomputed_responses_dict, 
        # upload_to_bq=False,
        output_dir=EXPERIMENT_DATA_PATH,
        timeout=300,
        polling_interval=5,
        rate_limit_requests_per_minute=1000,
        # reasoning_engine_id="5579399187381878784", # DHARMA_REASONING_ENGINE_ID = 5579399187381878784, RIO_FAST_2.5_REASONING_ENGINE_ID = 6324744925711695872
        # reasoning_engine_id="5148050880200704000", # RIO_FAST_2.5= 6324744925711695872, RIO_NANO_3.0= 2180987966321590272, RIO_3.0_PREVIEW = 5148050880200704000
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
