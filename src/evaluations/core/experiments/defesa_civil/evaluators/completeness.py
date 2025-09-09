# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class DefesaCivilCompletenessEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta de emergência é completa baseada nos critérios específicos.
    """

    name = "defesa_civil_completeness"

    PROMPT_TEMPLATE = """
Você é um especialista em comunicação de emergência da Defesa Civil.
Avalie se a resposta está completa baseada nos critérios específicos para esta situação.

**Pergunta Original:**
{task[prompt]}

**Resposta Gerada pela IA:**
{agent_response[message]}

**Critérios Específicos a Serem Avaliados:**
{task[metadata][criterios_avaliados]}

**Contexto da Situação:**
- Complexidade: {task[metadata][complexidade]}
- Urgência: {task[metadata][urgencia]}
- Contexto: {task[metadata][contexto]}
- Ferramentas necessárias: {task[metadata][tools]}

**Instruções:**
Verifique se a resposta aborda TODOS os critérios listados de forma adequada.
Para situações de alta urgência, a resposta deve ser direta e actionable.
Para situações complexas, deve incluir múltiplas orientações e alternativas.

**Escala:**
- 0.0: Critérios importantes não abordados
- 0.3: Alguns critérios abordados superficialmente
- 0.5: Metade dos critérios bem abordados
- 0.8: Quase todos critérios abordados adequadamente
- 1.0: Todos critérios completamente abordados

Responda EXATAMENTE no formato:
Score: <valor entre 0.0 e 1.0>
Reasoning: <explicação detalhando quais critérios foram ou não atendidos>
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de completude da resposta.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )