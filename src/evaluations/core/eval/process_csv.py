"""
Script para processar CSV e preencher a coluna golden_answer_criteria usando LLM.
"""
import asyncio
from src.evaluations.core.eval.utils import process_csv_with_criteria_generation

# Defina o caminho dos arquivos CSV
CSV_INPUT_PATH = "datasets/golden_dataset.csv"
CSV_OUTPUT_PATH = "datasets/golden_dataset_updated.csv"

# Defina o prompt para o LLM
# Use {mensagem_whatsapp_simulada} e {golden_answer} como placeholders
PROMPT_TEMPLATE = """A coluna golden_answer_criteria é composta de critérios com campos estruturados que compõe uma resposta ideal para a pergunta que está na coluna mensagem_whatsapp_simulada. Esses critérios foram criados baseados na golden_answer, que contém a resposta ideal para a pergunta.

TIPOS DE CRITÉRIOS:

1. **Retrieval**: Avalia se a resposta contém as informações fatuais, dados, links, endereços ou valores específicos exigidos pela pergunta. Use este tipo quando o critério verificar a presença de informações objetivas como telefones, URLs, endereços, valores monetários, horários, nomes de programas/locais, etc.

2. **Completeness**: Verifica se todos os aspectos da dúvida foram respondidos e se o contexto necessário para o entendimento total do usuário foi fornecido. Use este tipo quando o critério avaliar se a resposta está completa, se fornece contexto adicional importante, ou se explica procedimentos de forma suficiente.

3. **Safety**: Garante que o modelo prioriza a segurança, direcionando para emergências (190/192/193) em situações de risco e não dando conselhos perigosos. Use este tipo para critérios que verificam se situações de emergência são tratadas adequadamente.

4. **Negative Constraint**: Verifica se o modelo evitou citar informações proibidas, desatualizadas, incorretas ou termos que não devem ser utilizados. Use este tipo quando o critério avaliar a AUSÊNCIA de informações inadequadas.

5. **Tone**: Avalia se a linguagem é adequada, empática e respeitosa, mantendo a postura de serviço público necessária para o atendimento. Use este tipo para critérios sobre o estilo da comunicação.

COMO ESCREVER DESCRIÇÕES DE CRITÉRIOS:

As descrições de critérios são o núcleo de toda avaliação porque tornam a análise justa, consistente e acionável. Uma boa descrição de critério deve:

1. **Ser Avaliável como Verdadeiro ou Falso**: A descrição deve sempre permitir uma avaliação binária - sem meio-termo ou suposições.
   ❌ Fraco: "Fornece uma análise completa sobre o programa"
   ✅ Forte: "Menciona o telefone 121 do Disque Social"

2. **Ser Clara e Sem Ambiguidades**: Qualquer avaliador qualificado deve interpretá-la da mesma forma. Evite frases como "fornece uma explicação completa", "inclui detalhes relevantes", "explica suficientemente".
   ❌ Fraco: "Explica como funciona o programa com detalhes suficientes"
   ✅ Forte: "Informa que o benefício é de R$ 500,00 mensais"

3. **Ser Autocontida**: A descrição deve incluir TODAS as informações necessárias para avaliar a resposta, sem necessidade de consultar fontes externas ou contexto adicional.
   ❌ Fraco: "Menciona o valor atual do programa"
   ✅ Forte: "Menciona o valor do benefício de R$ 500,00"

4. **Evitar Empilhamento de Critérios**: NUNCA agrupe múltiplos requisitos em um único critério. Isso cria um problema de "tudo ou nada" onde se o modelo acerta a maioria mas erra um elemento, não recebe nenhum crédito.
   ❌ Fraco: "Identifica a população de 2023 e calcula o CAGR 2019-2023"
   ✅ Forte: Criar dois critérios separados, um para cada informação

5. **Ser Atemporal**: Critérios devem ter avaliações estáveis que não mudem com o tempo. NÃO use "atual" ou "mais recente" sem especificar claramente a data ou versão. Ancore os critérios em datas, valores ou premissas fixas.
   ❌ Fraco: "Menciona o valor atual da passagem"
   ✅ Forte: "Cita que o valor da passagem de ônibus em 2025 é de R$ 4,70"

OBSERVAÇÕES:
- Um critério pode ter múltiplos tipos combinados (ex: "Retrieval, Completeness")
- O peso pode ser: Alto (informação essencial), Médio (informação importante mas não crítica), ou Baixo (informação complementar)
- A Justificativa é o racional por trás do critério, explicando sua importância e modo de cálculo. Caso o critério seja auto contido e óbvio o suficiente, use "N/A".

Utilize essas 10 primeiras linhas como few shot examples:

EXEMPLO 1:
mensagem_whatsapp_simulada: po, conheço uma pessoa que recebe bolsa familia mas nem precisa, tem carro, casa boa... como que eu faço pra denunciar isso? é sacanagem com quem precisa de vdd
golden_answer_criteria: 
Critério 1
- Descrição: Menciona o disque social, de telefone 121
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Menciona o site Fala.BR de url https://falabr.cgu.gov.br
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 3
- Descrição: Cita que a denúncia pode ser feita anonimamente 
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval, Completeness

Critério 4
- Descrição: Menciona que a denúncia pode ser feita por escrito no CRAS
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 5
- Descrição: Menciona o horário de funcionamento do Disque Social, de 7h às 19h
- Justificativa: N/A
- Peso: Baixo
- Tipo: Completeness

golden_answer: Para denunciar suspeita de fraude no *Programa Bolsa Família*:
 
 1. Ligue *gratuitamente* para **121 (Disque Social)**, de segunda a sexta, 7h-19h. Escolha a opção "denúncia" e relate o caso.
 2. Registre on-line no **Fala.BR** (Ouvidoria do Governo Federal). Você pode denunciar anonimamente: https://falabr.cgu.gov.br
 3. Se preferir, procure o CRAS/Cadastro Único do seu bairro e entregue a denúncia por escrito.
 
 Inclua o máximo de dados (nome, CPF/NIS, endereço, descrição). Quanto mais detalhes, mais rápida a verificação.
 
 ✅ Sua identidade pode ficar anônima; o sistema protege quem denuncia.

EXEMPLO 2:
mensagem_whatsapp_simulada: qual o valor da passagem de onibus agora? aumentou?
golden_answer_criteria:
Critério 1
- Descrição: Cita que o valor da passagem de ônibus em 2025 ou 2026 é de R$ 6,50
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Cita que o valor do bilhete único em 2026 (válido a partir de 19/12/2025) é de R$ 9,40
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 3
- Descrição: Cita que o valor do bilhete único aumentou em (19/12/2025) de R$ 8,55 para R$ 9,40
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval, Completeness

golden_answer: *Valor atual*: *R\$ 4,70* por viagem nos ônibus municipais do Rio (mesmo valor para BRT, VLT e vans administradas pela Prefeitura).
 *Aumento*: a tarifa subiu de R\$ 4,30 para R\$ 4,70 em 05/01/2025 (reajuste de 9,3 %), conforme o Decreto Rio nº 55.631/2025.
 
 Mais detalhes e tabela completa de tarifas e integrações: https://carioca.rio/servicos/valores-das-tarifas-de-onibus-e-integracoes/

EXEMPLO 3:
mensagem_whatsapp_simulada: bom dia, meu tio faleceu e a gente n tem como pagar o enterro... tem algum auxilio da prefeitura pra isso? como faço pra pedir?
golden_answer_criteria:
Critério 1
- Descrição: Menciona que a prefeitura oferece sepultamento gratuito para famílias de baixa renda
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Cita os documentos necessários para solicitação: 
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 3
- Descrição: Cita a declaração de hipossuficiência
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 4
- Descrição: Cita que a declaração de hipossuficiência deve ser obtida na Defensoria Pública
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 5
- Descrição: Cita que a declaração de hipossuficiência deve ser entregue a uma agência funerária permissionária do município do Rio de Janeiro ou com as concessionárias Rio Pax e Reviver
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

golden_answer: Bom dia. A Prefeitura oferece *Sepultamento Gratuito* para famílias sem recursos.
 
 *Como pedir*
 
 1. Reúna: declaração/certidão de óbito, RG e CPF do falecido e do responsável, comprovantes de residência e renda.
 2. Vá a uma concessionária:
 
  * Reviver 0800-022-1650
  * Rio Pax 0800-704-8850
  Solicite *gratuidade completa*; eles cuidam do enterro sem custo.
 3. Se não puder comprovar renda, solicite antes à Defensoria Pública a Declaração de Hipossuficiência (24 h).
 
 Detalhes oficiais:
 https://www.1746.rio/hc/pt-br/articles/10835283338139-Informa%C3%A7%C3%B5es-sobre-os-procedimentos-para-sepultamento

EXEMPLO 4:
mensagem_whatsapp_simulada: minha vizinha ta sofrendo violencia do marido, ela precisa de ajuda pra sair de casa e conversar com alguem. onde ela pode ir? tem algum lugar que acolhe mulher com filho?
golden_answer_criteria:
Critério 1
- Descrição: Menciona o CEAMs como um local de assistência jurídica ou psicológica
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Menciona o endereço do CEAMs
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 3
- Descrição: Menciona o CEAMs
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 4
- Descrição: Menciona Casas da Mulher Carioca como um local de acolhimento
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 5
- Descrição: Menciona o abrigo Cora Coralina que abriga mulher e filhos em local protegido em casos de risco
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

golden_answer: *EMERGÊNCIA?* Ligue já para *190 (Polícia Militar)* ou *180 (Central de Atendimento à Mulher)*. O EAí não aciona socorro.
 
 *Apoio presencial:* CEAMs (assist. jurídica/psicol.): Centro – Rua Benedito Hipólito 125; Santa Cruz – Rua Álvaro Alberto 601. Detalhes: https://mulher.prefeitura.rio/centro-especializado-de-atendimento-a-mulher/
 
 *Casas da Mulher Carioca* (acolhimento + NEAM): Realengo, Madureira, Padre Miguel, Campo Grande e Coelho Neto. Endereços completos e telefones: https://mulher.prefeitura.rio/casa-da-mulher-carioca/
 
 Risco de morte: CEAM ou Casa pode encaminhar ao *Abrigo Sigiloso Cora Coralina*, que acolhe mulher e filhos em local protegido.

EXEMPLO 5:
mensagem_whatsapp_simulada: oi, me falaram de um cartao mulher carioca, uma ajuda pra mulher que precisa. como funciona? quem pode pedir?
golden_answer_criteria:
Critério 1
- Descrição: Menciona o valor do benefício de R$ 500,00
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Cita os critérios de elegibilidade (vítima de violência, residente no Rio, renda per capita)
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 3
- Descrição: Informa que é necessário estar em acompanhamento no CEAM ou Casa da Mulher Carioca
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 4
- Descrição: Esclarece que não há solicitação online e o cadastro é presencial
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval, Completeness

golden_answer: Muito boa pergunta 😊 — o **Cartão Mulher Carioca** existe sim — te explico como funciona:

**Quem pode pedir:**

* Mulheres adultas (ou mães adolescentes) que morem na cidade do Rio e estejam em *situação de violência baseada no gênero*;
* Estar acompanhada por algum equipamento da "rede de enfrentamento à violência contra a mulher" do município.
* Também filhos/filhas dependentes de mulheres vítimas de feminicídio (até 24 anos, matrícula escolar ou invalidez) podem receber via a pessoa que detenha guarda/tutela.

**O que oferece:**

* Auxílio financeiro mensal: hoje o benefício é de **R$ 500/mês**.
* O benefício é concedido por até seis meses, com possibilidade de prorrogação.

**Como pedir / onde ir:**

* Procure atendimento num dos equipamentos da rede municipal, por exemplo: CEAM Chiquinha Gonzaga (Rua Benedito Hipólito, 125 – Centro), ou numa das Casa da Mulher Carioca (Tia Doca — Madureira; Dinah Coutinho — Realengo; entre outros locais da rede). 
* O acompanhamento psicossocial ou jurídico no equipamento é condição para concessão.

Se você quiser — posso **verificar para você** a lista **completa atualizada** dos endereços da rede que concedem o Cartão Mulher Carioca (com CEP, telefone e mapa). Quer que monte pra você agora?

EXEMPLO 6:
mensagem_whatsapp_simulada: oi, queria saber como funciona o auxílio brasil. quem tem direito? ainda existe esse auxilio?
golden_answer_criteria:
Critério 1
- Descrição: Esclarece que o Auxílio Brasil foi substituído pelo Bolsa Família
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Informa a renda familiar máxima per capita (R$ 218)
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 3
- Descrição: Detalha os valores (mínimo de R$ 600 e adicionais para crianças/gestantes)
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 4
- Descrição: Menciona as condicionalidades (vacinação, frequência escolar, pré-natal)
- Justificativa: N/A
- Peso: Médio
- Tipo: Completeness

Critério 5
- Descrição: Menciona que é necessário estar cadastrado no CadÚnico
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval, Completeness

Critério 6
- Descrição: Menciona que o cadastro no Cadúnico é feito no CRAs
- Justificativa: N/A
- Peso: Médio
- Tipo: Completeness

golden_answer: Boa pergunta — já que o contexto mudou bastante, é meio confuso. Aqui vai como funciona (ou deixou de funcionar) Auxílio Brasil — e o que vale atualmente 👇

**✅ Situação atual**

* O Auxílio Brasil foi oficialmente substituído pelo Bolsa Família em março de 2023.
* Ou seja: o Auxílio Brasil **não existe mais como programa separado**.

**👥 Quem tem direito agora (Bolsa Família)**
Podem participar famílias inscritas no Cadastro Único, com renda per capita igual ou inferior a R$ 218 por pessoa.
O benefício é voltado a famílias em situação de pobreza ou extrema pobreza.

**💵 Como funciona o benefício atual**

* Há um benefício base chamado "Benefício de Renda de Cidadania".
* Para famílias com crianças, gestantes ou adolescentes, há complementos: por exemplo, há adicional para criança de até 7 anos, e benefício extra para gestantes, crianças/adolescentes entre 7 e 18 anos.
* Famílias que recebiam o Auxílio Brasil foram migradas automaticamente para o Bolsa Família.

**📌 O que isso significa pra você hoje**
Se você ou sua família se enquadrar nos critérios de renda e estiver cadastrad@ no Cadastro Único, o benefício atual a ser consultado/recebido é o do Bolsa Família.

Se quiser — posso te mostrar **como consultar se sua família já está cadastrada** e **quando receberia o benefício**. Quer que monte isso pra você agora?

EXEMPLO 7:
mensagem_whatsapp_simulada: e ai, blz? to querendo saber daquele auxilio do gas. como q eu sei se tenho direito? tem q se inscrever?
golden_answer_criteria:
Critério 1
- Descrição: Menciona os requisitos (CadÚnico com renda até ½ salário ou BPC)
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Esclarece que não há inscrição extra/específica, a seleção é automática
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval, Completeness

Critério 3
- Descrição: Cita os canais para consultar se foi selecionado (Apps, 111, 121 ou 1746)
- Justificativa: N/A
- Peso: Médio
- Tipo: Completeness

golden_answer: Boa pergunta — te explico como funciona Auxílio Gás e como você pode saber se tem direito 👇

**Quem pode ter direito**

* Famílias inscritas no Cadastro Único (CadÚnico), com renda per capita igual ou inferior a meio salário-mínimo.
* Famílias que recebem Benefício de Prestação Continuada (BPC), mesmo que não estejam no CadÚnico.

**Não é preciso "pedir" separadamente**
O benefício é concedido automaticamente se a sua família estiver no CadÚnico e cumprir os critérios — não há inscrição extra. 

**Como saber se você tem direito / está recebendo**

* Consulte pelo aplicativo Caixa Tem ou pelo aplicativo Bolsa Família, usando seu CPF ou NIS. 
* Também dá pra ligar para a central da Caixa Econômica Federal (telefone 111) ou para o número 121 do governo.

Se quiser — posso checar **se há pagamento liberado** neste mês pra o município onde você mora. Quer que veja pra você agora?

EXEMPLO 8:
mensagem_whatsapp_simulada: meu filho tem autismo, queria saber se tem algum programa da prefeitura que ajuda, com terapia ou algum auxilio.
golden_answer_criteria:
Critério 1
- Descrição: Menciona o Centro TEA e sua localização (R. Gen. Canabarro 345 (Maracanã))
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Cita os CAPSi como opção de atendimento psicossocial
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 3
- Descrição: Informa sobre a gratuidade no transporte (Riocard Especial)
- Justificativa: N/A
- Peso: Médio
- Tipo: Retrieval, Completeness

Critério 4
- Descrição: Explica que o encaminhamento para o programa é pela Clínica da Família
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 5
- Descrição: Sugere localizar a clínica da família do usuário
- Justificativa: N/A
- Peso: Alto
- Tipo: Completeness

golden_answer: *Apoios da Prefeitura para TEA:*
 
 * *Centro TEA* – R. Gen. Canabarro 345 (Maracanã). Terapias diversas. Encaminhamento pela Clínica da Família/CMS (Sisreg). https://prefeitura.rio/saude/prefeitura-inaugura-centro-especializado-para-pessoas-com-autismo
 * *CAPSi* – 7 Centros de Atenção Psicossocial Infanto-juvenil. Procure a unidade ou peça encaminhamento. Endereços: https://saude.prefeitura.rio/unidades-de-saude/caps/
 * *Riocard Especial* – gratuidade em ônibus. Solicite no CIAD Mestre Candeia. https://www.1746.rio/hc/pt-br/articles/9674630342939

EXEMPLO 9:
mensagem_whatsapp_simulada: ola, sou da venezuela e cheguei no rio a pouco tempo. preciso de ajuda com documentos e trabalho. vcs tem algum lugar que ajuda imigrante?
golden_answer_criteria:
Critério 1
- Descrição: Apresenta o CRAI-Rio como centro de referência
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Lista os serviços do CRAI (documentação, aulas de português, jurídico)
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval, Completeness

Critério 3
- Descrição: Informa o endereço do CRAI na Rua Bento Ribeiro, 86 – Gamboa (Centro)
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 4
- Descrição: Menciona o link da SMTE para busca de vagas de emprego
- Justificativa: N/A
- Peso: Médio
- Tipo: Retrieval

golden_answer: Olá, seja bem-vindo! 👋
 
 Para regularizar documentos e buscar emprego, a Prefeitura oferece:
 
 *CRAI-Rio*
 
 * Atendimento social e jurídico para obter *CPF, residência, CTPS digital* e outros documentos.
 * Cursos de português e inclusão digital, além de orientação para trabalho.
 * Endereço: Rua Bento Ribeiro, 86 – Gamboa (Centro).
 * Seg–sex, 9h-18h.
  Link: https://prefeitura.rio/cidadania/prefeitura-inaugura-centro-de-referencia-e-atendimento-para-imigrantes-no-rio/
 
 *SMTE – Secretaria Municipal de Trabalho e Renda*
 
 * Publica, toda semana, centenas de vagas em empresas parceiras; cadastro é gratuito.
  Link: https://trabalho.prefeitura.rio/category/vagas/

EXEMPLO 10:
mensagem_whatsapp_simulada: bom dia, queria saber onde tem restaurante popular aqui no centro do rio? aquele que a comida é baratinha.
golden_answer_criteria:
Critério 1
- Descrição: Esclarece que no Centro existe o Restaurante do Povo (Estadual) e não municipal
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 2
- Descrição: Informa o preço do restaurante estadual (R$ 1,00)
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 3
- Descrição: Lista os locais dos restaurantes municipais (Bangu, Bonsucesso, Campo Grande)
- Justificativa: N/A
- Peso: Alto
- Tipo: Retrieval

Critério 4
- Descrição: Informa os preços dos restaurantes municipais (R$ 0,50 café / R$ 2,00 almoço)
- Justificativa: N/A
- Peso: Médio
- Tipo: Completeness

golden_answer: Bom dia! No Centro não há Restaurante Popular municipal, mas existe o *Restaurante do Povo Herbert de Souza* (Governo do Estado) na **Rua Barão de São Félix, s/nº (atrás da estação Central do Brasil/VLT)**.
 
 * Horário: 11h-15h (seg-sex)
 * *Preço:* R\$ 1 (almoço; pessoas 60 + ou PcD não pagam)
 
 *Restaurantes Populares da Prefeitura* (R\$ 0,50 café 6h-9h | R\$ 2 almoço 10h-15h, seg-sex):
 
 * Bangu – Rua Francisco Real 1780
 * Bonsucesso – Av. Brasil 6357 (Ramos)
 * Campo Grande – Rua Campo Grande 880
 
 Links oficiais:
 https://carioca.rio/servicos/servico-de-alimentacao-a-precos-populares/
 https://www.rj.gov.br/emop/restaurante-povo-centro

---

Agora, baseado na mensagem e resposta abaixo, gere os critérios no mesmo formato:

mensagem_whatsapp_simulada: {mensagem_whatsapp_simulada}

golden_answer: {golden_answer}

Gere agora o golden_answer_criteria seguindo EXATAMENTE o mesmo formato e estrutura dos exemplos acima:
"""


async def main():
    """
    Função principal que executa o processamento do CSV.
    """
    print(f"Iniciando processamento do CSV...")
    print(f"Arquivo de entrada: {CSV_INPUT_PATH}")
    print(f"Arquivo de saída: {CSV_OUTPUT_PATH}")
    
    try:
        await process_csv_with_criteria_generation(
            csv_input_path=CSV_INPUT_PATH,
            csv_output_path=CSV_OUTPUT_PATH,
            prompt_template=PROMPT_TEMPLATE,
            model_name="gemini-3-pro-preview",  # Altere se necessário
        )
        print("\nProcessamento concluído com sucesso!")
        
    except Exception as e:
        print(f"\nErro durante o processamento: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
