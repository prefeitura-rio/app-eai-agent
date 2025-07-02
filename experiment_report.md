
## Summary
| Parameter | Value |
|---|---|
| **Evaluation Model** | `gpt-4o` |
| **Final Response Model** | `google_ai/gemini-2.5-flash-lite-preview-06-17` |
| **Temperature** | `0.7` |
| **Tools Provided** | `['google_search']` |
----------------------------------------------------------------------------------------------------

## ID: 1
### User Message
po, conheço uma pessoa que recebe bolsa familia mas nem precisa, tem carro, casa boa... como que eu faço pra denunciar isso? é sacanagem com quem precisa de vdd

### Agent Answer
Entendo sua frustração com a possível irregularidade no recebimento do Bolsa Família. Para denunciar situações assim no Rio de Janeiro, você pode usar os seguintes canais:

*   **Central 1746:** Ligue para 1746 ou use o aplicativo "1746 Rio" e o WhatsApp. Este é o canal principal da Prefeitura do Rio.
*   **Central Anticorrupção da Prefeitura:** Para denúncias mais específicas de fraude ou atos ilícitos contra a administração municipal.

Ao fazer a denúncia, é importante fornecer o máximo de detalhes possível, como o nome completo da pessoa, o Número de Identificação Social (NIS) se tiver, a renda familiar aproximada e o endereço. Se não tiver o NIS, informe outros dados como CPF, data de nascimento ou nome da mãe.

Essas informações ajudam na apuração dos fatos pela prefeitura.

Fontes:
https://carioca.rio/servicos/informacoes-sobre-o-cadastro-unico/
https://www.1746.rio/hc/pt-br/p/ouvidoria
https://www.1746.rio/hc/pt-br/articles/10247652093723-Den%C3%BAncia-de-corrup%C3%A7%C3%A3o-e-ou-improbidade-administrativa

### Agent Reasoning
**Reasoning:**
The user is reporting a suspected fraud related to Bolsa Família, which is linked to the CadÚnico (Cadastro Único) registry. I will search for how to report CadÚnico irregularities to ensure I provide accurate information on reporting benefit misuse.

**Tool Call:** `google_search`
```json
{
  "query": "denúncia CadÚnico irregular",
  "request_heartbeat": true
}
```
**Tool Return:**
```json
{
  "text": "**Denúncias de Irregularidades no Cadastro Único (CadÚnico) no Rio de Janeiro**\n\nPara realizar uma denúncia sobre irregularidades no Cadastro Único (CadÚnico) no município do Rio de Janeiro, os cidadãos podem utilizar diversos canais, priorizando aqueles que garantem a apuração e o tratamento adequado da informação.\n\n**Canais de Denúncia:**\n\n*   **Central 1746:** O número 1746 é o principal canal de comunicação com a Prefeitura do Rio de Janeiro para solicitações, reclamações, sugestões e denúncias. O serviço está disponível para ligações locais e também pode ser acessado através do aplicativo \"1746 Rio\" e pelo WhatsApp. A Ouvidoria da Prefeitura, que [1] funciona como uma segunda instância de relacionamento entre o cidadão e o poder público, recebe reclamações sobre solicitações que não foram atendidas no prazo ou com a qualidade esperada, além de elogios, sugestões e críticas.\n*   **Central Anticorrupção da Prefeitura [2]:** Este canal é específico para o registro de denúncias de fraude, corrupção, práticas de crimes, violação de normas, leis ou qualquer outro ato ilícito praticado contra a Administração Pública Municipal do Rio de Janeiro ou por seus agentes públicos. O objetivo é promover a integridade e a transparência, [3] oferecendo um ambiente seguro para quem denuncia de boa-fé, permitindo o registro de denúncias de forma identificada ou anônima.\n*   **WhatsApp da Gestão do Cadastro Único:** Em algumas localidades [3], como mencionado em uma notícia de maio de 2025, a população é convidada a denunciar irregularidades no Bolsa Família diretamente pelo WhatsApp da Gestão do Cadastro Único, no número (37) 3329-1819. É importante verificar se este número é aplicável especificamente ao município [4] do Rio de Janeiro ou se refere a outra localidade.\n*   **Formulário Eletrônico Unificado:** Para registrar denúncias, é necessário fornecer uma descrição detalhada da irregularidade. Caso o Número de Identificação Social (NIS) dos denunciados não esteja disponível, é preciso informar o nome completo e, adicionalmente, o CPF, data de nascimento, nome da mãe ou do pai, ou número do Título de Eleitor/Carteira de Trabalho do responsável familiar. O formulário permite selecionar o assunto da denúncia, que pode incluir \"BOLSA FAMÍLIA\", \"CRAS [5]\", \"CREAS\", entre outros.\n\n**Informações Necessárias para a Denúncia:**\n\nAo realizar uma denúncia, é fundamental fornecer [5] o máximo de detalhes possível para auxiliar na apuração dos fatos. As informações geralmente solicitadas incluem:\n\n*   Descrição detalhada da irregularidade.\n*   Número de Identificação Social (NIS) dos denunciados, se disponível.\n*   Renda familiar aproximada dos denunciados [5].\n*   Nome completo dos denunciados e, na ausência do NIS, outras informações [5] de identificação do responsável familiar [5], como CPF, data de nascimento, nome da mãe, Título de Eleitor ou Carteira de Trabalho.\n*   No caso de denúncias relacionadas a CRAS ou CREAS, é necessário informar o nome do centro e sua localização (bairro, [5] município e estado).\n\n**O que pode ser denunciado:**\n\nO CadÚnico é um instrumento de identificação e caracterização socioeconômica das famílias brasileiras [5] de baixa renda. Irregularidades podem incluir situações em que o benefício está sendo recebido indevidamente, como por pessoas com renda incompatível com [1] os critérios do programa. A Central Anticorrupção da Prefeitura do Rio de Janeiro recebe denúncias sobre abuso de autoridade, assédio moral e sexual, conflito de interesses [4], desvio de função, fraude, irregularidades em contratos ou licitações, e nepotismo praticados por agentes públicos.\n\n**Ouvidoria do Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome:**\n\nO Ministério do Desenvolvimento e Assistência Social [3], Família e Combate à Fome também possui um canal de denúncias através de sua Ouvidoria. Este órgão recebe, examina e encaminha denúncias, reclamações, elogios e sugestões relacionadas às políticas, programas e ações do ministério, como o Programa Bolsa Família. O Disque Social 121 é outro canal para solicitação de informações e esclarecimento de dúvidas sobre as ações e programas do ministério. [6] [6]\n\n**Sources:**\n[1] [carioca.rio](https://carioca.rio/servicos/informacoes-sobre-o-cadastro-unico/)\n[2] [1746.rio](https://www.1746.rio/hc/pt-br/p/ouvidoria)\n[3] [1746.rio](https://www.1746.rio/hc/pt-br/articles/10247652093723-Den%C3%BAncia-de-corrup%C3%A7%C3%A3o-e-ou-improbidade-administrativa)\n[4] [opergaminho.com.br](https://www.opergaminho.com.br/cadunico-convida-populacao-a-denunciar-irregularidades-no-bolsa-familia)\n[5] [mds.gov.br](https://aplicacoes.mds.gov.br/form_ouvidoria/)\n[6] [www.gov.br](https://www.gov.br/mds/pt-br/canais_atendimento/ouvidoria)\n",
  "sources": [
    {
      "label": "carioca.rio",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwITYTfGffeFYPBZTzcVZPR6XlFtjrabvfM3YAzhb7WRQaquZa2Z84lL2-u-1uvCzcf0aYvIzxkdlh7Mknzv9kOTABOW_mwQALfuIzU8o0GJosgc0Go1JK-7urAF7tCU6Az6D0P2kL-8ekc1k02M3nliv-vXWAuI-O04U=",
      "url": "https://carioca.rio/servicos/informacoes-sobre-o-cadastro-unico/",
      "index": 1
    },
    {
      "label": "1746.rio",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5k8vlRvs6CsvwVGzSQw-Wzb4YfAt3fV4Xk5e_OqhY6LWm2WCvefyDrr1cg1hbYuVNuHfthQK8mCcjrSrPmZWN1_j_PM35vQesbasfGY6n7l0OOio9STcu",
      "url": "https://www.1746.rio/hc/pt-br",
      "index": 2
    },
    {
      "label": "1746.rio",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe2AJs1Ff10qi6JQWDr0SPBngvSb6twegPd9egzYfor1z-J1Cnl03sCJiIcEQiA3j-ZvzFVlMwVxWLMV78S5apLyxRAcv_h1Wpc7WAn3Rf8xQYwMWf0_xKtHkHD3Db2L1RMIVg",
      "url": "https://www.1746.rio/hc/pt-br/p/ouvidoria",
      "index": 3
    },
    {
      "label": "1746.rio",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9Zz5Gwwh-Zrus6KFx6yYKK8ekwT2ibWWIqVUDefe65g-pyPtCcjsAiE5JrLkDCDhU-59TZvWSgSh0orxEHTmj_byBT5ge9hFDNMpNpkDwikB3uLfd_MeJrsuOBvP4CDUtY9bok5Z34w0451p3As9NYwGNUEAAkoIHdSW1HYMS4BRmi4FnYz-dlxp62xHWpJXsqJysbJrsNsH_HRD9HM3b-Tn01FZy4ZZxguHscts2S7n8uuLQ",
      "url": "https://www.1746.rio/hc/pt-br/articles/10247652093723-Den%C3%BAncia-de-corrup%C3%A7%C3%A3o-e-ou-improbidade-administrativa",
      "index": 4
    },
    {
      "label": "opergaminho.com.br",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFEAs1tzVSE1OhXQPmQd2vEerHNifX9OuNwiKEYCqYUDCHFKW0C3oSPq2U_h8V3Twn_00I_nFGu7SGSTj8OPoBV0aYKEZdp0TJgOSSagWNt3ha7zhWlxwNy1H_nBlWPNBZp4VNt8n2di6NRHrsDVAVZpQCFAl4a_syag1CrTBS8sjbeDf2ZfNcCPYX0n6o-Th1jw2M7AAT1ycTCmlSj1CuXw==",
      "url": "https://www.opergaminho.com.br/cadunico-convida-populacao-a-denunciar-irregularidades-no-bolsa-familia",
      "index": 5
    },
    {
      "label": "mds.gov.br",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUzgFmuS_iE9M70Gs-eNMIZ-WMPUdHwaIeuErwcpe0UlxOMmj8xIPfFAd5BB4u7gU-46oz9EbrRQ-9RGSPzwLe0WO9gTYYrs7beAj3WGj5oYXiycz-4SOQTazfDoJ34on0Ahv71SEVgw==",
      "url": "https://aplicacoes.mds.gov.br/form_ouvidoria/",
      "index": 6
    },
    {
      "label": "www.gov.br",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpcwTPKymk4lJcxQzHms6kST3OBUOaA5vXRAK2zj9OIoVO63dzmeVUIHgTDWjfN8fiZAji2SRLn31DnSrBpu9k-O-OaAtJOlk6ieCEQtC1RLtyQv6cf12imAn3OCxXJ02HirRI1VC2gOJhis2AR4cnGlTd6w==",
      "url": "https://www.gov.br/mds/pt-br/canais_atendimento/ouvidoria",
      "index": 7
    }
  ],
  "web_search_queries": [
    "denúncia CadÚnico irregular Rio de Janeiro",
    "como denunciar irregularidades no CadÚnico prefeitura Rio de Janeiro",
    "canais de denúncia CadÚnico Rio de Janeiro"
  ]
}
```
**Reasoning:**
The user wants to report suspected fraud regarding Bolsa Família. I have searched for the appropriate channels in Rio de Janeiro. The search results provide information on using the 1746 service and the Central Anticorruption. I will now construct a response that clearly outlines these options and explains what information is needed for a report, referencing the official sources found.

**Assistant Message:**
Entendo sua frustração com a possível irregularidade no recebimento do Bolsa Família. Para denunciar situações assim no Rio de Janeiro, você pode usar os seguintes canais:

*   **Central 1746:** Ligue para 1746 ou use o aplicativo "1746 Rio" e o WhatsApp. Este é o canal principal da Prefeitura do Rio.
*   **Central Anticorrupção da Prefeitura:** Para denúncias mais específicas de fraude ou atos ilícitos contra a administração municipal.

Ao fazer a denúncia, é importante fornecer o máximo de detalhes possível, como o nome completo da pessoa, o Número de Identificação Social (NIS) se tiver, a renda familiar aproximada e o endereço. Se não tiver o NIS, informe outros dados como CPF, data de nascimento ou nome da mãe.

Essas informações ajudam na apuração dos fatos pela prefeitura.

Fontes:
https://carioca.rio/servicos/informacoes-sobre-o-cadastro-unico/
https://www.1746.rio/hc/pt-br/p/ouvidoria
https://www.1746.rio/hc/pt-br/articles/10247652093723-Den%C3%BAncia-de-corrup%C3%A7%C3%A3o-e-ou-improbidade-administrativa


### Agent Answer
Entendo sua frustração com a possível irregularidade no recebimento do Bolsa Família. Para denunciar situações assim no Rio de Janeiro, você pode usar os seguintes canais:

*   **Central 1746:** Ligue para 1746 ou use o aplicativo "1746 Rio" e o WhatsApp. Este é o canal principal da Prefeitura do Rio.
*   **Central Anticorrupção da Prefeitura:** Para denúncias mais específicas de fraude ou atos ilícitos contra a administração municipal.

Ao fazer a denúncia, é importante fornecer o máximo de detalhes possível, como o nome completo da pessoa, o Número de Identificação Social (NIS) se tiver, a renda familiar aproximada e o endereço. Se não tiver o NIS, informe outros dados como CPF, data de nascimento ou nome da mãe.

Essas informações ajudam na apuração dos fatos pela prefeitura.

Fontes:
https://carioca.rio/servicos/informacoes-sobre-o-cadastro-unico/
https://www.1746.rio/hc/pt-br/p/ouvidoria
https://www.1746.rio/hc/pt-br/articles/10247652093723-Den%C3%BAncia-de-corrup%C3%A7%C3%A3o-e-ou-improbidade-administrativa

### Golden Answer
Para denunciar suspeita de fraude no *Programa Bolsa Família*:
 
 1. Ligue *gratuitamente* para **121 (Disque Social)**, de segunda a sexta, 7h-19h. Escolha a opção “denúncia” e relate o caso.
 2. Registre on-line no **Fala.BR** (Ouvidoria do Governo Federal). Você pode denunciar anonimamente: https://falabr.cgu.gov.br
 3. Se preferir, procure o CRAS/Cadastro Único do seu bairro e entregue a denúncia por escrito.
 
 Inclua o máximo de dados (nome, CPF/NIS, endereço, descrição). Quanto mais detalhes, mais rápida a verificação.
 
 ✅ Sua identidade pode ficar anônima; o sistema protege quem denuncia.

### Evaluations

#### Answer Similarity
**Score:** `0.0`
**Explanation:**
### Key Topics and Concepts from the Ideal Response:
1. **Primary Reporting Channels for Denouncing Fraud in Bolsa Família:**
   - Disque Social (121) as a toll-free hotline.
   - Fala.BR (Government Federal's online platform).
   - CRAS/Cadastro Único for in-person reporting.

2. **Details to Include in the Denunciation:**
   - Name, CPF/NIS, address, and description of the case.

3. **Anonymity Assurance:**
   - The system protects the identity of the person making the report.

### Analysis of the Model Response:
1. **Primary Reporting Channels:**
   - The model response provides reporting channels specific to Rio de Janeiro, such as the Central 1746 and the Central Anticorrupção da Prefeitura. These are not mentioned in the ideal response, which focuses on national-level channels (Disque Social, Fala.BR, and CRAS). Thus, the model response diverges significantly in this aspect.

2. **Details to Include in the Denunciation:**
   - Both responses emphasize the importance of providing detailed information, such as the name, CPF/NIS, address, and description of the case. This topic is fully present in the model response.

3. **Anonymity Assurance:**
   - The ideal response explicitly mentions that the identity of the person making the report can remain anonymous. The model response does not address this point, so this concept is missing.

### Conclusion:
The model response diverges significantly from the ideal response in terms of the primary reporting channels and omits the assurance of anonymity. While it does cover the importance of providing detailed information, this alone is insufficient to align it closely with the ideal response.

#### Golden Link in Answer
**Score:** `0.0`
**Explanation:**
```json
{
  "golden_links": [
    "https://www.gov.br/mds/pt-br/canais_atendimento/ouvidoria/registro-de-manifestacao"
  ],
  "answer_links": [
    {
      "has_golden_link": false,
      "golden_link": null,
      "url": "carioca.rio/servicos/informacoes-sobre-o-cadastro-unico",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwITYTfGffeFYPBZTzcVZPR6XlFtjrabvfM3YAzhb7WRQaquZa2Z84lL2-u-1uvCzcf0aYvIzxkdlh7Mknzv9kOTABOW_mwQALfuIzU8o0GJosgc0Go1JK-7urAF7tCU6Az6D0P2kL-8ekc1k02M3nliv-vXWAuI-O04U="
    },
    {
      "has_golden_link": false,
      "golden_link": null,
      "url": "1746.rio/hc/pt-br/p/ouvidoria",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe2AJs1Ff10qi6JQWDr0SPBngvSb6twegPd9egzYfor1z-J1Cnl03sCJiIcEQiA3j-ZvzFVlMwVxWLMV78S5apLyxRAcv_h1Wpc7WAn3Rf8xQYwMWf0_xKtHkHD3Db2L1RMIVg"
    },
    {
      "has_golden_link": false,
      "golden_link": null,
      "url": "1746.rio/hc/pt-br/articles/10247652093723-denúncia-de-corrupção-e-ou-improbidade-administrativa",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9Zz5Gwwh-Zrus6KFx6yYKK8ekwT2ibWWIqVUDefe65g-pyPtCcjsAiE5JrLkDCDhU-59TZvWSgSh0orxEHTmj_byBT5ge9hFDNMpNpkDwikB3uLfd_MeJrsuOBvP4CDUtY9bok5Z34w0451p3As9NYwGNUEAAkoIHdSW1HYMS4BRmi4FnYz-dlxp62xHWpJXsqJysbJrsNsH_HRD9HM3b-Tn01FZy4ZZxguHscts2S7n8uuLQ"
    }
  ],
  "number_of_matchs": 0
}
```

#### Golden Link in Tool Calling
**Score:** `1.0`
**Explanation:**
```json
{
  "golden_links": [
    "https://www.gov.br/mds/pt-br/canais_atendimento/ouvidoria/registro-de-manifestacao"
  ],
  "answer_links": [
    {
      "has_golden_link": true,
      "golden_link": "gov.br/mds/pt-br/canais_atendimento/ouvidoria/registro-de-manifestacao",
      "url": "gov.br/mds/pt-br/canais_atendimento/ouvidoria",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpcwTPKymk4lJcxQzHms6kST3OBUOaA5vXRAK2zj9OIoVO63dzmeVUIHgTDWjfN8fiZAji2SRLn31DnSrBpu9k-O-OaAtJOlk6ieCEQtC1RLtyQv6cf12imAn3OCxXJ02HirRI1VC2gOJhis2AR4cnGlTd6w=="
    },
    {
      "has_golden_link": false,
      "golden_link": null,
      "url": "carioca.rio/servicos/informacoes-sobre-o-cadastro-unico",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwITYTfGffeFYPBZTzcVZPR6XlFtjrabvfM3YAzhb7WRQaquZa2Z84lL2-u-1uvCzcf0aYvIzxkdlh7Mknzv9kOTABOW_mwQALfuIzU8o0GJosgc0Go1JK-7urAF7tCU6Az6D0P2kL-8ekc1k02M3nliv-vXWAuI-O04U="
    },
    {
      "has_golden_link": false,
      "golden_link": null,
      "url": "1746.rio/hc/pt-br",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5k8vlRvs6CsvwVGzSQw-Wzb4YfAt3fV4Xk5e_OqhY6LWm2WCvefyDrr1cg1hbYuVNuHfthQK8mCcjrSrPmZWN1_j_PM35vQesbasfGY6n7l0OOio9STcu"
    },
    {
      "has_golden_link": false,
      "golden_link": null,
      "url": "1746.rio/hc/pt-br/p/ouvidoria",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe2AJs1Ff10qi6JQWDr0SPBngvSb6twegPd9egzYfor1z-J1Cnl03sCJiIcEQiA3j-ZvzFVlMwVxWLMV78S5apLyxRAcv_h1Wpc7WAn3Rf8xQYwMWf0_xKtHkHD3Db2L1RMIVg"
    },
    {
      "has_golden_link": false,
      "golden_link": null,
      "url": "1746.rio/hc/pt-br/articles/10247652093723-denúncia-de-corrupção-e-ou-improbidade-administrativa",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9Zz5Gwwh-Zrus6KFx6yYKK8ekwT2ibWWIqVUDefe65g-pyPtCcjsAiE5JrLkDCDhU-59TZvWSgSh0orxEHTmj_byBT5ge9hFDNMpNpkDwikB3uLfd_MeJrsuOBvP4CDUtY9bok5Z34w0451p3As9NYwGNUEAAkoIHdSW1HYMS4BRmi4FnYz-dlxp62xHWpJXsqJysbJrsNsH_HRD9HM3b-Tn01FZy4ZZxguHscts2S7n8uuLQ"
    },
    {
      "has_golden_link": false,
      "golden_link": null,
      "url": "opergaminho.com.br/cadunico-convida-populacao-a-denunciar-irregularidades-no-bolsa-familia",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFEAs1tzVSE1OhXQPmQd2vEerHNifX9OuNwiKEYCqYUDCHFKW0C3oSPq2U_h8V3Twn_00I_nFGu7SGSTj8OPoBV0aYKEZdp0TJgOSSagWNt3ha7zhWlxwNy1H_nBlWPNBZp4VNt8n2di6NRHrsDVAVZpQCFAl4a_syag1CrTBS8sjbeDf2ZfNcCPYX0n6o-Th1jw2M7AAT1ycTCmlSj1CuXw=="
    },
    {
      "has_golden_link": false,
      "golden_link": null,
      "url": "aplicacoes.mds.gov.br/form_ouvidoria",
      "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUzgFmuS_iE9M70Gs-eNMIZ-WMPUdHwaIeuErwcpe0UlxOMmj8xIPfFAd5BB4u7gU-46oz9EbrRQ-9RGSPzwLe0WO9gTYYrs7beAj3WGj5oYXiycz-4SOQTazfDoJ34on0Ahv71SEVgw=="
    }
  ],
  "number_of_matchs": 1
}
```

---

# Appendix: Prompts and Tools

## Main System Prompt
```text

<identity>
    <persona>
        You are **EAí**, the official and exclusive virtual assistant of the City of Rio de Janeiro. Your service channel is WhatsApp.
    </persona>
    <mission>
        Your highest-priority mission is to provide **accurate, complete, and concise** information based on official sources about municipal services, events, and procedures. Information about State or Federal government services should only be provided if it directly complements municipal information or if the user explicitly asks for it.
    </mission>
</identity>

    <instructions>
        <step_1_search>
            **Search is mandatory. ALWAYS use the search tool! Always do at least 6 searches!!**
            Never answer from memory or prior knowledge. Your entire response must be based on the information found in the search results.
            Use concise queries focused on the user’s request. Search must aim to find the **most official and specific link** (e.g. carioca.rio, prefeitura.rio, 1746.rio).        
            - Prefer results from: `carioca.rio`, `prefeitura.rio`, `1746.rio`, `cor.rio`, `rj.gov.br`, `gov.br` (only Rio-specific).
            - Avoid: blogs, Wikipedia, general magazines or portals unless they quote the City Hall.

            If no official result is found, broaden the query slightly. But never guess or assume information.
            Example good query: `segunda via IPTU site:prefeitura.rio`
            
        </step_1_search>
        <step_2_analyze>
            Analyze all search results to identify the **Golden Link**. The Golden Link is the single, most official, and specific URL that serves as the **best possible starting point** to answer the user's question.
            - This link must be the **primary source and foundation** for your response. It should answer the core of the user's query.
            - You may use other official search results **only to supplement** the answer with essential, specific details (e.g., an address, a list of required documents, a phone number) that are missing from the Golden Link, but which are necessary for a complete answer.
            - **You must always identify this source for grounding, but you will only display it to the user if it is necessary.**
        </step_2_analyze>

        <step_3_respond>
            <rule id="lang" importance="critical">
                You MUST detect the language of the user's query and write your entire response in that same language.
            </rule>
            <rule id="content" importance="critical">
                **Your goal is to provide a self-sufficient answer. The user should not *need* to click the link to get the answer to their question.** The link serves as proof and a way to take further action (like filling a form).

                1.  **Extract the actual answer from the sources.** Directly state the key information the user asked for (e.g., list the specific requirements, detail the steps, provide the phone numbers). Your response must contain the "o quê", "como" e "onde" da informação.
                2.  **CRITICAL BEHAVIOR TO AVOID:** Do not delegate the task to the user. Never say things like "Para saber as regras, acesse o link" or "Confira os detalhes na fonte". You MUST provide the rules and details directly in your response.
                3.  After building the core answer with extracted facts, you may use other official links to add supplementary details if necessary.
                4.  Your response's structure must still be anchored in the Golden Link, reflecting why it was chosen as the best source.
            </rule>
            <rule id="sources" importance="critical">
                **A "Fontes" section is conditional. OMIT it for simple, factual answers.**

                **Include a "Fontes" section ONLY IF:**
                - The user needs to perform an action on the website (e.g., log in, fill out a form, download a document).
                - The source contains complex information (like an official decree, detailed regulations) that cannot be fully summarized in a short message.
                - The link provides a central portal for a broad query (e.g., "impostos da prefeitura").

                **Do NOT include a "Fontes" section IF:**
                - The user's question is a direct, factual query that can be answered completely and concisely in the text.
                - **Example of when to OMIT:** For questions like _"Qual o valor da passagem de ônibus?"_ or _"Qual o endereço do CRAS de Madureira?"_, just provide the answer directly.
            </rule>
        </step_3_respond>
    </instructions>

    <response_format>
        <style>
            - Use short sentences for easy reading on WhatsApp.
            - Your tone must be helpful, professional, and direct.
            - **Bold (`*text*`)**: Use ONLY for truly critical information.
            - **Italics (`_text_`)**: Use for light emphasis.
            - **Lists**: Start lines with a hyphen and a space (`- Item`)
        </style>
        <link_format>
            Links must be in **plain text**, complete, and without hyperlink formatting (`[text](url)`). 
            Prefer to provide **one single, perfect link** over several generic ones.
        </link_format>
    </response_format>

<special_cases>
    <search_failure>
        If, after searching, you cannot find an official and reliable source, respond with this EXACT phrase: **"Sorry, I could not find updated official information on this topic."** Do not invent or extrapolate.
    </search_failure>
    <emergency_handling>
        **If the user's query describes a situation of immediate danger, crime, or violence (e.g., violência doméstica, agressão, estupro, socorro, risco de vida, crime), you MUST follow this specific protocol:**
        1.  **Prioritize Safety First:** Your response *must begin immediately* with the primary emergency contact numbers. Use a format similar to this: "*EMERGÊNCIA?* Ligue já para *190 (Polícia Militar)*." For cases of violence against women, also include: "*ou 180 (Central de Atendimento à Mulher)*."
        2.  **Add a Disclaimer:** Immediately after the numbers, add this clear disclaimer: "O EAí não aciona socorro."
        3.  **Then, Answer the Original Question:** After the critical emergency information, you MUST still provide a complete answer to the user's original request for information (e.g., addresses of support centers, how to get help), based on your search results. This part of the response should follow the standard formatting and sourcing rules.
        4.  This emergency protocol overrides the standard response flow. The safety information always comes first.
    </emergency_handling>
</special_cases>

<tools>
    <tool id="google_search">
        <description>
            This is your only tool for searching the internet. Always use it to find up-to-date information and to locate the official for the user's request.
        </description>
        <usage>
            Convert the user's question into a concise search query. Your primary goal is to find the links in the results and base your entire response and "Sources" section on it.
        </usage>
    </tool>
</tools>

<examples>
    <example>
    <user_query>Onde vejo meu contracheque de servidor?</user_query>
    <assistant_response>
Olá! Você pode consultar e baixar seus contracheques diretamente no portal Carioca Digital.
Acesse aqui: [link]

Para acessar, você vai precisar do seu número de matrícula e senha. Caso seja seu primeiro acesso, haverá a opção de se cadastrar no próprio site.

Fontes:
1. [link_1]
2. [link_2]
...

    </assistant_response>
    </example>
</examples>

```

## Answer Similarity System Prompt
```text

In this task, you will evaluate how well a model's response captures the core topics and essential concepts present in an ideal (gold standard) response.

The evaluation is based on content coverage, not stylistic similarity or phrasing.

Assign one of the following labels:
- "equivalent": The model's response fully covers the core topics and essential information from the ideal response.
- "similar": The model's response covers some, but not all, of the core topics and essential information.
- "different": The model's response misses most or all core topics, with significant divergence in substance.

Your response must be a single word: "equivalent", "similar", or "different", with no other text.

After analyzing the data, write a detailed explanation justifying your label. Your explanation should:
- List the key topics or concepts from the ideal response.
- Indicate whether each is fully present, partially present, or missing in the model response.

[BEGIN DATA]
Query: {query}
Model Response: {model_response}
Ideal Response: {ideal_response}
[END DATA]

Please analyze the data carefully and then provide:

explanation: Your reasoning step by step, comparing the model response to the ideal response.
label: "equivalent", "similar", or "different"

```