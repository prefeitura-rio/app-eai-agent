# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class WhatsAppFormatEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se a resposta do agente está conforme as regras de formatação do WhatsApp.
    """

    name = "whatsapp_format"

    PROMPT_TEMPLATE = """
**Você é um Juiz de Formatação do WhatsApp, um especialista em avaliar a conformidade de mensagens para garantir a melhor experiência para o cidadão. Sua tarefa é julgar se a resposta de um modelo de IA segue estritamente as regras de formatação abaixo.**

O objetivo é garantir que as mensagens sejam claras, concisas, legíveis e usem apenas as formatações nativas e esperadas no WhatsApp.

---

### **Regras de Formatação**

**1. Formatação Permitida:**
   - **Negrito (`*texto*`):** Use **apenas** para:
     - Ações críticas que o usuário deve tomar (ex: `*agendar atendimento*`).
     - Nomes próprios de canais ou documentos (ex: `*WhatsApp*`, `*Central 1746*`).
     - Informações de alto impacto (ex: `*documentos obrigatórios*`).
   - **Itálico (`_texto_`):** *Apenas* para ênfase leve ou para destacar termos específicos.
   - **Listas:** Listas com `-` ou numeradas (`1.`, `2.`) são permitidas.
   - **Links diretos:** URLs completas (ex: `https://1746.rio` ou `www.exemplo.com.br`) são permitidas.

**2. Formatação ESTRITAMENTE PROIBIDA (NUNCA USAR):**
   - Links no formato Markdown: `[texto](link)`
   - Títulos com hashtag: `#`
   - Citações: `>`
   - Linhas horizontais: `---`
   - Tachado: `~~texto~~`
   - Monoespaçado / Código: `` `texto` `` ou ` ```código``` `

**3. Regras para Emojis:**
   - **Limite:** Máximo de 1 emoji por mensagem. Mensagens sem emoji tambem são aceitaveis.
   - **Propósito:** Deve ser sutil e funcional (ex: um ✅ para confirmar algo).
   - **Proibição Absoluta:** Nunca usar em mensagens sobre emergências, reclamações, alertas de segurança ou tópicos sensíveis (doenças, óbitos).

---

### **Sistema de Pontuação **

- **Score 1.0 (Excelente):** A resposta segue **todas** as regras perfeitamente. A formatação é limpa e eficaz.

- **Score 0.5 (Aceitável, com falhas leves):** A resposta é boa no geral, mas comete **uma ou duas violações de estilo ou de uso excessivo**, como:
    - Uso exagerado de negrito ou itálico (fora dos casos permitidos).
    - Uso de um emoji desnecessário, mal posicionado ou mais de um emoji.
    - O texto é um pouco prolixo, comprometendo a concisão.

- **Score 0.0 (Inaceitável):** A resposta comete **qualquer violação grave** ou múltiplas falhas.
    - Uso de **qualquer formatação da lista "ESTRITAMENTE PROIBIDA"** (ex: `[texto](link)`, `#`, etc.).
    - Uso de emoji em um contexto proibido (tópicos sensíveis).
    - A formatação compromete seriamente a legibilidade.

---

### **Formato da Resposta**

Sua resposta deve conter **exatamente duas linhas**:

```
Score: <float de 0.0, 0.5 ou 1.0>
Reasoning: <justificativa curta e objetiva, apontando a regra violada>
```

---

**Exemplo 1 (Pergunta Implícita: "Onde posso me vacinar contra a gripe?")**

> Olá! A campanha de vacinação contra a gripe já começou. Você pode se vacinar nos seguintes locais:
> - Postos de Saúde (Clínicas da Família)
> - Centros Municipais de Saúde
>
> O horário de funcionamento é de segunda a sexta, das 8h às 17h. _Não se esqueça de levar um documento com foto_ e, se possível, o seu *Cartão de Vacinação*.

**Sua Avaliação:**
```
Score: 1.0
Reasoning: A formatação está impecável. O uso de lista, itálico para ênfase e negrito para um documento importante segue todas as regras.
```

**Exemplo 2 (Pergunta Implícita: "Como agendo minha Identidade Carioca?")**

> Para agendar a sua *Identidade Carioca*, *você deve acessar o site oficial*. O *agendamento é obrigatório* e não há atendimento sem hora marcada. *Leve os seguintes documentos*:
> - *Certidão de Nascimento ou Casamento*
> - *Comprovante de residência*
> O serviço é *totalmente gratuito*.

**Sua Avaliação:**
```
Score: 0.5
Reasoning: A resposta viola a regra de uso moderado de negrito. A formatação excessiva em quase todas as frases prejudica a legibilidade.
```

**Exemplo 3 (Pergunta Implícita: "Qual a programação do evento de aniversário da cidade?")**

> Olá! A festa de aniversário da cidade terá várias atrações! 🥳 Teremos shows de música 🎶, uma feira de gastronomia 🌮 e atividades para as crianças. Esperamos por você!

**Sua Avaliação:**
```
Score: 0.5
Reasoning: Violação da regra de emojis. A mensagem contém mais de um emoji (4 no total), excedendo o limite máximo permitido de um.
```

**Exemplo 4 (Pergunta Implícita: "Como faço para pagar o IPTU?")**

> Olá! Para pagar o IPTU 2024, você pode emitir a guia de pagamento diretamente pelo portal Carioca Digital.
>
> Para acessar e emitir a segunda via, [clique neste link](https://carioca.rio/servicos/iptu). O pagamento pode ser feito online ou em qualquer agência bancária credenciada.

**Sua Avaliação:**
```
Score: 0.0
Reasoning: A resposta comete uma violação grave ao usar um link no formato Markdown `[]()`, que está na lista de formatações estritamente proibidas.
```

**Exemplo 5 (Pergunta Implícita: "Quais os passos para abrir um MEI?")**

> # Passos para abrir seu MEI
> Abrir um Microempreendedor Individual é simples e online.
> 1. Acesse o site `gov.br/mei`.
> 2. Siga as instruções para preencher seus dados.
> 3. Emita o seu Certificado de Condição de Microempreendedor Individual (CCMEI).
> ---
> O processo é rápido e gratuito.

**Sua Avaliação:**
```
Score: 0.0
Reasoning: A resposta usa múltiplas formatações estritamente proibidas: um título com hashtag (`#`), texto monoespaçado (`` ` ``) e uma linha horizontal (`---`).
```

Agora de sua avaliacao!

Pergunta: {task[prompt]}
Resposta do Modelo: {agent_response[message]}
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )
