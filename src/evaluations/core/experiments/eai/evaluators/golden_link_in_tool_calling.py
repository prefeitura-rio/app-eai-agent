# -*- coding: utf-8 -*-
import json
from typing import Dict, Any, Tuple
from src.evaluations.core.experiments.eai.evaluators.utils import (
    parse_golden_links,
    match_golden_link,
)
from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
    BaseOneTurnEvaluator,
)


class GoldenLinkInToolCallingEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta de um agente adere a uma persona pré-definida.
    """

    name = "golden_link_in_tool_calling"

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de aderência à persona usando o cliente juiz.
        """
        try:
            golden_field = task.golden_links_list
            golden_links = parse_golden_links(golden_field)

            answer_links = []
            if agent_response.reasoning_trace:
                for step in agent_response.reasoning_trace:
                    if step.message_type == "tool_call_message":
                        tool_call = step.content.get("tool_call", {})
                        tools = ["google_search", "equipments_instructions", "equipments_by_address"]
                        if tool_call.get("name") in tools:
                            arguments = tool_call.get("arguments", "{}")
                            try:
                                parsed_args = json.loads(arguments)
                            except (json.JSONDecodeError, TypeError):
                                parsed_args = arguments
                            
                            if isinstance(parsed_args, dict):
                                links = parsed_args.get("links", [])
                                answer_links.extend(links)

            if not answer_links or not golden_links:
                score = 0 
                annotations = "No links found in the answer or no golden links provided"
            else:
                answer_links, overall_count = match_golden_link(answer_links, golden_links)
                score = 1 if overall_count > 0 else 0
                annotations = {
                    "golden_links": golden_links,
                    "answer_links": answer_links,
                    "number_of_matches": overall_count,
                }

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
