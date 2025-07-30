# Análise do Framework de Avaliação de Agentes de IA

Este documento descreve a arquitetura e o fluxo de trabalho do framework de avaliação de agentes de IA encontrado em `src/evaluations/core`.

## Sumário

O framework foi projetado para executar experimentos de avaliação de forma assíncrona e modular. A ideia central é usar um "Juiz" (um LLM, como GPT-4o) para avaliar o desempenho de um "Agente" (outro LLM ou sistema de IA) em uma série de "Tarefas".

Os principais componentes são:

1.  **DataLoader**: Carrega as tarefas de avaliação a partir de fontes de dados como DataFrames, CSVs ou Google Sheets.
2.  **LLM Clients**: Fornece clientes para interagir com os LLMs. Crucialmente, o `AgentConversationManager` gerencia o ciclo de vida e a comunicação com o *agente que está sendo avaliado*, garantindo o isolamento entre as tarefas. Outros clientes (`AzureOpenAIClient`, `GeminiAIClient`) são usados pelo *Juiz* para realizar a avaliação.
3.  **Evals**: Contém a lógica das métricas de avaliação. Cada método de avaliação define como o Juiz deve analisar a resposta do Agente. O sistema é extensível através de um decorador (`@eval_method`).
4.  **Prompt Judges**: Centraliza todos os templates de prompt que são enviados ao Juiz, garantindo consistência e fácil manutenção.
5.  **AsyncExperimentRunner**: Orquestra todo o processo. Ele itera sobre as tarefas do DataLoader, gerencia a comunicação com o agente para cada tarefa e executa a suíte de avaliações, coletando os resultados.

O fluxo é totalmente assíncrono, permitindo que múltiplas tarefas sejam processadas em paralelo, otimizando o tempo de execução dos experimentos.

---

## Estrutura Detalhada do Projeto

A seguir, uma descrição detalhada de cada módulo e suas responsabilidades.

### `src/evaluations/core/`

```
.
├── __init__.py
├── dataloader.py         # Carrega e formata os dados de teste.
├── evals.py              # Define as métricas e a lógica de avaliação.
├── llm_clients.py        # Gerencia a comunicação com os LLMs (Agente e Juiz).
├── main.py               # Ponto de entrada para executar um experimento.
├── prompt_judges.py      # Armazena os templates de prompt para o Juiz.
├── runner.py             # Orquestra a execução do experimento.
└── test_data.py          # Contém dados de exemplo para os testes.
```

### Componentes Principais

#### 1. `dataloader.py`

-   **Classe `DataLoader`**: Responsável por carregar dados de teste de diferentes fontes (arquivos CSV, URLs do Google Sheets ou DataFrames do pandas).
-   **Funcionalidade**: Transforma cada linha da fonte de dados em uma "tarefa" (um dicionário Python), que contém um `id` e outras colunas de metadados (`metadata_cols`) necessárias para a avaliação (ex: `prompt`, `golden_answer`, `persona`).

#### 2. `llm_clients.py`

-   **Classe `AgentConversationManager`**: Componente crucial que gerencia o ciclo de vida de uma conversa com o agente a ser avaliado.
    -   `initialize()`: Cria uma nova instância do agente através da `EAIClient` (API interna) e armazena o `agent_id`.
    -   `send_message()`: Envia uma mensagem para o agente e aguarda a resposta. Usa o mesmo `agent_id` para manter o contexto da conversa.
    -   `close()`: Encerra a conversa.
    -   **Importante**: Garante que cada tarefa de avaliação seja executada em uma sessão de conversa isolada.
-   **Classes `AzureOpenAIClient` e `GeminiAIClient`**: Clientes simples para interagir com os LLMs que atuam como "Juízes". Eles recebem um prompt e retornam a resposta do modelo.

#### 3. `evals.py`

-   **Decorador `@eval_method`**: Um sistema de registro para novas métricas de avaliação. Ele associa uma função de avaliação a um nome e ao tipo de interação necessária (`turns`: "zero", "one" ou "multiple").
-   **Classe `Evals`**: Contém a suíte de avaliações.
    -   Cada método decorado (ex: `evaluate_conversational_reasoning`, `evaluate_semantic_correctness`) implementa a lógica para uma métrica específica.
    -   Esses métodos formatam um prompt do `prompt_judges.py` com os dados da tarefa e a resposta do agente, e então usam o `judge_client` para obter um julgamento (normalmente um JSON com `score` e `reasoning`).
    -   O método `run()` orquestra a execução das métricas solicitadas, gerenciando se a avaliação requer uma ou múltiplas interações com o agente.

#### 4. `prompt_judges.py`

-   Este arquivo é um repositório de constantes de string.
-   **Responsabilidade**: Centraliza todos os templates de prompt usados pelos Juízes. Isso desacopla a lógica de avaliação da formulação dos prompts, facilitando a alteração dos prompts sem modificar o código de avaliação.
-   Exemplos: `SEMANTIC_CORRECTNESS_PROMPT`, `CONVERSATIONAL_JUDGE_PROMPT`.

#### 5. `runner.py`

-   **Classe `AsyncExperimentRunner`**: O maestro do framework.
    -   `__init__()`: Recebe a configuração do agente a ser testado (`agent_config`), a suíte de avaliações (`evaluation_suite`) e a lista de métricas a serem executadas.
    -   `_process_task()`: Processa uma única tarefa. É aqui que o `AgentConversationManager` é instanciado e o ciclo de vida da avaliação para a tarefa é gerenciado (inicialização, execução, encerramento).
    -   `run()`: Recebe um `DataLoader`, obtém a lista de tarefas e executa `_process_task` para cada uma de forma concorrente usando `asyncio` e `tqdm_asyncio` para exibir uma barra de progresso.

#### 6. `main.py` e `test_data.py`

-   **`test_data.py`**: Fornece dados brutos (listas de prompts, respostas, etc.) para os testes, incluindo cenários simples e conversacionais.
-   **`main.py`**: Serve como um exemplo prático e ponto de entrada para executar um experimento. Ele demonstra como instanciar e conectar todos os componentes:
    1.  Configura o `DataLoader` com os dados de teste.
    2.  Define a configuração do `agent_config` a ser avaliado.
    3.  Instancia o `judge_client`.
    4.  Cria a `evaluation_suite` com o juiz.
    5.  Instancia o `AsyncExperimentRunner` com todos os componentes acima.
    6.  Executa o `runner` e salva os resultados em um arquivo JSON.

---

## Fluxo de Execução de um Experimento

1.  **Configuração (`main.py`)**: O usuário define o agente a ser testado, o juiz, as métricas e os dados de teste.
2.  **Início (`runner.run`)**: O `AsyncExperimentRunner` recebe o `DataLoader` e cria uma lista de tarefas assíncronas, uma para cada item de dados.
3.  **Processamento da Tarefa (`runner._process_task`)**: Para cada tarefa, em paralelo:
    a.  Uma nova instância do `AgentConversationManager` é criada, garantindo isolamento.
    b.  O `conversation_manager.initialize()` é chamado, criando um novo agente via API.
    c.  O `evaluation_suite.run()` é chamado, passando o `conversation_manager` e a tarefa.
4.  **Avaliação (`evals.run`)**:
    a.  A suíte de avaliação interage com o agente através do `conversation_manager.send_message()` (uma ou várias vezes, dependendo da métrica).
    b.  Após obter a(s) resposta(s) do agente, a suíte formata um prompt de julgamento (de `prompt_judges.py`).
    c.  O `judge_client` é usado para enviar este prompt ao LLM Juiz.
    d.  O Juiz retorna uma avaliação estruturada (JSON), que é coletada.
5.  **Encerramento (`runner._process_task`)**: O `conversation_manager.close()` é chamado para limpar os recursos da conversa.
6.  **Coleta de Resultados**: O `runner` agrega os resultados de todas as tarefas.
7.  **Salvamento (`main.py`)**: Os resultados finais são salvos em um arquivo JSON.
