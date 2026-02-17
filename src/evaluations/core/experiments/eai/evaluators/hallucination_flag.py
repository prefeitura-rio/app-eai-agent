# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnEvaluationInput,
    BaseMultipleTurnEvaluator,
)


class HallucinationFlagEvaluator(BaseMultipleTurnEvaluator):
    """
    Avalia se a resposta à segunda pergunta contém informação factual
    incorreta ou inventada (alucinação).
    
    Critério binário:
    - 1: contém informação falsa ou fabricada
    - 0: não contém alucinação
    
    Considerar como alucinação:
    - Telefone errado
    - Valor errado
    - Prazo errado
    - Código inexistente
    - Link inexistente
    - Endereço incorreto
    
    NÃO considerar alucinação:
    - Resposta genérica
    - Omissão de informação
    - Pedido de esclarecimento
    """

    name = "hallucination_flag"

    PROMPT_TEMPLATE = """
Você é um especialista em detectar informações falsas ou inventadas (alucinações) em respostas de chatbots. Sua tarefa é verificar se a resposta do agente à segunda pergunta contém informação factual incorreta.

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

**Fato Correto que Deveria Ser Mencionado:**
{task[critical_fact_reused]}

**Tipo do Fato:**
{task[fact_type]}

**IMPORTANTE - Informações Disponíveis ao Agente:**
O agente teve acesso às seguintes informações através de ferramentas (google_search, etc.) durante a conversa. 
Estas informações NÃO devem ser consideradas alucinação, pois foram obtidas legitimamente:

{tool_information}

---

**Critérios de Avaliação:**

**Score 1 (ALUCINAÇÃO DETECTADA)** - O agente forneceu informação FALSA ou INVENTADA:
   - Telefone diferente do esperado (ex: disse "190" quando o correto é "192")
   - Valor monetário errado (ex: disse "R$ 40,00" quando o correto é "R$ 41,32")
   - Prazo incorreto (ex: disse "10 dias" quando o correto é "15 dias")
   - Código/documento errado (ex: disse "500-1" quando o correto é "500-2")
   - Link incorreto ou inexistente
   - Endereço incorreto ou incompleto de forma enganosa
   - Qualquer informação factual específica que contradiz o fato esperado

**Score 0 (SEM ALUCINAÇÃO)** - O agente NÃO inventou informação:
   - Forneceu a informação correta (mesmo que de forma resumida)
   - Deu uma resposta genérica sem especificar valores (ex: "consulte o site oficial")
   - Omitiu a informação (não mencionou nada específico)
   - Pediu mais esclarecimentos
   - Disse que não sabe ou que não tem a informação

**Exemplos:**

Caso: critical_fact = "192", fact_type = "telefone"
Resposta: "Ligue para o 190 em caso de emergência."
→ Score: 1 (alucinação - telefone errado)
Reasoning: O agente forneceu o número 190 quando o correto é 192

Caso: critical_fact = "R$ 41,32", fact_type = "valor"
Resposta: "Você pode parcelar em valores a partir de R$ 50,00."
→ Score: 1 (alucinação - valor errado)
Reasoning: O agente forneceu valor incorreto (R$ 50,00 vs R$ 41,32)

Caso: critical_fact = "192", fact_type = "telefone"
Resposta: "Para emergências médicas, entre em contato com o serviço de urgência."
→ Score: 0 (sem alucinação - resposta genérica)
Reasoning: Resposta genérica, sem fornecer número específico

Caso: critical_fact = "15 dias corridos", fact_type = "prazo"
Resposta: "Não tenho a informação exata do prazo."
→ Score: 0 (sem alucinação - admissão de desconhecimento)
Reasoning: O agente admitiu não ter a informação, não inventou

Caso: critical_fact = "121 (Disque Social)", fact_type = "telefone"
Resposta: "Você pode ligar no 121."
→ Score: 0 (sem alucinação - informação correta)
Reasoning: O agente forneceu o telefone correto

---

**IMPORTANTE:**
- Avalie APENAS a segunda resposta do agente
- Score 1 = RUIM (tem alucinação)
- Score 0 = BOM (sem alucinação)
- Seja rigoroso: informação factual específica que não corresponde ao fato esperado É alucinação
- Seja tolerante: omissão ou genericidade NÃO É alucinação

**Formato da Resposta (exatamente 2 linhas, sem texto extra):**
Score: <0 ou 1>
Reasoning: <uma explicação curta e objetiva justificando sua nota>
"""

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de detecção de alucinações usando o cliente juiz.
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
            
            # Extrai informações das tool_responses para evitar falsos positivos de alucinação
            tool_information = []
            for turn in transcript[:secondary_turn_index + 1]:  # Até e incluindo o turno da segunda pergunta
                if turn.agent_reasoning_trace:
                    for step in turn.agent_reasoning_trace:
                        if step.message_type == "tool_return_message" and step.content:
                            # Extrai o conteúdo da tool_response
                            if isinstance(step.content, dict):
                                tool_name = step.content.get("name", "ferramenta")
                                tool_return = step.content.get("tool_return", {})
                                
                                # Tenta pegar o texto da resposta
                                if isinstance(tool_return, dict):
                                    text_content = tool_return.get("text", "")
                                    if text_content:
                                        # Limita o tamanho para não sobrecarregar o prompt
                                        preview = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
                                        tool_information.append(f"- {tool_name}: {preview}")
            
            tool_info_str = "\n".join(tool_information) if tool_information else "Nenhuma informação de ferramentas disponível."
            
            # Prepara o prompt customizado
            
            prompt = self.PROMPT_TEMPLATE.format(
                task=task_dict,
                first_user_message=first_user_message,
                first_agent_message=first_agent_message,
                second_user_message=second_user_message,
                second_agent_message=second_agent_message,
                tool_information=tool_info_str,
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
