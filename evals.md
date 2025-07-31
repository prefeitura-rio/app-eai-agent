# Análise do Módulo de Avaliações (`src/evaluations/core`)

Este documento detalha a arquitetura e o funcionamento do sistema de avaliação de agentes de IA, contido na pasta `src/evaluations/core`. O sistema é projetado para ser modular e assíncrono, permitindo a execução de experimentos complexos para medir diversas capacidades dos agentes.

## Visão Geral da Arquitetura

O fluxo de uma avaliação segue os seguintes passos:

1.  **Carregamento de Dados (`dataloader.py`)**: Os dados de teste (prompts, contextos, respostas esperadas) são carregados de uma fonte (CSV, Google Sheets, ou DataFrame) e transformados em "tarefas" padronizadas.
2.  **Configuração do Experimento (`main.py`)**: O script principal define qual dataset será usado, qual agente será avaliado, e quais métricas de avaliação serão aplicadas.
3.  **Execução do Experimento (`runner.py`)**: O `AsyncExperimentRunner` orquestra todo o processo. Para cada tarefa, ele:
    a.  Gerencia a interação com o agente, que pode ser de um único turno ou uma conversa complexa de múltiplos turnos (`llm_clients.py`, `evals.py`).
    b.  Coleta as respostas e a cadeia de raciocínio do agente.
    c.  Submete as respostas a um ou mais "juízes" LLM para avaliação.
4.  **Avaliação (`evals.py`)**: A classe `Evals` contém a lógica para cada métrica (ex: aderência à persona, correção semântica). Ela usa prompts específicos (`prompt_judges.py`) para instruir um LLM juiz (ex: GPT-4o) a pontuar a performance do agente.
5.  **Geração de Resultados (`runner.py`)**: Ao final, o runner agrega todas as pontuações, calcula estatísticas e salva um arquivo JSON detalhado com os resultados do experimento.

---

## Detalhamento dos Arquivos

### `main.py`

-   **Propósito**: Ponto de entrada para a execução de um experimento de avaliação.
-   **Funções Principais**:
    -   `run_experiment()`: Função assíncrona que configura e dispara o processo de avaliação.
-   **Lógica**:
    1.  **Configuração de Logging**: Inicializa o sistema de logs.
    2.  **Definição do Dataset**: Instancia o `DataLoader` com os dados de teste (neste caso, `UNIFIED_TEST_DATA` do arquivo `test_data.py`).
    3.  **Definição do Agente**: Cria um `CreateAgentRequest` com a configuração do agente a ser testado (modelo, system prompt, ferramentas, etc.).
    4.  **Definição da Suíte de Avaliação**: Instancia um cliente LLM para o "juiz" (ex: `AzureOpenAIClient`) e a classe `Evals`, passando o cliente. Define quais métricas serão executadas.
    5.  **Carregamento de Respostas (Opcional)**: Permite carregar respostas de agente pré-computadas de um arquivo JSON para acelerar o processo de avaliação, focando apenas na etapa de julgamento.
    6.  **Configuração do Runner**: Instancia o `AsyncExperimentRunner` com todas as configurações acima (nome do experimento, metadados, agente, suíte de avaliação, etc.).
    7.  **Execução**: Chama o método `runner.run(loader)` para iniciar o experimento.

### `dataloader.py`

-   **Propósito**: Carregar e preparar os dados para os experimentos.
-   **Classe Principal**: `DataLoader`
    -   `__init__(self, source, id_col, prompt_col, ...)`: O construtor pode receber um caminho de arquivo, uma URL de Google Sheets ou um DataFrame do pandas. Ele também recebe os nomes das colunas que contêm o ID da tarefa, o prompt inicial e outros metadados.
    -   `_create_dataset_config(...)`: Gera metadados para o dataset, incluindo um ID determinístico baseado no hash do conteúdo dos dados, garantindo rastreabilidade.
    -   `_load_from_file(...)` e `_load_from_gsheet(...)`: Métodos privados para carregar dados de CSV ou Google Sheets.
    -   `get_tasks()`: Um gerador que itera sobre o DataFrame e produz cada linha como um dicionário de "tarefa" padronizado, pronto para ser consumido pelo `runner`.

### `runner.py`

-   **Propósito**: Orquestrar a execução assíncrona de todo o experimento.
-   **Classe Principal**: `AsyncExperimentRunner`
    -   `__init__(self, ...)`: Recebe todas as configurações do experimento. Inicializa um `asyncio.Semaphore` para controlar a concorrência e evitar sobrecarga.
    -   `_get_one_turn_response(...)` e `_get_multi_turn_transcript(...)`: Funções para obter as respostas do agente, seja executando uma interação ao vivo ou carregando de um arquivo pré-computado.
    -   `_execute_evaluations(...)`: Executa as funções de avaliação (`Evals`) de forma concorrente para uma determinada tarefa. Mede o tempo de geração da resposta e o tempo do julgamento.
    -   `_process_task(...)`: O coração do runner. Para uma única tarefa, esta função gerencia a obtenção da resposta do agente e a execução das avaliações. É a unidade de trabalho que é executada em paralelo.
    -   `_calculate_metrics_summary(...)` e `_calculate_error_summary(...)`: Calculam estatísticas agregadas (média, mediana, desvio padrão, taxas de erro) a partir dos resultados de todas as tarefas.
    -   `run(self, loader)`: O método principal que recebe o `DataLoader`, obtém as tarefas e usa `tqdm_asyncio.gather` para processá-las em paralelo. Ao final, monta o objeto de resultado final e o salva em um arquivo JSON.

### `evals.py`

-   **Propósito**: Definir as métricas de avaliação e gerenciar a lógica de conversação para avaliações multi-turno.
-   **Decorador**: `@eval_method(name, turns)`
    -   Registra uma função de avaliação em um dicionário global (`_EVAL_METHODS_REGISTRY`), associando um nome e um tipo (`one` ou `multiple` turnos) a ela. Isso permite que o runner saiba qual tipo de resposta do agente (turno único ou transcrição completa) a métrica espera.
-   **Classe Principal**: `Evals`
    -   `__init__(self, judge_client)`: Recebe uma instância de um cliente LLM que atuará como juiz.
    -   `_get_llm_judgement(...)`: Uma função auxiliar que formata o prompt do juiz, envia para o LLM e extrai a pontuação da resposta.
    -   **Métodos de Avaliação**: Funções como `conversational_reasoning`, `semantic_correctness`, etc., cada uma decorada com `@eval_method`. Elas recebem a resposta do agente e a tarefa, e retornam um dicionário com a pontuação e as anotações do juiz.
-   **Classe**: `ConversationHandler`
    -   `__init__(self, conv_manager, evaluation_suite)`: Recebe um `AgentConversationManager` e uma instância de `Evals`.
    -   `conduct(self, task)`: Gerencia uma conversa de múltiplos turnos. Em cada turno, ele:
        1.  Envia a mensagem atual para o agente.
        2.  Usa o LLM juiz para decidir qual será a próxima fala na conversa, com base em um roteiro (`judge_context` da tarefa).
        3.  Continua até que o juiz decida encerrar a conversa.
        4.  Retorna a transcrição completa da interação.

### `llm_clients.py`

-   **Propósito**: Abstrair a comunicação com diferentes modelos de linguagem e com a API do agente (EAI Gateway).
-   **Classe**: `AgentConversationManager`
    -   Gerencia o ciclo de vida de uma conversa com um agente.
    -   `initialize()`: Cria um novo agente através da API e armazena seu ID.
    -   `send_message(...)`: Envia uma mensagem para o agente (usando o ID armazenado) e aguarda a resposta.
    -   `close()`: Limpa o ID do agente, encerrando a sessão.
-   **Classes de Cliente**: `AzureOpenAIClient` e `GeminiAIClient`
    -   Implementam a lógica específica para se comunicar com as APIs de LLM da Azure e do Google, respectivamente.
    -   Possuem um método `execute(prompt)` que envia o prompt e retorna a resposta do modelo. São usados pela classe `Evals` para os julgamentos.

### `prompt_judges.py`

-   **Propósito**: Centralizar todos os templates de prompt usados pelos juízes LLM.
-   **Conteúdo**: Contém strings de prompt formatáveis para diferentes cenários:
    -   `CONVERSATIONAL_JUDGE_PROMPT`: Usado pelo `ConversationHandler` para guiar o juiz durante uma conversa.
    -   `FINAL_CONVERSATIONAL_JUDGEMENT_PROMPT`: Usado para avaliar o raciocínio geral ao final de uma conversa.
    -   `FINAL_MEMORY_JUDGEMENT_PROMPT`: Usado para avaliar a memória do agente ao final de uma conversa.
    -   `SEMANTIC_CORRECTNESS_PROMPT`: Para avaliações de turno único, compara a resposta do agente com uma resposta ideal.
    -   `PERSONA_ADHERENCE_PROMPT`: Para avaliações de turno único, verifica se a resposta está de acordo com a persona definida.

### `test_data.py`

-   **Propósito**: Fornecer um conjunto de dados estático para os testes.
-   **Conteúdo**:
    -   `UNIFIED_TEST_DATA`: Um dicionário contendo listas de dados, que pode ser facilmente convertido em um DataFrame. Inclui:
        -   `id`: Identificador único para cada caso de teste.
        -   `initial_prompt`: A primeira mensagem a ser enviada ao agente.
        -   `persona`: A persona que o agente deve adotar.
        -   `judge_context`: O "roteiro secreto" que o LLM juiz deve seguir durante a conversa.
        -   `golden_summary`: Um resumo do que se espera que o agente faça, usado no julgamento final.
        -   `golden_response`: A resposta ideal para avaliações de turno único.

### `utils.py`

-   **Propósito**: Fornecer funções utilitárias.
-   **Funções**:
    -   `parse_reasoning_messages(messages)`: Uma função crucial que recebe a lista de mensagens brutas da API do agente (que pode ser complexa e aninhada) e a transforma em uma lista de dicionários limpa e padronizada, facilitando a análise e a exibição dos traços de raciocínio.

---

## Estrutura do JSON de Resultado (`results_{experiment_name}.json`)

O arquivo de resultado gerado pelo `AsyncExperimentRunner` é um JSON com a seguinte estrutura aninhada:

```json
{
  "dataset_name": "string",
  "dataset_description": "string",
  "dataset_id": "string (uuid)",
  "experiment_id": "string (uuid)",
  "experiment_name": "string",
  "experiment_description": "string",
  "experiment_timestamp": "string (ISO 8601)",
  "experiment_metadata": {
    "agent_config": {
      "model": "string",
      "system": "string",
      "tools": ["string"],
      "user_number": "string",
      "name": "string",
      "tags": ["string"]
    },
    "judges_prompts": {
      "conversational_agent": "string",
      "conversational_reasoning": "string",
      "conversational_memory": "string",
      "persona_adherence": "string",
      "semantic_correctness": "string"
    }
  },
  "execution_summary": {
    "total_duration_seconds": "float",
    "average_task_duration_seconds": "float",
    "average_metric_duration_seconds": "float"
  },
  "error_summary": {
    "total_failed_runs": "integer",
    "errors_per_metric": {
      "metric_name": "integer"
    },
    "failed_run_ids": ["string"]
  },
  "aggregate_metrics": [
    {
      "metric_name": "string",
      "total_runs": "integer",
      "successful_runs": "integer",
      "success_rate_percentage": "float",
      "failed_runs": "integer",
      "failure_rate_percentage": "float",
      "score_statistics": {
        "average": "float",
        "median": "float",
        "std_dev": "float",
        "min": "float",
        "max": "float"
      },
      "duration_statistics_seconds": {
        "average": "float",
        "median": "float",
        "std_dev": "float",
        "min": "float",
        "max": "float"
      },
      "score_distribution": [
        {
          "value": "float",
          "count": "integer",
          "percentage": "float"
        }
      ]
    }
  ],
  "runs": [
    {
      "duration_seconds": "float",
      "task_data": {
        "id": "string",
        "prompt": "string",
        "...outras colunas de metadados...": "any"
      },
      "agent_response": {
        "one_turn": "string | null",
        "multi_turn_final": "string | null"
      },
      "reasoning_trace": {
        "one_turn": [
          {
            "message_type": "string",
            "content": "any"
          }
        ],
        "multi_turn": [
          {
            "turn": "integer",
            "judge_message": "string",
            "agent_response": "string",
            "reasoning_trace": [
              {
                "message_type": "string",
                "content": "any"
              }
            ]
          }
        ]
      },
      "evaluations": [
        {
          "metric_name": "string",
          "duration_seconds": "float",
          "score": "float | null",
          "has_error": "boolean",
          "error_message": "string | null",
          "judge_annotations": "string | null"
        }
      ],
      "error": "string | null"
    }
  ]
}
```