# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    BaseAnalysisEvaluator,
    EvaluationContext,
    EvaluationResult,
)


class PersonaAdherenceEvaluator(BaseAnalysisEvaluator):
    """
    Avalia se a resposta de um agente adere a uma persona pré-definida.
    """

    name = "persona_adherence"
    required_context = "one_turn"

    PROMPT_TEMPLATE = """
Avalie se a resposta da IA adere à persona definida: **{context[task][persona]}**.
**Resposta Gerada pela IA:**
{context[one_turn_response][output]}
**Sua Tarefa:**
Ruim: 0.0
Bom: 0.5
Exelente:1.0

Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float>
Reasoning: <uma explicação curta sobre como a resposta se alinha (ou não) à persona>
"""

    async def _evaluate_logic(self, context: EvaluationContext) -> EvaluationResult:
        """
        Executa a avaliação de aderência à persona usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            context=context,
        )
