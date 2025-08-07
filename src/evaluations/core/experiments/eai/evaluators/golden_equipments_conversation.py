# -*- coding: utf-8 -*-
from typing import List
from src.evaluations.core.eval import (
    EvaluationTask,
    BaseConversationEvaluator,
)


class GoldenEquipmenConversation(BaseConversationEvaluator):
    """
    Avalia a ativação correta de ferramentas, identificação do equipamento correto e rapidez de resposta
    com base na transcrição completa da conversa.
    """

    name = "golden_equipment"

    PROMPT_TEMPLATE = """
Você é um especialista na avaliação de sistemas automatizados de chatbot. Sua tarefa é analisar uma conversa completa entre um chatbot e um usuário e atribuir notaas para três critérios:


**Objetivo da Tarefa:**
{agent_response[prompt]}
**Histórico da Conversa até agora:**
{history}

**Informações de Referência para Avaliação:**
- equipamento_correto: {task[golden_equipment]}
- ferramentas_corretas: {task[golden_equipment_type]}
- extra_info (se aplicável): {task[extra_info]}

**Critérios de Avaliação:**

1. **ferramentas_corretas**
Avalie se o chatbot ativou corretamente as ferramentas apropriadas durante a conversa. 
Para cada avaliação, será fornecida a lista de ferramentas corretas para aquela situação.
A nota é calculada da seguinte forma:
O número de ferramentas corretas chamadas dividido pelo tamanho da lista de ferramentas corretas mais o número de ferramentas chamadas incorretamente. 
Cada ferramenta conta no máximo uma vez para o número de acertos ou erros, independentemente do número de repetições.
Arredonde para duas casas decimais, p.ex. 0.678 → 0.67.
Em casos em que não há ferramentas_corretas, ou seja, ferramentas_corretas=(), a resposta correta é não chamar nenhuma ferramenta. Nesse caso, a nota é 1 se o agente não chamar nenhuma ferramenta e 0 caso contrário.

Por exemplo, se a lista de ferramentas corretas é (CF, CMS, CSE) e o chatbot chamou apenas (CF) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.33 (1 divido por (3+0)).
Se a lista de ferramentas corretas é (CF, CMS, CSE, Super Centro Carioca de Vacinação) e o chatbot chamou apenas (CF, CMS, CSE) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.75 (3 dividido por (4+0)).
Se a lista de ferramentas corretas é (CF, CMS, CSE) e o chatbot chamou (CF, CMS, CSE, Super Centro Carioca de Vacinação) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.75 (3 dividido por (3+1)).
Se a lista de ferramentas corretas é (UPA, CER) e o chatbot chamou (CAPS, UPA, CER) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0.66 (2 dividido por (2+1)).
Se a lista de ferramentas corretas é () e o chatbot chamou (CAPS) ao longo de todos os turnos da conversa, sua nota de ferramentas_corretas é 0 (correto seria não chamar nenhuma ferramenta).

2. **equipamento_correto**
Verifique se o agente identificou corretamente o equipamento que deve atender o cidadão.
Você receberá uma referência da única resposta correta.
A nota de equipamento_correto é binária, apenas 0 ou 1:
- 1 se o equipamento informado estiver correto (mesmo que não perfeitamente formatado).
- 0 se estiver incorreto, vago ou ausente.
Em casos em que não há equipamento_correto, ou seja, equipamento_correto="", a resposta correta é não enviar o cidadão a nenhum equipamento, e sim fazer de acordo com o informado na extra_info.
Nesse caso, a nota é 1 somente se o agente seguir corretamente as instruções contidas em `extra_info` e 0 caso contrário.

Por exemplo, se o equipamento_correto é “CAPS III Franco Basaglia Endereço: Avenida Venceslau Brás, 65, fundos - Botafogo.” e o chatbot retorna “SMS CMS JOAO BARROS BARRETO - AP 21 - Endereço: RUA TENREIRO ARANHA S/N”, sua nota de equipamento_correto é 0. Se ele não retorna nenhum equipamento ao longo de todos os turnos da conversa, sua nota também é 0.
Se o equipamento_correto é “Super Centro Carioca de Vacinação (SCCV)
Rua General Severiano, 91.” e o chatbot fala ao cidadão para ir ao “Super Centro Carioca de Vacinação”, sua nota de equipamento_correto é 1. Apesar de não ter dado a resposta absolutamente completa, o cidadão conseguirá achar o local facilmente ou poderá perguntar o local exato ao chatbot.
Agora, se o equipamento_correto é “Hospital Municipal Jesus - Rua Teodoro da Silva, 512 - Vila Isabel/RJ” e o chatbot fala ao cidadão que este deve ir ao “Hospital Municipal”, sem especificar qual, sua nota de equipamento_correto é 0.
Se o equipamento_correto é “”, ou seja, não há equipamento_correto, e o extra_info é “Ligue 192: SAMU. Serviço de atendimento de urgência em ambulância, que funciona 24 horas.”, e o chatbot não orienta o cidadão a ligar ao SAMU (192), sua nota é 0. Caso ele oriente a chamar o SAMU, sua nota é 1.

3. **rapidez_de_resposta**
Indique em que turno o equipamento correto foi mencionado pela primeira vez.
O primeiro turno do agente é considerado o turno 1, o segundo turno é o turno 2, e assim por diante.
Caso o equipamento correto não seja mencionado, retorne 0.
Em casos em que não há `ferramentas_corretas` nem `equipamento_correto`, a nota de `rapidez_de_resposta` é o primeiro turno em que o chatbot conseguiu cumprir corretamente o que está contido em `extra_info`.

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

**Formato da Resposta (exatamente 3 linhas, sem texto extra):**
ferramentas_corretas: <nota float com 2 casas decimais>
equipamento_correto: <0 ou 1>
rapidez_de_resposta: <número inteiro>

Exemplos de resposta esperada:
ferramentas_corretas: 0.75
equipamento_correto: 1
rapidez_de_resposta: 3
"""

    def get_judge_prompt(self, task: EvaluationTask, history: List[str]) -> str:
        """
        Implementa a lógica para formatar o prompt que guia o juiz
        com base no roteiro.
        """

        history_str = "\n".join(history)
        task_dict = task.model_dump(exclude_none=True)

        return self.PROMPT_TEMPLATE.format(
            task=task_dict,
            history=history_str,
            stop_signal=self.stop_signal,
        )
