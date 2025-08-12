# -*- coding: utf-8 -*-
from typing import List
from src.evaluations.core.eval import (
    BaseConversationEvaluator,
    EvaluationTask,
)


class BatmanLLMGuidedConversation(BaseConversationEvaluator):
    """
    Implementação específica para o experimento do Batman que conduz uma conversa
    onde um LLM-Juiz atua como o usuário, seguindo um roteiro definido no
    campo 'judge_context' da tarefa.
    """

    name = "batman_llm_guided_conversation"

    PROMPT_TEMPLATE = """
Você é um Juiz de IA conduzindo uma avaliação conversacional para o Batman. Sua tarefa é seguir um roteiro secreto para testar o agente.
Nesta conversa, você é o **Usuário** e deve assumir a persona do personagem indicado no roteiro (um vilão, um aliado, etc.).
Não inicie suas respostas com seu nome! Apenas incorpore a persona.

**Seu Roteiro (Contexto Secreto):**
{task[judge_context]}

**Histórico da Conversa até Agora:**
{history}

**Sua Próxima Ação:**

Com base no seu roteiro e no histórico, decida sua próxima ação:

1.  **Continuar a Conversa:** Se o roteiro ainda não foi concluído, formule a **sua próxima fala** para o agente, mantendo a persona.
2.  **Encerrar a Conversa:** Se o roteiro foi concluído, responda **apenas e exatamente** com a string de parada: `{stop_signal}`

**Sua Próxima Fala ou Sinal de Parada:**
"""

    def get_judge_prompt(self, task: EvaluationTask, history: List[str]) -> str:
        """
        Implementa a lógica para formatar o prompt que guia o juiz
        com base no roteiro do Batman.
        """
        history_str = "\n".join(history)
        task_dict = task.model_dump(exclude_none=True)

        return self.PROMPT_TEMPLATE.format(
            task=task_dict,
            history=history_str,
            stop_signal=self.stop_signal,
        )
