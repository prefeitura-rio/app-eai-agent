# -*- coding: utf-8 -*-
import time
from src.evaluations.core.eval import (
    BaseConversationEvaluator,
    EvaluationTask,
    AgentConversationManager,
    ConversationOutput,
    ConversationTurn,
    AgentResponse,
)


class LLMGuidedConversation(BaseConversationEvaluator):
    """
    Conduz uma conversa onde um LLM-Juiz atua como o usuário,
    seguindo um roteiro dinamicamente.
    """

    name = "llm_guided_conversation"

    CONVERSATIONAL_JUDGE_PROMPT = """
Você é um Juiz de IA conduzindo uma avaliação conversacional. Sua tarefa é seguir um roteiro.
Nesta conversa voce é o Usuario e deve assumir a persona especificada no roteiro!!
Nao inicie a suas respostas com seu nome!! Nem mencione ele em outras menssagens apenas na primeira!!

**Seu Roteiro (Contexto Secreto):**
{task[judge_context]}

**Histórico da Conversa até Agora:**
{agent_response[conversation_history]}

**Sua Próxima Ação:**

Com base no seu roteiro e no histórico, decida sua próxima ação:

1.  **Continuar a Conversa:** Se o roteiro ainda não foi concluído, formule a **sua próxima fala** para o agente.
2.  **Encerrar a Conversa:** Responda **apenas e exatamente** com a string de parada: `{stop_signal}`

**Sua Próxima Fala ou Sinal de Parada:**
"""

    async def evaluate(
        self, task: EvaluationTask, agent_manager: AgentConversationManager
    ) -> ConversationOutput:
        """
        Executa a lógica de condução da conversa.
        """
        start_time = time.monotonic()
        JUDGE_STOP_SIGNAL = "`EVALUATION_CONCLUDED`"

        transcript, history = [], []
        current_message = task.prompt or ""
        last_response = AgentResponse(output=None, messages=[])

        for turn in range(15):  # Limite de turnos para evitar loops infinitos
            agent_res = await agent_manager.send_message(current_message)
            last_response = agent_res
            transcript.append(
                ConversationTurn(
                    turn=turn + 1,
                    judge_message=current_message,
                    agent_response=agent_res.output,
                    reasoning_trace=agent_res.messages,
                )
            )
            history.append(
                f"Turno {turn+1} - User: {current_message}\nTurno {turn+1} - Agente: {agent_res.output}"
            )

            prompt_for_judge = self.CONVERSATIONAL_JUDGE_PROMPT.format(
                task=task.model_dump(),
                agent_response={"conversation_history": "\n".join(history)},
                stop_signal=JUDGE_STOP_SIGNAL,
            )
            judge_res = await self.judge_client.execute(prompt_for_judge)

            if JUDGE_STOP_SIGNAL in judge_res:
                history.append(f"Turno {turn+2} - User: {judge_res}")
                transcript.append(
                    ConversationTurn(
                        turn=turn + 2,
                        judge_message=judge_res,
                        agent_response=None,
                        reasoning_trace=None,
                    )
                )
                break
            current_message = judge_res

        end_time = time.monotonic()
        duration = end_time - start_time

        return ConversationOutput(
            transcript=transcript,
            final_agent_response=last_response,
            history_for_judge=history,
            duration_seconds=duration,
        )
