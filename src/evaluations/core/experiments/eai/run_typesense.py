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
    TypesenseFormatEvaluator,
    SearchPrecisionEvaluator,
    SearchRecallEvaluator,
    SearchAveragePrecisionEvaluator,
    AnswerCompletenessOldEvaluator,
)
from src.evaluations.core.experiments.eai.evaluators.prompts import (
    prompt_data,
)

from src.evaluations.core.experiments.eai.evaluators.agent_config import (
    agent_config_data,
)

from src.utils.infisical import update_typesense_parameters

EXPERIMENT_DATA_PATH = Path(__file__).parent / "data"
import time


async def run_experiment(typesense_params: Dict[str, Any]):
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    """
    await update_typesense_parameters(parameters=typesense_params)
    logger.info(
        "✅ Parâmetros do Typesense atualizados no Infisical com sucesso. Aguardando 5 minutos..."
    )
    time.sleep(
        5 * 60
    )  # espera 5 minutos para garantir que o Infisical atualize os parâmetros

    logger.info("--- Configurando o Experimento Unificado (Arquitetura Refatorada) ---")

    loader = DataLoader(
        source="https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=370781785",  # golden dataset
        # number_rows=3,
        id_col="id",
        prompt_col="mensagem_whatsapp_simulada",
        dataset_name="Golden Dataset 2.0 - 2026.1 - Typesense",
        dataset_description="Dataset de avaliacao de servicos",
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
        AnswerCompletenessEvaluator(judge_client),
        AnswerCompletenessOldEvaluator(judge_client),
        AnswerAddressingEvaluator(judge_client),
        ClarityEvaluator(judge_client),
        ActivateSearchEvaluator(judge_client),
        WhatsAppFormatEvaluator(judge_client),
        ProactivityEvaluator(judge_client),
        MessageLengthEvaluator(judge_client),
        TypesenseFormatEvaluator(judge_client),
        SearchPrecisionEvaluator(
            judge_client
        ),  # quantidade de documentos relevantes retornados / total de documentos retornados
        SearchRecallEvaluator(
            judge_client
        ),  # quantidade de documentos relevantes retornados / total de documentos relevantes existentes
        SearchAveragePrecisionEvaluator(
            judge_client
        ),  # precisão considerando o ranking dos documentos retornados. Maior peso para documentos relevantes no topo da lista
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
    typesense_params_description = {
        "type": typesense_params.get("type"),
        "threshold_semantic": typesense_params.get("threshold_semantic"),
        "threshold_hybrid": typesense_params.get("threshold_hybrid"),
        "alpha": typesense_params.get("alpha"),
    }
    runner = AsyncExperimentRunner(
        experiment_name=f"eai-{datetime.now().strftime('%Y-%m-%d-%H%M')}-v{prompt_data['version']}",
        experiment_description=f"{json.dumps(typesense_params_description)}",
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        output_dir=EXPERIMENT_DATA_PATH,
        timeout=300,
        polling_interval=5,
        rate_limit_requests_per_minute=1000,
    )
    logger.info(f"✅ Runner pronto para o experimento: '{runner.experiment_name}'")
    for i in range(1):
        await runner.run(loader)


if __name__ == "__main__":
    # generate a set of Typesense parameters to test
    typesense_params_list = []
    # 1. SEMANTIC: Apenas 11 combinações
    for ts in [0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9]:  # Focar na zona de "sucesso"
        typesense_params_list.append(
            {
                "type": "semantic",
                "threshold_semantic": ts,
                "threshold_hybrid": 0.7,  # Irrelevante aqui
                "alpha": 0.7,  # Irrelevante aqui
                "threshold_keyword": 1,
                "threshold_ai": 0.85,
                "page": 1,
                "per_page": 10,
            }
        )
    # 2. HYBRID: Focar na relação entre Alpha e Thresholds
    for alpha in [0.3, 0.5, 0.7, 0.8]:
        for th in [0.5, 0.7, 0.8]:
            typesense_params_list.append(
                {
                    "type": "hybrid",
                    "threshold_semantic": th,
                    "threshold_hybrid": th,
                    "alpha": alpha,
                    "threshold_keyword": 1,
                    "threshold_ai": 0.85,
                    "page": 1,
                    "per_page": 10,
                }
            )
    for i, typesense_params in enumerate(typesense_params_list):
        logger.info(
            f"🚀 Iniciando experimento {i + 1} de {len(typesense_params_list)}: {typesense_params}"
        )
        try:
            asyncio.run(run_experiment(typesense_params=typesense_params))
        except Exception as e:
            logging.getLogger(__name__).error(
                f"Ocorreu um erro fatal durante a execução do experimento: {e}",
                exc_info=True,
            )
