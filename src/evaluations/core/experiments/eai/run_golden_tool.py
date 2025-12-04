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
    ToolInvocationAccuracyEvaluator,
)
from src.evaluations.core.experiments.eai.evaluators.prompts import (
    prompt_data,
)


EXPERIMENT_DATA_PATH = Path(__file__).parent / "data"


async def run_golden_tool_experiment():
    """
    Run evaluation experiment for golden tool invocation accuracy.
    Uses a sheet with 'input' and 'golden tool' columns.
    """
    logger.info("--- Setting up Golden Tool Evaluation Experiment ---")

    loader = DataLoader(
        source="https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=1815504585#gid=1815504585",  # Replace with actual sheet URL
        id_col="id",
        prompt_col="input",
        dataset_name="Golden Tool Dataset",
        dataset_description="Dataset for evaluating tool invocation accuracy",
        metadata_cols=[
            "golden_tool",
        ],
    )
    logger.info(
        f"✅ DataLoader configured for dataset: '{loader.get_dataset_config()['dataset_name']}'"
    )

    judge_client = AzureOpenAIClient(model_name="gpt-4o")

    evaluators_to_run = [
        ToolInvocationAccuracyEvaluator(judge_client),
    ]

    evaluator_names = [e.name for e in evaluators_to_run]
    logger.info(f"✅ Evaluation suite configured to run: {evaluator_names}")

    metadata = {
        "system_prompt": prompt_data.get("prompt", ""),
        "judge_model": judge_client.model_name,
        "evaluation_type": "golden_tool_accuracy",
    }

    MAX_CONCURRENCY = 10

    runner = AsyncExperimentRunner(
        experiment_name=f"golden-tool-{datetime.now().strftime('%Y-%m-%d')}-v{prompt_data.get('version', '1')}",
        experiment_description="Golden Tool Invocation Accuracy Evaluation",
        metadata=metadata,
        evaluators=evaluators_to_run,
        max_concurrency=MAX_CONCURRENCY,
        output_dir=EXPERIMENT_DATA_PATH,
        timeout=180,
        polling_interval=5,
        rate_limit_requests_per_minute=10000,
    )
    
    logger.info(f"✅ Runner ready for experiment: '{runner.experiment_name}'")
    
    await runner.run(loader)


if __name__ == "__main__":
    try:
        asyncio.run(run_golden_tool_experiment())
    except Exception as e:
        logging.getLogger(__name__).error(
            f"Fatal error occurred during experiment execution: {e}",
            exc_info=True,
        )