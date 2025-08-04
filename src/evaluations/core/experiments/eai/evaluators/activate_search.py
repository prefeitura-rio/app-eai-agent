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


class ActivateSearchEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta de um agente adere a uma persona pré-definida.
    """

    name = "activate_search"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de aderência à persona usando o cliente juiz.
        """
        SEARCH_TOOL_NAMES = [
            # "public_services_grounded_search",
            "google_search",
            "equipments_instructions",
            "equipments_by_address",
        ]

        try:

            activated_tools = set()
            if agent_response.reasoning_trace:
                for step in agent_response.reasoning_trace:
                    tool_call = step.content.get("tool_call", {}) if step.message_type == "tool_call_message" else None
                    if tool_call and tool_call.get("name") in SEARCH_TOOL_NAMES:
                        activated_tools.add(tool_call.get("name"))

            explanation = f"Activated tools: {activated_tools}"
            score = len(activated_tools) > 0
            annotations = explanation
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
