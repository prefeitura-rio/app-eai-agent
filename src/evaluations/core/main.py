import asyncio
import pandas as pd
import logging

# Utilizando imports absolutos a partir da raiz do projeto (src)
from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import AzureOpenAIClient
from src.evaluations.core.evals import Evals
from src.evaluations.core.runner import AsyncExperimentRunner
from src.services.eai_gateway.api import CreateAgentRequest
from src.evaluations.core.test_data import CONVERSATIONAL_TEST_DATA


async def run_experiment():
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    """
    # Configuração básica do logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    logger.info("--- Configurando o Experimento ---")

    # --- 1. Definição do Dataset ---
    dataframe = pd.DataFrame(CONVERSATIONAL_TEST_DATA)
    loader = DataLoader(
        source=dataframe,
        id_col="id",
        prompt_col="initial_prompt",
        dataset_name="Batman Conversational Test",
        dataset_description="Um teste para avaliar a capacidade de raciocínio do Batman em uma conversa curta.",
        metadata_cols=[
            "judge_context",
            "golden_response_summary",
            "persona",
        ],
    )
    logger.info(
        f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    # --- 2. Definição do Agente (Metadados do Experimento) ---
    agent_config = CreateAgentRequest(
        model="google_ai/gemini-2.5-flash-lite-preview-06-17",
        system="Você é o Batman, um herói sombrio e direto que busca conectar informações. Detecte o idioma que o usuário está falando e responda na mesma língua.",
        tools=[],
        user_number="evaluation_user",
        name="BatmanConversationalAgent",
        tags=["batman", "conversational"],
    )
    logger.info(f"✅ Agente a ser avaliado configurado: {agent_config.name}")

    # --- 3. Definição da Suíte de Avaliação ---
    judge_client = AzureOpenAIClient(model_name="gpt-4o")
    evaluation_suite = Evals(judge_client=judge_client)
    metrics_to_run = ["conversational_reasoning"]
    logger.info(f"✅ Suíte de avaliações configurada para rodar: {metrics_to_run}")

    # --- 4. Configuração e Execução do Runner ---
    runner = AsyncExperimentRunner(
        experiment_name="BatmanConversationalAgent_Eval_v2",
        experiment_description="Avaliação da capacidade de raciocínio conversacional do Batman com a nova estrutura de runner.",
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
