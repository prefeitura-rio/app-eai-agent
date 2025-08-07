# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnEvaluationInput,
    BaseMultipleTurnEvaluator,
)


class EquipmentsCategoriesEvaluator(BaseMultipleTurnEvaluator):
    """
    Verifica se os valores do golden_equipment_type estão presentes no argumento categories da ferramenta equipments_by_address.
    """

    name = "equipments_categories"

    PROMPT_TEMPLATE = """
Você é um especialista na avaliação de sistemas automatizados de chatbot. Sua tarefa é analisar o raciocínio do agente e verificar se as categorias corretas foram usadas na ferramenta equipments_by_address.

**Categorias Usadas pelo Agente:**
{agent_response[transcript]}

**Categorias Esperadas (golden_equipment_type):**
{task[golden_equipment_type]}

**Critérios de Avaliação:**
Verifique se as categorias esperadas foram usadas corretamente no argumento "categories" da ferramenta "equipments_by_address".

A nota é binária, apenas 0 ou 1:
- 1 se todas as categorias esperadas foram usadas corretamente
- 0 se alguma categoria esperada não foi usada ou se foi usada incorretamente

**Exemplos:**
- Se golden_equipment_type é "CF, CMS, CSE" e o agente usou essas categorias, nota é 1
- Se golden_equipment_type é "UPA, CER" e o agente usou apenas "UPA", nota é 0
- Se golden_equipment_type é "CF, CMS" e o agente usou "CF, CMS, CSE", nota é 1 (categorias extras são aceitáveis)
- Se golden_equipment_type está vazio, nota é 1 (não há categorias para verificar)

**Formato da Resposta (exatamente 2 linhas, sem texto extra):**
Score: <0 ou 1>
Reasoning: <uma explicação curta e objetiva para a sua nota>
"""

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de categorias corretas usando o cliente juiz.
        """
        from copy import deepcopy
        from src.evaluations.core.eval import MultiTurnEvaluationInput

        # Cria uma cópia profunda do agent_response para não afetar o original
        agent_response_copy = deepcopy(agent_response)

        # Filtra apenas os traces relevantes para categorias
        filtered_transcript = self._filter_categories_traces(
            agent_response_copy.transcript
        )

        # Cria um novo agent_response apenas com os traces filtrados
        clean_agent_response = MultiTurnEvaluationInput(
            conversation_history=agent_response_copy.conversation_history,
            transcript=filtered_transcript,
        )

        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=clean_agent_response,
        )

    def _filter_categories_traces(self, transcript):
        """
        Filtra apenas os turnos que contêm equipments_by_address.
        """
        filtered_transcript = []

        for turn in transcript:
            # Verifica se o turn tem traces com equipments_by_address
            has_equipments_tool = False
            relevant_traces = []

            if turn.agent_reasoning_trace:
                for trace in turn.agent_reasoning_trace:
                    if (
                        trace.message_type == "tool_call_message"
                        and isinstance(trace.content, dict)
                        and trace.content.get("name") == "equipments_by_address"
                    ):
                        has_equipments_tool = True
                        relevant_traces.append(trace)

            # Só inclui o turn se tem a ferramenta equipments_by_address
            if has_equipments_tool:
                # Cria uma cópia do turn apenas com os traces relevantes
                filtered_turn = type(turn)(
                    turn=turn.turn,
                    user_message="nao relevante",
                    agent_message="nao relevante",
                    agent_reasoning_trace=relevant_traces,
                )
                filtered_transcript.append(filtered_turn)

        return filtered_transcript
