# # @eval_method(name="golden_equipment", turns="multiple")
# # async def golden_equipment(
# #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
# # ) -> Tuple[bool, str]:
# #     """Avalia se o equipamento correto foi chamado na resposta."""
# #     return await self._get_llm_judgement(
# #         prompt_judges.GOLDEN_EQUIPMENT_PROMPT,
# #         golden_summary=task.get("golden_response_multiple_shot", ""),
# #         transcript=agent_response,
# #     )



# # @eval_method(name="answer_addressing", turns="one")
# # async def answer_addressing(
# #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
# # ) -> Dict[str, Any]:
# #     """Avalia se a resposta aborda adequadamente a pergunta."""
# #     return await self._get_llm_judgement(
# #         prompt_judges.ANSWER_ADDRESSING_PROMPT,
# #         output=agent_response.get("output", ""),
# #         task=task,
# #     )

# # @eval_method(name="clarity", turns="one")
# # async def clarity(
# #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
# # ) -> Dict[str, Any]:
# #     """Avalia a clareza da resposta de uma única resposta."""
# #     return await self._get_llm_judgement(
# #         prompt_judges.CLARITY_PROMPT,
# #         output=agent_response.get("output", ""),
# #         task=task,
# #     )

# # @eval_method(name="activate_search", turns="one")
# # async def activate_search(
# #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
# # ) -> Tuple[bool, str]:
# #     """Avalia se a busca foi ativada corretamente."""
# #     grouped = agent_response.get("output", "").get("grouped", {})
# #     tool_msgs = grouped.get("tool_return_messages", [])

# #     SEARCH_TOOL_NAMES = [
# #         # "public_services_grounded_search",
# #         "google_search",
# #         "equipments_instructions",
# #         "equipments_by_address",
# #     ]

# #     activated = {
# #         msg.get("name") for msg in tool_msgs if msg.get("name") in SEARCH_TOOL_NAMES
# #     }
# #     explanation = f"Activated tools: {list(activated)}"

# #     return len(activated) > 0, explanation


# ANSWER_ADDRESSING_PROMPT = """
# In this task, you will evaluate whether the model's response directly and sufficiently answers the user's question or addresses their underlying need. Often, a user's query, especially if phrased as a complaint or a question about a problem (e.g., "is it normal for X not to work?"), implies a request for a solution or a next step. An effective answer addresses this implicit need.

# You will categorize the model's response using one of two labels:
# - "answered": The response addresses the main point of the query clearly and provides a reasonably complete and useful answer. This includes responses that offer a relevant solution, actionable advice, or a clear next step when the query describes a problem or implies a need for assistance, even if a direct question for a solution was not explicitly stated. Minor omissions are acceptable if the user would still consider their underlying need or explicit question adequately addressed.
# - "unanswered": The response misses or avoids the core intent of the query (explicit or implicit), answers only vaguely or incorrectly, fails to offer a relevant solution or next step when one is clearly implied by a problem statement, or leaves out key information that prevents the user from being satisfied or taking appropriate action to resolve their issue.

# Your response must be a single word: "answered" or "unanswered", with no other text.

# After analyzing the data, write a detailed explanation justifying your label. Your explanation should:
# 1. Identify the main point(s) or intent of the query, including any implicit request for a solution or assistance if the query describes a problem or expresses a complaint.
# 2. Analyze whether the response addresses these points (explicit and implicit) clearly and sufficiently, paying particular attention to whether a relevant solution or actionable next step was provided if the query indicated a problem.
# 3. If labeled "unanswered", explain exactly what was missing or unclear, or why the offered solution (if any) was inadequate, irrelevant to the user's underlying need, or if no attempt was made to address an implied problem.

# [BEGIN DATA]
# Query: {query}
# Model Response: {model_response}
# [END DATA]

# Please analyze the data carefully and then provide:

# explanation: Your reasoning step by step, identifying whether the model's response meets the user's explicit questions as well as their underlying needs, especially implied requests for solutions when a problem is presented.
# label: "answered" or "unanswered"
# """

# CLARITY_PROMPT = """
# In this task, you will evaluate if a response in Portuguese is clear and understandable for the common citizens of Rio de Janeiro seeking public services or information.

# A clear response for municipal services must be easily understood by citizens with varying education levels, avoiding bureaucratic language while remaining accurate and helpful.

# Evaluation criteria for citizen-friendly clarity:

# 1. **Simple Language**:
#    - Avoids complex bureaucratic terms ("juridiquês")
#    - Uses everyday Portuguese that a person with basic education can understand
#    - Explains technical terms when they must be used
#    - Avoids excessive use of acronyms without explanation

# 2. **Direct and Practical**:
#    - Answers the citizen's question without unnecessary detours
#    - Provides actionable information (where to go, what to bring, when to do it)
#    - Focuses on what the citizen needs to know to solve their problem
#    - Includes specific addresses, phone numbers, or websites when relevant

# 3. **Well-Organized**:
#    - Information is presented in logical order (most important first)
#    - Uses simple lists or steps when explaining procedures
#    - Breaks down complex processes into manageable parts
#    - Clear separation between different topics or requirements

# 4. **Complete but Concise**:
#    - Includes all essential information without overwhelming details
#    - Appropriate length for WhatsApp or mobile reading
#    - Avoids repetition
#    - Doesn't assume prior knowledge of government processes

# Labels:
# - "clear": The response is easily understood by common citizens and provides practical, actionable information
# - "unclear": The response uses complex language, is confusing, or fails to provide practical guidance

# Analyze the response from the perspective of a common citizen seeking help with municipal services. Consider someone who may have limited formal education, may be unfamiliar with government processes, and needs practical information to resolve their issue.

# Write a detailed explanation evaluating:
# - Whether bureaucratic or complex terms are used without explanation
# - If the response provides clear, actionable steps
# - Whether the information is organized in a helpful way
# - If the length and detail level are appropriate
# - Any issues that might confuse or frustrate a citizen

# Provide specific examples from the response to support your assessment.

# # Examples of unclear vs clear language in Portuguese:

# unclear: "Dirija-se à repartição competente munido da documentação pertinente para protocolar sua solicitação"
# clear: "Vá à delegacia (Rua X, número Y) com RG, CPF e comprovante de residência"

# unclear: "A emissão da certidão está condicionada à quitação dos débitos tributários"
# clear: "Para pegar a certidão, você precisa primeiro pagar todos os impostos em atraso"

# unclear: "O requerente deve observar os prazos regimentais"
# clear: "Você tem 30 dias para entregar os documentos"

# unclear: "Proceda ao agendamento através dos canais oficiais"
# clear: "Marque seu atendimento pelo site www.exemplo.com"

# [BEGIN DATA]
# Query: {query}
# Model Response: {model_response}
# [END DATA]

# Please analyze the data carefully and then provide:

# explanation: Your reasoning step by step, focusing on clarity, simplicity, and practical guidance for citizens.
# label: "clear" or "unclear"
# """

# GOLDEN_EQUIPMENT_PROMPT = """
# Você é um especialista na avaliação de sistemas automatizados de chatbot. Sua tarefa atual é a seguinte: dado um histórico de conversas entre um chatbot e um cidadão, você deve avaliar três critérios:

#    - Para o primeiro critério, denominado ferramentas_corretas, você deve identificar se o chatbot chamou as ferramentas corretas para a situação. Para cada avaliação, será fornecida a lista de ferramentas corretas para aquela situação.
# A nota de ferramentas_corretas o número de ferramentas chamadas corretamente (dentro da lista de ferramentas corretas) dividido pelo tamanho da lista de ferramentas corretas mais o número de ferramentas chamadas incorretamente (fora da lista de ferramentas corretas). Cada ferramenta conta no máximo uma vez para o número de acertos ou erros, independentemente do número de repetições.” Use truncamento (floor) para duas casas decimais para arredondar as notas, p.ex. 0.678 → 0.67.
# Em casos em que não há ferramentas_corretas, ou seja, ferramentas_corretas=(), a resposta correta é não chamar nenhuma ferramente. Nesse caso, a nota é 1 se o agente não chamar nenhuma ferramente e 0 se ele chamar.
# A lista de ferramentas_chamadas pelo chatbot será fornecido para a avaliação.

# Por exemplo, se a lista de ferramentas corretas é (CF, CMS, CSE) e o chatbot chamou apenas (CF) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.33 (1 divido por (3+0)).
# Se a lista de ferramentas corretas é (CF, CMS, CSE, Super Centro Carioca de Vacinação) e o chatbot chamou apenas (CF, CMS, CSE) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.75 (3 dividido por (4+0)).
# Se a lista de ferramentas corretas é (CF, CMS, CSE) e o chatbot chamou (CF, CMS, CSE, Super Centro Carioca de Vacinação) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.75 (3 dividido por (3+1)).
# Se a lista de ferramentas corretas é (UPA, CER) e o chatbot chamou (CAPS, UPA, CER) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.66 (2 dividido por (2+1)).
# Se a lista de ferramentas corretas é () e o chatbot chamou (CAPS) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0 (correto seria não chamar nenhuma ferramenta).


#    - Para o segundo critério, denominado equipamento_correto, você deve identificar se o chatbot identificou corretamente o equipamento a ser referenciado ao cidadão. Você receberá uma referência da única resposta correta.
# A nota de equipamento_correto é binária, apenas 0 ou 1. Caso o chatbot não retorne nenhum equipamento, a nota de equipamento_correto é sempre 0. No geral, seja leniente com a formatação do nome do equipamento, desde que fique claro e não confundível com outros equipamentos similares.
# Em casos em que não há equipamento_correto, ou seja, equipamento_correto=””, a resposta correta é não enviar o cidadão a nenhum equipamento, e sim fazer de acordo com o informado na extra_info. Nesse caso, a nota é 1 se o agente seguir o dito na extra_info e 0 se ele não seguir.

# Por exemplo, se o equipamento_correto é “CAPS III Franco Basaglia Endereço: Avenida Venceslau Brás, 65, fundos - Botafogo.” e o chatbot retorna “SMS CMS JOAO BARROS BARRETO - AP 21 - Endereço: RUA TENREIRO ARANHA S/N”, sua nota de equipamento_correto é 0. Se ele não retorna nenhum equipamento ao longo de todos os turnos da conversa, sua nota também é 0.
# Se o equipamento_correto é “Super Centro Carioca de Vacinação (SCCV)
# Rua General Severiano, 91.” e o chatbot fala ao cidadão para ir ao “Super Centro Carioca de Vacinação”, sua nota de equipamento_correto é 1. Apesar de não ter dado a resposta absolutamente completa, o cidadão conseguirá achar o local facilmente ou poderá perguntar o local exato ao chatbot.
# Agora, se o equipamento_correto é “Hospital Municipal Jesus - Rua Teodoro da Silva, 512 - Vila Isabel/RJ” e o chatbot fala ao cidadão que este deve ir ao “Hospital Municipal”, sem especificar qual, sua nota de equipamento_correto é 0.
# Se o equipamento_correto é “”, ou seja, não há equipamento_correto, e o extra_info é “Ligue 192: SAMU. Serviço de atendimento de urgência em ambulância, que funciona 24 horas.”, e o chatbot não orienta o cidadão a ligar ao SAMU (192), sua nota é 0. Caso ele oriente a chamar o SAMU, sua nota é 1.


#    - Para o terceiro critério, denominado rapidez_de_resposta, você deve identificar em que turno o chatbot conseguiu dizer ao cidadão o equipamento correto para ele ser atendido. A nota é o turno em que ele primeiro chamou a ferramenta correta.
# Para o critério rapidez_de_resposta, considere 'turno' como a contagem sequencial das respostas do chatbot. A primeira resposta do chatbot é o turno 1, a segunda é o turno 2, e assim por diante.


# Em casos em que não há ferramentas_corretas nem equipamento_correto, a o critério rapidez_de_resposta é o primeiro turno no qual o chatbot conseguiu cumprir o orientado no extra_info.

# Considere os seguintes exemplos:

# <exemplo_1>
# ferramentas_corretas=(CF, CMS, CSE)
# equipamento_correto=SMS CMS JOAO BARROS BARRETO - AP 21 Endereço: RUA TENREIRO ARANHA S/N

# Cidadão: Tô gripado, onde posso ir aqui em copacabana?
# Chatbot: Boa tarde! Para que possa lhe ajudar, você poderia fornecer seu endereço exato?
# Cidadão: Eu moro na Barata Ribeiro
# Chatbot: Qual o número do seu prédio/casa?
# Cidadão: 370
# Chatbot: Você pode ir ao CMS João Barros Barreto, na rua Tenreiro Aranha
# </exemplo_1>


# No exemplo 1, a nota de rapidez_de_resposta deve ser “3”, pois o chatbot identificou o equipamento_correto no terceiro turno.


# <exemplo_2>
# ferramentas_corretas=(UPA, CER)
# equipamento_correto=UPA Tijuca Rua Conde de Bonfim, s/nº, Tijuca, Rio de Janeiro – RJ, bem

# Cidadão: meu filho ta com febre há dias, onde levo?
# Chatbot: Boa tarde! Para que possa lhe ajudar, você poderia fornecer seu endereço exato?
# Cidadão: Eu moro na Conde de Bonfim, 700
# Chatbot: Você pode ir à UPA da Tijuca, na própria Conde de Bonfim
# </exemplo_2>


# No exemplo 2, a nota de rapidez_de_resposta deve ser “2”, pois o chatbot identificou o equipamento_correto no segundo turno.


# <exemplo_3>
# ferramentas_corretas=(Hospital)
# equipamento_correto=UPA Sepetiba Endereço: Rua José Fernandes, s/nº – Alagados – Sepetiba.

# Cidadão: dor de cabeça muito forte começou agora, pra onde vou?
# Chatbot: Boa tarde! Para que possa lhe ajudar, você poderia fornecer seu endereço exato?
# Cidadão: Eu moro na rua Seabra Filho, 200
# Chatbot: Você pode ir à UPA da Tijuca, na própria Conde de Bonfim
# </exemplo_3>


# No exemplo 3, o chatbot errou completamente a resposta, e não achou o equipamento correto. Nesses casos de erro, a nota de rapidez_de_resposta deve ser “0”. O nosso sistema de notas automaticamente detectará respostas iguais a 0 e as desconsiderará do cálculo de rapidez média. Retorne sempre 0 em caso de erro.


# <exemplo_4>
# ferramentas_corretas=()
# equipamento_correto=
# extra_info = Para consultar suas consultas agendadas no SISREG, acessar aplicativo MinhaSaude.Rio

# Cidadão: como vejo meu exame q marquei no sisreg?
# Chatbot: Boa tarde! Para consultas agendadas no SISREG, acesse o app MinhaSaude.Rio
# </exemplo_4>


# No exemplo 4, a nota de rapidez_de_resposta deve ser “1”, pois o chatbot forneceu a extra_info já no primeiro turno e não há ferramentas_corretas nem equipamento_correto.


# Exemplos de saída esperada:
# 1.
# ferramentas_corretas: 0.75
# equipamento_correto: 1
# rapidez_de_resposta: 3


# 2.
# ferramentas_corretas: 0.33
# equipamento_correto: 0
# rapidez_de_resposta: 2
# """
