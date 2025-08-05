# -*- coding: utf-8 -*-
from src.evaluations.core.eval import (
    EvaluationTask,
    EvaluationResult,
    MultiTurnEvaluationInput,
    BaseMultipleTurnEvaluator,
)


class GoldenEquipmentEvaluator(BaseMultipleTurnEvaluator):
    """
    Avalia o raciocínio do agente com base na transcrição completa de uma conversa.
    """

    name = "golden_equipment"

    GOLDEN_EQUIPMENT_PROMPT = """
Você é um especialista na avaliação de sistemas automatizados de chatbot. Sua tarefa atual é a seguinte: dado um histórico de conversas entre um chatbot e um cidadão, você deve avaliar três critérios:

   - Para o primeiro critério, denominado ferramentas_corretas, você deve identificar se o chatbot chamou as ferramentas corretas para a situação. Para cada avaliação, será fornecida a lista de ferramentas corretas para aquela situação.
A nota de ferramentas_corretas o número de ferramentas chamadas corretamente (dentro da lista de ferramentas corretas) dividido pelo tamanho da lista de ferramentas corretas mais o número de ferramentas chamadas incorretamente (fora da lista de ferramentas corretas). Cada ferramenta conta no máximo uma vez para o número de acertos ou erros, independentemente do número de repetições.” Use truncamento (floor) para duas casas decimais para arredondar as notas, p.ex. 0.678 → 0.67.
Em casos em que não há ferramentas_corretas, ou seja, ferramentas_corretas=(), a resposta correta é não chamar nenhuma ferramente. Nesse caso, a nota é 1 se o agente não chamar nenhuma ferramente e 0 se ele chamar.
A lista de ferramentas_chamadas pelo chatbot será fornecido para a avaliação.

Por exemplo, se a lista de ferramentas corretas é (CF, CMS, CSE) e o chatbot chamou apenas (CF) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.33 (1 divido por (3+0)).
Se a lista de ferramentas corretas é (CF, CMS, CSE, Super Centro Carioca de Vacinação) e o chatbot chamou apenas (CF, CMS, CSE) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.75 (3 dividido por (4+0)).
Se a lista de ferramentas corretas é (CF, CMS, CSE) e o chatbot chamou (CF, CMS, CSE, Super Centro Carioca de Vacinação) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.75 (3 dividido por (3+1)).
Se a lista de ferramentas corretas é (UPA, CER) e o chatbot chamou (CAPS, UPA, CER) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.66 (2 dividido por (2+1)).
Se a lista de ferramentas corretas é () e o chatbot chamou (CAPS) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0 (correto seria não chamar nenhuma ferramenta).


   - Para o segundo critério, denominado equipamento_correto, você deve identificar se o chatbot identificou corretamente o equipamento a ser referenciado ao cidadão. Você receberá uma referência da única resposta correta.
A nota de equipamento_correto é binária, apenas 0 ou 1. Caso o chatbot não retorne nenhum equipamento, a nota de equipamento_correto é sempre 0. No geral, seja leniente com a formatação do nome do equipamento, desde que fique claro e não confundível com outros equipamentos similares.
Em casos em que não há equipamento_correto, ou seja, equipamento_correto=””, a resposta correta é não enviar o cidadão a nenhum equipamento, e sim fazer de acordo com o informado na extra_info. Nesse caso, a nota é 1 se o agente seguir o dito na extra_info e 0 se ele não seguir.

Por exemplo, se o equipamento_correto é “CAPS III Franco Basaglia Endereço: Avenida Venceslau Brás, 65, fundos - Botafogo.” e o chatbot retorna “SMS CMS JOAO BARROS BARRETO - AP 21 - Endereço: RUA TENREIRO ARANHA S/N”, sua nota de equipamento_correto é 0. Se ele não retorna nenhum equipamento ao longo de todos os turnos da conversa, sua nota também é 0.
Se o equipamento_correto é “Super Centro Carioca de Vacinação (SCCV)
Rua General Severiano, 91.” e o chatbot fala ao cidadão para ir ao “Super Centro Carioca de Vacinação”, sua nota de equipamento_correto é 1. Apesar de não ter dado a resposta absolutamente completa, o cidadão conseguirá achar o local facilmente ou poderá perguntar o local exato ao chatbot.
Agora, se o equipamento_correto é “Hospital Municipal Jesus - Rua Teodoro da Silva, 512 - Vila Isabel/RJ” e o chatbot fala ao cidadão que este deve ir ao “Hospital Municipal”, sem especificar qual, sua nota de equipamento_correto é 0.
Se o equipamento_correto é “”, ou seja, não há equipamento_correto, e o extra_info é “Ligue 192: SAMU. Serviço de atendimento de urgência em ambulância, que funciona 24 horas.”, e o chatbot não orienta o cidadão a ligar ao SAMU (192), sua nota é 0. Caso ele oriente a chamar o SAMU, sua nota é 1.


   - Para o terceiro critério, denominado rapidez_de_resposta, você deve identificar em que turno o chatbot conseguiu dizer ao cidadão o equipamento correto para ele ser atendido. A nota é o turno em que ele primeiro chamou a ferramenta correta.
Para o critério rapidez_de_resposta, considere 'turno' como a contagem sequencial das respostas do chatbot. A primeira resposta do chatbot é o turno 1, a segunda é o turno 2, e assim por diante.


Em casos em que não há ferramentas_corretas nem equipamento_correto, a o critério rapidez_de_resposta é o primeiro turno no qual o chatbot conseguiu cumprir o orientado no extra_info.

Considere os seguintes exemplos:

<exemplo_1>
ferramentas_corretas=(CF, CMS, CSE)
equipamento_correto=SMS CMS JOAO BARROS BARRETO - AP 21 Endereço: RUA TENREIRO ARANHA S/N

Cidadão: Tô gripado, onde posso ir aqui em copacabana?
Chatbot: Boa tarde! Para que possa lhe ajudar, você poderia fornecer seu endereço exato?
Cidadão: Eu moro na Barata Ribeiro
Chatbot: Qual o número do seu prédio/casa?
Cidadão: 370
Chatbot: Você pode ir ao CMS João Barros Barreto, na rua Tenreiro Aranha
</exemplo_1>


No exemplo 1, a nota de rapidez_de_resposta deve ser “3”, pois o chatbot identificou o equipamento_correto no terceiro turno.


<exemplo_2>
ferramentas_corretas=(UPA, CER)
equipamento_correto=UPA Tijuca Rua Conde de Bonfim, s/nº, Tijuca, Rio de Janeiro – RJ, bem

Cidadão: meu filho ta com febre há dias, onde levo?
Chatbot: Boa tarde! Para que possa lhe ajudar, você poderia fornecer seu endereço exato?
Cidadão: Eu moro na Conde de Bonfim, 700
Chatbot: Você pode ir à UPA da Tijuca, na própria Conde de Bonfim
</exemplo_2>


No exemplo 2, a nota de rapidez_de_resposta deve ser “2”, pois o chatbot identificou o equipamento_correto no segundo turno.


<exemplo_3>
ferramentas_corretas=(Hospital)
equipamento_correto=UPA Sepetiba Endereço: Rua José Fernandes, s/nº – Alagados – Sepetiba.

Cidadão: dor de cabeça muito forte começou agora, pra onde vou?
Chatbot: Boa tarde! Para que possa lhe ajudar, você poderia fornecer seu endereço exato?
Cidadão: Eu moro na rua Seabra Filho, 200
Chatbot: Você pode ir à UPA da Tijuca, na própria Conde de Bonfim
</exemplo_3>


No exemplo 3, o chatbot errou completamente a resposta, e não achou o equipamento correto. Nesses casos de erro, a nota de rapidez_de_resposta deve ser “0”. O nosso sistema de notas automaticamente detectará respostas iguais a 0 e as desconsiderará do cálculo de rapidez média. Retorne sempre 0 em caso de erro.


<exemplo_4>
ferramentas_corretas=()
equipamento_correto=
extra_info = Para consultar suas consultas agendadas no SISREG, acessar aplicativo MinhaSaude.Rio

Cidadão: como vejo meu exame q marquei no sisreg?
Chatbot: Boa tarde! Para consultas agendadas no SISREG, acesse o app MinhaSaude.Rio
</exemplo_4>


No exemplo 4, a nota de rapidez_de_resposta deve ser “1”, pois o chatbot forneceu a extra_info já no primeiro turno e não há ferramentas_corretas nem equipamento_correto.


Exemplos de saída esperada:
1.
ferramentas_corretas: 0.75
equipamento_correto: 1
rapidez_de_resposta: 3


2.
ferramentas_corretas: 0.33
equipamento_correto: 0
rapidez_de_resposta: 2
"""

    async def evaluate(
        self, agent_response: MultiTurnEvaluationInput, task: EvaluationTask
    ) -> EvaluationResult:
        """
        Executa a avaliação de raciocínio conversacional usando o cliente juiz.
        """
        return await self._get_llm_judgement(
            prompt_template=self.GOLDEN_EQUIPMENT_PROMPT,
            task=task,
            agent_response=agent_response,
        )
