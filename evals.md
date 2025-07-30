# Documentação do Framework de Avaliação (`src/evaluations/core`)

## Sumário

O diretório `src/evaluations/core` contém um framework robusto e assíncrono para a avaliação automatizada de agentes de IA conversacionais. Ele foi projetado para orquestrar experimentos complexos que medem múltiplas facetas do desempenho de um agente, como raciocínio, memória, aderência à persona e correção semântica.

O sistema opera com base nos seguintes componentes principais:
- **Runner**: O orquestrador central que gerencia a execução do experimento.
- **DataLoader**: Responsável por carregar e preparar os dados de teste de várias fontes.
- **LLM Clients**: Clientes para interagir tanto com o agente a ser avaliado (via `AgentConversationManager`) quanto com os LLMs "Juízes" que realizam a avaliação (`AzureOpenAIClient`, `GeminiAIClient`).
- **Evals**: Uma suíte de métodos de avaliação que utilizam os Juízes para pontuar as respostas do agente.
- **Prompt Judges**: Uma coleção centralizada de templates de prompt que guiam o comportamento dos Juízes.
- **Test Data**: Um conjunto de dados estruturado para os testes.

---

## Fluxo de Execução de um Experimento

1.  **Ponto de Entrada (`main.py`)**: O script `run_experiment` inicia o processo, configurando todos os componentes necessários.
2.  **Carregamento de Dados (`DataLoader`)**: O `DataLoader` é instanciado com os dados de teste (ex: `UNIFIED_TEST_DATA`), definindo as colunas de ID, prompt e metadados.
3.  **Configuração do Experimento**: O agente a ser testado, a suíte de avaliação (`Evals`) e as métricas a serem executadas são definidas.
4.  **Orquestração (`AsyncExperimentRunner`)**: O `runner` é inicializado com os metadados do experimento.
5.  **Execução de Tarefas**: O `runner` itera sobre cada "tarefa" fornecida pelo `DataLoader`.
    *   Para cada tarefa, ele instancia um `AgentConversationManager` para gerenciar a interação com o agente.
    *   Dependendo da métrica, ele conduz uma conversa de um ou múltiplos turnos. Em conversas multi-turno, um LLM Juiz pode ser usado para guiar a conversa dinamicamente com base em um roteiro (`judge_context`).
6.  **Avaliação (`Evals`)**: Após a conclusão da interação com o agente, o `runner` invoca os métodos de avaliação definidos na suíte `Evals`.
    *   Cada método de avaliação formata um prompt específico (de `prompt_judges.py`) com os dados da conversa e da tarefa.
    *   Ele envia este prompt para um LLM Juiz (`AzureOpenAIClient` ou `GeminiAIClient`) que retorna uma pontuação e um raciocínio.
7.  **Coleta de Resultados**: O `runner` coleta os resultados de todas as avaliações para todas as tarefas.
8.  **Salvamento**: Um arquivo JSON final contendo a configuração do dataset, os metadados do experimento e os resultados detalhados de cada "run" é salvo no diretório `evaluation_results/`.

---

## Detalhamento dos Componentes

### `main.py`
- **Propósito**: Ponto de entrada principal para a execução de um experimento.
- **Função Principal**: `run_experiment()`
- **Responsabilidades**:
    - Configurar o logging.
    - Definir o dataset a ser usado, instanciando o `DataLoader`.
    - Definir a configuração do agente a ser avaliado (`CreateAgentRequest`).
    - Instanciar o cliente LLM Juiz (ex: `AzureOpenAIClient`).
    - Instanciar a suíte de avaliações (`Evals`).
    - Definir a lista de métricas a serem executadas.
    - Instanciar e executar o `AsyncExperimentRunner`.

### `runner.py`
- **Classe Principal**: `AsyncExperimentRunner`
- **Propósito**: Orquestrar todo o ciclo de vida de um experimento de avaliação.
- **Responsabilidades**:
    - Gerenciar a execução assíncrona de múltiplas tarefas de avaliação em paralelo.
    - Para cada tarefa, conduzir a interação com o agente através do `AgentConversationManager`. As conversas podem ser de turno único ou múltiplo.
    - Invocar os métodos de avaliação (`Evals`) de forma concorrente após a interação.
    - Coletar, estruturar e agregar os resultados de todas as tarefas.
    - Gerar um ID de experimento único e metadados de execução.
    - Salvar o resultado final em um arquivo JSON formatado.

### `dataloader.py`
- **Classe Principal**: `DataLoader`
- **Propósito**: Carregar, validar e preparar dados de teste de diferentes fontes.
- **Responsabilidades**:
    - Carregar dados de arquivos CSV, Google Sheets ou DataFrames do pandas.
    - Validar a existência das colunas necessárias (ID, prompt, metadados).
    - Gerar uma configuração de dataset com um ID determinístico baseado no conteúdo dos dados, garantindo rastreabilidade.
    - Fornecer um gerador (`get_tasks()`) que produz cada linha do dataset como um dicionário de tarefa padronizado.

### `evals.py`
- **Classe Principal**: `Evals`
- **Propósito**: Conter a lógica para os diferentes métodos de avaliação.
- **Responsabilidades**:
    - Implementar métodos de avaliação específicos (ex: `conversational_reasoning`, `semantic_correctness`).
    - Utilizar um cliente LLM Juiz (`judge_client`) para obter julgamentos.
    - Formatar os prompts (de `prompt_judges.py`) com os dados da tarefa e a resposta do agente.
    - Extrair a pontuação e as anotações da resposta do Juiz.
- **Decorador**: `@eval_method(name, turns)`
    - Registra um método de avaliação, especificando seu nome e tipo de interação (`one` para turno único, `multiple` para múltiplos turnos). Este registro é usado pelo `runner` para orquestrar as interações com o agente corretamente.

### `llm_clients.py`
- **Propósito**: Abstrair a comunicação com diferentes LLMs, tanto para o agente em avaliação quanto para os juízes.
- **Classes Principais**:
    - `AgentConversationManager`: Gerencia o ciclo de vida de uma conversa com o agente sendo avaliado. Ele cria o agente via `EAIClient`, envia mensagens e mantém o `agent_id` para interações sequenciais.
    - `AzureOpenAIClient`: Cliente para interagir com os modelos da Azure OpenAI, usado principalmente para os LLMs Juízes.
    - `GeminiAIClient`: Cliente para interagir com os modelos da Google Gemini, também usado para os LLMs Juízes.

### `prompt_judges.py`
- **Propósito**: Centralizar todos os templates de prompt usados pelos LLMs Juízes.
- **Responsabilidades**:
    - Manter a consistência e facilitar a manutenção dos prompts.
- **Tipos de Prompts**:
    - **Condução da Conversa**: Prompts que instruem o Juiz a atuar como usuário para testar o agente dinamicamente.
    - **Julgamento Final**: Prompts para avaliar uma transcrição completa com base em critérios como raciocínio e memória.
    - **Avaliação de Turno Único**: Prompts para avaliações mais diretas, como correção semântica e aderência à persona.

### `test_data.py`
- **Propósito**: Fornecer um conjunto de dados estático e bem definido para os experimentos.
- **Variável Principal**: `UNIFIED_TEST_DATA`
- **Estrutura**: Um dicionário contendo listas de dados para cada coluna, incluindo:
    - `id`: Identificador único da tarefa.
    - `initial_prompt`: A primeira mensagem a ser enviada ao agente.
    - `persona`: A persona que o agente deve seguir.
    - `judge_context`: O "roteiro secreto" para o LLM Juiz conduzir a conversa.
    - `golden_summary`: O resumo do resultado esperado para avaliações de múltiplos turnos.
    - `golden_response`: A resposta ideal para avaliações de turno único.
