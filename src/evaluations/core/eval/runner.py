import asyncio
import hashlib
import json
import os
import uuid
import time
from datetime import datetime, timezone
from typing import (
    List,
    Dict,
    Any,
    Optional,
    Tuple,
    Union,
    TypedDict,
    List as TypingList,
    AsyncGenerator,
)
from collections import defaultdict, Counter
import statistics
from pathlib import Path
from contextlib import asynccontextmanager

from tqdm.asyncio import tqdm_asyncio

from src.evaluations.core.eval.dataloader import DataLoader
from src.evaluations.core.eval.llm_clients import (
    AgentConversationManager,
    BaseJudgeClient,
)
from src.evaluations.core.eval.evaluators.base import (
    BaseEvaluator,
    BaseConversationEvaluator,
)
from src.evaluations.core.eval.schemas import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
    ConversationTurn,
    RunResult,
    OneTurnAnalysis,
    MultiTurnAnalysis,
    ReasoningStep,
    MultiTurnContext,
    ConversationOutput,
)
from src.services.eai_gateway.api import CreateAgentRequest
from src.utils.bigquery import upload_experiment_to_bq
from src.evaluations.core.eval.log import logger


class MetricStats(TypedDict):
    """Estrutura para armazenar estatísticas de métricas."""

    scores: TypingList[float]
    times: TypingList[float]
    errors: int


class AsyncExperimentRunner:
    """
    Orquestra a execução de experimentos de avaliação de agentes de IA.

    Suporta avaliações de turno único e múltiplos turnos, com capacidade de usar
    respostas pré-computadas para acelerar experimentos repetidos.
    """

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
        output_dir: Union[str, Path] = "./data",
    ):
        """
        Inicializa o runner de experimentos.

        Args:
            experiment_name: Nome único do experimento
            experiment_description: Descrição detalhada do experimento
            metadata: Metadados adicionais do experimento
            agent_config: Configuração do agente a ser testado
            evaluators: Lista de avaliadores para executar
            judge_client: Cliente para avaliação das respostas
            precomputed_responses: Respostas pré-computadas (opcional)
            max_concurrency: Máximo de tarefas simultâneas
            upload_to_bq: Se deve fazer upload para BigQuery
            output_dir: Diretório para salvar resultados
        """
        self.experiment_name = experiment_name
        self.experiment_description = experiment_description
        self.metadata = metadata
        self.agent_config = agent_config
        self.evaluators = evaluators
        self.judge_client = judge_client
        self.precomputed_responses = precomputed_responses or {}
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.upload_to_bq = upload_to_bq
        self.output_dir = Path(output_dir)

        # Cache para avaliadores categorizados
        self._evaluator_cache = self._categorize_evaluators()

        self._validate_evaluators()

        if self.precomputed_responses:
            logger.info(
                f"✅ Runner inicializado com {len(self.precomputed_responses)} "
                f"respostas pré-computadas."
            )

    def _categorize_evaluators(self) -> Dict[str, List[BaseEvaluator]]:
        """Categoriza avaliadores por tipo para otimizar acesso."""
        categories: Dict[str, List[BaseEvaluator]] = {
            "one_turn": [],
            "multi_turn": [],
            "conversation": [],
        }

        for evaluator in self.evaluators:
            if isinstance(evaluator, BaseConversationEvaluator):
                categories["conversation"].append(evaluator)
            elif evaluator.turn_type == "one":
                categories["one_turn"].append(evaluator)
            elif evaluator.turn_type == "multiple":
                categories["multi_turn"].append(evaluator)

        return categories

    def _validate_evaluators(self) -> None:
        """Valida a configuração dos avaliadores."""
        conversation_evaluators = self._evaluator_cache["conversation"]
        multi_turn_evaluators = self._evaluator_cache["multi_turn"]

        if len(conversation_evaluators) > 1:
            raise ValueError(
                "Apenas um avaliador do tipo 'conversation' é permitido por experimento."
            )

        if multi_turn_evaluators and not conversation_evaluators:
            raise ValueError(
                "Avaliadores do tipo 'multiple' requerem um avaliador do tipo "
                "'conversation' para gerar a transcrição."
            )

    @asynccontextmanager
    async def _get_agent_manager(
        self, task_id: str
    ) -> AsyncGenerator[Optional[AgentConversationManager], None]:
        """Context manager para gerenciar ciclo de vida do agente."""
        if self.precomputed_responses:
            # Se temos precomputed_responses, nunca usar agente real
            yield None
            return

        agent_manager = AgentConversationManager(
            CreateAgentRequest(**self.agent_config)
        )
        try:
            await agent_manager.initialize()
            yield agent_manager
        finally:
            await agent_manager.close()

    async def _get_one_turn_response(
        self,
        task: EvaluationTask,
    ) -> Tuple[AgentResponse, float]:
        """Obtém resposta de turno único com tratamento melhorado de erros."""
        task_id = task.id

        # Se temos precomputed_responses, só usar dados pré-computados
        if self.precomputed_responses:
            precomputed_data = self.precomputed_responses.get(task_id, {})

            if "one_turn_output" in precomputed_data:
                logger.debug(f"↪️ Usando one-turn pré-computado para {task_id}")
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
            else:
                # Dados insuficientes - retorna resposta vazia que causará erro nas avaliações
                logger.warning(
                    f"❌ Dados one-turn não encontrados para {task_id} em precomputed_responses"
                )
                return AgentResponse(output=None, messages=[]), 0.0

        logger.debug(f"▶️ Gerando one-turn ao vivo para {task_id}")
        start_time = time.perf_counter()
        try:
            async with self._get_agent_manager(task_id) as agent_manager:
                if agent_manager is None:  # Verificação de segurança
                    raise RuntimeError("Falha ao inicializar o agente para one-turn.")

                response = await agent_manager.send_message(task.prompt)
                return response, time.perf_counter() - start_time
        except Exception as e:
            logger.error(f"Erro ao gerar resposta one-turn para {task_id}: {e}")
            return (
                AgentResponse(output=None, messages=[]),
                time.perf_counter() - start_time,
            )

    async def _get_multi_turn_transcript(
        self,
        task: EvaluationTask,
        conv_evaluator: BaseConversationEvaluator,
    ) -> Optional[ConversationOutput]:
        """Obtém transcrição multi-turn com tratamento melhorado de erros."""
        task_id = task.id

        # Se temos precomputed_responses, só usar dados pré-computados
        if self.precomputed_responses:
            precomputed_data = self.precomputed_responses.get(task_id, {})

            if "multi_turn_transcript" in precomputed_data:
                logger.debug(f"↪️ Usando multi-turn pré-computado para {task_id}")
                try:
                    transcript_data = precomputed_data["multi_turn_transcript"]
                    transcript = [ConversationTurn(**turn) for turn in transcript_data]

                    history = [
                        f"Turno {t.turn} - User: {t.judge_message}\n"
                        f"Turno {t.turn} - Agente: {t.agent_response}"
                        for t in transcript
                        if t.agent_response
                    ]

                    final_response = transcript[-1] if transcript else None
                    final_agent_response = AgentResponse(
                        output=(
                            final_response.agent_response if final_response else None
                        ),
                        messages=(
                            final_response.reasoning_trace if final_response else []
                        ),
                    )

                    return ConversationOutput(
                        transcript=transcript,
                        final_agent_response=final_agent_response,
                        history_for_judge=history,
                        duration_seconds=0.0,
                    )
                except Exception as e:
                    logger.error(
                        f"Erro ao processar transcript pré-computado para {task_id}: {e}"
                    )
                    return None
            else:
                # Dados insuficientes - retorna None que causará erro nas avaliações multi-turn
                logger.warning(
                    f"❌ Dados multi-turn não encontrados para {task_id} em precomputed_responses"
                )
                return None

        logger.debug(f"▶️ Gerando multi-turn ao vivo para {task_id}")
        try:
            async with self._get_agent_manager(task_id) as agent_manager:
                if agent_manager is None:  # Verificação de segurança
                    raise RuntimeError("Falha ao inicializar o agente para multi-turn.")
                return await conv_evaluator.evaluate(task, agent_manager)
        except Exception as e:
            logger.error(f"Erro ao gerar multi-turn para {task_id}: {e}")
            return None

    async def _execute_single_evaluation(
        self,
        evaluator: BaseEvaluator,
        task: EvaluationTask,
        one_turn_response: AgentResponse,
        multi_turn_output: Optional[ConversationOutput],
    ) -> Tuple[Dict[str, Any], float]:
        """Executa uma única avaliação com medição de tempo."""
        log_context_string = f"{evaluator.turn_type}/{evaluator.name}"
        with logger.contextualize(task_id=task.id, turn_type=log_context_string):
            start_time = time.perf_counter()
            try:
                if evaluator.turn_type == "multiple":
                    if not multi_turn_output:
                        raise ValueError(
                            f"Dados multi-turn não disponíveis para tarefa '{task.id}'. "
                            f"Verifique se os dados pré-computados contêm 'multi_turn_transcript' "
                            f"ou se o avaliador conversation está configurado corretamente."
                        )

                    multi_turn_context = MultiTurnContext(
                        conversation_history="\n".join(
                            multi_turn_output.history_for_judge
                        ),
                        transcript=multi_turn_output.transcript,
                    )
                    result = await evaluator.evaluate(
                        agent_response=multi_turn_context, task=task
                    )

                elif evaluator.turn_type == "one":
                    if one_turn_response.output is None:
                        raise ValueError(
                            f"Dados one-turn não disponíveis para tarefa '{task.id}'. "
                            f"Verifique se os dados pré-computados contêm 'one_turn_output' "
                            f"ou se o agente está configurado corretamente."
                        )

                    result = await evaluator.evaluate(
                        agent_response=one_turn_response, task=task
                    )
                else:
                    raise ValueError(
                        f"Tipo de avaliador inválido: {evaluator.turn_type}"
                    )

                eval_duration = time.perf_counter() - start_time
                eval_result = EvaluationResult.model_validate(result)

                return {
                    "metric_name": evaluator.name,
                    "duration_seconds": round(eval_duration, 4),
                    **eval_result.model_dump(),
                    "turn_type": evaluator.turn_type,
                }, eval_duration

            except Exception as e:
                eval_duration = time.perf_counter() - start_time
                error_msg = f"Erro na avaliação {evaluator.name} para tarefa {task.id}: {str(e)}"
                logger.error(error_msg)

                eval_result = EvaluationResult(
                    annotations=error_msg,
                    has_error=True,
                    error_message=str(e),
                    score=None,  # Garantir que score seja None em caso de erro
                )

                return {
                    "metric_name": evaluator.name,
                    "duration_seconds": round(eval_duration, 4),
                    **eval_result.model_dump(),
                    "turn_type": evaluator.turn_type,
                }, eval_duration

    async def _execute_evaluations(
        self,
        task: EvaluationTask,
        one_turn_response: AgentResponse,
        one_turn_duration: float,
        multi_turn_output: Optional[ConversationOutput],
    ) -> List[Dict[str, Any]]:
        """Executa todas as avaliações para uma tarefa."""
        analysis_evaluators = (
            self._evaluator_cache["one_turn"] + self._evaluator_cache["multi_turn"]
        )

        if not analysis_evaluators:
            return []

        # Executa avaliações em paralelo
        evaluation_tasks = [
            self._execute_single_evaluation(
                evaluator, task, one_turn_response, multi_turn_output
            )
            for evaluator in analysis_evaluators
        ]

        results = await asyncio.gather(*evaluation_tasks, return_exceptions=True)

        evaluation_results = []
        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                evaluator = analysis_evaluators[i]
                logger.error(f"Erro crítico na avaliação {evaluator.name}: {result}")

                eval_result = EvaluationResult(
                    annotations=f"Erro crítico: {str(result)}",
                    has_error=True,
                    error_message=str(result),
                )

                evaluation_results.append(
                    {
                        "metric_name": evaluator.name,
                        "duration_seconds": 0.0,
                        **eval_result.model_dump(),
                        "turn_type": evaluator.turn_type,
                    }
                )
            else:
                eval_dict, judge_duration = result
                # Adiciona duração de geração ao tempo total
                gen_duration = (
                    multi_turn_output.duration_seconds
                    if eval_dict["turn_type"] == "multiple" and multi_turn_output
                    else one_turn_duration
                )
                eval_dict["duration_seconds"] = round(gen_duration + judge_duration, 4)
                evaluation_results.append(eval_dict)

        return sorted(evaluation_results, key=lambda x: x["metric_name"])

    async def _process_task(self, task: EvaluationTask) -> Dict[str, Any]:
        """Processa uma única tarefa com controle de concorrência."""
        async with self.semaphore:
            task_id = task.id
            logger.info(f"Iniciando processamento da tarefa: {task_id}")
            start_time = time.perf_counter()

            try:
                needs_one_turn = bool(self._evaluator_cache["one_turn"])
                needs_multi_turn = bool(self._evaluator_cache["multi_turn"])

                conv_evaluator: Optional[BaseConversationEvaluator] = None
                if self._evaluator_cache["conversation"]:
                    potential_evaluator = self._evaluator_cache["conversation"][0]
                    if isinstance(potential_evaluator, BaseConversationEvaluator):
                        conv_evaluator = potential_evaluator
                    else:
                        logger.error(
                            f"Erro de tipo inesperado: o avaliador em 'conversation' "
                            f"não é um BaseConversationEvaluator para a tarefa {task_id}"
                        )

                # Inicializa as variáveis de tarefa como None fora dos blocos if
                one_turn_task = None
                multi_turn_task = None

                # Cria as tarefas se necessário
                if needs_one_turn:

                    async def one_turn_with_context():
                        with logger.contextualize(
                            task_id=task_id, turn_type="one-turn"
                        ):
                            return await self._get_one_turn_response(task)

                    one_turn_task = asyncio.create_task(one_turn_with_context())

                if needs_multi_turn and conv_evaluator:

                    async def multi_turn_with_context():
                        with logger.contextualize(
                            task_id=task_id, turn_type="multi-turn"
                        ):
                            return await self._get_multi_turn_transcript(
                                task, conv_evaluator
                            )

                    multi_turn_task = asyncio.create_task(multi_turn_with_context())

                # Coleta apenas as tarefas que foram realmente criadas
                tasks_to_run = [
                    t for t in [one_turn_task, multi_turn_task] if t is not None
                ]

                if not tasks_to_run:
                    results = []
                else:
                    results = await asyncio.gather(*tasks_to_run)

                # Desempacota os resultados
                one_turn_response, one_turn_duration = (
                    AgentResponse(output=None, messages=[]),
                    0.0,
                )
                multi_turn_output = None

                result_index = 0
                # Verifica se a TAREFA foi criada para saber se devemos esperar um resultado
                if one_turn_task:
                    one_turn_response, one_turn_duration = results[result_index]
                    result_index += 1
                if multi_turn_task:
                    multi_turn_output = results[result_index]

                # Desempacota os resultados na ordem correta
                one_turn_response, one_turn_duration = (
                    AgentResponse(output=None, messages=[]),
                    0.0,
                )
                multi_turn_output = None

                result_index = 0
                if one_turn_task:
                    one_turn_response, one_turn_duration = results[result_index]
                    result_index += 1
                if multi_turn_task:
                    multi_turn_output = results[result_index]

                # O resto do método continua como está...
                evaluations = await self._execute_evaluations(
                    task, one_turn_response, one_turn_duration, multi_turn_output
                )

                # Separa avaliações por tipo
                one_turn_evals = [e for e in evaluations if e.get("turn_type") == "one"]
                multi_turn_evals = [
                    e for e in evaluations if e.get("turn_type") == "multiple"
                ]

                # Constrói resultado final
                run_result = RunResult(
                    duration_seconds=round(time.perf_counter() - start_time, 4),
                    task_data=task,
                    one_turn_analysis=OneTurnAnalysis(
                        agent_response=one_turn_response.output,
                        reasoning_trace=one_turn_response.messages,
                        evaluations=one_turn_evals,
                    ),
                    multi_turn_analysis=MultiTurnAnalysis(
                        final_agent_response=(
                            multi_turn_output.final_agent_response.output
                            if multi_turn_output
                            else None
                        ),
                        conversation_transcript=(
                            multi_turn_output.transcript if multi_turn_output else None
                        ),
                        evaluations=multi_turn_evals,
                    ),
                )

                return run_result.model_dump(exclude_none=True)

            except Exception as e:
                duration = round(time.perf_counter() - start_time, 4)
                logger.error(
                    f"Erro irrecuperável ao processar tarefa {task_id}: {e}",
                    exc_info=True,
                )
                return {
                    "duration_seconds": duration,
                    "task_data": task.model_dump(),
                    "error": f"Erro irrecuperável: {str(e)}",
                }

    def _safe_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calcula estatísticas de forma segura."""
        if not values:
            return {}

        stats = {
            "average": round(statistics.mean(values), 4),
            "median": round(statistics.median(values), 4),
            "min": min(values),
            "max": max(values),
        }

        if len(values) > 1:
            stats["std_dev"] = round(statistics.stdev(values), 4)
        else:
            stats["std_dev"] = 0.0

        return stats

    def _calculate_metrics_summary(
        self, runs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calcula resumo das métricas com melhor tratamento de erros."""
        stats_by_metric: defaultdict[str, MetricStats] = defaultdict(
            lambda: {"scores": [], "times": [], "errors": 0}
        )

        # Coleta dados de todas as execuções
        for run in runs:
            if "error" in run:
                continue

            all_evaluations = []

            # Coleta avaliações de ambos os tipos
            for analysis_key in ["one_turn_analysis", "multi_turn_analysis"]:
                analysis = run.get(analysis_key)
                if analysis and "evaluations" in analysis:
                    all_evaluations.extend(analysis["evaluations"])

            # Processa cada avaliação
            for evaluation in all_evaluations:
                metric_name = evaluation.get("metric_name", "unknown")
                stats = stats_by_metric[metric_name]

                # Adiciona tempo de duração
                duration = evaluation.get("duration_seconds", 0.0)
                stats["times"].append(duration)

                # Verifica erros e scores
                if evaluation.get("has_error") or evaluation.get("score") is None:
                    stats["errors"] += 1
                else:
                    score = evaluation.get("score")
                    if isinstance(score, (int, float)):
                        stats["scores"].append(float(score))

        # Gera resumo para cada métrica
        metrics_summary = []
        for metric_name, stats in stats_by_metric.items():
            scores, times, error_count = (
                stats["scores"],
                stats["times"],
                stats["errors"],
            )
            successful_runs = len(scores)
            total_runs = successful_runs + error_count

            if total_runs == 0:
                continue

            # Calcula distribuição de scores
            score_distribution = []
            if successful_runs > 0:
                score_counts = Counter(scores)
                for score_value, count in sorted(score_counts.items()):
                    score_distribution.append(
                        {
                            "value": score_value,
                            "count": count,
                            "percentage": round((count / successful_runs) * 100, 2),
                        }
                    )

            summary = {
                "metric_name": metric_name,
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "success_rate_percentage": round(
                    (successful_runs / total_runs) * 100, 2
                ),
                "failed_runs": error_count,
                "failure_rate_percentage": round((error_count / total_runs) * 100, 2),
                "score_statistics": self._safe_statistics(scores) if scores else None,
                "duration_statistics_seconds": (
                    self._safe_statistics(times) if times else None
                ),
                "score_distribution": score_distribution,
            }
            metrics_summary.append(summary)

        return sorted(metrics_summary, key=lambda x: x["metric_name"])

    def _calculate_error_summary(self, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula resumo de erros de forma mais eficiente."""
        error_breakdown = defaultdict(int)
        failed_run_ids = set()

        for run in runs:
            run_id = run.get("task_data", {}).get("id", "unknown")

            # Verifica erro na execução da tarefa
            if "error" in run:
                failed_run_ids.add(run_id)
                continue

            # Verifica erros nas avaliações
            has_evaluation_error = False

            for analysis_key in ["one_turn_analysis", "multi_turn_analysis"]:
                analysis = run.get(analysis_key)
                if not analysis or "evaluations" not in analysis:
                    continue

                for evaluation in analysis["evaluations"]:
                    if evaluation.get("has_error"):
                        has_evaluation_error = True
                        metric_name = evaluation.get("metric_name", "unknown")
                        error_breakdown[metric_name] += 1

            if has_evaluation_error:
                failed_run_ids.add(run_id)

        return {
            "total_failed_runs": len(failed_run_ids),
            "errors_per_metric": dict(sorted(error_breakdown.items())),
            "failed_run_ids": sorted(list(failed_run_ids)),
        }

    def _calculate_execution_summary(
        self,
        runs: List[Dict[str, Any]],
        total_duration: float,
        aggregate_metrics: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Calcula resumo da execução."""
        # Duração média por tarefa
        task_durations = [
            r.get("duration_seconds", 0) for r in runs if "error" not in r
        ]
        avg_task_duration = (
            round(sum(task_durations) / len(task_durations), 2)
            if task_durations
            else 0.0
        )

        # Duração média por métrica
        metric_durations = [
            m.get("duration_statistics_seconds", {}).get("average", 0)
            for m in aggregate_metrics
            if m.get("duration_statistics_seconds")
        ]
        avg_metric_duration = (
            round(sum(metric_durations) / len(metric_durations), 2)
            if metric_durations
            else 0.0
        )

        return {
            "total_duration_seconds": round(total_duration, 2),
            "average_task_duration_seconds": avg_task_duration,
            "average_metric_duration_seconds": avg_metric_duration,
        }

    def _generate_experiment_id(self) -> int:
        """Gera ID único para o experimento."""
        experiment_hash = hashlib.sha256(
            f"{self.experiment_name}_{datetime.now(timezone.utc).isoformat()}_{uuid.uuid4().hex}".encode()
        ).hexdigest()
        return int(experiment_hash[:16], 16) & (2**63 - 1)

    async def _save_results(self, final_result: Dict[str, Any]) -> Path:
        """Salva resultados em arquivo JSON."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"results_{self.experiment_name}.json"

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(final_result, f, indent=2, ensure_ascii=False)
            logger.info(f"Resultados salvos em: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {e}")
            raise

    async def run(self, loader: DataLoader) -> Dict[str, Any]:
        """
        Executa o experimento completo.

        Args:
            loader: DataLoader com as tarefas a serem executadas

        Returns:
            Dicionário com resultados completos do experimento
        """
        logger.info(f"Iniciando experimento: {self.experiment_name}")
        start_time = time.perf_counter()

        # Carrega tarefas
        tasks = list(loader.get_tasks())
        logger.info(f"Carregadas {len(tasks)} tarefas para processamento")

        if not tasks:
            raise ValueError("Nenhuma tarefa encontrada no loader")

        # Executa processamento das tarefas
        runs = await tqdm_asyncio.gather(
            *[self._process_task(task) for task in tasks],
            desc=f"Executando: {self.experiment_name}",
        )

        total_duration = time.perf_counter() - start_time

        # Calcula métricas agregadas
        logger.info("Calculando métricas agregadas...")
        aggregate_metrics = self._calculate_metrics_summary(runs)
        error_summary = self._calculate_error_summary(runs)
        execution_summary = self._calculate_execution_summary(
            runs, total_duration, aggregate_metrics
        )

        # Obtém configuração do dataset
        dataset_config = loader.get_dataset_config()

        # Monta resultado final
        final_result = {
            "dataset_name": dataset_config.get("dataset_name"),
            "dataset_description": dataset_config.get("dataset_description"),
            "dataset_id": dataset_config.get("dataset_id"),
            "experiment_id": self._generate_experiment_id(),
            "experiment_name": self.experiment_name,
            "experiment_description": self.experiment_description,
            "experiment_timestamp": datetime.now(timezone.utc).isoformat(),
            "experiment_metadata": self.metadata,
            "execution_summary": execution_summary,
            "error_summary": error_summary,
            "aggregate_metrics": aggregate_metrics,
            "runs": runs,
        }

        # Salva resultados
        await self._save_results(final_result)

        # Upload para BigQuery se habilitado
        if self.upload_to_bq:
            try:
                logger.info("Fazendo upload para BigQuery...")
                upload_experiment_to_bq(result_data=final_result)
                logger.info("Upload para BigQuery concluído")
            except Exception as e:
                logger.error(f"Erro no upload para BigQuery: {e}")
                # Não falha o experimento por erro de upload

        logger.info(
            f"Experimento '{self.experiment_name}' concluído em "
            f"{execution_summary['total_duration_seconds']}s"
        )

        return final_result
