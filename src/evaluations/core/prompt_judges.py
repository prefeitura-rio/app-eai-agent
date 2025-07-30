# -*- coding: utf-8 -*-

"""
Este arquivo centraliza todos os templates de prompt usados pelos Juízes LLM.
"""

# 1. PROMPT PARA CONDUZIR A CONVERSA
CONVERSATIONAL_JUDGE_PROMPT = """
Você é um Juiz de IA conduzindo uma avaliação conversacional. Sua tarefa é seguir um roteiro.

**Seu Roteiro (Contexto Secreto):**
{judge_context}

**Histórico da Conversa até Agora:**
{conversation_history}

**Sua Próxima Ação:**
Com base no seu roteiro e no histórico, decida sua próxima ação:

1.  **Continuar a Conversa:** Se o roteiro ainda não foi concluído, formule a **sua próxima fala** para o agente.
2.  **Encerrar a Conversa:** Se o roteiro instrui a terminar, responda **apenas e exatamente** com a string de parada: `{stop_signal}`

**Sua Próxima Fala ou Sinal de Parada:**
"""

# 2. PROMPTS PARA O JULGAMENTO FINAL (APÓS A CONVERSA)

FINAL_CONVERSATIONAL_JUDGEMENT_PROMPT = """
Você é um Juiz de IA. Sua tarefa é fornecer um julgamento final sobre o **RACIOCÍNIO** de um agente com base em uma conversa.

**Objetivo da Avaliação (Golden Summary):**
O agente deve ser capaz de conectar o roubo na Ace Chemicals com a nova toxina, sugerindo o envolvimento de vilões conhecidos.

**Transcrição Completa da Conversa:**
{transcript}

**Sua Tarefa:**
Analise a transcrição e compare o desempenho do agente com o objetivo.
Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float de 0.0 a 1.0 para a capacidade de RACIOCÍNIO>
Reasoning: <uma explicação curta e objetiva para a sua nota de RACIOCÍNIO>
"""

FINAL_MEMORY_JUDGEMENT_PROMPT = """
Você é um Juiz de IA. Sua tarefa é fornecer um julgamento final sobre a **MEMÓRIA** de um agente com base em uma conversa.

**Objetivo da Avaliação (Golden Summary):**
O agente deve ser capaz de lembrar o nome 'Alfred' após várias perguntas de distração


**Transcrição Completa da Conversa:**
{transcript}

**Sua Tarefa:**
Analise a transcrição e compare o desempenho do agente com o objetivo.
Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float de 0.0 a 1.0 para a capacidade de MEMÓRIA>
Reasoning: <uma explicação curta e objetiva para a sua nota de MEMÓRIA>
"""

# 3. PROMPTS PARA AVALIAÇÕES DE TURNO ÚNICO

SEMANTIC_CORRECTNESS_PROMPT = """
Avalie similaridade semântica da resposta gerada por uma IA em relacao a Resposta ideal.
**Resposta Gerada pela IA:**
{output}
**Resposta Ideal:**
{task[golden_response]}

**Sua Tarefa:**
Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float de 0.0 a 1.0>
Reasoning: <uma explicação curta e objetiva para a sua nota>
"""

PERSONA_ADHERENCE_PROMPT = """
Avalie se a resposta da IA adere à persona definida: **{task[persona]}**.
**Resposta Gerada pela IA:**
{output}
**Sua Tarefa:**
Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float de 0.0 a 1.0>
Reasoning: <uma explicação curta sobre como a resposta se alinha (ou não) à persona>
"""
