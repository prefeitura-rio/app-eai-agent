import httpx
import os
import json
import asyncio
import textwrap
from datetime import datetime

import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir.split("src")[0]
if project_root:  # Check if split found 'src'
    sys.path.append(project_root)

import pandas as pd

from src.evaluations.letta.mlflow.model import Model


import logging

logging.basicConfig(level=logging.INFO)

for var in [
    "MLFLOW_TRACKING_URL",
    "MLFLOW_TRACKING_USERNAME",
    "MLFLOW_TRACKING_PASSWORD",
    "AGENTIC_SEARCH_URL",
    "AGENTIC_SEARCH_TOKEN",
    "GEMINI_API_KEY",
]:
    assert os.environ.get(var), f"Environment variable {var} is not set"


async def get_response_from_letta(query: str) -> dict:
    url = os.getenv("AGENTIC_SEARCH_URL")
    payload = {
        "agent_id": "agent-23301e87-a554-4487-be6e-18f299af803a",
        "message": query,
        "name": "kkkkkkkk",
    }
    bearer_token = os.getenv("AGENTIC_SEARCH_TOKEN")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    return response.json()


async def call_judges(eval_results: dict, judges: list) -> dict:
    """
    Asynchronously call multiple judges to evaluate results.

    Args:
        eval_results: Dictionary containing the evaluation data
        judges: List of judge names to evaluate

    Returns:
        List of judge results
    """
    model = Model(model="gemini-2.5-flash-preview-04-17", temperature=0.1)
    logging.info("Getting response from judges")
    tasks = [
        model.judge(judge_name=judge_name, eval_results=eval_results)
        for judge_name in judges
    ]
    return await asyncio.gather(*tasks)


async def process_evaluation(eval_results: dict, judges: list) -> dict:
    """
    Process a single evaluation case asynchronously.

    Args:
        eval_results: Dictionary containing the evaluation data
        judges: List of judge names to evaluate the response

    Returns:
        Dictionary containing the processed evaluation results
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    eval_results = {"updated_at": now, **eval_results}

    logging.info(
        f"Getting response from letta api for query: {eval_results['query'][:50]}..."
    )
    response = await get_response_from_letta(query=eval_results["query"])

    eval_results["letta_response"] = response["assistant_messages"][0]["content"]
    # eval_results["core_memory"] = core_memory
    # eval_results["tool_definitions"] = tool_definitions

    search_tool_results = [
        {"name": tool_return.get("name"), "tool_return": tool_return["tool_return"]}
        for tool_return in response["tool_return_messages"]
    ]
    eval_results["search_tool_results"] = (
        json.dumps(search_tool_results) if search_tool_results else None
    )
    tool_call = [tool.get("tool_call") for tool in response["tool_call_messages"]]
    eval_results["search_tool_query"] = json.dumps(tool_call) if tool_call else None
    eval_results["tool_call"] = json.dumps(tool_call) if tool_call else None

    judges_results = await call_judges(eval_results=eval_results, judges=judges)
    eval_results["judges"] = judges_results

    eval_results["letta_usage_statistics"] = response["letta_usage_statistics"]
    eval_results["reasoning_messages"] = response["reasoning_messages"]
    eval_results["letta_complete_response"] = response

    return eval_results


async def main():

    eval_dataset = json.load(open(f"{current_dir}/eval_dataset.json", "r"))
    eval_dataset = eval_dataset[:1]
    csv_save_path = f"{current_dir}/eval_results.csv"

    if os.path.exists(csv_save_path):
        os.remove(csv_save_path)

    judges = [
        "clarify",
        "location_policy_compliance",
        "emergency_handling_compliance",
        "feedback_handling_compliance",
        "security_privacy_compliance",
        "whatsapp_formating",
        "answer_completness",
        "entity_presence",
        "gold_standart",
        "groundness",
        "tool_calling",
        "search_query_effectiveness",
        "search_result_coverage",
    ]

    # Process all evaluations concurrently
    tasks = [process_evaluation(eval_results, judges) for eval_results in eval_dataset]
    final_results = await asyncio.gather(*tasks)

    # Save results to CSV
    dataframe = pd.DataFrame(final_results)
    dataframe.to_csv(
        csv_save_path,
        index=False,
        sep=";",
    )

    # Save results to JSON
    json.dump(
        json.loads(json.dumps(final_results)),
        open(f"{current_dir}/eval_results.json", "w"),
        indent=4,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    asyncio.run(main())
