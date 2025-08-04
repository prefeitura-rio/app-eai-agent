# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
)
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class AnswerAddressingEvaluator(BaseOneTurnEvaluator):
    """
    Avalia a capacidade de memória do agente com base na transcrição
    completa de uma conversa.
    """

    name = "answer_addressing"

    ANSWER_ADDRESSING_PROMPT = """
In this task, you will evaluate whether the model's response directly and sufficiently answers the user's question or addresses their underlying need. Often, a user's query, especially if phrased as a complaint or a question about a problem (e.g., "is it normal for X not to work?"), implies a request for a solution or a next step. An effective answer addresses this implicit need.

You will categorize the model's response using one of two labels:
- "answered": The response addresses the main point of the query clearly and provides a reasonably complete and useful answer. This includes responses that offer a relevant solution, actionable advice, or a clear next step when the query describes a problem or implies a need for assistance, even if a direct question for a solution was not explicitly stated. Minor omissions are acceptable if the user would still consider their underlying need or explicit question adequately addressed.
- "unanswered": The response misses or avoids the core intent of the query (explicit or implicit), answers only vaguely or incorrectly, fails to offer a relevant solution or next step when one is clearly implied by a problem statement, or leaves out key information that prevents the user from being satisfied or taking appropriate action to resolve their issue.

Your response must be a single word: "answered" or "unanswered", with no other text.

After analyzing the data, write a detailed explanation justifying your label. Your explanation should:
1. Identify the main point(s) or intent of the query, including any implicit request for a solution or assistance if the query describes a problem or expresses a complaint.
2. Analyze whether the response addresses these points (explicit and implicit) clearly and sufficiently, paying particular attention to whether a relevant solution or actionable next step was provided if the query indicated a problem.
3. If labeled "unanswered", explain exactly what was missing or unclear, or why the offered solution (if any) was inadequate, irrelevant to the user's underlying need, or if no attempt was made to address an implied problem.

[BEGIN DATA]
Query: {query}
Model Response: {model_response}
[END DATA]

Please analyze the data carefully and then provide:

explanation: Your reasoning step by step, identifying whether the model's response meets the user's explicit questions as well as their underlying needs, especially implied requests for solutions when a problem is presented.
label: "answered" or "unanswered"
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de aderência à persona usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.ANSWER_ADDRESSING_PROMPT,
            task=task,
            agent_response=agent_response,
        )
