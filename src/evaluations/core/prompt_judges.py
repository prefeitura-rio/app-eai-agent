# -*- coding: utf-8 -*-

"""
Este arquivo centraliza todos os templates de prompt usados pelos Juízes LLM
nas avaliações. Manter os prompts aqui facilita a manutenção, o versionamento
e a consistência entre os experimentos.
"""

# Template para avaliar a correção semântica de uma resposta
SEMANTIC_CORRECTNESS_PROMPT = """
Avalie a correção semântica da resposta gerada por uma IA em relação a uma resposta de referência.
Concentre-se no significado e na informação, ignorando pequenas diferenças de estilo ou formulação.

**Pergunta Original:**
{task[prompt]}

**Resposta de Referência (Golden):**
{task[golden_response]}

**Resposta Gerada pela IA:**
{output}

**Sua Tarefa:**
Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float de 0.0 a 1.0>
Reasoning: <uma explicação curta e objetiva para a sua nota>
"""

# Template para avaliar se a resposta segue uma persona específica
PERSONA_ADHERENCE_PROMPT = """
Avalie se a resposta da IA adere à persona definida.
A persona é: **{task[persona]}**.

**Resposta Gerada pela IA:**
{output}

**Sua Tarefa:**
Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float de 0.0 a 1.0>
Reasoning: <uma explicação curta sobre como a resposta se alinha (ou não) à persona>
"""

# Adicione outros templates de prompt de juiz aqui...

# Template para um Juiz que conduz uma conversa de avaliação e a conclui
CONVERSATIONAL_JUDGE_PROMPT = """
Você é um Juiz de IA conduzindo uma avaliação conversacional para avaliar a capacidade de raciocínio de outro agente de IA.

**Seu Objetivo e Roteiro (Contexto Secreto):**
{judge_context}

**Resumo da Resposta Ideal (Golden Summary):**
{golden_summary}

**Histórico da Conversa até Agora:**
{conversation_history}

**Sua Próxima Ação:**
Siga o roteiro passo a passo. Sua resposta deve ser uma de duas opções:

1.  **Continuar a Conversa:** Se o roteiro ainda não foi concluído, formule a **sua próxima fala** para o agente como uma string de texto simples.
2.  **Encerrar e Avaliar:** Se o roteiro instrui a terminar ou você já tem informações suficientes, sua resposta DEVE ser EXATAMENTE assim:
    `
    Stop Signal: {stop_signal}
    Score: <seu_score_de_0.0_a_1.0>
    Reasoning: <sua_justificativa_curta>`

**Sua Resposta (Próxima fala ou Avaliação Final com Sinal de Parada):**
"""
