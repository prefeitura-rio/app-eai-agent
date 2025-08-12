# -*- coding: utf-8 -*-
from src.evaluations.core.experiments.eai.evaluators.utils import (
    parse_golden_links,
    extract_links_from_text,
    match_golden_link,
)
from src.evaluations.core.eval import (
    AgentResponse,
    BaseOneTurnEvaluator,
    EvaluationTask,
    EvaluationResult,
)


class GoldenLinkInAnswerEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente contém links que correspondem a links de referência (golden links).
    """

    name = "golden_link_in_answer"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        try:
            golden_links = parse_golden_links(task.golden_links_list)
            answer_links = extract_links_from_text(agent_response.message)

            if not answer_links or not golden_links:
                return EvaluationResult(
                    score=0,
                    annotations="No links found in the answer or no golden links provided",
                    has_error=False,
                    error_message=None,
                )

            matched_links, match_count = match_golden_link(answer_links, golden_links)
            score = 1 if match_count > 0 else 0

            return EvaluationResult(
                score=score,
                annotations={
                    "golden_links": golden_links,
                    "answer_links": matched_links,
                    "number_of_matches": match_count,
                },
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
