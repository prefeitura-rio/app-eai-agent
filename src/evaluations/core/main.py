import asyncio
import pandas as pd
import logging
import json
from typing import Dict, Any, Optional

from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import AzureOpenAIClient, GeminiAIClient
from src.evaluations.core.runner import AsyncExperimentRunner
from src.evaluations.core.conversation import ConversationHandler
from src.services.eai_gateway.api import CreateAgentRequest
from src.evaluations.core.data.test_data import UNIFIED_TEST_DATA
from src.utils.log import logger

# Importa os avaliadores modulares
from src.evaluations.core.evaluators.persona_adherence import (
    PersonaAdherenceEvaluator,
)
from src.evaluations.core.evaluators.conversational_reasoning import (
    ConversationalReasoningEvaluator,
)
from src.evaluations.core.evaluators.conversational_memory import (
    ConversationalMemoryEvaluator,
)
from src.evaluations.core.evaluators.semantic_correctness import (
    SemanticCorrectnessEvaluator,
)


async def run_experiment():
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    """
    logger.info("--- Configurando o Experimento Unificado (Arquitetura Refatorada) ---")

    # --- 1. Definição do Dataset ---
    dataframe = pd.DataFrame(UNIFIED_TEST_DATA)
    loader = DataLoader(
        source=dataframe.head(1),
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
    # Adiciona o prompt de condução da conversa, que agora está em ConversationHandler
    judges_prompts["conversational_agent"] = (
        ConversationHandler.CONVERSATIONAL_JUDGE_PROMPT
    )

    metadata = {
        "agent_config": agent_config.model_dump(exclude_none=True),
        "judge_model": judge_client.model_name,
        "judges_prompts": judges_prompts,
    }

    # --- 4. Carregamento de Respostas Pré-computadas (Opcional) ---
    PRECOMPUTED_RESPONSES_PATH = (
        "./src/evaluations/core/data/precomputed_responses.json"  # ou None
    )
    precomputed_responses_dict: Optional[Dict[str, Dict[str, Any]]] = None
    if PRECOMPUTED_RESPONSES_PATH:
        try:
            with open(PRECOMPUTED_RESPONSES_PATH, "r", encoding="utf-8") as f:
                responses = json.load(f)
                precomputed_responses_dict = {item["id"]: item for item in responses}
            logger.info(
                f"✅ Respostas pré-computadas carregadas de {PRECOMPUTED_RESPONSES_PATH}"
            )
        except FileNotFoundError:
            logger.warning(
                f"⚠️ Arquivo de respostas pré-computadas não encontrado: {PRECOMPUTED_RESPONSES_PATH}"
            )
        except Exception as e:
            logger.error(f"❌ Erro ao carregar {PRECOMPUTED_RESPONSES_PATH}: {e}")

    # --- 5. Configuração e Execução do Runner ---
    MAX_CONCURRENCY = 10

    runner = AsyncExperimentRunner(
        experiment_name="Batman_Unified_Eval_v2_Refactored",
        experiment_description="Avaliação de múltiplas facetas com arquitetura de avaliadores plugáveis.",
        metadata=metadata,
        agent_config=agent_config.model_dump(exclude_none=True),
        evaluators=evaluators_to_run,
        judge_client=judge_client,
        max_concurrency=MAX_CONCURRENCY,
        # precomputed_responses=precomputed_responses_dict,
        upload_to_bq=False,
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
