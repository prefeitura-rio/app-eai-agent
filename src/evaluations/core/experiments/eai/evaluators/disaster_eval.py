# -*- coding: utf-8 -*-
from src.evaluations.core.eval import EvaluationTask, EvaluationResult
from src.evaluations.core.eval.evaluators.base import BaseOneTurnEvaluator
from src.evaluations.core.eval.schemas import AgentResponse


class ToolUsageEvaluator(BaseOneTurnEvaluator):
    """
    Avalia se o agente utilizou as ferramentas corretas (MCP tools) para responder à pergunta
    sobre desastres hidrológicos.
    """

    name = "tool_usage"

    PROMPT_TEMPLATE = """
Nesta tarefa, você irá avaliar se o agente utilizou as ferramentas (MCP tools) corretas para responder à pergunta sobre desastres hidrológicos.

**CONTEXTO: FERRAMENTAS DISPONÍVEIS**

O agente tem acesso a 2 ferramentas MCP (Model Context Protocol):

1. **create_cor_alert** - Criar alerta para o Centro de Operações Rio (COR)
   - **Quando usar**: Situações de enchente/alagamento ATIVAS ou IMINENTES
   - **Propósito**: Alertar autoridades sobre ocorrências em tempo real
   - **Parâmetros**: tipo do alerta (alagamento, enchente, dano_chuva), gravidade (alta/crítica), descrição, endereço
   - **Exemplos de uso apropriado**:
     - "A água já está chegando na porta"
     - "Tá começando a entrar água"
     - "Aqui está alagando mas nem está chovendo"
     - "O rio subiu muito"

2. **equipments_by_address** - Buscar equipamentos públicos próximos
   - **Quando usar**:
     - Situações de risco que requerem evacuação → buscar PONTOS_DE_APOIO
     - Emergências médicas pós-desastre → buscar CF ou CMS.
     - Solicitação de rota segura ou abrigo
   - **Parâmetros**: endereço, categoria de equipamento.
   - **Exemplos de uso apropriado**:
     - "Preciso de uma rota segura agora" → PONTOS_DE_APOIO
     - "Onde tem abrigo perto de mim?" → PONTOS_DE_APOIO
     - "Entrei na água suja e tenho um corte" → CF ou CMS
     - "Tô com febre alta depois da enchente" → UPA ou HOSPITAL

**QUANDO NÃO USAR FERRAMENTAS**:
- Perguntas sobre preparação preventiva (antes da chuva)
- Dicas e listas de itens
- Planejamento familiar
- Instruções sobre como fazer algo (vedar porta, etc.)
- Nestes casos, apenas fornecer orientações é suficiente

**COMBINAÇÃO DE FERRAMENTAS**:
Em situações de risco iminente à vida por enchente/alagamento, **AMBAS** as ferramentas devem ser usadas:
- `create_cor_alert`: para alertar o COR
- `equipments_by_address`: para oferecer ponto de apoio

**AVALIAÇÃO**

Ferramentas Esperadas: {task[golden_tool]}
(Vazio = nenhuma ferramenta necessária; múltiplas ferramentas separadas por vírgula)

Analise a resposta do agente e avalie:

1. **Uso Correto (50%)**:
   - O agente usou as ferramentas esperadas?
   - Se esperava múltiplas ferramentas (ex: "create_cor_alert,equipments_by_address"), ambas foram usadas?
   - Se não esperava ferramentas (campo vazio), o agente corretamente NÃO usou ferramentas?

2. **Evidências na Resposta (30%)**:
   - Há evidências de que a ferramenta foi executada? (ex: "te mostro o ponto de apoio", "te envio o endereço")
   - Para create_cor_alert: O agente NÃO deve mencionar ao usuário que criou um alerta (isso é interno)
   - Para equipments_by_address: O agente deve mencionar que vai buscar/mostrar o equipamento

3. **Apropriação ao Contexto (20%)**:
   - O uso (ou não uso) da ferramenta foi apropriado para o nível de urgência?
   - Em emergências ativas, ferramentas foram priorizadas?

**PONTUAÇÃO**:
- **1.0 (excelente)**: Usou exatamente as ferramentas esperadas de forma apropriada
- **0.7 (boa)**: Usou as ferramentas corretas mas com pequenas limitações
- **0.4 (parcial)**: Usou apenas parte das ferramentas esperadas OU usou quando não deveria
- **0.0 (ruim)**: Não usou ferramentas quando deveria OU usou ferramentas incorretas

**ATENÇÃO**: Se o campo golden_tool está vazio, significa que NÃO era esperado uso de ferramentas. Neste caso, se o agente NÃO usou ferramentas, a nota deve ser 1.0.

Sua resposta deve conter **exatamente duas linhas**, com o seguinte formato:
Score: <um valor float entre 0.0 e 1.0>
Reasoning: <explicação curta citando quais tools foram/deveriam ser usadas e se foi apropriado>

Pergunta: {task[prompt]}
Ferramentas Esperadas: {task[golden_tool]}
Resposta do Agente: {agent_response[message]}
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        # Verifica se existe golden_tool no task
        if not hasattr(task, "golden_tool"):
            return EvaluationResult(
                score=None,
                annotations="No golden_tool field in dataset",
                has_error=True,
                error_message="Missing golden_tool field in task",
            )

        # Se golden_tool está vazio, significa que não era esperado uso de ferramentas
        # Isso é válido - não retornar erro
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )


class CivilDefenseDisasterResponseEvaluator(BaseOneTurnEvaluator):
    """
    Avalia a qualidade de respostas sobre desastres hidrológicos (enchentes, alagamentos)
    com base em diretrizes de defesa civil.
    """

    name = "civil_defense_disaster_response"

    PROMPT_TEMPLATE = """
Nesta tarefa, você irá avaliar a qualidade de uma resposta de um assistente virtual especializado em orientações sobre enchentes e alagamentos.

**CONTEXTO DO ASSISTENTE**

O assistente é um chatbot de orientação para cidadãos do Rio de Janeiro sobre prevenção e resposta a desastres hidrológicos (enchentes e alagamentos). Ele deve:

- Fornecer orientações práticas baseadas em Defesa Civil
- Usar linguagem conversacional e acessível.
- Adaptar a resposta ao momento (preparação, emergência, pós-desastre)
- Coletar informações quando necessário (endereço para rotas, número de pessoas para planos)
- Identificar emergências médicas e encaminhar corretamente
- Fornecer ações específicas e concretas, não genéricas

**TIPOS DE PERGUNTAS E RESPOSTAS ESPERADAS**

1. **Preparação Preventiva** (antes da chuva):
   - Ações específicas: elevar geladeira em blocos, vedar portas com panos/borracha, guardar documentos em sacos plásticos
   - Tom proativo e didático
   - Exemplo CORRETO: "elevar geladeira e máquina usando base fixa"
   - Exemplo INCORRETO: "proteja seus eletrodomésticos" (genérico demais)

2. **Ação Imediata** (água entrando):
   - Orientações de segurança urgentes: vedar portas/ralos, desligar energia, afastar produtos químicos
   - Tom direto e tranquilizador
   - Deve priorizar segurança sobre proteção de bens

3. **Planejamento** (plano familiar, listas):
   - Coleta informações necessárias: número de pessoas, endereço, presença de crianças/idosos/pets
   - Fornece listas detalhadas: kit de emergência, documentos, rotas
   - Explica o porquê dos itens

4. **Encaminhamentos** (rotas, abrigos):
   - Solicita endereço para fornecer rotas específicas
   - Menciona "ponto de apoio mais próximo" ou "rota segura"
   - Orienta sobre o que levar (documentos, água, remédios)

5. **Emergências Médicas**:
   - Identifica gravidade: febre alta pós-enchente, choque elétrico, corte com água contaminada
   - Encaminha corretamente:
     * Corte com água suja → CF ou CMS
     * Febre alta pós-enchente → UPA ou hospital
     * Choque elétrico/inconsciente → 193 (Bombeiros) ou 192 (SAMU) IMEDIATAMENTE
   - Não minimiza sintomas

**CONHECIMENTOS TÉCNICOS DE DEFESA CIVIL**

Diretrizes que devem estar refletidas nas respostas:

- **Riscos principais**: choque elétrico (água + tomadas), leptospirose (água contaminada + cortes), afogamento (correnteza, bueiros abertos)
- **Limites de segurança**: não atravessar água acima do joelho ou com correnteza
- **Telefones**: 199 (Defesa Civil), 193 (Bombeiros), 192 (SAMU)
- **Prevenção**: elevar bens, vedar entradas, limpar calhas, guardar documentos no alto
- **Emergência**: desligar energia, não atravessar água, procurar local alto
- **Pós-desastre**: desinfecção com água sanitária, descarte de alimentos contaminados, atenção a sintomas de leptospirose

**CRITÉRIOS DE AVALIAÇÃO**

Avalie a resposta do agente considerando:

1. **Adequação ao Contexto** (30%):
   - A resposta reconhece o momento (preparação vs emergência)?
   - A urgência da orientação é apropriada?
   - Coleta informações quando necessário (endereço, número de pessoas)?
   - Em emergências médicas, identifica gravidade corretamente?

2. **Ações Específicas e Práticas** (30%):
   - As orientações são concretas e acionáveis?
   - Evita genericidade ("proteja seus bens" vs "eleve geladeira em blocos")?
   - Fornece detalhes úteis (materiais, quantidades, locais)?
   - Em planejamentos, oferece listas e estrutura clara?

3. **Segurança e Priorização** (25%):
   - Prioriza corretamente (vida > bens)?
   - Alerta para riscos principais (choque, leptospirose, afogamento)?
   - Em emergências, orienta ação imediata apropriada?
   - Encaminha corretamente (CF/CMS vs UPA/Hospital vs emergência 193/192)?
   - NÃO fornece orientações perigosas?

4. **Tom e Proatividade** (15%):
   - Usa linguagem conversacional e empática?
   - Tom apropriado (calmo em emergência, didático em preparação)?
   - Demonstra disposição em ajudar?
   - Pede informações de forma natural quando precisa?

**PONTUAÇÃO**

- **1.0 (excelente)**: Resposta adequada ao contexto, com ações específicas, segura, e tom apropriado
- **0.7 (boa)**: Resposta apropriada mas com pequenas limitações (ex: poderia ser mais específica, ou faltou coletar uma informação)
- **0.4 (regular)**: Resposta parcialmente correta mas com problemas (ex: muito genérica, tom inadequado, ou omite risco importante)
- **0.0 (ruim)**: Resposta inadequada ao contexto, perigosa, ou completamente genérica

**EXEMPLOS DE AVALIAÇÃO**

Pergunta: "O que posso fazer hoje pra deixar minha casa mais segura antes da chuva?"
- EXCELENTE (1.0): Lista ações específicas (elevar geladeira em blocos, vedar portas com panos, guardar documentos em sacos plásticos)
- REGULAR (0.4): "Proteja seus bens, tenha um plano de evacuação" (genérico demais)

Pergunta: "A água já está chegando na porta, o que faço agora?"
- EXCELENTE (1.0): "Vede a porta e ralos imediatamente. Se for seguro, desligue a energia do pavimento. Recolha produtos de limpeza do chão"
- RUIM (0.0): "Mantenha a calma e aguarde orientações" (não fornece ação imediata)

Pergunta: "Preciso de uma rota segura agora"
- EXCELENTE (1.0): Solicita endereço para fornecer rota específica + orienta o que levar
- REGULAR (0.4): Fornece orientações genéricas sem pedir endereço

Pergunta: "Tô com febre alta depois da enchente"
- EXCELENTE (1.0): Identifica gravidade, orienta ir AGORA para UPA/hospital, oferece endereço
- RUIM (0.0): "Beba bastante água e descanse" (minimiza sintoma grave)

Sua resposta deve conter **exatamente duas linhas**, com o seguinte formato:
Score: <um valor float entre 0.0 e 1.0>
Reasoning: <explicação curta citando os critérios: adequação ao contexto, especificidade, segurança, e tom>

Pergunta do Usuário: {task[prompt]}
Resposta do Agente: {agent_response[message]}
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )


class ResponseQualityEvaluator(BaseOneTurnEvaluator):
    """
    Avalia a qualidade geral da resposta considerando relevância, tom apropriado e utilidade.
    """

    name = "response_quality"

    PROMPT_TEMPLATE = """
Nesta tarefa, você irá avaliar a qualidade geral de uma resposta fornecida por um assistente virtual de serviços públicos.

Critérios de avaliação:

1. **Relevância** (35%):
   - A resposta aborda diretamente a pergunta do usuário?
   - Todas as partes da pergunta foram respondidas?
   - Há informações desnecessárias ou fora do contexto?

2. **Tom e Abordagem** (25%):
   - O tom é apropriado para atendimento ao cidadão (empático, respeitoso, profissional)?
   - A linguagem é adequada ao contexto (formal quando necessário, acessível sempre)?
   - Demonstra disposição em ajudar?

3. **Utilidade Prática** (25%):
   - Fornece informações acionáveis que o cidadão pode usar?
   - Inclui detalhes importantes (endereços, telefones, horários, documentos)?
   - Orienta próximos passos de forma clara?

4. **Precisão e Confiabilidade** (15%):
   - A informação parece precisa e confiável?
   - Evita especulações ou informações vagas?
   - Quando não sabe, indica claramente ou sugere onde buscar?

Pontuações possíveis:
- 1.0 (excelente): Resposta relevante, útil, com tom apropriado e informações precisas
- 0.7 (boa): Resposta adequada mas com pequenas limitações
- 0.4 (regular): Resposta aceitável mas com problemas notáveis
- 0.0 (ruim): Resposta inadequada, irrelevante ou problemática

Sua resposta deve conter **exatamente duas linhas**, com o seguinte formato:
Score: <um valor float entre 0.0 e 1.0>
Reasoning: <uma explicação curta e objetiva justificando sua nota>

Pergunta: {task[prompt]}
Resposta do Agente: {agent_response[message]}
"""

    async def evaluate(
        self, agent_response: AgentResponse, task: EvaluationTask
    ) -> EvaluationResult:
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )