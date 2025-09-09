# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class DefesaCivilSemanticCorrectnessEvaluator(BaseOneTurnEvaluator):
    """
    Avalia a correção semântica de uma resposta de emergência da Defesa Civil 
    comparada à resposta esperada.
    """

    name = "defesa_civil_semantic_correctness"

    PROMPT_TEMPLATE = """
Você é um especialista em emergências da Defesa Civil do Rio de Janeiro.
Avalie se a resposta gerada pela IA está semanticamente correta em relação à resposta esperada.

**Pergunta Original:**
{task[prompt]}

**Resposta Gerada pela IA:**
{agent_response[message]}

**Resposta Esperada:**
{task[metadata][resposta_esperada]}

**Critérios de Avaliação:**
- Informações técnicas corretas (números de telefone, procedimentos)
- Instruções de segurança apropriadas
- Clareza e urgência adequada ao contexto
- Completude da resposta

**Escala de Pontuação:**
- 0.0: Informações incorretas ou perigosas
- 0.3: Informações corretas mas incompletas  
- 0.5: Informações corretas mas pouco claras
- 0.8: Informações corretas e claras, mas falta algum detalhe
- 1.0: Resposta perfeita - correta, completa e clara

Responda EXATAMENTE no formato:
Score: <valor entre 0.0 e 1.0>
Reasoning: <explicação objetiva da nota>
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de correção semântica para respostas de emergência.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )