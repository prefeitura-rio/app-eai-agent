# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnEvaluationInput,
    BaseMultipleTurnEvaluator,
)


class EquipmentsSpeedEvaluator(BaseMultipleTurnEvaluator):
    """
    Avalia em que turno o equipamento correto foi mencionado pela primeira vez.
    """

    name = "equipments_speed"

    PROMPT_TEMPLATE = """
Você é um especialista na avaliação de sistemas automatizados de chatbot. Sua tarefa é analisar uma conversa completa entre um chatbot e um usuário e determinar em que turno o equipamento correto foi mencionado pela primeira vez.

**Objetivo da Tarefa:**
{task[prompt]}

**Historico da Conversa:**
{agent_response[conversation_history]}

**Equipamento Correto de Referência:**
{task[golden_equipment]}

**Informações Extras (se aplicável):**
{task[extra_info]}

**Critérios de Avaliação:**
Indique em que turno o equipamento correto foi mencionado pela primeira vez.
O primeiro turno do agente é considerado o turno 1, o segundo turno é o turno 2, e assim por diante.
Caso o equipamento correto não seja mencionado, retorne 0.

Em casos em que não há `golden_equipment`, a nota é o primeiro turno em que o chatbot conseguiu cumprir corretamente o que está contido em `extra_info`.

**Exemplos:**
- Se o equipamento correto é "CMS João Barros Barreto" e o chatbot menciona no terceiro turno, retorne 3.
- Se o equipamento correto é "UPA Tijuca" e o chatbot menciona no segundo turno, retorne 2.
- Se o equipamento correto não é mencionado em nenhum turno, retorne 0.
- Se não há equipamento correto mas o extra_info é "Ligue 192: SAMU" e o chatbot orienta no primeiro turno, retorne 1.

**Formato da Resposta (exatamente 2 linhas, sem texto extra):**
Score: <número inteiro do turno ou 0>
Reasoning: <uma explicação curta e objetiva para a sua nota>
"""

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de rapidez da resposta usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )
