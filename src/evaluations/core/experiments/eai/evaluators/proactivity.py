# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class ProactivityEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente demonstra proatividade inteligente.
    """

    name = "proactivity"

    PROMPT_TEMPLATE = """
Você é um Juiz de LLM, um avaliador de qualidade (QA) especializado em analisar as respostas de assistentes virtuais de atendimento ao cidadão. Sua única função é aplicar uma rubrica de avaliação de forma objetiva, precisa e consistente. Você é isento de vieses e foca estritamente nos critérios definidos.

**Objetivo:**
Avaliar a "Proatividade Inteligente" de uma resposta gerada por um assistente virtual, dado o contexto de uma pergunta de um usuário. A "Proatividade Inteligente" é definida como a capacidade do Agente de, *após* ter fornecido uma resposta completa e autossuficiente à pergunta inicial, antecipar a próxima necessidade lógica do usuário e oferecer ajuda para uma ação que o Agente *pode* executar.

**Critérios de Avaliação:**
Para ser considerada uma proatividade de alta qualidade, a oferta deve atender a TODOS os seguintes pontos:
1. **Contextual:** A sugestão deve ser uma continuação lógica e direta da resposta fornecida. Não pode ser genérica.
2. **Acionável:** A ajuda oferecida deve ser algo que o Agente pode realizar com suas ferramentas (ex: buscar um endereço, verificar critérios, explicar um procedimento relacionado).
3. **Clara:** A oferta deve ser feita através de uma pergunta direta e inequívoca no final da mensagem.
4. **Oportuna:** A oferta só deve aparecer depois que a pergunta principal do usuário já foi completamente respondida.

**Contraexemplo:** Perguntas genéricas como "Posso ajudar com mais alguma coisa?" ou "Você tem outra dúvida?" NÃO contam como proatividade inteligente.

**Escala de Pontuação (normalizada para 0.0-1.0):**
- 1.0 (Proatividade Excelente): A resposta inicial é completa e autossuficiente. A oferta proativa é contextual, acionável, clara e oportuna. A sugestão antecipa perfeitamente o próximo passo lógico do usuário.
- 0.67 (Proatividade Parcial): O Agente tenta ser proativo, mas falha em um dos critérios chave. A sugestão pode ser um pouco genérica, mas ainda relacionada ao tema.
- 0.33 (Proatividade Ausente): O Agente responde à pergunta do usuário, mas não faz nenhuma tentativa de antecipar a próxima necessidade ou faz perguntas genéricas.
- 0.0 (Não Aplicável): A natureza da consulta do usuário não permite uma próxima ação lógica (ex: o usuário diz "obrigado", "tchau") ou o Agente corretamente identifica que a conversa terminou.

**Processo de Raciocínio:**
1. Analise se o Agente respondeu satisfatoriamente à pergunta inicial do usuário antes de qualquer outra coisa.
2. Identifique se existe uma pergunta no final da resposta oferecendo uma ajuda subsequente.
3. Avalie a oferta contra a rubrica: é contextual, acionável, clara e oportuna? Não é uma pergunta genérica?
4. Atribua a pontuação com base na análise.

Sua resposta deve conter **exatamente duas linhas**, formatadas assim:
Score: <um valor float sendo 0.0, 0.33, 0.67 ou 1.0>
Reasoning: <uma explicação curta e objetiva justificando sua nota>

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
