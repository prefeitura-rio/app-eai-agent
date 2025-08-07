# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnEvaluationInput,
    BaseMultipleTurnEvaluator,
)


class EquipmentsToolsEvaluator(BaseMultipleTurnEvaluator):
    """
    Verifica se as ferramentas necessárias foram chamadas na ordem correta.
    """

    name = "equipments_tools"

    PROMPT_TEMPLATE = """
Você é um especialista na avaliação de sistemas automatizados de chatbot. Sua tarefa é analisar as chamadas de ferramentas do agente e verificar se as ferramentas necessárias foram chamadas na ordem correta.

**Chamadas de Ferramentas do Agente:**
{agent_response[transcript]}

**Critérios de Avaliação:**
Verifique se as ferramentas necessárias foram chamadas na ordem correta:
1. equipments_instructions (deve ser chamada primeiro)
2. equipments_by_address (deve ser chamada segundo)

A nota é binária, apenas 0 ou 1:
- 1 se ambas as ferramentas foram chamadas na ordem correta
- 0 se alguma ferramenta não foi chamada ou se a ordem está incorreta

**Exemplos:**
- Se o agente chamou "equipments_instructions" e depois "equipments_by_address", nota é 1
- Se o agente chamou apenas "equipments_instructions", nota é 0
- Se o agente chamou "equipments_by_address" primeiro, nota é 0
- Se o agente não chamou nenhuma das ferramentas, nota é 0

**Formato da Resposta (exatamente 2 linhas, sem texto extra):**
Score: <0 ou 1>
Reasoning: <uma explicação curta e objetiva para a sua nota>
"""

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de ferramentas necessárias usando o cliente juiz.
        """
        from copy import deepcopy
        from src.evaluations.core.eval import MultiTurnEvaluationInput

        # Cria uma cópia profunda do agent_response para não afetar o original
        agent_response_copy = deepcopy(agent_response)

        # Filtra apenas os traces de tool calls
        filtered_transcript = self._filter_tool_calls(agent_response_copy.transcript)

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

    def _filter_tool_calls(self, transcript):
        """
        Filtra apenas os traces de tool_call_message.
        """
        filtered_transcript = []

        for turn in transcript:
            # Coleta apenas traces de tool_call_message
            tool_call_traces = []

            if turn.agent_reasoning_trace:
                for trace in turn.agent_reasoning_trace:
                    if trace.message_type == "tool_call_message":
                        tool_call_traces.append(trace)

            # Só inclui o turn se tem tool calls
            if tool_call_traces:
                # Cria uma cópia do turn apenas com os traces de tool calls
                filtered_turn = type(turn)(
                    turn=turn.turn,
                    user_message="nao relevante",
                    agent_message="nao relevante",
                    agent_reasoning_trace=tool_call_traces,
                )
                filtered_transcript.append(filtered_turn)

        return filtered_transcript
