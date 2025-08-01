# -*- coding: utf-8 -*-
import time
import asyncio
from typing import List, Dict, Any, Optional

from src.evaluations.core.eval.schemas import (
    EvaluationTask,
    AgentResponse,
    RunResult,
    ConversationOutput,
    EvaluationResult,
    EvaluationContext,
)
from src.evaluations.core.eval.evaluators.base import (
    BaseEvaluator,
    BaseConversationEvaluator,
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
        self.analysis_evaluators = self.evaluator_cache.get("analysis", [])
        self.conversation_evaluator = self.evaluator_cache.get("conversation", [None])[
            0
        ]

    async def process(self, task: EvaluationTask) -> Dict[str, Any]:
        """
        Processa uma única tarefa, retornando seu resultado completo.
        """
        task_id = task.id
        logger.info(f"Iniciando processamento da tarefa: {task_id}")
        start_time = time.perf_counter()

        # 1. Inicia a coleta de dados de forma concorrente
        one_turn_task = asyncio.create_task(
            self._get_one_turn_response_safely(task)
        )
        multi_turn_task = asyncio.create_task(
            self._get_multi_turn_output_safely(task)
        )

        # 2. Aguarda a conclusão de ambas as coletas
        one_turn_response, multi_turn_output = await asyncio.gather(
            one_turn_task, multi_turn_task
        )

        # 3. Cria o contexto unificado para os avaliadores
        evaluation_context = EvaluationContext(
            task=task,
            one_turn_response=one_turn_response,
            multi_turn_output=multi_turn_output,
        )

        # 4. Executa as avaliações de análise
        evaluations = await self._execute_analysis_evaluations(evaluation_context)

        # 5. Monta o resultado final
        run_result = RunResult(
            duration_seconds=round(time.perf_counter() - start_time, 4),
            task_data=task,
            one_turn_response=one_turn_response,
            multi_turn_output=multi_turn_output,
            evaluations=evaluations,
        )
        return run_result.model_dump()

    async def _get_one_turn_response_safely(
        self, task: EvaluationTask
    ) -> AgentResponse:
        """Obtém a resposta de turno único, capturando exceções."""
        try:
            response, _ = await self.response_manager.get_one_turn_response(task)
            return response
        except Exception as e:
            error_msg = f"Falha crítica ao obter resposta one-turn: {e}"
            logger.error(f"{error_msg} para a tarefa {task.id}", exc_info=False)
            return AgentResponse(has_error=True, error_message=error_msg)

    async def _get_multi_turn_output_safely(
        self, task: EvaluationTask
    ) -> Optional[ConversationOutput]:
        """Obtém a transcrição multi-turno, capturando exceções."""
        if not self.conversation_evaluator:
            return None

        # Garante que o avaliador é do tipo correto antes de passá-lo adiante.
        if not isinstance(self.conversation_evaluator, BaseConversationEvaluator):
            error_msg = f"Configuração inválida: o avaliador '{self.conversation_evaluator.name}' não é um 'BaseConversationEvaluator'."
            logger.error(error_msg)
            return ConversationOutput(has_error=True, error_message=error_msg)

        try:
            return await self.response_manager.get_multi_turn_transcript(
                task, self.conversation_evaluator
            )
        except Exception as e:
            error_msg = f"Falha crítica ao obter resposta multi-turn: {e}"
            logger.error(f"{error_msg} para a tarefa {task.id}", exc_info=False)
            return ConversationOutput(has_error=True, error_message=error_msg)

    async def _execute_analysis_evaluations(
        self,
        context: EvaluationContext,
    ) -> List[Dict[str, Any]]:
        """Executa todas as avaliações de análise para uma tarefa."""
        if not self.analysis_evaluators:
            return []

        eval_tasks = [
            self._execute_single_evaluation(evaluator, context)
            for evaluator in self.analysis_evaluators
        ]
        results = await asyncio.gather(*eval_tasks)
        return sorted(results, key=lambda x: x["metric_name"])

    async def _execute_single_evaluation(
        self,
        evaluator: BaseEvaluator,
        context: EvaluationContext,
    ) -> Dict[str, Any]:
        """Executa uma única avaliação com medição de tempo."""
        log_context = f"analysis/{evaluator.name}"
        with logger.contextualize(task_id=context.task.id, turn_type=log_context):
            start_time = time.perf_counter()
            try:
                result = await evaluator.evaluate(context)
            except Exception as e:
                error_msg = f"Erro inesperado na avaliação {evaluator.name} para tarefa {context.task.id}: {e}"
                logger.error(error_msg, exc_info=True)
                result = EvaluationResult(
                    annotations=error_msg,
                    has_error=True,
                    error_message=str(e),
                )
            duration = time.perf_counter() - start_time
            return {
                "metric_name": evaluator.name,
                "duration_seconds": round(duration, 4),
                **result.model_dump(),
            }
