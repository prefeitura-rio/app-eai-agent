import asyncio
import pandas as pd
import logging
import json
from typing import Dict, Any, Optional

from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import AzureOpenAIClient, GeminiAIClient
from src.evaluations.core.evals import Evals
from src.evaluations.core.runner import AsyncExperimentRunner
from src.services.eai_gateway.api import CreateAgentRequest
from src.evaluations.core.test_data import UNIFIED_TEST_DATA
from src.evaluations.core.prompt_judges import (
    CONVERSATIONAL_JUDGE_PROMPT,
    FINAL_CONVERSATIONAL_JUDGEMENT_PROMPT,
    FINAL_MEMORY_JUDGEMENT_PROMPT,
    SEMANTIC_CORRECTNESS_PROMPT,
    PERSONA_ADHERENCE_PROMPT,
)


async def run_experiment():
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    logger.info("--- Configurando o Experimento Unificado ---")

    # --- 1. Definição do Dataset ---
    dataframe = pd.DataFrame(UNIFIED_TEST_DATA)
    loader = DataLoader(
        source=dataframe.head(3),
        id_col="id",
        prompt_col="initial_prompt",
        dataset_name="Batman Unified Conversation Test",
        dataset_description="Um teste unificado para avaliar raciocínio, memória, aderência à persona e correção semântica em uma única conversa.",
        metadata_cols=["persona", "judge_context", "golden_summary", "golden_response"],
    )
    logger.info(
        f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    # --- 2. Definição do Agente (Metadados do Experimento) ---
    # Se estiver usando respostas pré-computadas, estes metadados podem ser apenas para registro.
    agent_config = CreateAgentRequest(
        model="google_ai/gemini-2.5-flash-lite-preview-06-17",
        system="Você é o Batman, um herói sombrio, direto e que não confia em ninguém.",
        tools=[],
        user_number="evaluation_user",
        name="BatmanUnifiedAgent",
        tags=["batman", "unified_test"],
    )
    logger.info(f"✅ Agente a ser avaliado configurado: {agent_config.name}")

    # --- 3. Definição da Suíte de Avaliação ---
    judge_client = AzureOpenAIClient(model_name="gpt-4o")
    # judge_client = GeminiAIClient(model_name="gemini-2.5-flash")
    evaluation_suite = Evals(judge_client=judge_client)

    metrics_to_run = [
        "conversational_reasoning",
        "conversational_memory",
        "persona_adherence",
        "semantic_correctness",
    ]
    logger.info(f"✅ Suíte de avaliações configurada para rodar: {metrics_to_run}")

    metadata = {
        "agent_config": agent_config.model_dump(exclude_none=True),
        "judges_prompts": {
            "conversational_agent": CONVERSATIONAL_JUDGE_PROMPT,
            "conversational_reasoning": FINAL_CONVERSATIONAL_JUDGEMENT_PROMPT,
            "conversational_memory": FINAL_MEMORY_JUDGEMENT_PROMPT,
            "persona_adherence": PERSONA_ADHERENCE_PROMPT,
            "semantic_correctness": SEMANTIC_CORRECTNESS_PROMPT,
        },
    }

    # --- 4. Carregamento de Respostas Pré-computadas (Opcional) ---
    PRECOMPUTED_RESPONSES_PATH = "precomputed_responses.json"  # ou None
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
    runner = AsyncExperimentRunner(
        experiment_name="Batman_Unified_Eval_v1",
        experiment_description="Avaliação de múltiplas facetas em uma única conversa, com julgamentos em paralelo.",
        metadata=metadata,
        agent_config=agent_config.model_dump(exclude_none=True),
        evaluation_suite=evaluation_suite,
        metrics_to_run=metrics_to_run,
        # precomputed_responses=precomputed_responses_dict,
    )
    logger.info(f"✅ Runner pronto para o experimento: '{runner.experiment_name}'")

    await runner.run(loader)


if __name__ == "__main__":
    try:
        asyncio.run(run_experiment())
    except Exception as e:
        # Usar logging.getLogger aqui garante que o logger exista mesmo se a configuração falhar.
        logging.getLogger(__name__).error(
            f"Ocorreu um erro fatal durante a execução do experimento: {e}",
            exc_info=True,
        )
