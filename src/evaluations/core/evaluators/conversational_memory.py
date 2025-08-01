# -*- coding: utf-8 -*-
from src.evaluations.core.evaluators.base import BaseEvaluator
from src.evaluations.core.schemas import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnContext,
)


class ConversationalMemoryEvaluator(BaseEvaluator):
    """
    Avalia a capacidade de memória do agente com base na transcrição
    completa de uma conversa.
    """

    name = "conversational_memory"
    turn_type = "multiple"

    PROMPT_TEMPLATE = """
Você é um Juiz de IA. Sua tarefa é fornecer um julgamento final sobre a **MEMÓRIA** de um agente com base em uma conversa.

**Objetivo da Avaliação:**
{task[golden_response_multiple_shot]}

**Transcrição Completa da Conversa:**
{agent_response[conversation_history]}

**Sua Tarefa:**
Ruim: 0.0
Bom: 0.5
Exelente:1.0
Analise a transcrição e compare o desempenho do agente com o objetivo.
Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float para a capacidade de MEMÓRIA>
Reasoning: <uma explicação curta e objetiva para a sua nota de MEMÓRIA>
"""

    async def evaluate(
        self, agent_response: MultiTurnContext, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de memória conversacional usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )
