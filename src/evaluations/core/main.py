import asyncio
import pandas as pd
import logging

from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import AzureOpenAIClient
from src.evaluations.core.evals import Evals
from src.evaluations.core.runner import AsyncExperimentRunner
from src.services.eai_gateway.api import CreateAgentRequest
from src.evaluations.core.test_data import UNIFIED_TEST_DATA


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
        source=dataframe,
        id_col="id",
        prompt_col="initial_prompt",
        dataset_name="Batman Unified Conversation Test",
        dataset_description="Um teste unificado para avaliar raciocínio, memória, aderência à persona e correção semântica em uma única conversa.",
        metadata_cols=["persona", "judge_context", "golden_summary", "golden_response"],
    )
    logger.info(f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'")

    # --- 2. Definição do Agente (Metadados do Experimento) ---
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
    evaluation_suite = Evals(judge_client=judge_client)
    
    # Define todas as métricas que serão executadas
    metrics_to_run = [
        "conversational_reasoning", 
        "conversational_memory",
        "persona_adherence",
        "semantic_correctness"
    ]
    logger.info(f"✅ Suíte de avaliações configurada para rodar: {metrics_to_run}")

    # --- 4. Configuração e Execução do Runner ---
    runner = AsyncExperimentRunner(
        experiment_name="Batman_Unified_Eval_v1",
        experiment_description="Avaliação de múltiplas facetas em uma única conversa, com julgamentos em paralelo.",
        metadata=agent_config.model_dump(exclude_none=True),
        evaluation_suite=evaluation_suite,
        metrics_to_run=metrics_to_run,
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