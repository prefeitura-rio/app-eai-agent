# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse
from src.evaluations.core.experiments.eai.evaluators.utils import extract_links_from_text


class HasLinkEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente contém algum link.
    """

    name = "has_link"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            answer_links = extract_links_from_text(agent_response.message)
            score = 1 if answer_links else 0
            annotations = f"Links in Answer: {answer_links}" if answer_links else "No links found in the answer."

            return EvaluationResult(
                score=score,
                annotations=annotations,
                has_error=False,
                error_message=None,
            )

        except Exception as e:
            return EvaluationResult(
                score=None,
                annotations=None,
                has_error=True,
                error_message=str(e),
            )
