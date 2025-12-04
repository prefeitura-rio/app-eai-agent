# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
    BaseOneTurnEvaluator,
)


class ActivateSearchEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta de um agente aciona ferramentas de busca específicas.
    """

    name = "activate_search"
    SEARCH_TOOL_NAMES = [
        "google_search",
        "equipments_instructions",
        "equipments_by_address",
        "dharma_search_tool",
        "web_search_surkai",
        # "public_services_grounded_search",
    ]

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        try:
            activated_tools = self._extract_activated_tools(agent_response)
            score = len(activated_tools) > 0
            annotations = f"Activated tools: {list(activated_tools)}"
            
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

    def _extract_activated_tools(self, agent_response: AgentResponse) -> set[str]:
        activated = set()

        if not agent_response.reasoning_trace:
            return activated
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue

            if step.content.get("name") in self.SEARCH_TOOL_NAMES:
                activated.add(step.content.get("name"))
        
        return activated
