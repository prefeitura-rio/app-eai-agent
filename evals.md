### **Resumo do Módulo de Avaliações (`src/evaluations/core`)**

O diretório `src/evaluations/core` contém um sistema completo para avaliar agentes de IA de forma assíncrona e modular. Ele permite a execução de experimentos complexos para medir diversas capacidades dos agentes, como raciocínio, memória, aderência à persona e correção semântica.

**Arquitetura e Fluxo de Execução:**

1.  **Carregamento dos Dados (`dataloader.py`):** O processo começa com o `DataLoader`, que carrega os dados de teste (prompts, contextos, respostas esperadas) de fontes como CSV, Google Sheets ou DataFrames do pandas. Ele padroniza esses dados em "tarefas" e pode versionar o dataset no BigQuery.

2.  **Configuração do Experimento (`main.py`):** Este é o ponto de entrada. Aqui, você define qual dataset será usado, qual agente será avaliado (configurando seu modelo, system prompt, ferramentas, etc.) e quais métricas de avaliação (`evals`) serão aplicadas.

3.  **Execução Orquestrada (`runner.py`):** O `AsyncExperimentRunner` é o maestro do processo. Ele gerencia a execução concorrente das tarefas, controlando o paralelismo para não sobrecarregar os sistemas. Para cada tarefa, ele:
    *   Obtém a resposta do agente, seja em uma interação de turno único ou em uma conversa complexa de múltiplos turnos.
    *   Coleta a resposta final e também a "cadeia de raciocínio" (reasoning trace) do agente.
    *   Submete a resposta a um ou mais "juízes" (LLMs como o GPT-4o) para avaliação.

4.  **Lógica de Avaliação (`evals.py`):** A classe `Evals` contém a implementação de cada métrica. Ela utiliza prompts específicos, definidos em `prompt_judges.py`, para instruir um LLM juiz a pontuar a performance do agente em critérios como "correção semântica" ou "raciocínio conversacional".

5.  **Geração dos Resultados (`runner.py`):** Ao final de todas as execuções, o runner agrega as pontuações, calcula estatísticas detalhadas (média, mediana, desvio padrão, etc.) e salva um arquivo JSON completo com todos os dados do experimento, incluindo os resultados de cada tarefa individual e os metadados do teste.

---

### **Detalhamento por Arquivo:**

*   **`main.py`**:
    *   **Propósito:** Ponto de entrada para rodar um experimento.
    *   **Principais Funções:** `run_experiment()` que configura o `DataLoader`, o agente, a suíte de avaliação (com o cliente LLM para o juiz) e o `AsyncExperimentRunner`. Permite carregar respostas pré-computadas para acelerar a fase de julgamento.

*   **`dataloader.py`**:
    *   **Propósito:** Carregar e preparar os dados.
    *   **Classe Principal:** `DataLoader` que lida com a ingestão de dados de diferentes fontes, valida as colunas necessárias e gera um ID determinístico para o dataset, garantindo rastreabilidade.

*   **`runner.py`**:
    *   **Propósito:** Orquestrar a execução assíncrona do experimento.
    *   **Classe Principal:** `AsyncExperimentRunner` que gerencia o paralelismo, obtém as respostas do agente (sejam elas ao vivo ou de um cache), executa as avaliações de forma concorrente, calcula métricas agregadas e salva o resultado final em JSON, com a opção de fazer upload para o BigQuery.

*   **`evals.py`**:
    *   **Propósito:** Definir as métricas de avaliação.
    *   **Decorador:** `@eval_method` que registra uma função como um método de avaliação, especificando se ela se aplica a conversas de turno único ou múltiplos turnos.
    *   **Classe Principal:** `Evals` que contém a lógica para cada avaliação (ex: `conversational_reasoning`, `persona_adherence`), usando um cliente LLM "juiz" para pontuar o agente.
    *   **Classe Auxiliar:** `ConversationHandler` que gerencia uma conversa de múltiplos turnos, onde o juiz guia a interação para testar o agente de forma dinâmica.

*   **`llm_clients.py`**:
    *   **Propósito:** Abstrair a comunicação com as APIs dos LLMs e do agente.
    *   **Classe Principal:** `AgentConversationManager` que gerencia o ciclo de vida de uma conversa com um agente através da API EAI Gateway, cuidando da criação, envio de mensagens e encerramento da sessão.
    *   **Classes de Cliente:** `AzureOpenAIClient` e `GeminiAIClient` que implementam a comunicação com as APIs da OpenAI e do Google, respectivamente. São usadas principalmente para os julgamentos.

*   **`prompt_judges.py`**:
    *   **Propósito:** Centralizar todos os templates de prompts usados pelos juízes LLM. Isso torna as avaliações mais consistentes e fáceis de manter.

*   **`test_data.py`**:
    *   **Propósito:** Fornecer um conjunto de dados estático para os testes.
    *   **Conteúdo:** O dicionário `UNIFIED_TEST_DATA` que contém IDs, prompts iniciais, personas, contextos para o juiz e as respostas esperadas ("golden").

*   **`utils.py`**:
    *   **Propósito:** Fornecer funções utilitárias.
    *   **Função Principal:** `parse_reasoning_messages` que transforma a lista de mensagens brutas da API do agente em uma estrutura limpa e padronizada, facilitando a análise.
