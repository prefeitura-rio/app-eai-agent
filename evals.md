# Resumo da Estrutura de Avaliação

Este documento detalha a estrutura e a funcionalidade dos arquivos no diretório `src/evaluations/core/`. O sistema é projetado para carregar dados, executar experimentos de avaliação de LLM de forma assíncrona, avaliar as respostas usando "juízes" de LLM e registrar os resultados.

---

### 1. `dataloader.py`

Este arquivo é responsável por carregar e preparar os dados para os experimentos de avaliação.

-   **Classe `DataLoader`**:
    -   **Propósito**: Carrega dados de várias fontes (arquivos CSV, Google Sheets ou DataFrames do pandas), valida as colunas necessárias e formata os dados em "tarefas" para avaliação.
    -   **Método `__init__`**:
        -   Recebe uma fonte de dados, nomes de colunas para ID, prompt e metadados.
        -   Recebe o nome e a descrição do conjunto de dados.
        -   Cria uma configuração de conjunto de dados determinística, incluindo um ID de hash.
        -   Opcionalmente, faz o upload da configuração e dos dados para o BigQuery.
    -   **Método `_load_from_file`**: Carrega dados de um arquivo CSV.
    -   **Método `_load_from_gsheet`**: Carrega dados de uma planilha do Google Sheets usando a URL de exportação CSV.
    -   **Método `_validate_columns`**: Garante que todas as colunas essenciais existam no DataFrame.
    -   **Método `get_tasks`**: Retorna um gerador que produz cada linha do DataFrame como um dicionário de tarefas padronizado, pronto para ser usado pelo executor do experimento.

---

### 2. `llm_clients.py`

Este arquivo define os clientes para interagir com os modelos de linguagem (LLMs), tanto para o agente que está sendo avaliado quanto para o "juiz" que realiza a avaliação.

-   **Classe `AgentConversationManager`**:
    -   **Propósito**: Gerencia o ciclo de vida de uma única conversa com um agente através da API EAI Gateway. Garante que um `agent_id` consistente seja usado para todas as interações em uma conversa.
    -   **Método `initialize`**: Cria um novo agente usando a API e armazena o `agent_id` para a sessão.
    -   **Método `send_message`**: Envia uma mensagem para o agente criado e aguarda a resposta completa, incluindo a cadeia de pensamento (reasoning).
    -   **Método `close`**: Encerra a sessão de conversação.

-   **Classe `AzureOpenAIClient`**:
    -   **Propósito**: Cliente para interagir com a API do Azure OpenAI. Usado principalmente para o "juiz" da avaliação.
    -   **Método `execute`**: Envia um prompt para o modelo do Azure e retorna a resposta de texto.

-   **Classe `GeminiAIClient`**:
    -   **Propósito**: Cliente para interagir com a API do Google Gemini. Também usado como um "juiz".
    -   **Método `execute`**: Envia um prompt para o modelo Gemini e retorna a resposta de texto.

---

### 3. `prompt_judges.py`

Este arquivo é um repositório central para todos os templates de prompt usados pelos "juízes" LLM para avaliar as respostas do agente.

-   **Constantes de Prompt**:
    -   `CONVERSATIONAL_JUDGE_PROMPT`: Usado para guiar o juiz durante uma conversa multi-turno, instruindo-o sobre como continuar ou encerrar a conversa com base em um roteiro.
    -   `FINAL_CONVERSATIONAL_JUDGEMENT_PROMPT`: Usado para uma avaliação final do **raciocínio** do agente após uma conversa completa.
    -   `FINAL_MEMORY_JUDGEMENT_PROMPT`: Usado para uma avaliação final da **memória** do agente após uma conversa completa.
    -   `SEMANTIC_CORRECTNESS_PROMPT`: Avalia a correção semântica de uma resposta de turno único em comparação com uma resposta ideal ("golden").
    -   `PERSONA_ADHERENCE_PROMPT`: Avalia se a resposta de turno único do agente adere a uma persona predefinida.

---

### 4. `evals.py`

Este arquivo contém a lógica de avaliação principal, usando os clientes LLM e os prompts de julgamento para pontuar as respostas do agente.

-   **Decorador `@eval_method`**:
    -   Registra uma função de avaliação em um registro global (`_EVAL_METHODS_REGISTRY`), especificando seu nome e o tipo de avaliação (`one` para turno único, `multiple` para multi-turno).

-   **Classe `Evals`**:
    -   **Propósito**: Contém os métodos de avaliação que chamam o LLM juiz.
    -   **Método `_get_llm_judgement`**: Uma função auxiliar que formata um prompt com os dados da tarefa, envia-o para o cliente juiz e extrai uma pontuação numérica da resposta.
    -   **Métodos de Avaliação (decorados com `@eval_method`)**:
        -   `conversational_reasoning`: Avalia o raciocínio em uma conversa multi-turno.
        -   `conversational_memory`: Avalia a memória em uma conversa multi-turno.
        -   `semantic_correctness`: Avalia a correção semântica de uma resposta de turno único.
        -   `persona_adherence`: Avalia a aderência à persona de uma resposta de turno único.

-   **Classe `ConversationHandler`**:
    -   **Propósito**: Orquestra uma conversa completa entre o agente e o juiz LLM.
    -   **Método `conduct`**: Inicia uma conversa, envia mensagens em turnos, obtém a próxima ação do juiz e continua até que um sinal de parada seja recebido. Retorna a transcrição completa da conversa.

---

### 5. `runner.py`

Este arquivo contém o orquestrador principal para executar um experimento de avaliação de ponta a ponta.

-   **Classe `AsyncExperimentRunner`**:
    -   **Propósito**: Gerencia a execução de todas as tarefas em um conjunto de dados, executa as avaliações de forma concorrente e compila os resultados.
    -   **Método `__init__`**: Configura o nome do experimento, metadados, configuração do agente, suíte de avaliação e o nível de concorrência. Pode ser inicializado com respostas pré-computadas para evitar a execução ao vivo do agente.
    -   **Método `_process_task`**: Processa uma única tarefa do conjunto de dados. Ele obtém a resposta do agente (seja ao vivo ou pré-computada), executa todas as avaliações configuradas em paralelo e retorna um resultado estruturado para a tarefa.
    -   **Métodos `_get_one_turn_response` e `_get_multi_turn_transcript`**: Funções auxiliares para obter as respostas do agente, usando dados pré-computados se disponíveis.
    -   **Método `_execute_evaluations`**: Executa as funções de avaliação relevantes para uma tarefa, medindo o tempo de execução.
    -   **Métodos de sumarização (`_calculate_metrics_summary`, `_calculate_error_summary`)**: Calculam métricas agregadas (média, mediana, etc.) e resumos de erros em todos os `runs`.
    -   **Método `run`**: O ponto de entrada principal. Pega um `DataLoader`, itera sobre as tarefas, processa-as em paralelo usando `asyncio.gather` e `tqdm` para uma barra de progresso, calcula os resumos e salva o resultado final em um arquivo JSON e, opcionalmente, no BigQuery.

---

### 6. `utils.py`

Este arquivo fornece funções de utilidade, principalmente para o processamento dos dados de resposta.

-   **Função `parse_reasoning_messages`**:
    -   **Propósito**: Transforma a lista de mensagens brutas retornadas pela API EAI Gateway em uma estrutura mais limpa e padronizada.
    -   **Lógica**: Itera sobre as mensagens, extrai o conteúdo relevante com base no `message_type` e tenta analisar strings JSON aninhadas (como argumentos de chamada de ferramenta ou retornos de ferramenta) em objetos Python.

---

### 7. `main.py`

Este arquivo serve como o ponto de entrada para executar um experimento de exemplo.

-   **Função `run_experiment`**:
    -   **Propósito**: Demonstra como configurar e executar um experimento completo.
    -   **Passos**:
        1.  **Define o Dataset**: Cria um `DataLoader` com um DataFrame de exemplo.
        2.  **Define o Agente**: Cria um `CreateAgentRequest` com a configuração do agente a ser testado.
        3.  **Define a Suíte de Avaliação**: Instancia um cliente juiz (por exemplo, `AzureOpenAIClient`) e a classe `Evals`.
        4.  **Configura o Runner**: Instancia o `AsyncExperimentRunner` com todas as configurações, incluindo metadados, métricas a serem executadas e, opcionalmente, respostas pré-computadas.
        5.  **Executa**: Chama o método `runner.run()` para iniciar o processo de avaliação.