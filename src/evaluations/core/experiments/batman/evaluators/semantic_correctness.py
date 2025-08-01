# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    BaseAnalysisEvaluator,
    EvaluationContext,
    EvaluationResult,
)


class SemanticCorrectnessEvaluator(BaseAnalysisEvaluator):
    """
    Avalia a correção semântica de uma única resposta do agente em comparação
    com uma resposta de referência ("golden").
    """

    name = "semantic_correctness"
    required_context = "one_turn"

    PROMPT_TEMPLATE = """
Avalie similaridade semântica da resposta gerada por uma IA em relacao a Resposta ideal.
**Resposta Gerada pela IA:**
{context[one_turn_response][output]}
**Resposta Ideal:**
{context[task][golden_response_one_shot]}

**Sua Tarefa:**
Ruim: 0.0
Bom: 0.5
Exelente:1.0

Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float >
Reasoning: <uma explicação curta e objetiva para a sua nota>
"""

    async def _evaluate_logic(self, context: EvaluationContext) -> EvaluationResult:
        """
        Executa a avaliação de correção semântica usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            context=context,
        )
