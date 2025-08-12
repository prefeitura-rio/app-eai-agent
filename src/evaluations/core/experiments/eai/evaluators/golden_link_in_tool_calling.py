# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    AgentResponse,
    BaseOneTurnEvaluator,
    EvaluationResult,
    EvaluationTask,
)
from src.evaluations.core.experiments.eai.evaluators.utils import (
    parse_golden_links,
    match_golden_link,
)


class GoldenLinkInToolCallingEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente utiliza corretamente os
    golden links durante chamadas de tools.
    """

    name = "golden_link_in_tool_calling"

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        try:
            golden_links = parse_golden_links(task.golden_links_list)
            answer_links = self._extract_links_from_trace(agent_response)

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
    
    def _extract_links_from_trace(self, agent_response: AgentResponse) -> list[str]:
        links = []
        tools = ["google_search"]

        if not agent_response or not agent_response.reasoning_trace:
            return links
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue
            
            if step.content.get("name") not in tools:
                continue

            tool_call = step.content.get("tool_return", {})
            sources = tool_call.get("sources", [])

            for source in sources:
                url = source.get("url")
                if url:
                    links.append(url) 
        
        return links
