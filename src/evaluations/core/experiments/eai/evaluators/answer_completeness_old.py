# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class AnswerCompletenessOldEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente cobre os conceitos principais da resposta ideal.
    """

    name = "answer_completeness_old"

    # - 1.0 (excelente): A resposta cobre todos ou quase todos os conceitos importantes da resposta ideal. Detalhes pequenos ausentes são aceitáveis se os pontos principais estiverem claros.
    # - 0.5 (bom): A resposta captura parcialmente os pontos centrais, mas perde informações importantes que comprometem o entendimento completo.
    # - 0.0 (ruim): A resposta ignora ou omite a maior parte das ideias principais, ou diverge muito em significado.

    PROMPT_TEMPLATE = """
Nesta tarefa, você irá avaliar o quanto a resposta de um modelo cobre os tópicos centrais e os conceitos essenciais presentes em uma resposta ideal.

A avaliação deve ser feita com base na cobertura do conteúdo, não na similaridade de estilo ou na forma de redigir.
Concentre-se em verificar se a resposta do modelo inclui os *pontos-chave* mais importantes. Omissões menores ou diferenças de linguagem não devem penalizar a resposta se a substância principal estiver presente.

Atribua uma das seguintes pontuações:
- 1.0 (equivalente): A resposta do modelo cobre todos ou a maioria dos conceitos da resposta ideal. Detalhes pequenos ausentes são aceitáveis se os pontos principais estiverem claros.
- 0.0 (diferente): A resposta do modelo ignora ou omite a maior parte das ideias principais ou diverge muito em significado.

Sua resposta deve conter **exatamente duas linhas**, com o seguinte formato:
Score: <um valor float sendo 0.0 ou 1.0>
Reasoning: <uma explicação curta e objetiva justificando sua nota>

Para o `Reasoning`, considere:
- Quais são os conceitos ou tópicos essenciais presentes na resposta ideal?
- Algum conceito importante foi omitido? Qual? O que ele representa? Como sua ausência afeta o entendimento?

Pergunta: {task[prompt]}
Resposta do Modelo: {agent_response[message]}
Resposta Ideal: {task[golden_answer]}
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )