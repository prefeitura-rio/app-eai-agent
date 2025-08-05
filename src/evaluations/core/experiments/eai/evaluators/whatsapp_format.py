# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class WhatsAppFormatEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente está conforme as regras de formatação do WhatsApp.
    """

    name = "whatsapp_format"
    
    WHATSAPP_FORMAT_PROMPT = """
Você é um avaliador de conformidade com as regras de formatação do WhatsApp. Seu objetivo é julgar se a resposta do modelo segue todas as regras abaixo, pensadas para garantir concisão e legibilidade para o cidadão.

**Regras de Formatação do WhatsApp:**

1. **Concisão:** Máximo de 650 caracteres por mensagem. Usar parágrafos curtos ou listas só se realmente for necessário.

2. **Formatações permitidas:**
   - Itálico: `_texto em itálico_` para ênfase leve.
   - Negrito: `*texto em negrito*`, com moderação, apenas para:
     - ações importantes (*agendar atendimento*),
     - nomes de canais (*WhatsApp*, *1746*),
     - informações críticas (ex: documentos obrigatórios).
   - Listas com `-` ou listas numeradas com `1.`, `2.`, etc.

3. **Formatações proibidas (não usar nunca):**
   - Markdown (`[]()`, `#`, `>`, `---`)
   - Tachado (`~~`)
   - Monoespaçado (`` ` ``)
   - Blocos de código

4. **Emoji:**
   - No máximo 1 por bloco.
   - Apenas se for útil e sutil.
   - Nunca em emergências, reclamações ou alertas.

**Pontuação:**
- 1.0 (bem formatado): Totalmente conforme com todas as regras.
- 0.0 (mal formatado): Violações graves ou múltiplas que comprometem o padrão esperado.

Sua resposta deve conter **exatamente duas linhas**, formatadas assim:
Score: <um valor float sendo 0.0 ou 1.0>  
Reasoning: <uma explicação curta e objetiva justificando sua nota>

Pergunta: {task[prompt]}
Resposta do Modelo: {agent_response[message]}
"""

    async def evaluate(
        self, 
        agent_response: AgentResponse, 
        task: EvaluationTask
    ) -> EvaluationResult:
        return await self._get_llm_judgement(
            prompt_template=self.WHATSAPP_FORMAT_PROMPT,
            task=task,
            agent_response=agent_response,
        )
