# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    BaseEvaluator,
    EvaluationTask,
    AgentResponse,
    EvaluationResult,
)


class SemanticCorrectnessEvaluator(BaseEvaluator):
    """
    Avalia a correção semântica de uma única resposta do agente em comparação
    com uma resposta de referência ("golden").
    """

    name = "semantic_correctness"
    turn_type = "one"

    PROMPT_TEMPLATE = """
Avalie similaridade semântica da resposta gerada por uma IA em relacao a Resposta ideal.
**Resposta Gerada pela IA:**
{agent_response[output]}
**Resposta Ideal:**
{task[golden_response_one_shot]}

**Sua Tarefa:**
Ruim: 0.0
Bom: 0.5
Exelente:1.0

Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float >
Reasoning: <uma explicação curta e objetiva para a sua nota>
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de correção semântica usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )
