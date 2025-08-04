# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
)
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class ClarityEvaluator(BaseOneTurnEvaluator):
    """
    Avalia a capacidade de memória do agente com base na transcrição
    completa de uma conversa.
    """

    name = "clarity"

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

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de aderência à persona usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.CLARITY_PROMPT,
            task=task,
            agent_response=agent_response,
        )