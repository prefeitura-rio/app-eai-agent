import asyncio
import json
import os
import uuid
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import logging
from tqdm.asyncio import tqdm_asyncio

from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import AgentConversationManager
from src.evaluations.core.evals import (
    Evals,
    _EVAL_METHODS_REGISTRY,
    ConversationHandler,
)
from src.services.eai_gateway.api import CreateAgentRequest

logger = logging.getLogger(__name__)


class AsyncExperimentRunner:
    """Orquestra a execução de um experimento, monta o resultado final e o salva."""

    def __init__(
        self,
        experiment_name: str,
        experiment_description: str,
        metadata: Dict[str, Any],
        agent_config: Dict[str, Any],
        evaluation_suite: Evals,
        metrics_to_run: List[str],
        precomputed_responses: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self.experiment_name = experiment_name
        self.experiment_description = experiment_description
        self.metadata = metadata
        self.agent_config = agent_config
        self.evaluation_suite = evaluation_suite
        self.metrics_to_run = metrics_to_run
        self.precomputed_responses = (
            precomputed_responses if precomputed_responses else {}
        )
        if self.precomputed_responses:
            logger.info(
                f"✅ Runner inicializado com {len(self.precomputed_responses)} respostas pré-computadas."
            )
            self._validate_precomputed_responses()

    def _validate_precomputed_responses(self):
        """Valida a estrutura do dicionário de respostas pré-computadas."""
        for task_id, response_data in self.precomputed_responses.items():
            if not isinstance(response_data, dict):
                raise TypeError(
                    f"A resposta para o ID '{task_id}' deve ser um dicionário."
                )
            if (
                "one_turn_output" not in response_data
                and "multi_turn_transcript" not in response_data
            ):
                raise ValueError(
                    f"A resposta para o ID '{task_id}' não contém nem 'one_turn_output' nem 'multi_turn_transcript'."
                )

    async def _get_one_turn_response(
        self, task: Dict[str, Any], agent_config: CreateAgentRequest
    ) -> Tuple[Dict[str, Any], float]:
        """Obtém a resposta de turno único e o tempo de geração."""
        task_id = task.get("id")
        precomputed_data = self.precomputed_responses.get(task_id)

        if precomputed_data and "one_turn_output" in precomputed_data:
            logger.info(f"↪️ Usando resposta pré-computada para a tarefa {task_id}.")
            response = {
                "output": precomputed_data["one_turn_output"],
                "messages": [precomputed_data["one_turn_output"]],
            }
            return response, 0.0

        if not self.precomputed_responses:
            logger.info(f"▶️ Gerando resposta ao vivo para a tarefa {task_id}.")
            start_time = time.monotonic()
            agent_one = AgentConversationManager(agent_config)
            await agent_one.initialize()
            response = await agent_one.send_message(task.get("prompt"))
            await agent_one.close()
            end_time = time.monotonic()
            return response, end_time - start_time

        return {}, 0.0

    async def _get_multi_turn_transcript(
        self, task: Dict[str, Any], agent_config: CreateAgentRequest
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any], float]:
        """Obtém a transcrição multi-turno e o tempo de geração."""
        task_id = task.get("id")
        precomputed_data = self.precomputed_responses.get(task_id)

        if precomputed_data and "multi_turn_transcript" in precomputed_data:
            logger.info(f"↪️ Usando transcrição pré-computada para a tarefa {task_id}.")
            transcript = precomputed_data["multi_turn_transcript"]
            last_response = (
                {"output": transcript[-1].get("agent_response")} if transcript else {}
            )
            return transcript, last_response, 0.0

        if not self.precomputed_responses:
            logger.info(f"▶️ Gerando transcrição ao vivo para a tarefa {task_id}.")
            start_time = time.monotonic()
            agent_multiple = AgentConversationManager(agent_config)
            await agent_multiple.initialize()
            handler = ConversationHandler(
                conv_manager=agent_multiple,
                evaluation_suite=self.evaluation_suite,
            )
            transcript, last_response = await handler.conduct(task)
            end_time = time.monotonic()
            # O fechamento do agente precisa ser tratado fora
            return transcript, last_response, end_time - start_time

        return [], {}, 0.0

    async def _execute_evaluations(
        self,
        task: Dict[str, Any],
        one_turn_response: Dict[str, Any],
        transcript: List[Dict[str, Any]],
        one_turn_duration: float,
        multi_turn_duration: float,
    ) -> List[Dict[str, Any]]:
        """Executa avaliações, combinando o tempo de geração com o tempo de julgamento."""
        task_id = task.get("id")
        evaluation_results = []

        async def _time_evaluation(coro: asyncio.Task) -> Tuple[Any, float]:
            start_time = time.monotonic()
            try:
                result = await coro
            except Exception as e:
                result = e
            end_time = time.monotonic()
            return result, end_time - start_time

        coroutine_map = []
        for metric_name in self.metrics_to_run:
            eval_info = _EVAL_METHODS_REGISTRY[metric_name]
            eval_func = getattr(self.evaluation_suite, metric_name)
            error_msg = None

            if eval_info["turns"] == "multiple":
                if transcript:
                    transcript_str = json.dumps(transcript, indent=2, ensure_ascii=False)
                    coro = eval_func(agent_response=transcript_str, task=task)
                    coroutine_map.append((metric_name, _time_evaluation(coro)))
                elif self.precomputed_responses:
                    error_msg = f"Chave 'multi_turn_transcript' não encontrada para a tarefa '{task_id}'"
            else:  # turns == "one"
                if one_turn_response:
                    coro = eval_func(agent_response=one_turn_response, task=task)
                    coroutine_map.append((metric_name, _time_evaluation(coro)))
                elif self.precomputed_responses:
                    error_msg = f"Chave 'one_turn_output' não encontrada para a tarefa '{task_id}'"

            if error_msg:
                evaluation_results.append({
                    "eval_name": metric_name, "score": None, "error": True,
                    "error_msg": error_msg, "annotations": None, "execution_time_seconds": 0.0
                })

        if coroutine_map:
            gathered_results = await asyncio.gather(*[c for _, c in coroutine_map])
            valid_metrics = [m for m, _ in coroutine_map]

            for i, (res, judge_duration) in enumerate(gathered_results):
                metric_name = valid_metrics[i]
                eval_info = _EVAL_METHODS_REGISTRY[metric_name]
                
                generation_duration = multi_turn_duration if eval_info["turns"] == "multiple" else one_turn_duration
                total_duration = round(generation_duration + judge_duration, 4)

                result_dict = {"eval_name": metric_name, "execution_time_seconds": total_duration}
                if isinstance(res, Exception):
                    error_msg = f"Exceção durante a avaliação: {str(res)}"
                    result_dict.update({
                        "score": None, "error": True,
                        "error_msg": error_msg, "annotations": None,
                    })
                else:
                    result_dict.update({
                        "score": res.get("score", None), "error": False,
                        "error_msg": None, "annotations": res.get("annotations"),
                    })
                evaluation_results.append(result_dict)

        return sorted(evaluation_results, key=lambda x: x["eval_name"])

    async def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_id = task.get("id")
        logger.info(f"Iniciando processamento da tarefa: {task_id}")
        start_time = time.monotonic()

        try:
            agent_config_obj = CreateAgentRequest(**self.agent_config)

            one_turn_response, one_turn_duration = await self._get_one_turn_response(task, agent_config_obj)
            transcript, last_response, multi_turn_duration = await self._get_multi_turn_transcript(task, agent_config_obj)

            evaluation_results = await self._execute_evaluations(
                task, one_turn_response, transcript, one_turn_duration, multi_turn_duration
            )
            
            end_time = time.monotonic()
            total_duration = round(end_time - start_time, 4)

            return {
                "execution_time_seconds": total_duration,
                "task": task,
                "agent_response": {
                    "one": one_turn_response.get("output"),
                    "multiple": last_response.get("output"),
                },
                "reasoning": {
                    "one": one_turn_response.get("messages"),
                    "multiple": transcript,
                },
                "evaluation_results": evaluation_results,
            }
        except Exception as e:
            logger.error(f"Erro irrecuperável ao processar a tarefa {task_id}: {e}", exc_info=True)
            end_time = time.monotonic()
            total_duration = round(end_time - start_time, 4)
            return {
                "execution_time_seconds": total_duration,
                "task": task, 
                "error": f"Erro irrecuperável: {e}"
            }

    def _calculate_metrics_summary(self, runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcula um sumário estatístico detalhado para cada métrica, incluindo scores e tempos de execução.
        """
        from collections import defaultdict, Counter
        import statistics

        stats_by_metric = defaultdict(lambda: {"scores": [], "times": [], "errors": 0})

        for run in runs:
            if "error" in run:
                continue
            for result in run.get("evaluation_results", []):
                metric_name = result["eval_name"]
                stats_by_metric[metric_name]["times"].append(result.get("execution_time_seconds", 0.0))
                if result.get("error") or result.get("score") is None:
                    stats_by_metric[metric_name]["errors"] += 1
                else:
                    stats_by_metric[metric_name]["scores"].append(result["score"])

        metrics_summary = []
        for metric_name, stats in stats_by_metric.items():
            scores = stats["scores"]
            times = stats["times"]
            error_runs = stats["errors"]
            successful_runs = len(scores)
            total_runs = successful_runs + error_runs

            if total_runs == 0:
                continue

            score_stats, time_stats, score_dist = {}, {}, []
            if successful_runs > 0:
                score_stats["average"] = round(statistics.mean(scores), 4)
                score_stats["median"] = round(statistics.median(scores), 4)
                score_stats["std_dev"] = round(statistics.stdev(scores), 4) if successful_runs > 1 else 0.0
                score_stats["min"] = min(scores)
                score_stats["max"] = max(scores)
                
                score_counts = Counter(scores)
                for score_value, count in sorted(score_counts.items()):
                    score_dist.append({
                        "value": score_value, "count": count,
                        "percentage": round((count / successful_runs) * 100, 2)
                    })

            if times:
                time_stats["average"] = round(statistics.mean(times), 4)
                time_stats["median"] = round(statistics.median(times), 4)
                time_stats["std_dev"] = round(statistics.stdev(times), 4) if len(times) > 1 else 0.0
                time_stats["min"] = min(times)
                time_stats["max"] = max(times)

            summary = {
                "metric": metric_name, "total_runs": total_runs,
                "successful_runs": successful_runs,
                "successful_runs_percentage": round((successful_runs / total_runs) * 100, 2),
                "error_runs": error_runs,
                "error_runs_percentage": round((error_runs / total_runs) * 100, 2),
                "score_statistics": score_stats if score_stats else None,
                "execution_time_statistics": time_stats if time_stats else None,
                "score_distribution": score_dist,
            }
            metrics_summary.append(summary)

        return sorted(metrics_summary, key=lambda x: x['metric'])

    def _calculate_error_summary(self, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Agrega todos os erros ocorridos durante o experimento."""
        from collections import defaultdict

        error_breakdown = defaultdict(int)
        failed_run_ids = set()
        
        for run in runs:
            has_error = "error" in run
            for result in run.get("evaluation_results", []):
                if result.get("error"):
                    has_error = True
                    error_breakdown[result["eval_name"]] += 1
            
            if has_error:
                failed_run_ids.add(run["task"]["id"])
        
        return {
            "total_error_runs": len(failed_run_ids),
            "error_breakdown_by_metric": dict(sorted(error_breakdown.items())),
            "failed_run_ids": sorted(list(failed_run_ids)),
        }

    async def run(self, loader: DataLoader):
        start_time = time.monotonic()
        tasks = list(loader.get_tasks())
        
        runs = await tqdm_asyncio.gather(
            *[self._process_task(task) for task in tasks],
            desc=f"Executando: {self.experiment_name}",
        )
        
        end_time = time.monotonic()
        
        # --- Geração de Sumários ---
        metrics_summary = self._calculate_metrics_summary(runs)
        error_summary = self._calculate_error_summary(runs)
        
        total_execution_time = round(end_time - start_time, 2)
        
        # Correção: Calcula a média da latência de cada task individualmente.
        task_latencies = [r.get("execution_time_seconds", 0) for r in runs]
        avg_latency_per_task = round(sum(task_latencies) / len(task_latencies), 2) if task_latencies else 0
        
        avg_metric_latencies = [
            m.get("execution_time_statistics", {}).get("average", 0)
            for m in metrics_summary
        ]
        avg_latency_per_metric = round(sum(avg_metric_latencies) / len(avg_metric_latencies), 2) if avg_metric_latencies else 0

        execution_details = {
            "total_execution_time_seconds": total_execution_time,
            "average_latency_per_task_seconds": avg_latency_per_task,
            "average_latency_per_metric_seconds": avg_latency_per_metric,
        }

        final_result = {
            **loader.get_dataset_config(),
            "experiment_id": f"exp_{uuid.uuid4()}",
            "experiment_name": self.experiment_name,
            "experiment_description": self.experiment_description,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": self.metadata,
            "execution_details": execution_details,
            "error_summary": error_summary,
            "metrics_summary": metrics_summary,
            "runs": runs,
        }

        output_dir = "evaluation_results"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"results_{self.experiment_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        logger.info(f"Resultados salvos em: {output_path}")
