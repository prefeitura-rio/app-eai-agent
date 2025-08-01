# -*- coding: utf-8 -*-
from src.evaluations.core.llm_clients import AgentConversationManager, BaseJudgeClient
from src.evaluations.core.schemas import (
    EvaluationTask,
    AgentResponse,
    ConversationTurn,
)


class ConversationHandler:
    """
    Gerencia a condução de uma única conversa entre um juiz LLM e o agente
    a ser avaliado.
    """

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

    def __init__(
        self, conv_manager: AgentConversationManager, judge_client: BaseJudgeClient
    ):
        self.conv_manager = conv_manager
        self.judge_client = judge_client

    async def conduct(self, task: EvaluationTask):
        """
        Conduz uma conversa multi-turno, guiada por um juiz, e retorna a
        transcrição completa, a resposta final do agente e o histórico
        formatado para avaliações.
        """
        JUDGE_STOP_SIGNAL = "`EVALUATION_CONCLUDED`"

        transcript, history = [], []
        current_message = task.prompt or ""
        last_response = AgentResponse(output=None, messages=[])

        for turn in range(15):  # Limite de turnos para evitar loops infinitos
            agent_res = await self.conv_manager.send_message(current_message)
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

        return transcript, last_response, history
