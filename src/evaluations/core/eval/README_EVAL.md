# EAI Evaluation Framework

Este documento detalha a arquitetura e o uso do Framework de Avaliação de Agentes de IA (`eval`). O framework é projetado para ser modular, extensível e fornecer resultados detalhados sobre o desempenho dos agentes.

## Visão Geral da Arquitetura

O framework opera em torno de alguns componentes principais que trabalham juntos para executar um experimento de ponta a ponta.

1.  **`AsyncExperimentRunner`**: O orquestrador central. Ele gerencia a execução concorrente de todas as tarefas, coleta os resultados e os passa para análise e persistência.
2.  **`DataLoader`**: Responsável por carregar os dados de teste de várias fontes (CSVs, Google Sheets, DataFrames pandas), validá-los e transformá-los em `EvaluationTask`, a unidade de trabalho do framework.
3.  **Avaliadores (`Evaluators`)**: O coração da avaliação. São classes modulares que herdam de uma base e encapsulam a lógica para medir uma métrica específica (ex: Aderência à Persona, Raciocínio Conversacional).
4.  **LLM-as-a-Judge**: O framework utiliza um LLM externo (o "Juiz") para realizar avaliações qualitativas. Cada avaliador define seu próprio prompt para instruir o juiz sobre como pontuar uma resposta.
5.  **`TaskProcessor`**: Processa uma única `EvaluationTask`, gerenciando a interação com o agente, a execução de todos os avaliadores relevantes e a coleta dos resultados.
6.  **Schemas Pydantic**: Todos os objetos de dados (`EvaluationTask`, `AgentResponse`, `EvaluationResult`, etc.) são estritamente definidos usando Pydantic para garantir a consistência e validação dos dados em todo o fluxo.

---

## Como Executar um Experimento

Siga estes passos para configurar e rodar um novo experimento.

### Passo 1: Estrutura de Pastas

Crie uma nova pasta para o seu experimento dentro de `src/evaluations/core/experiments/`. A estrutura recomendada é:

```
experiments/
└── nome_do_seu_experimento/
    ├── __init__.py
    ├── data/
    │   ├── __init__.py
    │   └── test_data.py  # Ou um arquivo .csv
    ├── evaluators/
    │   ├── __init__.py
    │   └── seu_avaliador_customizado.py
    └── run_eval.py
```

### Passo 2: Preparar o Dataset

Os dados para o experimento podem ser um `pd.DataFrame`, um arquivo `.csv` ou um Google Sheet. Cada linha do seu dataset representa uma tarefa de avaliação.

-   **Colunas Obrigatórias**:
    -   `id`: Um identificador único para cada tarefa.
    -   `prompt` (ou a coluna que você mapear para `prompt_col`): O prompt inicial que será enviado ao agente.
-   **Colunas de Metadados (Opcional)**: Você pode adicionar quantas colunas de metadados forem necessárias para suas avaliações (ex: `golden_response`, `persona`, `judge_context`).

### Passo 3: Criar os Avaliadores

Os avaliadores são o núcleo da sua medição. Existem três tipos principais:

#### A. `BaseOneTurnEvaluator`
Avalia uma única resposta do agente. Ideal para métricas como correção semântica ou aderência à persona em uma única interação.

**Exemplo (`semantic_correctness.py`):**
```python
from src.evaluations.core.eval import BaseOneTurnEvaluator, EvaluationTask, AgentResponse, EvaluationResult

class SemanticCorrectnessEvaluator(BaseOneTurnEvaluator):
    name = "semantic_correctness"
    PROMPT_TEMPLATE = """
    Avalie a similaridade semântica da resposta gerada pela IA em relação à Resposta Ideal.
    **Resposta Gerada pela IA:** {agent_response[message]}
    **Resposta Ideal:** {task[golden_response_one_shot]}
    ...
    Score: <um valor float>
    Reasoning: <uma explicação>
    """

    async def evaluate(self, agent_response: AgentResponse, task: EvaluationTask) -> EvaluationResult:
        return await self._get_llm_judgement(
            prompt_template=self.PROMPT_TEMPLATE,
            task=task,
            agent_response=agent_response,
        )
```

#### B. `BaseMultipleTurnEvaluator`
Avalia uma conversa completa (multi-turno). Requer que um `BaseConversationEvaluator` tenha sido executado primeiro para gerar a transcrição da conversa.

#### C. `BaseConversationEvaluator` (Gerador de Conversa)
Este tipo especial de avaliador não pontua nada. Sua função é **gerar a conversa** que será usada pelos `BaseMultipleTurnEvaluator`. A classe base já contém a lógica do loop de conversação. Para criar um gerador de conversa customizado, você só precisa herdar dela e implementar um método.

**Exemplo (`batman_llm_guided_conversation.py`):**
```python
from src.evaluations.core.eval import BaseConversationEvaluator, EvaluationTask
from typing import List

class BatmanLLMGuidedConversation(BaseConversationEvaluator):
    name = "batman_llm_guided_conversation"
    PROMPT_TEMPLATE = """
    Você é um Juiz de IA...
    **Seu Roteiro (Contexto Secreto):** {task[judge_context]}
    **Histórico da Conversa:** {history}
    ...
    Responda com a string de parada: `{stop_signal}`
    """

    def get_judge_prompt(self, task: EvaluationTask, history: List[str]) -> str:
        """Implementa a lógica para formatar o prompt que guia o juiz."""
        history_str = "\n".join(history)
        task_dict = task.model_dump(exclude_none=True)
        return self.PROMPT_TEMPLATE.format(
            task=task_dict,
            history=history_str,
            stop_signal=self.stop_signal,
        )
```

### Passo 4: Criar o Script `run_eval.py`

Este é o ponto de entrada do seu experimento. Ele consiste em 5 seções principais:

1.  **Definição do Dataset**:
    ```python
    from src.evaluations.core.eval import DataLoader
    from .data.test_data import YOUR_TEST_DATA # Dicionário ou DataFrame

    dataframe = pd.DataFrame(YOUR_TEST_DATA)
    loader = DataLoader(
        source=dataframe,
        id_col="id",
        prompt_col="initial_prompt",
        dataset_name="My Awesome Test",
        dataset_description="Description of my test.",
        metadata_cols=["persona", "golden_response_one_shot", "judge_context"],
    )
    ```

2.  **Definição do Agente**:
    ```python
    from src.services.eai_gateway.api import CreateAgentRequest

    agent_config = CreateAgentRequest(
        model="google_ai/gemini-1.5-pro-latest",
        system="Você é um agente prestativo.",
        tools=["google_search"],
        name="MyTestAgent",
    )
    ```

3.  **Definição da Suíte de Avaliação**:
    ```python
    from src.evaluations.core.eval import AzureOpenAIClient
    from .evaluators import (
        BatmanLLMGuidedConversation,
        ConversationalReasoningEvaluator,
        SemanticCorrectnessEvaluator,
    )

    judge_client = AzureOpenAIClient(model_name="gpt-4o")

    evaluators_to_run = [
        BatmanLLMGuidedConversation(judge_client), # Gerador da conversa
        ConversationalReasoningEvaluator(judge_client), # Analisa a conversa
        SemanticCorrectnessEvaluator(judge_client), # Analisa o turno único
    ]
    ```

4.  **(Opcional) Respostas Pré-computadas**:
    Para acelerar o desenvolvimento, você pode fornecer um JSON com respostas já geradas, pulando a interação ao vivo com o agente.
    ```python
    # precomputed_responses_dict = ...
    ```

5.  **Configuração e Execução do Runner**:
    ```python
    from src.evaluations.core.eval import AsyncExperimentRunner

    runner = AsyncExperimentRunner(
        experiment_name="My_Experiment_V1",
        experiment_description="First version of my awesome experiment.",
        metadata={"agent_config": agent_config.model_dump(), "judge_model": judge_client.model_name},
        agent_config=agent_config.model_dump(),
        evaluators=evaluators_to_run,
        # precomputed_responses=precomputed_responses_dict,
        upload_to_bq=False,
        output_dir=Path(__file__).parent / "data",
    )
    await runner.run(loader)
    ```

---

## Schema do Resultado (`results_*.json`)

O resultado de um experimento é um arquivo JSON rico em detalhes. Aqui está a estrutura completa:

```json
{
  "dataset_name": "Nome do seu dataset",
  "dataset_description": "Descrição do seu dataset",
  "dataset_id": 1234567890123456789,
  "experiment_id": 9876543210987654321,
  "experiment_name": "Nome do seu experimento",
  "experiment_description": "Descrição do seu experimento",
  "experiment_timestamp": "2025-08-01T18:00:00.000Z",
  "experiment_metadata": {
    "agent_config": { "..."},
    "judge_model": "gpt-4o",
    "judges_prompts": { "metric_name": "prompt_template_string" }
  },
  "execution_summary": {
    "total_duration_seconds": 60.0,
    "average_task_duration_seconds": 30.0,
    "average_metric_duration_seconds": 5.0
  },
  "error_summary": {
    "total_failed_runs": 1,
    "errors_per_metric": {
      "conversational_reasoning": 1
    },
    "failed_run_ids": ["task_id_002"]
  },
  "aggregate_metrics": [
    {
      "metric_name": "semantic_correctness",
      "total_runs": 2,
      "successful_runs": 2,
      "success_rate_percentage": 100.0,
      "failed_runs": 0,
      "failure_rate_percentage": 0.0,
      "score_statistics": {
        "average": 0.75, "median": 0.75, "min": 0.5, "max": 1.0, "std_dev": 0.35
      },
      "duration_statistics_seconds": { "..."},
      "score_distribution": [
        { "value": 0.5, "count": 1, "percentage": 50.0 },
        { "value": 1.0, "count": 1, "percentage": 50.0 }
      ]
    }
  ],
  "runs": [
    {
      "duration_seconds": 30.0,
      "task_data": {
        "id": "task_id_001",
        "prompt": "Qual a capital da França?",
        "golden_response_one_shot": "Paris."
      },
      "one_turn_analysis": {
        "agent_message": "A capital da França é Paris.",
        "agent_reasoning_trace": [
          {
            "message_type": "reasoning_message",
            "content": "O usuário fez uma pergunta factual."
          },
          {
            "message_type": "assistant_message",
            "content": "A capital da França é Paris."
          }
        ],
        "evaluations": [
          {
            "metric_name": "semantic_correctness",
            "duration_seconds": 2.5,
            "score": 1.0,
            "annotations": "Score: 1.0\nReasoning: A resposta é semanticamente idêntica à resposta ideal.",
            "has_error": false,
            "error_message": null
          }
        ],
        "has_error": false,
        "error_message": null
      },
      "multi_turn_analysis": {
        "final_agent_message": "Sim, eu me lembro que seu nome é Dr. Crane.",
        "transcript": [
          {
            "turn": 1,
            "user_message": "Meu nome é Dr. Crane. Qual a capital da França?",
            "agent_message": "Paris.",
            "agent_reasoning_trace": [ { "..."} ]
          },
          {
            "turn": 2,
            "user_message": "Qual o meu nome?",
            "agent_message": "Sim, eu me lembro que seu nome é Dr. Crane.",
            "agent_reasoning_trace": [ { "..."} ]
          }
        ],
        "evaluations": [
          {
            "metric_name": "conversational_memory",
            "duration_seconds": 25.0,
            "score": 1.0,
            "annotations": "Score: 1.0\nReasoning: O agente lembrou o nome corretamente.",
            "has_error": false,
            "error_message": null
          }
        ],
        "has_error": false,
        "error_message": null
      }
    }
  ]
}
```