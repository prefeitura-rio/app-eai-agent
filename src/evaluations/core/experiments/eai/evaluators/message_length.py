# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class MessageLengthEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente está conforme as regras de formatação do WhatsApp.
    """

    name = "menssage_lengh"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            msg = agent_response.message

            length = len(str(msg))
            if length <= 650:
                score = 1
            elif length > 650 and length <= 1000:
                score = 0.75
            elif length > 1000 and length <= 2000:
                score = 0.5
            elif length > 2000 and length <= 3000:
                score = 0.25
            else:
                score = 0

            return EvaluationResult(
                score=score,
                annotations=f"Message length {length}",
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
