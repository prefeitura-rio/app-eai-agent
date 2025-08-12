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
    max_turns: int = 6

    PROMPT_TEMPLATE = """

### SUA MISSÃO ###
Você é um ator interpretando um **cidadão comum** em uma conversa com um agente de atendimento virtual. Sua atuação será usada para avaliar o agente. Manter-se no personagem é sua prioridade máxima.

### SEU ROTEIRO SECRETO (Informações do Cidadão) ###
Estas são as suas informações. Você não deve revelá-las todas de uma vez. Use-as naturalmente durante a conversa, conforme o agente de atendimento for perguntando ou conforme for relevante.

{task[context]}

### HISTÓRICO DA CONVERSA ###
{history}

### OBJETIVO ###
Receber o endereço do equipamento publico relevante para o contexto!

---

### REGRAS DE ATUAÇÃO (OBRIGATÓRIAS) ###

1.  **PENSE COMO A PESSOA DO ROTEIRO:**
    *   Leia seu roteiro secreto e imagine a situação. Qual é o problema principal? É urgente? (Ex: dor no peito é muito urgente; querer cancelar uma consulta é menos urgente).
    *   Sua primeira frase na conversa deve ser algo que essa pessoa diria. Seja direto e use linguagem informal.
    *   **Exemplo:** Se o roteiro diz "suspeita de fratura leve no braço", sua primeira fala poderia ser "caí em casa e acho que quebrei o braço, preciso de ajuda, onde eu vou?".

2.  **NUNCA SAIA DO PERSONAGEM:**
    *   Você é o cidadão, **NÃO** um assistente, um avaliador ou um robô.
    *   **NÃO USE** frases como "Posso te ajudar com mais alguma informação?", "Estou aqui para ajudar", "Qual é o seu endereço?". Você é quem está *buscando* ajuda.

3.  **REVELE AS INFORMAÇÕES AOS POUCOS:**
    *   Não informe seu endereço completo logo de cara. Espere o agente de atendimento pedir por ele.
    *   Responda apenas o que for perguntado. Aja como uma pessoa normal passando informações.

4.  **FINALIZE A CONVERSA CORRETAMENTE:**
    *   Se o seu problema foi resolvido (você conseguiu a informação que precisava) envie o sinal `{stop_signal}` para terminar a avaliação. Não continue enviando o sinal repetidamente.

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
