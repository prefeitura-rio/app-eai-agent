# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnEvaluationInput,
    BaseMultipleTurnEvaluator,
)


class EquipmentsCorrectnessEvaluator(BaseMultipleTurnEvaluator):
    """
    Avalia se o agente identificou corretamente o equipamento que deve atender o cidadão.
    """

    name = "equipments_correctness"

    PROMPT_TEMPLATE = """
Você é um especialista na avaliação de sistemas automatizados de chatbot. Sua tarefa é analisar uma conversa completa entre um chatbot e um usuário e verificar se o equipamento correto foi identificado.

**Historico da Conversa:**
{agent_response[conversation_history]}

**Equipamento Correto de Referência:**
{task[golden_equipment]}

**Informações Extras (se aplicável):**
{task[extra_info]}

**Critérios de Avaliação:**
A nota de equipamento_correto é binária, apenas 0 ou 1:
- 1 se o equipamento informado estiver correto (mesmo que não perfeitamente formatado).
- 0 se estiver incorreto, vago ou ausente.

Em casos em que não há equipamento_correto, ou seja, equipamento_correto="", a resposta correta é não enviar o cidadão a nenhum equipamento, e sim fazer de acordo com o informado na extra_info.
Nesse caso, a nota é 1 somente se o agente seguir corretamente as instruções contidas em `extra_info` e 0 caso contrário.

**Exemplos:**
- Se o equipamento_correto é "CAPS III Franco Basaglia Endereço: Avenida Venceslau Brás, 65, fundos - Botafogo." e o chatbot retorna "SMS CMS JOAO BARROS BARRETO - AP 21 - Endereço: RUA TENREIRO ARANHA S/N", sua nota é 0.
- Se o equipamento_correto é "Super Centro Carioca de Vacinação (SCCV) Rua General Severiano, 91." e o chatbot fala ao cidadão para ir ao "Super Centro Carioca de Vacinação", sua nota é 1.
- Se o equipamento_correto é "" e o extra_info é "Ligue 192: SAMU. Serviço de atendimento de urgência em ambulância, que funciona 24 horas.", e o chatbot orienta a chamar o SAMU, sua nota é 1.

**Formato da Resposta (exatamente 2 linhas, sem texto extra):**
Score: <0 ou 1>
Reasoning: <uma explicação curta e objetiva para a sua nota>
"""

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de equipamento correto usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )
