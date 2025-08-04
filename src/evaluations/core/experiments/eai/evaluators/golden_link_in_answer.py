# -*- coding: utf-8 -*-
from src.evaluations.core.experiments.eai.evaluators.utils import (
    parse_golden_links,
    extract_links_from_text,
    match_golden_link,
)
from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
    BaseOneTurnEvaluator,
)


class GoldenLinkInAnswerEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta de um agente adere a uma persona pré-definida.
    """

    name = "golden_link_in_answer"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de aderência à persona usando o cliente juiz.
        """
        try:
            message = agent_response.message
            golden_field = task.golden_links_list
            golden_links = parse_golden_links(golden_field)

            answer_links = extract_links_from_text(message)

            if not answer_links or not golden_links:
                score = 0
                annotations = "No links found in the answer or no golden links provided"
            else:
                score = 1
                annotations = "Golden links found in the answer"

            has_error = False
            error_message = None
        except Exception as e:
            score = None
            annotations = None
            has_error = True
            error_message = str(e)

        return EvaluationResult(
            score=score,
            annotations=annotations,
            has_error=has_error,
            error_message=error_message,
        )
