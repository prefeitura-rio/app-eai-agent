# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    AgentResponse,
    BaseOneTurnEvaluator,
    EvaluationResult,
    EvaluationTask,
)


class ToolInvocationAccuracyEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente invocou a ferramenta esperada ("golden tool").
    """

    name = "tool_invocation_accuracy"

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        try:
            golden_tool = self._extract_golden_tool(task)
            if not golden_tool:
                return EvaluationResult(
                    score=0,
                    annotations="No golden tool specified in task",
                    has_error=False,
                    error_message=None,
                )
            
            invoked_tools = self._extract_invoked_tools(agent_response)
            
            if not invoked_tools and not golden_tool:
                score = 1            
            elif golden_tool in invoked_tools:
                score = 1
            else:
                score = 0
            
            return EvaluationResult(
                score=score,
                annotations={
                    "golden_tool": golden_tool,
                    "invoked_tools": list(invoked_tools),
                    "match": golden_tool in invoked_tools,
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

    def _extract_golden_tool(self, task: EvaluationTask) -> str | None:
        if hasattr(task, 'golden_tool'):
            return task.golden_tool
        
        if hasattr(task, 'metadata') and task.metadata:
            return task.metadata.get('golden_tool')
        
        return None

    def _extract_invoked_tools(self, agent_response: AgentResponse) -> set[str]:
        invoked = set()
        
        if not agent_response.reasoning_trace:
            return invoked
        
        for step in agent_response.reasoning_trace:
            if step.message_type != "tool_return_message":
                continue

            tool_name = step.content.get("name")
            if tool_name:
                invoked.add(tool_name)

        return invoked