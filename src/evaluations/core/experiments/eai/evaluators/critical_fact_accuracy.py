# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnEvaluationInput,
    BaseMultipleTurnEvaluator,
)


class CriticalFactAccuracyEvaluator(BaseMultipleTurnEvaluator):
    """
    Avalia se a resposta à segunda pergunta contém corretamente o
    critical_fact_reused definido no dataset.
    
    Critério binário:
    - 1: fato correto e preciso
    - 0: fato incorreto, incompleto ou ausente
    
    Regras importantes:
    - Pequenas variações textuais são permitidas
    - O valor deve ser semanticamente idêntico
    - Respostas genéricas sem mencionar o fato → score 0
    """

    name = "critical_fact_accuracy"

    PROMPT_TEMPLATE = """
Você é um especialista em avaliar a precisão factual de respostas de chatbots. Sua tarefa é verificar se a resposta do agente à segunda pergunta do usuário contém corretamente o fato crítico esperado.

**Contexto do Tema:**
{task[tema]}

**Primeira Pergunta do Usuário:**
{first_user_message}

**Primeira Resposta do Agente:**
{first_agent_message}

**Segunda Pergunta do Usuário:**
{second_user_message}

**Segunda Resposta do Agente (A SER AVALIADA):**
{second_agent_message}

**Fato Crítico Esperado:**
{task[critical_fact_reused]}

**Tipo do Fato:**
{task[fact_type]}

**Tipo de Dependência:**
{task[dependency_type]}

---

**Critérios de Avaliação:**

1. **Score 1** - O agente mencionou corretamente o fato crítico:
   - O valor/informação está presente na segunda resposta
   - Pequenas variações textuais são aceitáveis (ex: "R$ 41,32" vs "41 reais e 32 centavos")
   - A informação é semanticamente idêntica ao fato esperado
   - Telefones, endereços, valores, prazos, documentos, etc. devem estar corretos

2. **Score 0** - O agente NÃO forneceu o fato corretamente:
   - O fato crítico não foi mencionado
   - O fato foi mencionado de forma vaga ou genérica (ex: "cerca de 40 reais" quando o esperado é "R$ 41,32")
   - O fato foi mencionado incorretamente (número errado, endereço errado, etc.)
   - O agente respondeu genericamente sem fornecer a informação específica

**Exemplos:**

Caso: critical_fact = "R$ 41,32"
✔ "O valor mínimo é R$ 41,32." → Score: 1
✖ "O valor mínimo é cerca de R$ 40." → Score: 0
✖ "Existe um valor mínimo definido no site." → Score: 0

Caso: critical_fact = "121 (Disque Social)"
✔ "Você pode ligar no 121, o Disque Social." → Score: 1
✔ "Ligue para o Disque Social no número 121." → Score: 1
✖ "Você pode fazer uma denúncia ligando para a Prefeitura." → Score: 0

Caso: critical_fact = "192"
✔ "Ligue para o 192." → Score: 1
✔ "O número é 192, que é o SAMU." → Score: 1
✖ "Ligue para a emergência." → Score: 0

---

**IMPORTANTE:**
- Avalie APENAS a segunda resposta do agente
- Não inferir ou assumir; apenas verificar se o fato está explicitamente presente
- Seja rigoroso com precisão numérica (telefones, valores, prazos, códigos)
- Seja flexível com pequenas variações de redação

**Formato da Resposta (exatamente 2 linhas, sem texto extra):**
Score: <0 ou 1>
Reasoning: <uma explicação curta e objetiva justificando sua nota>
"""

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de precisão do fato crítico usando o cliente juiz.
        """
        try:
            transcript = agent_response.transcript
            task_dict = task.model_dump(exclude_none=True)
            secondary_message = task_dict.get('secondary_user_message', '')
            
            # Identifica qual turno contém a secondary_user_message
            secondary_turn_index = None
            for idx, turn in enumerate(transcript):
                if turn.user_message and secondary_message.lower() in turn.user_message.lower():
                    secondary_turn_index = idx
                    break
            
            # Se não encontrou a segunda pergunta, retorna erro
            if secondary_turn_index is None:
                return EvaluationResult(
                    score=None,
                    annotations=f"secondary_user_message ('{secondary_message}') não encontrada na conversa",
                    has_error=True,
                    error_message="Segunda pergunta não foi feita na conversa"
                )
            
            # Extrai as mensagens relevantes
            first_user_message = transcript[0].user_message if len(transcript) > 0 else ""
            first_agent_message = transcript[0].agent_message if len(transcript) > 0 else ""
            second_user_message = transcript[secondary_turn_index].user_message
            second_agent_message = transcript[secondary_turn_index].agent_message or ""
            
            # Prepara o prompt customizado
            
            prompt = self.PROMPT_TEMPLATE.format(
                task=task_dict,
                first_user_message=first_user_message,
                first_agent_message=first_agent_message,
                second_user_message=second_user_message,
                second_agent_message=second_agent_message,
            )
            
            # Executa o julgamento
            judgement_response = await self.judge_client.execute(prompt)
            
            # Extrai o score (0 ou 1)
            import re
            score_match = re.search(r"Score:\s*([01])", judgement_response, re.IGNORECASE)
            score = int(score_match.group(1)) if score_match else 0
            
            return EvaluationResult(
                score=score,
                annotations=judgement_response,
                has_error=False,
                error_message=None,
            )
            
        except Exception as e:
            return EvaluationResult(
                score=None,
                annotations=None,
                has_error=True,
                error_message=str(e),
            )
