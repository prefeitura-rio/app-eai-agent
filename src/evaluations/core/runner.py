import asyncio
import hashlib
import json
import os
import uuid
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from tqdm.asyncio import tqdm_asyncio

from src.evaluations.core.dataloader import DataLoader
from src.evaluations.core.llm_clients import AgentConversationManager, BaseJudgeClient
from src.evaluations.core.evaluators.base import BaseEvaluator
from src.evaluations.core.conversation import ConversationHandler
from src.evaluations.core.schemas import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
    ConversationTurn,
    RunResult,
    OneTurnAnalysis,
    MultiTurnAnalysis,
    ReasoningStep,
    MultiTurnContext,
)
from src.services.eai_gateway.api import CreateAgentRequest
from src.utils.bigquery import upload_experiment_to_bq
from src.utils.log import logger


class AsyncExperimentRunner:
    """Orquestra a execução de um experimento, monta o resultado final e o salva."""

    def __init__(
        self,
        experiment_name: str,
        experiment_description: str,
        metadata: Dict[str, Any],
        agent_config: Dict[str, Any],
        evaluators: List[BaseEvaluator],
        judge_client: BaseJudgeClient,
        precomputed_responses: Optional[Dict[str, Dict[str, Any]]] = None,
        max_concurrency: int = 10,
        upload_to_bq: bool = True,
    ):
        self.experiment_name = experiment_name
        self.experiment_description = experiment_description
        self.metadata = metadata
        self.agent_config = agent_config
        self.evaluators = evaluators
        self.judge_client = judge_client
        self.precomputed_responses = (
            precomputed_responses if precomputed_responses else {}
        )
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.upload_to_bq = upload_to_bq

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
        self, task: EvaluationTask, agent_config: CreateAgentRequest
    ) -> Tuple[AgentResponse, float]:
        """Obtém a resposta de turno único e o tempo de geração."""
        task_id = task.id
        precomputed_data = self.precomputed_responses.get(task_id)

        if precomputed_data and "one_turn_output" in precomputed_data:
            logger.info(f"↪️ Usando resposta pré-computada para a tarefa {task_id}.")
            response = AgentResponse(
                output=precomputed_data["one_turn_output"],
                messages=[
                    ReasoningStep(
                        message_type="precomputed",
                        content=precomputed_data["one_turn_output"],
                    )
                ],
            )
            return response, 0.0

        if not self.precomputed_responses:
            logger.info(f"▶️ Gerando resposta ao vivo para a tarefa {task_id}.")
            start_time = time.monotonic()
            agent_one = AgentConversationManager(agent_config)
            await agent_one.initialize()
            response = await agent_one.send_message(task.prompt)
            await agent_one.close()
            end_time = time.monotonic()
            return response, end_time - start_time

        return AgentResponse(output=None, messages=[]), 0.0

    async def _get_multi_turn_transcript(
        self, task: EvaluationTask, agent_config: CreateAgentRequest
    ) -> Tuple[List[ConversationTurn], AgentResponse, list, float]:
        """Obtém a transcrição multi-turno e o tempo de geração."""
        task_id = task.id
        precomputed_data = self.precomputed_responses.get(task_id)

        if precomputed_data and "multi_turn_transcript" in precomputed_data:
            logger.info(f"↪️ Usando transcrição pré-computada para a tarefa {task_id}.")
            transcript_data = precomputed_data["multi_turn_transcript"]
            transcript = [ConversationTurn(**turn) for turn in transcript_data]

            history = []
            for msg in transcript:
                if msg.agent_response:
                    m = f"Turno {msg.turn} - User: {msg.judge_message}\nTurno {msg.turn} - Agente: {msg.agent_response}"
                else:
                    m = f"Turno {msg.turn} - User: {msg.judge_message}"
                history.append(m)

            last_response = AgentResponse(
                output=transcript[-1].agent_response if transcript else None,
                messages=transcript[-1].reasoning_trace if transcript else [],
            )
            return transcript, last_response, history, 0.0

        if not self.precomputed_responses:
            logger.info(f"▶️ Gerando transcrição ao vivo para a tarefa {task_id}.")
            start_time = time.monotonic()
            agent_multiple = AgentConversationManager(agent_config)
            await agent_multiple.initialize()
            handler = ConversationHandler(
                conv_manager=agent_multiple,
                judge_client=self.judge_client,
            )
            transcript, last_response, history = await handler.conduct(task)
            end_time = time.monotonic()
            return transcript, last_response, history, end_time - start_time

        return [], AgentResponse(output=None, messages=[]), [], 0.0

    async def _execute_evaluations(
        self,
        task: EvaluationTask,
        one_turn_response: AgentResponse,
        transcript: List[ConversationTurn],
        history: List[str],
        one_turn_duration: float,
        multi_turn_duration: float,
    ) -> List[Dict[str, Any]]:
        """Executa avaliações, combinando o tempo de geração com o tempo de julgamento."""
        task_id = task.id
        evaluation_results = []

        async def _time_evaluation(coro: asyncio.Task) -> Tuple[Any, float]:
            start_time = time.monotonic()
            result = await coro
            end_time = time.monotonic()
            return result, end_time - start_time

        coroutine_map = []
        for evaluator in self.evaluators:
            error_msg = None
            if evaluator.turn_type == "multiple":
                if history:
                    multi_turn_context = MultiTurnContext(
                        conversation_history="\n".join(history),
                        transcript=transcript,
                    )
                    coro = evaluator.evaluate(
                        agent_response=multi_turn_context, task=task
                    )
                    coroutine_map.append((evaluator, _time_evaluation(coro)))
                elif self.precomputed_responses:
                    error_msg = f"Chave 'multi_turn_transcript' não encontrada para a tarefa '{task_id}'"
            else:  # turn_type == "one"
                if one_turn_response.output is not None:
                    coro = evaluator.evaluate(
                        agent_response=one_turn_response, task=task
                    )
                    coroutine_map.append((evaluator, _time_evaluation(coro)))
                elif self.precomputed_responses:
                    error_msg = f"Chave 'one_turn_output' não encontrada para a tarefa '{task_id}'"

            if error_msg:
                evaluation_results.append(
                    {
                        "metric_name": evaluator.name,
                        "score": None,
                        "has_error": True,
                        "error_message": error_msg,
                        "annotations": None,
                        "duration_seconds": 0.0,
                        "turn_type": evaluator.turn_type,
                    }
                )

        if coroutine_map:
            gathered_results = await asyncio.gather(*[c for _, c in coroutine_map])
            valid_evaluators = [e for e, _ in coroutine_map]

            for i, (res, judge_duration) in enumerate(gathered_results):
                evaluator = valid_evaluators[i]
                res_model = EvaluationResult.model_validate(res)

                generation_duration = (
                    multi_turn_duration
                    if evaluator.turn_type == "multiple"
                    else one_turn_duration
                )
                total_duration = round(generation_duration + judge_duration, 4)

                result_dict = {
                    "metric_name": evaluator.name,
                    "duration_seconds": total_duration,
                    "score": res_model.score,
                    "has_error": res_model.has_error,
                    "error_message": res_model.error_message,
                    "annotations": res_model.annotations,
                    "turn_type": evaluator.turn_type,
                }
                evaluation_results.append(result_dict)

        return sorted(evaluation_results, key=lambda x: x["metric_name"])

    async def _process_task(self, task: EvaluationTask) -> Dict[str, Any]:
        async with self.semaphore:
            task_id = task.id
            logger.info(f"Iniciando processamento da tarefa: {task_id}")
            start_time = time.monotonic()

            try:
                agent_config_obj = CreateAgentRequest(**self.agent_config)

                metrics_by_turns = {"one": False, "multiple": False}
                for evaluator in self.evaluators:
                    if evaluator.turn_type in metrics_by_turns:
                        metrics_by_turns[evaluator.turn_type] = True

                one_turn_response, one_turn_duration = (
                    AgentResponse(output=None, messages=[]),
                    0.0,
                )
                transcript, last_response, history, multi_turn_duration = (
                    [],
                    AgentResponse(output=None, messages=[]),
                    [],
                    0.0,
                )

                data_coroutines = []
                if metrics_by_turns["one"]:
                    data_coroutines.append(
                        self._get_one_turn_response(task, agent_config_obj)
                    )
                if metrics_by_turns["multiple"]:
                    data_coroutines.append(
                        self._get_multi_turn_transcript(task, agent_config_obj)
                    )

                if data_coroutines:
                    results = await asyncio.gather(*data_coroutines)
                    if metrics_by_turns["one"]:
                        one_turn_response, one_turn_duration = results.pop(0)
                    if metrics_by_turns["multiple"]:
                        transcript, last_response, history, multi_turn_duration = (
                            results.pop(0)
                        )

                evaluations = await self._execute_evaluations(
                    task,
                    one_turn_response,
                    transcript,
                    history,
                    one_turn_duration,
                    multi_turn_duration,
                )

                one_turn_evals = [e for e in evaluations if e.get("turn_type") == "one"]
                multi_turn_evals = [
                    e for e in evaluations if e.get("turn_type") == "multiple"
                ]

                end_time = time.monotonic()
                total_duration = round(end_time - start_time, 4)

                one_turn_analysis_obj = OneTurnAnalysis(
                    agent_response=one_turn_response.output,
                    reasoning_trace=one_turn_response.messages,
                    evaluations=one_turn_evals,
                )

                multi_turn_analysis_obj = MultiTurnAnalysis(
                    final_agent_response=last_response.output,
                    conversation_transcript=transcript,
                    evaluations=multi_turn_evals,
                )

                run_result = RunResult(
                    duration_seconds=total_duration,
                    task_data=task,
                    one_turn_analysis=one_turn_analysis_obj,
                    multi_turn_analysis=multi_turn_analysis_obj,
                )
                return run_result.model_dump(exclude_none=True)
            except Exception as e:
                logger.error(
                    f"Erro irrecuperável ao processar a tarefa {task_id}: {e}",
                    exc_info=True,
                )
                end_time = time.monotonic()
                total_duration = round(end_time - start_time, 4)

                return {
                    "duration_seconds": total_duration,
                    "task_data": task.model_dump(),
                    "error": f"Erro irrecuperável: {e}",
                }

    def _calculate_metrics_summary(
        self, runs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        from collections import defaultdict, Counter
        import statistics
        from typing import TypedDict, List as TypingList

        class MetricStats(TypedDict):
            scores: TypingList[float]
            times: TypingList[float]
            errors: int

        stats_by_metric: defaultdict[str, MetricStats] = defaultdict(
            lambda: {"scores": [], "times": [], "errors": 0}
        )

        for run in runs:
            if "error" in run:
                continue

            # Acessa as avaliações de ambos os tipos de análise
            one_turn_evals = run.get("one_turn_analysis", {}).get("evaluations", [])
            multi_turn_evals = run.get("multi_turn_analysis", {}).get("evaluations", [])
            all_evals = one_turn_evals + multi_turn_evals

            for result in all_evals:
                metric_name = result["metric_name"]
                metric_stats = stats_by_metric[metric_name]
                metric_stats["times"].append(result.get("duration_seconds", 0.0))
                if result.get("has_error") or result.get("score") is None:
                    metric_stats["errors"] += 1
                else:
                    metric_stats["scores"].append(result["score"])

        metrics_summary = []
        for metric_name, stats in stats_by_metric.items():
            scores, times, error_runs = stats["scores"], stats["times"], stats["errors"]
            successful_runs = len(scores)
            total_runs = successful_runs + error_runs

            if total_runs == 0:
                continue

            score_stats, time_stats, score_dist = {}, {}, []
            if successful_runs > 0:
                score_stats = {
                    "average": round(statistics.mean(scores), 4),
                    "median": round(statistics.median(scores), 4),
                    "std_dev": (
                        round(statistics.stdev(scores), 4)
                        if successful_runs > 1
                        else 0.0
                    ),
                    "min": min(scores),
                    "max": max(scores),
                }
                score_counts = Counter(scores)
                for score_value, count in sorted(score_counts.items()):
                    score_dist.append(
                        {
                            "value": score_value,
                            "count": count,
                            "percentage": round((count / successful_runs) * 100, 2),
                        }
                    )

            if times:
                time_stats = {
                    "average": round(statistics.mean(times), 4),
                    "median": round(statistics.median(times), 4),
                    "std_dev": (
                        round(statistics.stdev(times), 4) if len(times) > 1 else 0.0
                    ),
                    "min": min(times),
                    "max": max(times),
                }

            summary = {
                "metric_name": metric_name,
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "success_rate_percentage": round(
                    (successful_runs / total_runs) * 100, 2
                ),
                "failed_runs": error_runs,
                "failure_rate_percentage": round((error_runs / total_runs) * 100, 2),
                "score_statistics": score_stats or None,
                "duration_statistics_seconds": time_stats or None,
                "score_distribution": score_dist,
            }
            metrics_summary.append(summary)

        return sorted(metrics_summary, key=lambda x: x["metric_name"])

    def _calculate_error_summary(self, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        from collections import defaultdict

        error_breakdown = defaultdict(int)
        failed_run_ids = set()

        for run in runs:
            has_run_error = "error" in run

            one_turn_evals = run.get("one_turn_analysis", {}).get("evaluations", [])
            multi_turn_evals = run.get("multi_turn_analysis", {}).get("evaluations", [])
            all_evals = one_turn_evals + multi_turn_evals

            for result in all_evals:
                if result.get("has_error"):
                    has_run_error = True
                    error_breakdown[result["metric_name"]] += 1

            if has_run_error:
                failed_run_ids.add(run["task_data"]["id"])

        return {
            "total_failed_runs": len(failed_run_ids),
            "errors_per_metric": dict(sorted(error_breakdown.items())),
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

        aggregate_metrics = self._calculate_metrics_summary(runs)
        error_summary = self._calculate_error_summary(runs)

        total_duration_seconds = round(end_time - start_time, 2)

        task_latencies = [
            r.get("duration_seconds", 0) for r in runs if "error" not in r
        ]
        avg_task_duration = (
            round(sum(task_latencies) / len(task_latencies), 2) if task_latencies else 0
        )

        avg_metric_latencies = [
            m.get("duration_statistics_seconds", {}).get("average", 0)
            for m in aggregate_metrics
        ]
        avg_metric_duration = (
            round(sum(avg_metric_latencies) / len(avg_metric_latencies), 2)
            if avg_metric_latencies
            else 0
        )

        execution_summary = {
            "total_duration_seconds": total_duration_seconds,
            "average_task_duration_seconds": avg_task_duration,
            "average_metric_duration_seconds": avg_metric_duration,
        }

        dataset_config = loader.get_dataset_config()

        exp_hash_hex = hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest()
        experiment_id = int(exp_hash_hex[:16], 16) & (2**63 - 1)

        final_result = {
            "dataset_name": dataset_config.get("dataset_name"),
            "dataset_description": dataset_config.get("dataset_description"),
            "dataset_id": dataset_config.get("dataset_id"),
            "experiment_id": experiment_id,
            "experiment_name": self.experiment_name,
            "experiment_description": self.experiment_description,
            "experiment_timestamp": datetime.now(timezone.utc).isoformat(),
            "experiment_metadata": self.metadata,
            "execution_summary": execution_summary,
            "error_summary": error_summary,
            "aggregate_metrics": aggregate_metrics,
            "runs": runs,
        }

        output_dir = "./src/evaluations/core/data"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"results_{self.experiment_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        logger.info(f"Resultados salvos em: {output_path}")

        if self.upload_to_bq:
            upload_experiment_to_bq(result_data=final_result)
