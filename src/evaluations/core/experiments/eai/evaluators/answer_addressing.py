# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class AnswerAddressingEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do modelo aborda diretamente o objetivo da pergunta
    do usuário e oferece uma resposta útil, clara e prática.
    """

    name = "answer_addressing"

# - 1.0 (excelente): A resposta aborda claramente o ponto principal da consulta e fornece uma resposta útil e razoavelmente completa. Isso inclui soluções relevantes, orientações práticas ou próximos passos claros, mesmo que a solicitação de ajuda não esteja explicitamente formulada. Pequenas omissões são aceitáveis se a necessidade do usuário for atendida de forma satisfatória.
# - 0.5 (bom): A resposta aborda parcialmente a questão, mas falta clareza, profundidade ou deixa lacunas relevantes para a necessidade do usuário.
# - 0.0 (ruim): A resposta ignora ou evita o objetivo central da pergunta (explícito ou implícito), responde de forma vaga ou incorreta, não oferece solução ou orientação quando o problema exige, ou omite informações-chave que impeçam o usuário de agir ou sentir-se atendido.

    ANSWER_ADDRESSING_PROMPT = """
Nesta tarefa, você irá avaliar se a resposta do modelo atende de forma direta e suficiente à pergunta do usuário ou à necessidade implícita presente na consulta. Frequentemente, uma pergunta (especialmente quando formulada como uma reclamação ou dúvida sobre um problema — ex: "é normal o X não funcionar?") carrega um pedido implícito por solução ou próximo passo. Uma resposta eficaz deve contemplar essa necessidade implícita.

Você deverá atribuir uma das seguintes pontuações:
- 1.0 (respondida): A resposta do modelo aborda claramente o ponto principal da query e fornece uma resposta útil e razoavelmente completa. Isso inclui soluções relevantes, orientações práticas ou próximos passos claros, mesmo que a solicitação de ajuda não esteja explicitamente formulada. Pequenas omissões são aceitáveis se a necessidade do usuário for atendida de forma satisfatória.
- 0.0 (não respondida): A resposta ignora ou evita o objetivo central da pergunta (explícito ou implícito), responde de forma vaga ou incorreta, não oferece solução ou orientação quando o problema exige, ou omite informações-chave que impeçam o usuário de agir ou sentir-se atendido.

Sua resposta deve conter **exatamente duas linhas**, com o seguinte formato:
Score: <um valor float sendo 0.0 ou 1.0>
Reasoning: <uma explicação curta e objetiva justificando sua nota>

Para o `Reasoning`, considere:
1. Qual é o objetivo principal ou intenção da pergunta? Há um pedido implícito por ajuda ou solução?
2. A resposta atendeu de forma clara e suficiente esses pontos (explícitos ou implícitos)?
3. Se a nota for 0.0, explique o que faltou, o que estava inadequado ou por que a resposta não permitiu que o usuário agisse ou se sentisse atendido.

Pergunta: {task[prompt]}
Resposta do Modelo: {agent_response[message]}
"""

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        return await self._get_llm_judgement(
            prompt_template=self.ANSWER_ADDRESSING_PROMPT,
            task=task,
            agent_response=agent_response,
        )
