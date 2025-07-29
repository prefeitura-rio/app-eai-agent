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
Responda com um objeto JSON contendo duas chaves:
1. "score": Um valor float de 0.0 (completamente incorreto) a 1.0 (perfeitamente correto).
2. "reasoning": Uma explicação curta e objetiva para a sua nota.

**JSON de Avaliação:**
"""

# Template para avaliar se a resposta segue uma persona específica
PERSONA_ADHERENCE_PROMPT = """
Avalie se a resposta da IA adere à persona definida.
A persona é: **{task[persona]}**.

**Resposta Gerada pela IA:**
{output}

**Sua Tarefa:**
Responda com um objeto JSON contendo duas chaves:
1. "score": Um valor float de 0.0 (não adere à persona) a 1.0 (adere perfeitamente).
2. "reasoning": Uma explicação curta sobre como a resposta se alinha (ou não) à persona.

**JSON de Avaliação:**
"""

# Adicione outros templates de prompt de juiz aqui...
