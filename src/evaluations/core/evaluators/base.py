# -*- coding: utf-8 -*-
import re
from abc import ABC, abstractmethod
from typing import Any, Union

from src.evaluations.core.llm_clients import BaseJudgeClient
from src.evaluations.core.schemas import (
    EvaluationTask,
    EvaluationResult,
    AgentResponse,
    MultiTurnContext,
)
from src.utils.log import logger


def _extract_evaluation_score(response: str) -> float:
    """Extrai o score de uma string formatada, retornando 0.0 se não encontrado."""
    score_match = re.search(r"Score:\s*([0-9.]+)", response, re.IGNORECASE)
    return float(score_match.group(1)) if score_match else 0.0


class BaseEvaluator(ABC):
    """
    Classe base abstrata para todos os avaliadores de métricas.
    Define a interface que cada avaliador deve implementar, garantindo que
    cada métrica seja um componente modular e "plugável".
    """

    name: str
    turn_type: str  # 'one' ou 'multiple'

    def __init__(self, judge_client: BaseJudgeClient):
        """
        Inicializa o avaliador com um cliente de LLM que atuará como juiz.

        Args:
            judge_client (BaseJudgeClient): Uma instância de um cliente de LLM
                                            que adere à interface BaseJudgeClient.
        """
        self.judge_client = judge_client

    @abstractmethod
    async def evaluate(
        self, agent_response: Any, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Método abstrato que executa a lógica de avaliação específica da métrica.

        Args:
            agent_response (Any): A resposta do agente. Pode ser um `AgentResponse`
                                  para avaliações de turno único ou um `MultiTurnContext`
                                  para avaliações multi-turno.
            task (EvaluationTask): A tarefa de avaliação contendo os dados de entrada
                                   e os metadados necessários.

        Returns:
            EvaluationResult: O resultado padronizado da avaliação.
        """
        raise NotImplementedError

    async def _get_llm_judgement(
        self,
        prompt_template: str,
        task: EvaluationTask,
        agent_response: Union[AgentResponse, MultiTurnContext],
    ) -> EvaluationResult:
        """
        Formata um prompt, executa-o contra o cliente juiz e retorna um
        resultado de avaliação padronizado.

        Este método é uma implementação auxiliar para ser usada pelas subclasses.
        """
        try:
            task_dict = task.model_dump(exclude_none=True)
            response_dict = (
                agent_response
                if isinstance(agent_response, dict)
                else agent_response.model_dump(exclude_none=True)
            )

            prompt = prompt_template.format(
                task=task_dict, agent_response=response_dict
            )
            judgement_response = await self.judge_client.execute(prompt)
            score = _extract_evaluation_score(judgement_response)
            return EvaluationResult(score=score, annotations=judgement_response)
        except Exception as e:
            logger.error(
                f"Erro durante o julgamento do LLM para o avaliador '{self.name}': {e}",
                exc_info=True,
            )
            return EvaluationResult(
                score=None,
                annotations=f"Erro na formatação ou execução do prompt: {e}",
                has_error=True,
                error_message=str(e),
            )
