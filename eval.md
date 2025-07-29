# Análise do Script `experiments.py`

## Resumo da Funcionalidade

O script `src/evaluations/letta/phoenix/training_dataset/experiments.py` é uma ferramenta para orquestrar a avaliação de modelos de linguagem (LLMs) e configurações de prompts. Ele utiliza a biblioteca `phoenix` para executar experimentos, comparar as saídas de diferentes agentes com um "golden dataset" (conjunto de dados de referência) e avaliar a qualidade das respostas com base em métricas customizadas.

O fluxo principal do script é:
1.  **Configuração**: Define uma lista de configurações de experimentos (`experiments_configs`). Cada configuração especifica o dataset a ser usado, o nome do experimento, os avaliadores, as ferramentas disponíveis para o agente (ex: `google_search`), o modelo, e o system prompt.
2.  **Coleta de Respostas**: Para cada experimento, o script interage com um agente (potencialmente um modelo da OpenAI ou Google) para gerar respostas para as perguntas do dataset. Ele faz isso em lotes (`batches`) para processar o conjunto de dados de forma eficiente. Há também um modo que pula esta etapa para usar respostas pré-geradas (ex: do ChatGPT).
3.  **Execução da Avaliação**: Utiliza a função `run_experiment` do `phoenix` para executar os avaliadores definidos. Os avaliadores são funções que medem aspectos da qualidade da resposta, como clareza (`clarity`), se a resposta aborda a pergunta (`answer_adressing`), e a completude da resposta (`answer_completeness`).
4.  **Logging e Metadados**: Registra informações detalhadas sobre cada experimento, incluindo metadados como a versão do prompt, os modelos utilizados e os parâmetros (ex: temperatura), o que permite rastrear e comparar os resultados ao longo do tempo.

Em suma, o script automatiza o ciclo de teste e avaliação de diferentes abordagens de agentes de IA, permitindo que a equipe compare objetivamente o desempenho de várias configurações.

## Pontos Fracos

1.  **Configuração "Hardcoded"**: A principal fraqueza é que as configurações dos experimentos (`experiments_configs`) estão fixas no código. Para adicionar, remover ou modificar um experimento, é necessário editar o script diretamente. Isso é inflexível, propenso a erros e dificulta a gestão de um grande número de experimentos.
2.  **Baixa Manutenibilidade**: A função `main` é longa e contém muita lógica de orquestração, incluindo a construção de nomes de experimentos e o tratamento de casos especiais (como o tipo `"resposta_gpt"`). Isso viola o princípio de responsabilidade única e torna o código difícil de ler e manter.
3.  **Dependência de um Passo Manual**: Os comentários no topo do arquivo (`## NOTE: ... ME CHAMA (FRED) QUE EU EXPLICO O QUE FAZER.`) indicam a existência de um passo manual não documentado que é necessário para rodar o código. Isso é um grande risco para a reprodutibilidade e automação dos experimentos. Qualquer dependência de uma modificação manual no código torna o processo frágil e dependente de conhecimento tribal.
4.  **Caminhos de Arquivo Fixos**: O script possui um fallback para ler um arquivo CSV (`respostas_formatadas.csv`) de um caminho fixo e relativo. Isso torna o script menos portável e propenso a quebrar se a estrutura de diretórios mudar ou se o arquivo não estiver presente.
5.  **Gestão de Prompts**: Os system prompts são importados diretamente de um módulo Python. Embora isso funcione, acopla o código de avaliação diretamente às definições dos prompts. Seria mais flexível carregar os prompts de arquivos de texto ou de uma base de dados, permitindo testes com novas versões sem alterar o código.

## Oportunidades de Melhoria

1.  **Externalizar a Configuração**: Mover a lista `experiments_configs` para arquivos de configuração externos (ex: YAML ou JSON). Cada arquivo poderia definir um ou mais experimentos. Isso desacopla a configuração da lógica do script, permitindo que qualquer pessoa adicione ou modifique testes sem precisar entender ou alterar o código Python.
2.  **Criar uma Interface de Linha de Comando (CLI)**: Implementar uma CLI usando `argparse` ou `click`. Isso permitiria executar experimentos específicos a partir do terminal, passando o caminho para o arquivo de configuração como argumento. Exemplo: `python experiments.py --config-file configs/eai_v2_test.yaml`.
3.  **Refatoração e Modularização**:
    *   Dividir a função `main` em funções menores e mais focadas (ex: `load_config`, `run_experiment_from_config`).
    *   Criar uma classe `ExperimentRunner` que encapsule a lógica de um único experimento (carregar dados, coletar respostas, rodar avaliação). O loop principal apenas instanciaria e executaria essa classe para cada configuração.
4.  **Documentar e Automatizar o "Passo Peculiar"**: A etapa manual mencionada nos comentários deve ser claramente documentada. Idealmente, ela deveria ser eliminada e automatizada, talvez através de um parâmetro de configuração ou uma variável de ambiente que controle o comportamento do agente.
5.  **Flexibilizar o Carregamento de Dados e Prompts**: Em vez de caminhos e imports fixos, os arquivos de configuração dos experimentos deveriam especificar os caminhos para os datasets, prompts e respostas pré-coletadas. O script então carregaria esses recursos dinamicamente com base na configuração fornecida.
6.  **Utilizar Variáveis de Ambiente (Dotenv)**: Para configurações de ambiente como as credenciais do Phoenix, usar um arquivo `.env` e a biblioteca `python-dotenv` para carregá-las é uma prática padrão que evita "hardcodar" valores no script.