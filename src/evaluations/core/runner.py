import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging
from tqdm.asyncio import tqdm_asyncio

from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import AgentConversationManager
from src.evaluations.core.evals import Evals, _EVAL_METHODS_REGISTRY
from src.evaluations.core import prompt_judges
from src.services.eai_gateway.api import CreateAgentRequest

logger = logging.getLogger(__name__)
JUDGE_STOP_SIGNAL = "EVALUATION_CONCLUDED"


class AsyncExperimentRunner:
    """Orquestra a execução de um experimento, monta o resultado final e o salva."""

    def __init__(
        self,
        experiment_name: str,
        experiment_description: str,
        metadata: Dict[str, Any],
        evaluation_suite: Evals,
        metrics_to_run: List[str],
    ):
        self.experiment_name = experiment_name
        self.experiment_description = experiment_description
        self.metadata = metadata
        self.evaluation_suite = evaluation_suite
        self.metrics_to_run = metrics_to_run

    async def _conduct_conversation(self, task, conv_manager):
        transcript, history = [], []
        current_message = task.get("prompt")
        last_response = {}
        for turn in range(10):
            agent_res = await conv_manager.send_message(current_message)
            last_response = agent_res
            transcript.append(
                {
                    "turn": turn + 1,
                    "judge_message": current_message,
                    "agent_response": agent_res.get("output"),
                    "agent_response_raw": agent_res.get("messages"),
                }
            )
            history.append(
                f"Turno {turn+1} - Juiz: {current_message}\nTurno {turn+1} - Agente: {agent_res.get('output')}"
            )

            prompt_for_judge = prompt_judges.CONVERSATIONAL_JUDGE_PROMPT.format(
                judge_context=task["judge_context"],
                conversation_history="\n".join(history),
                stop_signal=JUDGE_STOP_SIGNAL,
            )
            judge_res = await self.evaluation_suite.judge_client.execute(
                prompt_for_judge
            )
            if JUDGE_STOP_SIGNAL in judge_res:
                break
            current_message = judge_res
        return transcript, last_response

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_id = task.get("id")
        logger.info(f"Iniciando processamento da tarefa: {task_id}")

        try:
            agent_config_obj = CreateAgentRequest(**self.metadata)

            metrics_by_turns = {"one": [], "multiple": []}
            for m in self.metrics_to_run:
                metrics_by_turns[
                    _EVAL_METHODS_REGISTRY.get(m, {}).get("turns", "one")
                ].append(m)

            transcript, conv_last_response = [], {}
            one_turn_response = {}

            if metrics_by_turns["multiple"]:
                agent_multiple = AgentConversationManager(agent_config_obj)
                await agent_multiple.initialize()
                transcript, conv_last_response = await self._conduct_conversation(
                    task, agent_multiple
                )

            if metrics_by_turns["one"]:
                agent_one = AgentConversationManager(agent_config_obj)
                await agent_one.initialize()
                one_turn_response = await agent_one.send_message(task.get("prompt"))

            coroutines = []
            transcript_str = json.dumps(transcript, indent=2, ensure_ascii=False)
            for metric_name in self.metrics_to_run:
                eval_info = _EVAL_METHODS_REGISTRY[metric_name]
                eval_func = getattr(self.evaluation_suite, metric_name)

                if eval_info["turns"] == "multiple":
                    coroutines.append(
                        eval_func(agent_response=transcript_str, task=task)
                    )
                else:  # turns == "one"
                    coroutines.append(
                        eval_func(agent_response=one_turn_response, task=task)
                    )

            results_from_evals = await asyncio.gather(
                *coroutines, return_exceptions=True
            )

            evaluation_results = []
            for i, res in enumerate(results_from_evals):
                metric_name = self.metrics_to_run[i]
                if isinstance(res, Exception):
                    evaluation_results.append(
                        {
                            "eval_name": metric_name,
                            "score": 0.0,
                            "annotations": {"error": str(res)},
                        }
                    )
                else:
                    evaluation_results.append({"eval_name": metric_name, **res})

            return {
                "task": task,
                "agent_response": {
                    "one": (
                        one_turn_response.get("output")
                        if metrics_by_turns["one"]
                        else None
                    ),
                    "multiple": (
                        conv_last_response.get("output")
                        if metrics_by_turns["multiple"]
                        else None
                    ),
                },
                "agent_response_raw": {
                    "one": (
                        one_turn_response.get("messages")
                        if metrics_by_turns["one"]
                        else None
                    ),
                    "multiple": transcript if metrics_by_turns["multiple"] else None,
                },
                "evaluation_results": evaluation_results,
            }
        except Exception as e:
            logger.error(
                f"Erro irrecuperável ao processar a tarefa {task_id}: {e}",
                exc_info=True,
            )
            return {"task": task, "error": f"Erro irrecuperável: {e}"}
        finally:
            if "conv_manager" in locals() and conv_manager.agent_id:
                await conv_manager.close()

    async def run(self, loader: DataLoader):
        tasks = list(loader.get_tasks())
        runs = await tqdm_asyncio.gather(
            *[self._process_task(task) for task in tasks],
            desc=f"Executando: {self.experiment_name}",
        )

        final_result = {
            **loader.get_dataset_config(),
            "experiment_id": f"exp_{uuid.uuid4()}",
            "experiment_name": self.experiment_name,
            "experiment_description": self.experiment_description,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": self.metadata,
            "runs": runs,
        }

        output_dir = "evaluation_results"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"results_{self.experiment_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        logger.info(f"Resultados salvos em: {output_path}")
