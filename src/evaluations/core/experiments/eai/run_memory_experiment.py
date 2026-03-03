import asyncio
import logging
from pathlib import Path
from datetime import datetime

from src.evaluations.core.eval import (
    DataLoader,
    AzureOpenAIClient,
    AsyncExperimentRunner,
)
from src.utils.log import logger

from src.evaluations.core.experiments.eai.evaluators import (
    MemoryTestLLMGuidedConversation,
    SearchCallsAfterSecondQuestionEvaluator,
    CriticalFactAccuracyEvaluator,
    HallucinationFlagEvaluator,
    TokenUsageTotalEvaluator,
)
from src.evaluations.core.experiments.eai.evaluators.prompts import (
    prompt_data,
)

EXPERIMENT_DATA_PATH = Path(__file__).parent / "data"

# ========================================
# CONFIGURAÇÃO DO EXPERIMENTO
# ========================================

# Escolha qual versão rodar: "v1" ou "v2"
VERSION = "v2"  # Altere aqui para "v2" quando quiser testar memória restrita

# IDs dos reasoning engines (configure com seus IDs reais ou use None para padrão)
REASONING_ENGINE_IDS = {
    "v1": None,  # Memória Total - None usa o engine padrão
    "v2": "5697391078693404672",  # Memória Restrita - ou None para padrão
}

# Descrições automáticas por versão
DESCRIPTIONS = {
    "v1": "Full memory - includes tool_call and tool_response",
    "v2": "Restricted memory - only user_message, reasoning, ia_response",
}

# ========================================


async def run_experiment(
    version: str = "v1",
    reasoning_engine_id: str = None,
    description: str = "",
):
    """
    Executa o experimento de teste de memória para avaliar o impacto da
    retenção de tool_call e tool_response no histórico de conversa.
    
    Args:
        version: Versão da configuração ('v1' = memória total, 'v2' = memória restrita)
        reasoning_engine_id: ID do reasoning engine a ser usado
        description: Descrição adicional para o experimento
    """
    logger.info(f"--- Configurando o Experimento de Memória - {version.upper()} ---")

    # --- 1. Configuração do DataLoader ---
    loader = DataLoader(
        source="https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=969839054#gid=969839054",  # Multi-turn memory test
        # number_rows=3,  # Descomente para testar com menos linhas
        id_col="id_original",
        prompt_col="initial_user_message",
        dataset_name="Multi-Turn Memory Test",
        dataset_description="Dataset de avaliação de memória multi-turno com dependência factual",
        metadata_cols=[
            "tema",
            "secondary_user_message",
            "dependency_type",
            "critical_fact_reused",
            "fact_type",
            "memory_sensitivity_level",
        ],
        # upload_to_bq=False,  # Descomente para não fazer upload ao BigQuery
    )
    logger.info(
        f"✅ DataLoader configurado para o dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    # --- 2. Configuração do Cliente Judge (LLM) ---
    judge_client = AzureOpenAIClient(model_name="gpt-4o")
    # judge_client = GeminiAIClient(model_name="gemini-1.5-flash-latest")

    # --- 3. Definição da Suíte de Avaliação ---
    evaluators_to_run = [
        MemoryTestLLMGuidedConversation(judge_client),
        SearchCallsAfterSecondQuestionEvaluator(judge_client),
        CriticalFactAccuracyEvaluator(judge_client),
        HallucinationFlagEvaluator(judge_client),
        TokenUsageTotalEvaluator(judge_client),
    ]

    evaluator_names = [e.name for e in evaluators_to_run]
    logger.info(f"✅ Suíte de avaliações configurada para rodar: {evaluator_names}")

    # --- 4. Coleta de Metadados do Experimento ---
    judges_prompts = {
        evaluator.name: evaluator.PROMPT_TEMPLATE
        for evaluator in evaluators_to_run
        if hasattr(evaluator, "PROMPT_TEMPLATE")
    }

    metadata = {
        "version": version,
        "version_description": description,
        "system_prompt": prompt_data["prompt"],
        "prompt_version": prompt_data["version"],
        "judge_model": judge_client.model_name,
        "judges_prompts": judges_prompts,
        "experiment_type": "memory_test",
        "memory_config": {
            "v1": "Full memory (includes tool_call and tool_response)",
            "v2": "Restricted memory (only user_message, reasoning, ia_response)",
        }.get(version, "Unknown"),
    }

    # --- 5. Configuração e Execução do Runner ---
    MAX_CONCURRENCY = 20

    runner = AsyncExperimentRunner(
        experiment_name=f"eai-memory-{version}-{datetime.now().strftime('%Y-%m-%d')}",
        experiment_description=description or f"Memory test - {version}",
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        # upload_to_bq=False,  # Descomente para não fazer upload ao BigQuery
        output_dir=EXPERIMENT_DATA_PATH,
        rate_limit_requests_per_minute=1000,
        reasoning_engine_id=reasoning_engine_id,
    )
    logger.info(f"✅ Runner pronto para o experimento: '{runner.experiment_name}'")
    
    # Executa o experimento
    await runner.run(loader)


if __name__ == "__main__":
    """
    Para rodar o experimento:
    
    1. Configure a VERSION no topo do arquivo ("v1" ou "v2")
    2. Configure os REASONING_ENGINE_IDS com seus IDs reais
    3. Execute: uv run src/evaluations/core/experiments/eai/run_memory_experiment.py
    """
    
    # Valida a configuração
    if VERSION not in ["v1", "v2"]:
        print(f"❌ Erro: VERSION deve ser 'v1' ou 'v2', mas está configurada como '{VERSION}'")
        print("   Edite a variável VERSION no topo do arquivo.")
        exit(1)
    
    # Pega o reasoning_engine_id (pode ser None para usar o padrão)
    reasoning_engine_id = REASONING_ENGINE_IDS.get(VERSION)
    
    description = DESCRIPTIONS.get(VERSION, f"Memory test - {VERSION}")
    
    # Exibe a configuração atual
    print("=" * 60)
    print(f"🚀 EXPERIMENTO DE MEMÓRIA - {VERSION.upper()}")
    print("=" * 60)
    print(f"Versão: {VERSION}")
    print(f"Descrição: {description}")
    print(f"Reasoning Engine ID: {reasoning_engine_id or 'Padrão (None)'}")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(run_experiment(
            version=VERSION,
            reasoning_engine_id=reasoning_engine_id,
            description=description
        ))
    except Exception as e:
        logging.getLogger(__name__).error(
            f"Ocorreu um erro fatal durante a execução do experimento: {e}",
            exc_info=True,
        )
