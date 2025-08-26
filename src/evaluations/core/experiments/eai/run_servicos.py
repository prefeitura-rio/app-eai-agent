import asyncio
import uuid
import pandas as pd
import logging
import json
import argparse
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
    GoldenLinkInAnswerEvaluator,
    GoldenLinkInToolCallingEvaluator,
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


def load_precomputed_responses_from_csv(csv_file_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load precomputed responses from the dharma.json CSV file.
    
    Args:
        csv_file_path: Path to the dharma.json file
    
    Returns:
        Dictionary mapping task IDs to precomputed responses
    """
    logger.info(f"Loading precomputed responses from: {csv_file_path}")
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        user_inputs = data.get("user_input", {})
        responses = data.get("response", {})
        
        precomputed_responses = {}
        
        for idx in user_inputs.keys():
            if idx in responses and responses[idx] is not None:
                task_id = str(int(idx) + 1)  # Convert to 1-based indexing to match dataset IDs
                precomputed_responses[task_id] = {
                    "id": task_id,
                    "one_turn_agent_message": responses[idx],
                    "one_turn_reasoning_trace": None,
                    "multi_turn_transcript": None,
                }
        
        logger.info(f"Loaded {len(precomputed_responses)} precomputed responses")
        return precomputed_responses
        
    except Exception as e:
        logger.error(f"Error loading precomputed responses: {e}")
        raise


async def run_experiment(use_precomputed: bool = False, precomputed_file: Optional[str] = None):
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    
    Args:
        use_precomputed: Whether to use precomputed responses instead of calling EAI_GATEWAY
        precomputed_file: Path to the file containing precomputed responses (e.g., dharma.json)
    """
    if use_precomputed:
        logger.info("--- Configurando o Experimento com Respostas Pré-computadas ---")
        if not precomputed_file:
            raise ValueError("precomputed_file must be provided when use_precomputed=True")
    else:
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
        ],
    )
    logger.info(
        f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    # Load precomputed responses if requested
    precomputed_responses = None
    if use_precomputed:
        precomputed_responses = load_precomputed_responses_from_csv(precomputed_file)
        logger.info(f"✅ Carregadas {len(precomputed_responses)} respostas pré-computadas")

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
        "use_precomputed": use_precomputed,
        "precomputed_file": precomputed_file if use_precomputed else None,
    }

    # --- 5. Configuração e Execução do Runner ---
    MAX_CONCURRENCY = 10

    experiment_suffix = "precomputed" if use_precomputed else "live"
    experiment_name = f"eai-{datetime.now().strftime('%Y-%m-%d')}-v{prompt_data['version']}-{experiment_suffix}"

    runner = AsyncExperimentRunner(
        experiment_name=experiment_name,
        experiment_description="gemini-2.5-flash" + (" (precomputed)" if use_precomputed else ""),
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        precomputed_responses=precomputed_responses,
        # upload_to_bq=False,
        output_dir=EXPERIMENT_DATA_PATH,
        timeout=180,
        polling_interval=5,
        rate_limit_requests_per_minute=1000,
    )
    logger.info(f"✅ Runner pronto para o experimento: '{runner.experiment_name}'")
    for i in range(1):
        await runner.run(loader)


if __name__ == "__main__":
    # Add command line argument parsing
    parser = argparse.ArgumentParser(description="Run EAI experiment with optional precomputed responses")
    parser.add_argument(
        "--use-precomputed", 
        action="store_true", 
        help="Use precomputed responses instead of calling EAI_GATEWAY"
    )
    parser.add_argument(
        "--precomputed-file",
        type=str,
        default="datasets/dharma.json",
        help="Path to file containing precomputed responses (default: datasets/dharma.json)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.use_precomputed and not Path(args.precomputed_file).exists():
        print(f"Error: Precomputed file '{args.precomputed_file}' does not exist.")
        exit(1)
    
    try:
        asyncio.run(run_experiment(
            use_precomputed=args.use_precomputed,
            precomputed_file=args.precomputed_file if args.use_precomputed else None
        ))
    except Exception as e:
        logging.getLogger(__name__).error(
            f"Ocorreu um erro fatal durante a execução do experimento: {e}",
            exc_info=True,
        )
