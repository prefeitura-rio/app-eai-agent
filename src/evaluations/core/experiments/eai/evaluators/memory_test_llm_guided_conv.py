# -*- coding: utf-8 -*-
from typing import List
from src.evaluations.core.eval import (
    BaseConversationEvaluator,
    EvaluationTask,
)


class MemoryTestLLMGuidedConversation(BaseConversationEvaluator):
    """
    Avaliador que conduz uma conversa de 3-4 turnos para testar a capacidade
    do agente de reutilizar informações de tool_calls anteriores.
    
    O LLM-Juiz atua como um cidadão comum que:
    1. Faz uma pergunta inicial que força o uso de google_search
    2. Interage naturalmente com o agente por 1-2 turnos
    3. Faz uma pergunta de seguimento que depende da resposta inicial
    """

    name = "memory_test_llm_guided_conversation"
    max_turns: int = 6  # Permite até 6 turnos para incluir stop_signal separado

    PROMPT_TEMPLATE = """
### SUA MISSÃO ###
Você é um ator interpretando um **cidadão comum** em uma conversa com um agente de atendimento virtual da Prefeitura do Rio. Sua atuação será usada para avaliar a memória do agente. Manter-se no personagem é sua prioridade máxima.

### CONTEXTO DA SUA SITUAÇÃO ###
Tema: {task[tema]}

### HISTÓRICO DA CONVERSA ###
{history}

### SUAS INSTRUÇÕES PARA ESTE TURNO ###
{turn_instructions}

---

### REGRAS DE ATUAÇÃO (OBRIGATÓRIAS) ###

1. **SEJA NATURAL E DIRETO:**
   * Fale como um cidadão comum falaria ao buscar informação da prefeitura
   * Use linguagem informal e objetiva
   * Não seja excessivamente educado ou formal
   * Vá direto ao ponto

2. **NUNCA SAIA DO PERSONAGEM:**
   * Você é o cidadão, **NÃO** um assistente, avaliador ou robô
   * **NÃO USE** frases como "Posso ajudar?", "Estou aqui para ajudar"
   * Você é quem está *buscando* ajuda

3. **SIGA EXATAMENTE AS INSTRUÇÕES DO TURNO:**
   * Leia com atenção o que você deve fazer neste turno
   * Não antecipe perguntas futuras
   * Seja natural e conversacional

4. **INTERAJA NATURALMENTE:**
   * Responda às perguntas do agente
   * Agradeça informações úteis
   * Peça esclarecimentos se necessário

**Sua Próxima Fala ou Sinal de Parada:**
"""

    def get_judge_prompt(self, task: EvaluationTask, history: List[str]) -> str:
        """
        Gera o prompt para o juiz com base no turno atual da conversa.
        """
        task_dict = task.model_dump(exclude_none=True)
        history_str = "\n".join(history) if history else "A conversa ainda não começou."
        
        # Conta quantos turnos do usuário já foram feitos
        user_turns = len([h for h in history if "User:" in h])
        
        # Flag para identificar se já fizemos a secondary_user_message
        secondary_question_sent = any(
            task_dict.get('secondary_user_message', '') in h 
            for h in history if "User:" in h
        )
        
        if user_turns == 0:
            # PRIMEIRO TURNO: Pergunta inicial
            turn_instructions = f"""
**TURNO 1 - PERGUNTA INICIAL:**
Faça a seguinte pergunta ao agente de forma natural:

"{task_dict.get('initial_user_message', '')}"

Seja direto e use linguagem informal, como um cidadão comum faria.
"""
        elif user_turns >= 1 and user_turns < 3:
            # TURNOS INTERMEDIÁRIOS: Interação natural
            turn_instructions = f"""
**TURNO {user_turns + 1} - INTERAÇÃO NATURAL:**
O agente acabou de te responder. Agora você deve manter a conversa natural:

* Se o agente te deu uma informação importante, mostre interesse fazendo uma pergunta de acompanhamento simples e relevante (ex: "e isso funciona todos os dias?", "qualquer pessoa pode usar?", "tem algum documento necessário?")
* Se o agente te fez uma pergunta, responda de forma natural e objetiva
* Se o agente pediu mais informações (como endereço), forneça de forma completa

**EXEMPLOS DE BOA INTERAÇÃO:**
- Agente menciona um telefone → Você: "esse telefone funciona 24h?"
- Agente menciona um local → Você: "precisa agendar ou é por ordem de chegada?"
- Agente menciona um serviço online → Você: "tem um link que você pode me passar?"

**IMPORTANTE:** 
- Seja curioso e engajado, mas mantenha mensagens CURTAS (máximo 1-2 linhas)
- NÃO agradeça e encerre ainda ("valeu, era só isso")
- NÃO faça a pergunta final ainda
"""
        elif not secondary_question_sent:
            # TURNO DA SEGUNDA PERGUNTA: Fazer a secondary_user_message
            turn_instructions = f"""
**PERGUNTA DE SEGUIMENTO:**
Agora é hora de fazer a segunda pergunta. Faça de forma natural, como se você tivesse acabado de lembrar:

"{task_dict.get('secondary_user_message', '')}"

**IMPORTANTE:** Faça APENAS a pergunta. NÃO envie o sinal de parada ainda. O agente precisa responder primeiro.
"""
        else:
            # TURNO FINAL: Stop signal após a resposta à segunda pergunta
            turn_instructions = f"""
**ENCERRAMENTO:**
O agente respondeu sua segunda pergunta. Agora envie APENAS o sinal de parada para finalizar a avaliação:

`{self.stop_signal}`

Não adicione nada além do sinal.
"""
        
        return self.PROMPT_TEMPLATE.format(
            task=task_dict,
            history=history_str,
            turn_instructions=turn_instructions,
            stop_signal=self.stop_signal,
        )
