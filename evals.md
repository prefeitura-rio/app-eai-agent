# Módulo de Avaliação Core

## Visão Geral

O módulo `src/evaluations/core` fornece um framework robusto e assíncrono para conduzir avaliações de ponta a ponta de agentes baseados em LLM. Ele foi projetado para medir a qualidade das respostas de um agente em relação a um conjunto de dados de referência, utilizando tanto métricas objetivas quanto avaliações subjetivas realizadas por um "Juiz" LLM.

A arquitetura é modular, separando o carregamento de dados, a execução do agente, a lógica de avaliação e a orquestração do experimento, facilitando a extensão e manutenção.

## Arquitetura e Fluxo de Execução

O fluxo de um experimento de avaliação segue os seguintes passos:

1.  **Configuração (`main.py`)**: O ponto de entrada (`run_experiment`) configura todos os componentes necessários:
    *   **DataLoader**: Carrega o conjunto de dados (local ou de uma fonte externa como Google Sheets) que contém os prompts, as respostas de referência (`golden_response`) e outros metadados.
    *   **Agente Avaliado (`EvaluatedLLMClient`)**: Configura o agente cujo desempenho será medido.
    *   **Juiz LLM (`AzureOpenAIClient` ou `GeminiAIClient`)**: Instancia o cliente LLM que será usado para julgar a qualidade das respostas do agente avaliado.
    *   **Suíte de Avaliações (`Evals`)**: Define o conjunto de métricas que serão aplicadas a cada resultado do agente.
    *   **Runner (`AsyncExperimentRunner`)**: Injeta todos os componentes acima para orquestrar a execução.

2.  **Execução (`AsyncExperimentRunner`)**:
    *   O `runner` itera sobre cada "tarefa" fornecida pelo `DataLoader`.
    *   Para cada tarefa, ele invoca o `EvaluatedLLMClient` para obter a resposta do agente para o prompt da tarefa.
    *   Em seguida, o `runner` passa o resultado do agente e a tarefa original para a `Evals`.

3.  **Avaliação (`Evals`)**:
    *   A suíte de avaliações executa, em paralelo, todas as métricas configuradas (ex: `semantic_correctness`, `persona_adherence`).
    *   Métricas que exigem julgamento (como correção semântica) utilizam o **Juiz LLM**, formatando um prompt específico a partir dos templates em `prompt_judges.py`.
    *   Métricas objetivas (como `keyword_match`) são executadas diretamente.

4.  **Resultados**:
    *   O `runner` coleta os resultados de todas as tarefas, que incluem a tarefa original, a resposta do agente e o output de cada avaliação.
    *   O `main.py` salva a lista completa de resultados em um arquivo JSON para análise posterior.

## Componentes Principais

Abaixo está a descrição de cada arquivo no módulo:

-   **`main.py`**:
    O ponto de entrada que orquestra a configuração e execução de um experimento. É responsável por instanciar e conectar todos os outros componentes.

-   **`dataloader.py` (`DataLoader`)**:
    Classe responsável por carregar e padronizar os dados de avaliação. Consegue ler dados de DataFrames do pandas, arquivos CSV locais ou planilhas do Google Sheets, transformando cada linha em uma "tarefa" padronizada (um dicionário Python).

-   **`llm_clients.py`**:
    Contém as classes para interagir com diferentes serviços de LLM.
    -   `EvaluatedLLMClient`: Um cliente para o agente que está sendo avaliado. Ele se comunica com uma API interna (`EAIClient`) para executar o agente configurado.
    -   `AzureOpenAIClient` / `GeminiAIClient`: Clientes para os LLMs usados como "Juízes". Eles são responsáveis por executar os prompts de avaliação e retornar um julgamento estruturado (geralmente em JSON).

-   **`evals.py` (`Evals`)**:
    O coração da lógica de avaliação.
    -   Utiliza um decorador (`@eval_method`) para registrar dinamicamente diferentes funções de avaliação.
    -   A classe `Evals` recebe uma instância de um cliente "Juiz" e executa uma lista de avaliações em paralelo para um determinado resultado, otimizando o tempo de execução.

-   **`prompt_judges.py`**:
    Centraliza todos os templates de prompt usados pelos Juízes LLM. Manter os prompts neste arquivo facilita a manutenção, o versionamento e a consistência entre os experimentos.

-   **`runner.py` (`AsyncExperimentRunner`)**:
    A classe que orquestra a execução do experimento de ponta a ponta. Ela gerencia o loop assíncrono sobre as tarefas, chama o agente, executa a suíte de avaliação e coleta os resultados, exibindo uma barra de progresso.

-   **`test_data.py`**:
    Fornece um conjunto de dados de amostra (`TEST_DATA`) usado para executar experimentos locais e testes. Contém listas de prompts, respostas de referência, personas e palavras-chave.
