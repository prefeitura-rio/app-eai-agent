# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class ClarityEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente é clara e acessível para cidadãos comuns.
    """

    name = "clarity"

    # - 1.0 (excelente): A resposta é clara, acessível e traz orientações práticas e úteis
    # - 0.5 (boa): A resposta é parcialmente clara, mas tem pontos que dificultam o entendimento ou limitam a utilidade
    # - 0.0 (ruim): A resposta é confusa, usa linguagem complicada ou não traz orientação prática

    PROMPT_TEMPLATE = """
Nesta tarefa, você irá avaliar se uma resposta em português é clara e compreensível para cidadãos comuns do Rio de Janeiro que buscam serviços públicos ou informações.
Uma resposta clara deve ser fácil de entender por pessoas com diferentes níveis de escolaridade, evitando linguagem burocrática, sem perder a precisão ou a utilidade.

Critérios de avaliação da clareza para o cidadão:

1. **Linguagem Simples**:
   - Evita termos burocráticos ou jurídicos difíceis
   - Usa português do dia a dia, acessível a quem tem escolaridade básica
   - Explica termos técnicos quando for necessário usá-los
   - Evita siglas e abreviações sem explicação

2. **Direta e Prática**:
   - Responde à dúvida do cidadão sem rodeios
   - Oferece informações acionáveis (onde ir, o que levar, quando fazer)
   - Foca no que a pessoa precisa saber para resolver seu problema
   - Inclui endereços, telefones ou sites quando for relevante

3. **Bem Organizada**:
   - A informação segue uma ordem lógica (do mais importante primeiro)
   - Usa listas ou etapas simples ao explicar procedimentos
   - Divide processos complexos em partes fáceis de entender
   - Separa claramente tópicos ou exigências diferentes

4. **Completa mas Concisa**:
   - Traz todas as informações essenciais, sem exagerar nos detalhes
   - Tem um tamanho apropriado para leitura no WhatsApp ou celular
   - Evita repetições
   - Não pressupõe que o cidadão já entenda processos do governo

Pontuações possíveis:
- 1.0 (clara): A resposta é clara, acessível e traz orientações práticas e úteis
- 0.0 (pouco clara): A resposta é confusa, usa linguagem complicada ou não traz orientação prática

Sua resposta deve conter **exatamente duas linhas**, com o seguinte formato:
Score: <um valor float sendo 0.0 ou 1.0>
Reasoning: <uma explicação curta e objetiva justificando sua nota>

Analise a resposta com o olhar de um cidadão comum que está pedindo ajuda com serviços públicos. Considere alguém com pouca escolaridade formal, que não entende a linguagem do governo, e precisa de orientação direta para resolver seu problema.

Para o `Reasoning`, considere:
- A resposta usa linguagem burocrática ou complexa sem explicação?
- Ela traz passos claros e acionáveis?
- Está bem organizada e fácil de seguir?
- O nível de detalhe e o tamanho são adequados?
- Existe algo que possa confundir ou frustrar o cidadão?

# Exemplos de linguagem pouco clara vs. linguagem clara:

pouco clara: "Dirija-se à repartição competente munido da documentação pertinente para protocolar sua solicitação"
clara: "Vá à delegacia (Rua X, número Y) com RG, CPF e comprovante de residência"

pouco clara: "A emissão da certidão está condicionada à quitação dos débitos tributários"
clara: "Para pegar a certidão, você precisa primeiro pagar todos os impostos em atraso"

pouco clara: "O requerente deve observar os prazos regimentais"
clara: "Você tem 30 dias para entregar os documentos"

pouco clara: "Proceda ao agendamento através dos canais oficiais"
clara: "Marque seu atendimento pelo site www.exemplo.com"

Pergunta: {task[prompt]}
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
