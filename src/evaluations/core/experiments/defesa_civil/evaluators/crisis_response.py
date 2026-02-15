# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class DefesaCivilCrisisResponseEvaluator(BaseOneTurnEvaluator):
    """
    Avalia a adequação da resposta para situações de emergência e crise,
    considerando urgência, complexidade e contexto.
    """

    name = "defesa_civil_crisis_response"

    PROMPT_TEMPLATE = """
Você é um especialista em gestão de crises e comunicação de emergência da Defesa Civil.
Avalie se a resposta é adequada para a situação específica de emergência apresentada.

**Pergunta Original:**
{task[prompt]}

**Resposta Gerada pela IA:**
{agent_response[message]}

**Características da Situação:**
- Urgência: {task[metadata][urgencia]}
- Complexidade: {task[metadata][complexidade]}
- Contexto: {task[metadata][contexto]}

**Critérios de Avaliação por Urgência:**

URGÊNCIA BAIXA:
- Informações educativas e preventivas
- Tom informativo e explicativo
- Detalhes técnicos quando apropriados

URGÊNCIA MÉDIA:
- Instruções claras de preparação
- Sinais de alerta a observar
- Medidas preventivas específicas

URGÊNCIA ALTA:
- Ações imediatas prioritárias
- Instruções step-by-step claras
- Números de emergência visíveis

URGÊNCIA CRÍTICA:
- Comandos diretos e imperativos
- Priorização de vidas sobre bens
- Comunicação rápida e decisiva
- Coordenação de múltiplos recursos

**Escala de Pontuação:**
- 0.0: Resposta inadequada para o nível de urgência (muito lenta para crítico ou alarmista para baixo)
- 0.3: Parcialmente adequada mas tom/velocidade incorretos
- 0.5: Adequada mas falta precisão no tom de urgência
- 0.8: Bem adequada ao nível de urgência com pequenos ajustes
- 1.0: Perfeitamente calibrada para a situação de emergência

Responda EXATAMENTE no formato:
Score: <valor entre 0.0 e 1.0>
Reasoning: <explicação sobre adequação ao nível de urgência e contexto>
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de adequação à situação de crise.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )
