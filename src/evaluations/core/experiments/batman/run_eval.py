import asyncio
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
from src.evaluations.core.experiments.batman.evaluators import (
    PersonaAdherenceEvaluator,
    ConversationalReasoningEvaluator,
    ConversationalMemoryEvaluator,
    SemanticCorrectnessEvaluator,
)
from src.evaluations.core.eval.evaluators.llm_guided_conversation import (
    LLMGuidedConversation,
)

EXPERIMENT_DATA_PATH = Path(__file__).parent / "data"


async def run_experiment():
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    """
    logger.info("--- Configurando o Experimento Unificado (Arquitetura Refatorada) ---")

    # --- 1. Definição do Dataset ---
    dataframe = pd.DataFrame(UNIFIED_TEST_DATA)
    loader = DataLoader(
        source=dataframe,
        id_col="id",
        prompt_col="initial_prompt",
        dataset_name="Batman Unified Conversation Test",
        dataset_description="Um teste unificado para avaliar raciocínio, memória, aderência à persona e correção semântica em uma única conversa.",
        metadata_cols=[
            "persona",
            "judge_context",
            "golden_response_multiple_shot",
            "golden_response_one_shot",
        ],
    )
    logger.info(
        f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    # --- 2. Definição do Agente (Metadados do Experimento) ---
    agent_config = CreateAgentRequest(
        model="google_ai/gemini-2.5-flash-lite-preview-06-17",
        system="Você é o Batman, um herói sombrio, direto e que não confia em ninguém",
        tools=["google_search"],
        user_number="evaluation_user",
        name="BatmanUnifiedAgent",
        tags=["batman", "unified_test"],
    )
    logger.info(f"✅ Agente a ser avaliado configurado: {agent_config.name}")

    # --- 3. Definição da Suíte de Avaliação ---
    judge_client = AzureOpenAIClient(model_name="gpt-4o")
    # judge_client = GeminiAIClient(model_name="gemini-1.5-flash-latest")

    # Instancia os avaliadores que serão executados
    evaluators_to_run = [
        LLMGuidedConversation(judge_client),
        ConversationalReasoningEvaluator(judge_client),
        ConversationalMemoryEvaluator(judge_client),
        PersonaAdherenceEvaluator(judge_client),
        SemanticCorrectnessEvaluator(judge_client),
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
        "agent_config": agent_config.model_dump(exclude_none=True),
        "judge_model": judge_client.model_name,
        "judges_prompts": judges_prompts,
    }

    # --- 4. Carregamento de Respostas Pré-computadas (Opcional) ---
    PRECOMPUTED_RESPONSES_PATH = EXPERIMENT_DATA_PATH / "precomputed_responses.json"
    precomputed_responses_dict: Optional[Dict[str, Dict[str, Any]]] = None
    if PRECOMPUTED_RESPONSES_PATH and PRECOMPUTED_RESPONSES_PATH.exists():
        try:
            with open(PRECOMPUTED_RESPONSES_PATH, "r", encoding="utf-8") as f:
                responses = json.load(f)
                precomputed_responses_dict = {item["id"]: item for item in responses}
            logger.info(
                f"✅ Respostas pré-computadas carregadas de {PRECOMPUTED_RESPONSES_PATH}"
            )
        except Exception as e:
            logger.error(f"❌ Erro ao carregar {PRECOMPUTED_RESPONSES_PATH}: {e}")

    # --- 5. Configuração e Execução do Runner ---
    MAX_CONCURRENCY = 10

    runner = AsyncExperimentRunner(
        experiment_name="Batman_Unified_Eval_v3_Refactored",
        experiment_description="Avaliação com ConversationEvaluator plugável.",
        metadata=metadata,
        agent_config=agent_config.model_dump(exclude_none=True),
        evaluators=evaluators_to_run,
        judge_client=judge_client,
        max_concurrency=MAX_CONCURRENCY,
        precomputed_responses=precomputed_responses_dict,
        upload_to_bq=False,
        output_dir=EXPERIMENT_DATA_PATH,
    )
    logger.info(f"✅ Runner pronto para o experimento: '{runner.experiment_name}'")
    await runner.run(loader)


if __name__ == "__main__":
    try:
        asyncio.run(run_experiment())
    except Exception as e:
        logging.getLogger(__name__).error(
            f"Ocorreu um erro fatal durante a execução do experimento: {e}",
            exc_info=True,
        )
