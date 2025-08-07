# -*- coding: utf-8 -*-
from typing import List
from src.evaluations.core.eval import (
    BaseConversationEvaluator,
    EvaluationTask,
)


class GoldenEquipmentLLMGuidedConversation(BaseConversationEvaluator):
    """
    Implementação específica para o experimento do Batman que conduz uma conversa
    onde um LLM-Juiz atua como o usuário, seguindo um roteiro definido no
    campo 'judge_context' da tarefa.
    """
    name = "golden_equipment_llm_guided_conversation"

    GOLDEN_EQUIPMENT_LLM_GUIDED_PROMPT = """
Você é um Juiz de IA conduzindo uma avaliação conversacional para testar o agente.

Sua função é **simular o comportamento de um cidadão** com base no roteiro abaixo. Esse roteiro representa o problema que o cidadão está tentando resolver.

**Roteiro Secreto (Contexto do Cidadão):**
{task[context]}

**Histórico da Conversa até Agora:**
{history}

**Sua Próxima Ação:**

1. Continue a conversa como o cidadão, mantendo o estilo e objetivo do roteiro.
2. Se o objetivo do cidadão já foi atingido ou a conversa não precisa continuar, responda com: `{stop_signal}`

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
