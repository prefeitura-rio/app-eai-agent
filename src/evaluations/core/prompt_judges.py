# -*- coding: utf-8 -*-

"""
Este arquivo centraliza todos os templates de prompt usados pelos Juízes LLM.
"""

# 1. PROMPT PARA CONDUZIR A CONVERSA
CONVERSATIONAL_JUDGE_PROMPT = """
Você é um Juiz de IA conduzindo uma avaliação conversacional. Sua tarefa é seguir um roteiro.
Nesta conversa voce é o Usuario e deve assumir a persona especificada no roteiro!! 
Nao inicie a suas respostas com seu nome!! Nem mencione ele em outras menssagens apenas na primeira!!

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
{golden_summary}
**Transcrição Completa da Conversa:**
{transcript}

**Sua Tarefa:**
Ruim: 0.0
Bom: 0.5
Exelente:1.0
Analise a transcrição e compare o desempenho do agente com o objetivo.
Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float para a capacidade de RACIOCÍNIO>
Reasoning: <uma explicação curta e objetiva para a sua nota de RACIOCÍNIO>
"""

FINAL_MEMORY_JUDGEMENT_PROMPT = """
Você é um Juiz de IA. Sua tarefa é fornecer um julgamento final sobre a **MEMÓRIA** de um agente com base em uma conversa.

**Objetivo da Avaliação (Golden Summary):**
{golden_summary}

**Transcrição Completa da Conversa:**
{transcript}

**Sua Tarefa:**
Ruim: 0.0
Bom: 0.5
Exelente:1.0
Analise a transcrição e compare o desempenho do agente com o objetivo.
Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float para a capacidade de MEMÓRIA>
Reasoning: <uma explicação curta e objetiva para a sua nota de MEMÓRIA>
"""

# 3. PROMPTS PARA AVALIAÇÕES DE TURNO ÚNICO

SEMANTIC_CORRECTNESS_PROMPT = """
Avalie similaridade semântica da resposta gerada por uma IA em relacao a Resposta ideal.
**Resposta Gerada pela IA:**
{output}
**Resposta Ideal:**
{task[golden_response_one_shot]}



**Sua Tarefa:**
Ruim: 0.0
Bom: 0.5
Exelente:1.0

Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float >
Reasoning: <uma explicação curta e objetiva para a sua nota>
"""

PERSONA_ADHERENCE_PROMPT = """
Avalie se a resposta da IA adere à persona definida: **{task[persona]}**.
**Resposta Gerada pela IA:**
{output}
**Sua Tarefa:**
Ruim: 0.0
Bom: 0.5
Exelente:1.0

Responda em duas linhas separadas, formatadas EXATAMENTE assim:
Score: <um valor float>
Reasoning: <uma explicação curta sobre como a resposta se alinha (ou não) à persona>
"""

ANSWER_COMPLETENESS_PROMPT = """
In this task, you will evaluate how well a model's response captures the core topics and essential concepts present in an ideal (gold standard) response.

The evaluation is based on content coverage, not stylistic similarity or phrasing.
Focus on whether the model response includes the *key points* that matter most. Minor omissions or differences in wording should not count agains the response if the main substance is captured.

Assign one of the following labels:
- "equivalent": The model's response captures all or most important concepts from the ideal response. Minor missing details are acceptable if the main points are clearly conveyed.
- "different": The model's response misses most key ideas or diverges substantially in meaning.

Your response must be a single word: "equivalent" or "different", with no other text.

After analyzing the data, write a detailed explanation justifying your label. Your explanation should:
- Briefly list the key topics or concepts from the ideal response.
- If any of the important key topics is missing, list it and explain what it is and how that impacts understanding.

[BEGIN DATA]
Query: {query}
Model Response: {model_response}
Ideal Response: {ideal_response}
[END DATA]

Please analyze the data carefully and then provide:

explanation: Your reasoning step by step, comparing the model response to the ideal response, and mentioning what (if anything) was missing.
label: "equivalent" or "different"
"""

ANSWER_ADDRESSING_PROMPT = """
In this task, you will evaluate whether the model's response directly and sufficiently answers the user's question or addresses their underlying need. Often, a user's query, especially if phrased as a complaint or a question about a problem (e.g., "is it normal for X not to work?"), implies a request for a solution or a next step. An effective answer addresses this implicit need.

You will categorize the model's response using one of two labels:
- "answered": The response addresses the main point of the query clearly and provides a reasonably complete and useful answer. This includes responses that offer a relevant solution, actionable advice, or a clear next step when the query describes a problem or implies a need for assistance, even if a direct question for a solution was not explicitly stated. Minor omissions are acceptable if the user would still consider their underlying need or explicit question adequately addressed.
- "unanswered": The response misses or avoids the core intent of the query (explicit or implicit), answers only vaguely or incorrectly, fails to offer a relevant solution or next step when one is clearly implied by a problem statement, or leaves out key information that prevents the user from being satisfied or taking appropriate action to resolve their issue.

Your response must be a single word: "answered" or "unanswered", with no other text.

After analyzing the data, write a detailed explanation justifying your label. Your explanation should:
1. Identify the main point(s) or intent of the query, including any implicit request for a solution or assistance if the query describes a problem or expresses a complaint.
2. Analyze whether the response addresses these points (explicit and implicit) clearly and sufficiently, paying particular attention to whether a relevant solution or actionable next step was provided if the query indicated a problem.
3. If labeled "unanswered", explain exactly what was missing or unclear, or why the offered solution (if any) was inadequate, irrelevant to the user's underlying need, or if no attempt was made to address an implied problem.

[BEGIN DATA]
Query: {query}
Model Response: {model_response}
[END DATA]

Please analyze the data carefully and then provide:

explanation: Your reasoning step by step, identifying whether the model's response meets the user's explicit questions as well as their underlying needs, especially implied requests for solutions when a problem is presented.
label: "answered" or "unanswered"
"""

CLARITY_PROMPT = """
In this task, you will evaluate if a response in Portuguese is clear and understandable for the common citizens of Rio de Janeiro seeking public services or information.

A clear response for municipal services must be easily understood by citizens with varying education levels, avoiding bureaucratic language while remaining accurate and helpful.

Evaluation criteria for citizen-friendly clarity:

1. **Simple Language**: 
   - Avoids complex bureaucratic terms ("juridiquês")
   - Uses everyday Portuguese that a person with basic education can understand
   - Explains technical terms when they must be used
   - Avoids excessive use of acronyms without explanation

2. **Direct and Practical**:
   - Answers the citizen's question without unnecessary detours
   - Provides actionable information (where to go, what to bring, when to do it)
   - Focuses on what the citizen needs to know to solve their problem
   - Includes specific addresses, phone numbers, or websites when relevant

3. **Well-Organized**:
   - Information is presented in logical order (most important first)
   - Uses simple lists or steps when explaining procedures
   - Breaks down complex processes into manageable parts
   - Clear separation between different topics or requirements

4. **Complete but Concise**:
   - Includes all essential information without overwhelming details
   - Appropriate length for WhatsApp or mobile reading
   - Avoids repetition
   - Doesn't assume prior knowledge of government processes

Labels:
- "clear": The response is easily understood by common citizens and provides practical, actionable information
- "unclear": The response uses complex language, is confusing, or fails to provide practical guidance

Analyze the response from the perspective of a common citizen seeking help with municipal services. Consider someone who may have limited formal education, may be unfamiliar with government processes, and needs practical information to resolve their issue.

Write a detailed explanation evaluating:
- Whether bureaucratic or complex terms are used without explanation
- If the response provides clear, actionable steps
- Whether the information is organized in a helpful way
- If the length and detail level are appropriate
- Any issues that might confuse or frustrate a citizen

Provide specific examples from the response to support your assessment.

# Examples of unclear vs clear language in Portuguese:

unclear: "Dirija-se à repartição competente munido da documentação pertinente para protocolar sua solicitação"
clear: "Vá à delegacia (Rua X, número Y) com RG, CPF e comprovante de residência"

unclear: "A emissão da certidão está condicionada à quitação dos débitos tributários"
clear: "Para pegar a certidão, você precisa primeiro pagar todos os impostos em atraso"

unclear: "O requerente deve observar os prazos regimentais"
clear: "Você tem 30 dias para entregar os documentos"

unclear: "Proceda ao agendamento através dos canais oficiais"
clear: "Marque seu atendimento pelo site www.exemplo.com"

[BEGIN DATA]
Query: {query}
Model Response: {model_response}
[END DATA]

Please analyze the data carefully and then provide:

explanation: Your reasoning step by step, focusing on clarity, simplicity, and practical guidance for citizens.
label: "clear" or "unclear"
"""