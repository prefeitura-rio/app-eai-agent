# Resumo da Estrutura e Funcionamento do Framework de Avaliação

O diretório `src/evaluations/core/` contém o framework principal para a avaliação de agentes de IA. A estrutura foi refatorada para promover a modularidade e a separação de responsabilidades.

### Estrutura de Arquivos

```
src/evaluations/core/
├── eval/
│   ├── __init__.py                 # Ponto de entrada do pacote `eval`
│   ├── dataloader.py               # Carregamento e preparação de dados
│   ├── llm_clients.py              # Clientes para interagir com LLMs (agentes e juízes)
│   ├── schemas.py                  # Modelos Pydantic para estruturação de dados
│   ├── log.py                      # Configuração de logging contextualizado
│   ├── utils.py                    # Funções utilitárias
│   ├── evaluators/                 # Lógica de avaliação de métricas
│   │   ├── __init__.py
│   │   ├── base.py                 # Classes base para todos os avaliadores
│   │   └── llm_guided_conversation.py # Avaliador que conduz uma conversa
│   └── runner/                     # Orquestração e execução de experimentos
│       ├── __init__.py
│       ├── orchestrator.py         # O orquestrador principal do experimento
│       ├── persistence.py          # Lógica para salvar resultados
│       ├── response_manager.py     # Gerencia a obtenção de respostas do agente
│       ├── result_analyzer.py      # Analisa os resultados agregados
│       └── task_processor.py       # Processa uma única tarefa de avaliação
└── experiments/
    └── ... (Estrutura de experimentos específicos, como 'batman')
```

### Detalhamento dos Arquivos e Classes

#### 1. `eval/dataloader.py`

-   **`DataLoader`**:
    -   **Responsabilidade**: Carregar dados de diferentes fontes (CSV, Google Sheets, DataFrame), validar a presença de colunas essenciais e preparar os dados como tarefas de avaliação.
    -   **Métodos Principais**:
        -   `__init__(...)`: Inicializa com a fonte de dados, nomes de colunas e metadados do dataset. Pode fazer o upload para o BigQuery.
        -   `get_tasks()`: Retorna um gerador de objetos `EvaluationTask`, que são usados pelo runner.
        -   `get_dataset_config()`: Retorna um dicionário com metadados do dataset, incluindo um ID determinístico.

#### 2. `eval/llm_clients.py`

-   **`AgentConversationManager`**:
    -   **Responsabilidade**: Gerenciar o ciclo de vida de uma conversa com um agente EAI, garantindo que o mesmo `agent_id` seja usado em todas as interações.
    -   **Métodos Principais**:
        -   `initialize()`: Cria o agente via API antes de qualquer interação.
        -   `send_message(...)`: Envia uma mensagem para o agente e retorna um `AgentResponse` padronizado, com o *reasoning* já processado.
        -   `close()`: Encerra a conversa.
-   **`BaseJudgeClient` (Abstrata)**:
    -   **Responsabilidade**: Define a interface para qualquer cliente de LLM que atuará como "juiz", garantindo um método `execute`.
-   **`AzureOpenAIClient` / `GeminiAIClient`**:
    -   **Responsabilidade**: Implementações concretas do `BaseJudgeClient` para os respectivos serviços de LLM.

#### 3. `eval/schemas.py`

-   **Responsabilidade**: Define a estrutura de todos os dados usados no framework de avaliação usando Pydantic. Isso garante consistência e validação automática.
-   **Schemas Principais**:
    -   `EvaluationTask`: Uma única tarefa de avaliação (uma linha do dataset).
    -   `AgentResponse`: A resposta de um agente, incluindo o output final e o *reasoning trace*.
    -   `EvaluationResult`: A saída padronizada de um avaliador (score, anotações, erro).
    -   `ConversationTurn`: Um único turno (usuário + agente) em uma conversa.
    -   `RunResult`: O resultado completo para uma única `EvaluationTask`, agregando as análises de turno único e múltiplos turnos.

#### 4. `eval/evaluators/base.py`

-   **`BaseEvaluator` (Abstrata)**:
    -   **Responsabilidade**: Classe base para todos os avaliadores de métricas. Define a interface (`evaluate`) e fornece um método auxiliar (`_get_llm_judgement`) para formatar o prompt e obter o julgamento do LLM.
-   **`BaseConversationEvaluator` (Abstrata)**:
    -   **Responsabilidade**: Classe base para avaliadores que **geram** uma conversa multi-turno. Seu propósito não é pontuar, mas sim produzir a transcrição que outros avaliadores irão analisar.

#### 5. `eval/runner/` (Componentes do Runner Refatorado)

-   **`orchestrator.py` -> `AsyncExperimentRunner`**:
    -   **Responsabilidade**: Orquestrador de alto nível. Inicializa os outros componentes, carrega as tarefas e coordena o fluxo do experimento.
    -   **Método Principal**: `run(loader)`: Executa o experimento completo, delegando o trabalho para os outros componentes.
-   **`response_manager.py` -> `ResponseManager`**:
    -   **Responsabilidade**: Abstrai a origem das respostas do agente (execução ao vivo ou cache pré-computado).
    -   **Métodos Principais**: `get_one_turn_response()`, `get_multi_turn_transcript()`.
-   **`task_processor.py` -> `TaskProcessor`**:
    -   **Responsabilidade**: Processa **uma única** `EvaluationTask`. Obtém as respostas via `ResponseManager`, executa os avaliadores e retorna o `RunResult`.
    -   **Método Principal**: `process(task)`.
-   **`result_analyzer.py` -> `ResultAnalyzer`**:
    -   **Responsabilidade**: Calcula todas as estatísticas agregadas (médias, desvio padrão, taxas de erro) a partir da lista completa de `RunResult`.
    -   **Método Principal**: `analyze(runs, total_duration)`.
-   **`persistence.py` -> `ResultPersistence`**:
    -   **Responsabilidade**: Salva os resultados finais em disco (JSON) e, opcionalmente, no BigQuery.
    -   **Método Principal**: `save(final_result)`.
