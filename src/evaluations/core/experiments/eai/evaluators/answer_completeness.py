# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
)
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class AnswerCompletenessEvaluator(BaseOneTurnEvaluator):
    """
    Avalia a capacidade de memória do agente com base na transcrição
    completa de uma conversa.
    """

    name = "answer_completeness"

    ANSWER_COMPLETENESS_PROMPT = """
In this task, you will evaluate how well a model's response captures the core topics and essential concepts present in an ideal (gold standard) response.

The evaluation is based on content coverage, not stylistic similarity or phrasing.
Focus on whether the model response includes the *key points* that matter most. Minor omissions or differences in wording should not count agains the response if the main substance is captured.

Assign one of the following labels:
- "equivalent": The model's response captures all or most important concepts from the ideal response. Minor missing details are acceptable if the main points are clearly conveyed.
- "different": The model's response misses most key ideas or diverges substantially in meaning.

Your response must be a single word: "equivalent" or "different", with no other text.

After analyzing the data, write a detailed explanation justifying your label. Your explanation should:
- Briefly list the key topics or concepts from the ideal response.
- If any of the important key topics is missing, list it and explain what it is and how that impacts understanding.

[BEGIN DATA]
Query: {query}
Model Response: {model_response}
Ideal Response: {ideal_response}
[END DATA]

Please analyze the data carefully and then provide:

explanation: Your reasoning step by step, comparing the model response to the ideal response, and mentioning what (if anything) was missing.
label: "equivalent" or "different"
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de aderência à persona usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.ANSWER_COMPLETENESS_PROMPT,
            task=task,
            agent_response=agent_response,
        )