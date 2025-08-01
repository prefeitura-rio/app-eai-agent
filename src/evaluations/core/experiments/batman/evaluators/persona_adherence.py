# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
    BaseOneTurnEvaluator,
)


class PersonaAdherenceEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta de um agente adere a uma persona pré-definida.
    """

    name = "persona_adherence"

    PROMPT_TEMPLATE = """
Avalie se a resposta da IA adere à persona definida: **{task[persona]}**.
**Resposta Gerada pela IA:**
{agent_response[message]}
**Sua Tarefa:**
Ruim: 0.0
Bom: 0.5
Exelente:1.0

Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float>
Reasoning: <uma explicação curta sobre como a resposta se alinha (ou não) à persona>
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de aderência à persona usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )
