# -*- coding: utf-8 -*-
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple

from src.evaluations.core.eval.schemas import (
    EvaluationTask,
    AgentResponse,
    TaskOutput,
    OneTurnAnalysis,
    MultiTurnAnalysis,
    ConversationOutput,
    EvaluationResult,
    MultiTurnEvaluationInput,
)
from src.evaluations.core.eval.evaluators.base import (
    BaseEvaluator,
    BaseConversationEvaluator,
    BaseOneTurnEvaluator,
    BaseMultipleTurnEvaluator,
)
from src.evaluations.core.eval.runner.response_manager import ResponseManager
from src.evaluations.core.eval.log import logger


class TaskProcessor:
    """
    Orquestra o processamento de uma única tarefa de avaliação,
    desde a obtenção da resposta até a execução de todas as métricas.
    """

    def __init__(
        self,
        evaluator_cache: Dict[str, List[BaseEvaluator]],
        response_manager: ResponseManager,
    ):
        self.evaluator_cache = evaluator_cache
        self.response_manager = response_manager

    async def process(self, task: EvaluationTask) -> Dict[str, Any]:
        """
        Processa uma única tarefa, retornando seu resultado completo.
        Falhas na obtenção de resposta de um tipo (one-turn vs multi-turn)
        são registradas, mas não impedem o processamento do outro.
        """
        task_id = task.id
        logger.info(f"Iniciando processamento da tarefa: {task_id}")
        start_time = time.perf_counter()

        # 1. Coleta de dados de forma resiliente
        one_turn_task = asyncio.create_task(self._get_one_turn_response(task))
        multi_turn_task = asyncio.create_task(self._get_multi_turn_output(task))

        results = await asyncio.gather(
            one_turn_task, multi_turn_task, return_exceptions=True
        )

        one_turn_result, multi_turn_result = results

        # 2. Processa o resultado de one-turn
        one_turn_response = AgentResponse(message=None, reasoning_trace=[])
        one_turn_duration = 0.0
        one_turn_analysis = OneTurnAnalysis()

        if isinstance(one_turn_result, Exception):
            error_msg = f"Falha ao obter resposta one-turn: {str(one_turn_result)}"
            logger.error(f"{error_msg} para a tarefa {task_id}", exc_info=False)
            one_turn_analysis.has_error = True
            one_turn_analysis.error_message = error_msg
        else:
            one_turn_response, one_turn_duration = one_turn_result
            one_turn_analysis.agent_message = one_turn_response.message
            one_turn_analysis.agent_reasoning_trace = one_turn_response.reasoning_trace

        # 3. Processa o resultado de multi-turn
        multi_turn_output: Optional[ConversationOutput] = None
        multi_turn_analysis = MultiTurnAnalysis()

        if isinstance(multi_turn_result, Exception):
            error_msg = f"Falha ao obter resposta multi-turn: {str(multi_turn_result)}"
            logger.error(f"{error_msg} para a tarefa {task_id}", exc_info=False)
            multi_turn_analysis.has_error = True
            multi_turn_analysis.error_message = error_msg
        else:
            multi_turn_output = multi_turn_result
            if multi_turn_output:
                multi_turn_analysis.final_agent_message = (
                    multi_turn_output.final_agent_message_details.message
                )
                multi_turn_analysis.transcript = multi_turn_output.transcript

        # 4. Executa as avaliações com os dados disponíveis
        evaluations_with_type = await self._execute_evaluations(
            task, one_turn_response, one_turn_duration, multi_turn_output
        )

        one_turn_analysis.evaluations = [
            result_dict
            for evaluator, result_dict in evaluations_with_type
            if isinstance(evaluator, BaseOneTurnEvaluator)
        ]
        multi_turn_analysis.evaluations = [
            result_dict
            for evaluator, result_dict in evaluations_with_type
            if isinstance(evaluator, BaseMultipleTurnEvaluator)
        ]

        # 5. Monta o resultado final
        task_output = TaskOutput(
            duration_seconds=round(time.perf_counter() - start_time, 4),
            task_data=task,
            one_turn_analysis=one_turn_analysis,
            multi_turn_analysis=multi_turn_analysis,
        )
        return task_output.model_dump()

    async def _get_one_turn_response(
        self, task: EvaluationTask
    ) -> Tuple[AgentResponse, float]:
        if not self.evaluator_cache["one_turn"]:
            return AgentResponse(message=None, reasoning_trace=[]), 0.0

        with logger.contextualize(task_id=task.id, turn_type="one"):
            return await self.response_manager.get_one_turn_response(task)

    async def _get_multi_turn_output(
        self, task: EvaluationTask
    ) -> Optional[ConversationOutput]:
        conv_evaluator = self._get_conversation_evaluator(task.id)
        if not self.evaluator_cache["multi_turn"] or not conv_evaluator:
            return None

        with logger.contextualize(task_id=task.id, turn_type="multi"):
            return await self.response_manager.get_multi_turn_transcript(
                task, conv_evaluator
            )

    def _get_conversation_evaluator(
        self, task_id: str
    ) -> Optional[BaseConversationEvaluator]:
        if not self.evaluator_cache["conversation"]:
            return None
        evaluator = self.evaluator_cache["conversation"][0]
        if isinstance(evaluator, BaseConversationEvaluator):
            return evaluator
        logger.error(
            f"Erro de tipo: avaliador em 'conversation' não é um "
            f"BaseConversationEvaluator para a tarefa {task_id}"
        )
        return None

    async def _execute_evaluations(
        self,
        task: EvaluationTask,
        one_turn_response: AgentResponse,
        one_turn_duration: float,
        multi_turn_output: Optional[ConversationOutput],
    ) -> List[Tuple[BaseEvaluator, Dict[str, Any]]]:
        """Executa todas as avaliações de análise para uma tarefa."""
        analysis_evaluators = (
            self.evaluator_cache["one_turn"] + self.evaluator_cache["multi_turn"]
        )
        if not analysis_evaluators:
            return []

        eval_tasks = [
            self._execute_single_evaluation(
                evaluator, task, one_turn_response, multi_turn_output
            )
            for evaluator in analysis_evaluators
        ]
        results = await asyncio.gather(*eval_tasks, return_exceptions=True)

        processed_results = []
        for i, result in enumerate(results):
            evaluator = analysis_evaluators[i]
            if isinstance(result, BaseException):
                logger.error(f"Erro crítico na avaliação {evaluator.name}: {result}")
                eval_result = EvaluationResult(
                    annotations=f"Erro crítico: {str(result)}",
                    has_error=True,
                    error_message=str(result),
                )
                result_dict = {
                    "metric_name": evaluator.name,
                    "duration_seconds": 0.0,
                    **eval_result.model_dump(),
                }
            else:
                eval_dict, judge_duration = result
                gen_duration = (
                    multi_turn_output.duration_seconds
                    if isinstance(evaluator, BaseMultipleTurnEvaluator)
                    and multi_turn_output
                    else one_turn_duration
                )
                eval_dict["duration_seconds"] = round(gen_duration + judge_duration, 4)
                result_dict = eval_dict

            processed_results.append((evaluator, result_dict))

        return sorted(processed_results, key=lambda x: x[1]["metric_name"])

    async def _execute_single_evaluation(
        self,
        evaluator: BaseEvaluator,
        task: EvaluationTask,
        one_turn_response: AgentResponse,
        multi_turn_output: Optional[ConversationOutput],
    ) -> Tuple[Dict[str, Any], float]:
        """Executa uma única avaliação com medição de tempo."""
        log_context = f"{evaluator.turn_type}/{evaluator.name}"
        with logger.contextualize(task_id=task.id, turn_type=log_context):
            start_time = time.perf_counter()
            try:
                if isinstance(evaluator, BaseMultipleTurnEvaluator):
                    result = await self._evaluate_multi_turn(
                        evaluator, task, multi_turn_output
                    )
                elif isinstance(evaluator, BaseOneTurnEvaluator):
                    result = await self._evaluate_one_turn(
                        evaluator, task, one_turn_response
                    )
                else:
                    raise ValueError(
                        f"Tipo de avaliador não suportado: {type(evaluator).__name__}"
                    )

                duration = time.perf_counter() - start_time
                eval_result = EvaluationResult.model_validate(result)
                return {
                    "metric_name": evaluator.name,
                    "duration_seconds": round(duration, 4),
                    **eval_result.model_dump(),
                }, duration

            except Exception as e:
                duration = time.perf_counter() - start_time
                error_msg = str(e)
                logger.error(error_msg)
                eval_result = EvaluationResult(
                    annotations=error_msg,
                    has_error=True,
                    error_message=str(e),
                    score=None,
                )
                return {
                    "metric_name": evaluator.name,
                    "duration_seconds": round(duration, 4),
                    **eval_result.model_dump(),
                }, duration

    async def _evaluate_multi_turn(
        self,
        evaluator: BaseEvaluator,
        task: EvaluationTask,
        multi_turn_output: Optional[ConversationOutput],
    ) -> EvaluationResult:
        if not multi_turn_output:
            raise ValueError(
                f"a coluna/chave obrigatória 'multi_turn_transcript' não foi encontrada nos dados pré-computados para a tarefa '{task.id}'."
            )
        multi_turn_evaluation_input = MultiTurnEvaluationInput(
            conversation_history="\n".join(multi_turn_output.conversation_history),
            transcript=multi_turn_output.transcript,
        )
        return await evaluator.evaluate(
            agent_response=multi_turn_evaluation_input, task=task
        )

    async def _evaluate_one_turn(
        self,
        evaluator: BaseEvaluator,
        task: EvaluationTask,
        one_turn_response: AgentResponse,
    ) -> EvaluationResult:
        if one_turn_response.message is None:
            raise ValueError(
                f"a coluna/chave obrigatória 'one_turn_agent_message' não foi encontrada nos dados pré-computados para a tarefa '{task.id}'."
            )
        return await evaluator.evaluate(agent_response=one_turn_response, task=task)
