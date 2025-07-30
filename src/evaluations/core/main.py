import asyncio
import json
import os
import pandas as pd

# Utilizando imports absolutos a partir da raiz do projeto (src)
from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import EvaluatedLLMClient, AzureOpenAIClient
from src.evaluations.core.evals import Evals
from src.evaluations.core.runner import AsyncExperimentRunner
from src.services.eai_gateway.api import CreateAgentRequest
from src.evaluations.core.test_data import TEST_DATA


async def run_experiment():
    """
    Ponto de entrada principal para configurar e executar um experimento de avaliação.
    """
    print("--- 1. Configurando o Experimento ---")

    # --- Configuração do DataLoader ---
    # Cria um DataFrame de teste local para o experimento, agora com 50 exemplos.

    dataframe = pd.DataFrame(TEST_DATA)

    loader = DataLoader(
        source=dataframe.head(50),
        id_col="id",
        metadata_cols=["prompt", "golden_response", "persona", "keywords"],
    )
    print("✅ DataLoader configurado com um DataFrame local de 50 exemplos.")

    # --- Configuração do Agente a ser Avaliado ---
    agent_config = CreateAgentRequest(
        model="google_ai/gemini-2.5-flash-lite-preview-06-17",
        system="Você é o Batman, um herói sombrio e direto.",
        tools=["google_search"],
        user_number="evaluation_user",
        name="BatmanEvaluationAgent",
        tags=["batman"],
    )
    evaluated_client = EvaluatedLLMClient(agent_config=agent_config)
    print(f"✅ Agente a ser avaliado configurado: {agent_config.name}")

    # --- Configuração do Juiz (instanciado uma única vez) ---
    judge_client = AzureOpenAIClient(model_name="gpt-4o")
    print(f"✅ Juiz LLM configurado: {judge_client.model_name}")

    # --- Configuração da Suíte de Avaliações ---
    evaluation_suite = Evals(judge_client=judge_client)

    # Define a lista de nomes das métricas que queremos rodar.
    metrics_to_run = ["semantic_correctness", "persona_adherence", "keyword_match"]
    print(f"✅ Suíte de avaliações configurada para rodar: {metrics_to_run}")

    # --- Configuração do Runner ---
    runner = AsyncExperimentRunner(
        evaluated_client=evaluated_client,
        evaluation_suite=evaluation_suite,
        metrics_to_run=metrics_to_run,
    )
    print("✅ Runner pronto para execução.")

    # --- 2. Execução do Experimento ---
    print("\n--- 2. Iniciando a Execução do Experimento ---")
    results = await runner.run(loader)

    # --- 3. Salvando os Resultados ---
    print("\n--- 3. Salvando os Resultados ---")
    output_dir = "evaluation_results"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"results_{agent_config.name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Experimento concluído! Resultados salvos em: {output_path}")


if __name__ == "__main__":
    try:
        asyncio.run(run_experiment())
    except Exception as e:
        print(f"Ocorreu um erro fatal durante a execução do experimento: {e}")
