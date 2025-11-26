# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class AnswerCompletenessEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente cobre os conceitos principais da resposta ideal.
    """

    name = "answer_completeness"

    # - 1.0 (excelente): A resposta cobre todos ou quase todos os conceitos importantes da resposta ideal. Detalhes pequenos ausentes são aceitáveis se os pontos principais estiverem claros.
    # - 0.5 (bom): A resposta captura parcialmente os pontos centrais, mas perde informações importantes que comprometem o entendimento completo.
    # - 0.0 (ruim): A resposta ignora ou omite a maior parte das ideias principais, ou diverge muito em significado.

    PROMPT_TEMPLATE = """
Nesta tarefa, você atuará como um avaliador objetivo para verificar se a resposta de um assistente cumpre uma lista de requisitos técnicos e informativos obrigatórios.

Você deve verificar a lista de "Critérios de Avaliação". Cada critério possui uma descrição e um peso (Alto ou Baixo).

Diretrizes de Avaliação:
1. Analise cada item listado nos "Critérios de Avaliação".
2. Verifique se a "Resposta do Modelo" satisfaz a condição descrita no critério.
3. Critérios com Peso **Alto** são muito importantes. A ausência da informação ou ação descrita em pelo menos 75% deles resulta em falha.
4. Critérios com Peso **Baixo** são complementares. Sua ausência não deve penalizar a nota total, desde que os critérios de peso Alto estejam presentes.

Atribua uma das seguintes pontuações:
- 1.0 (Aprovado): A resposta cumpre pelo menos 75% dos critérios de peso 'Alto'.
- 0.0 (Reprovado): A resposta falha em cumprir um ou mais critérios de peso 'Alto', ou fornece informações incorretas que contradizem os critérios.

Sua resposta deve conter **exatamente duas linhas**, com o seguinte formato:
Score: <um valor float sendo 0.0 ou 1.0>
Reasoning: <explicação curta citando quais critérios foram atendidos e quais falharam>

Para o `Reasoning`:
- Seja direto. Cite o número do critério que causou a reprovação, se houver (ex: "Falhou no Critério 2").
- Se aprovado, confirme o cumprimento dos requisitos principais.

Pergunta: {task[prompt]}
Critérios de Avaliação: {task[golden_answer_criteria]}
Resposta do Modelo: {agent_response[message]}
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )
