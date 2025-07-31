# Plano de Integração com BigQuery para Resultados de Avaliações

Este documento descreve o plano para persistir os resultados dos experimentos de avaliação em tabelas no Google BigQuery. O objetivo é criar um repositório de dados estruturado que possa ser facilmente consultado para análises e para alimentar um frontend de visualização.

A integração será dividida em duas tabelas principais: `datasets` e `experiments`.

---

## 1. Tabela `datasets`

Esta tabela armazenará uma versão imutável de cada conjunto de dados usado em um experimento. O `dataset_id`, gerado a partir do hash do conteúdo, garante que um mesmo dataset não seja duplicado.

### 1.1. Schema da Tabela

| Nome da Coluna        | Tipo de Dado | Descrição                                                                                             |
| --------------------- | ------------ | ----------------------------------------------------------------------------------------------------- |
| `dataset_id`          | `STRING`     | **Chave Primária.** Identificador único e determinístico do dataset, gerado via hash do seu conteúdo.   |
| `dataset_name`        | `STRING`     | Nome legível e descritivo para o conjunto de dados.                                                   |
| `dataset_description` | `STRING`     | Descrição detalhada sobre o propósito e o conteúdo do dataset.                                        |
| `created_at`          | `TIMESTAMP`  | Timestamp de quando o dataset foi registrado pela primeira vez no BigQuery.                           |
| `data`                | `JSON`       | Um campo JSON contendo a lista completa de todas as "tarefas" do dataset, como gerado pelo `DataLoader`. |

### 1.2. Plano de Implementação

-   **Arquivo Responsável**: `src/evaluations/core/dataloader.py`
-   **Classe**: `DataLoader`
-   **Método de Gatilho**: A lógica de upload será adicionada ao final do método `__init__`.

**Lógica Detalhada:**

1.  Ao final do método `__init__` da classe `DataLoader`, após a criação do `self._dataset_config`, uma nova função privada será chamada, por exemplo, `self._upload_dataset_to_bq()`.
2.  Esta função irá:
    a.  Inicializar um cliente BigQuery.
    b.  Executar uma verificação para evitar duplicatas: `SELECT dataset_id FROM datasets WHERE dataset_id = @id LIMIT 1`, usando o `dataset_id` recém-gerado.
    c.  **Se o `dataset_id` não existir na tabela**, a função prosseguirá com a inserção.
    d.  Os dados para a inserção serão mapeados da seguinte forma:
        -   `dataset_id`: `self._dataset_config['dataset_id']`
        -   `dataset_name`: `self._dataset_config['dataset_name']`
        -   `dataset_description`: `self._dataset_config['dataset_description']`
        -   `created_at`: `self._dataset_config['dataset_created_at']`
        -   `data`: O DataFrame `self.df` será convertido para uma string JSON (`self.df.to_json(orient='records')`) e inserido no campo `JSON`.
3.  A chamada para `_upload_dataset_to_bq()` será envolvida em um bloco `try...except` para que, em caso de falha na comunicação com o BigQuery, a execução principal do experimento não seja interrompida.

---

## 2. Tabela `experiments`

Esta tabela armazenará o resultado de alto nível de cada execução de um experimento. Cada linha corresponde a um relatório completo gerado pelo `AsyncExperimentRunner`.

### 2.1. Schema da Tabela

| Nome da Coluna           | Tipo de Dado | Descrição                                                                                                  |
| ------------------------ | ------------ | ---------------------------------------------------------------------------------------------------------- |
| `dataset_id`             | `STRING`     | **Chave de Partição.** ID do dataset usado neste experimento. Facilita a junção com a tabela `datasets`.      |
| `experiment_id`          | `STRING`     | **Chave Primária.** Identificador único para esta execução específica do experimento.                        |
| `experiment_name`        | `STRING`     | Nome legível do experimento.                                                                               |
| `experiment_description` | `STRING`     | Descrição detalhada dos objetivos do experimento.                                                          |
| `experiment_timestamp`   | `TIMESTAMP`  | Timestamp de quando o experimento foi concluído.                                                           |
| `experiment_metadata`    | `JSON`       | Objeto JSON contendo a configuração do agente (`agent_config`) e os prompts dos juízes (`judges_prompts`). |
| `execution_summary`      | `JSON`       | Objeto JSON com as métricas de tempo de execução (duração total, média por tarefa, etc.).                  |
| `error_summary`          | `JSON`       | Objeto JSON que resume as falhas, incluindo contagem de erros por métrica e IDs das tarefas com falha.     |
| `aggregate_metrics`      | `JSON`       | Objeto JSON com as estatísticas agregadas para cada métrica (média, mediana, distribuição de scores, etc.). |
| `runs`                   | `JSON`       | Objeto JSON contendo a lista detalhada de cada "run" (tarefa), incluindo a resposta do agente e avaliações. |

### 2.2. Plano de Implementação

-   **Arquivo Responsável**: `src/evaluations/core/runner.py`
-   **Classe**: `AsyncExperimentRunner`
-   **Método de Gatilho**: A lógica de upload será adicionada ao final do método `run`.

**Lógica Detalhada:**

1.  No método `run` da classe `AsyncExperimentRunner`, após o dicionário `final_result` ser completamente montado, uma nova função será chamada, por exemplo, `self._upload_experiment_to_bq(final_result)`.
2.  Esta função irá:
    a.  Inicializar um cliente BigQuery.
    b.  Executar uma operação de `INSERT` na tabela `experiments`. Não há necessidade de verificar a existência, pois cada `experiment_id` é um UUID novo.
    c.  O mapeamento dos dados do dicionário `final_result` para as colunas da tabela será direto. Os campos que são dicionários ou listas em Python (`experiment_metadata`, `execution_summary`, etc.) serão serializados para strings JSON antes da inserção nos campos `JSON` do BigQuery.
3.  A chamada será feita antes ou depois de salvar o arquivo JSON localmente e também será envolvida em um bloco `try...except` para garantir que a falha no upload não interrompa o fluxo principal.
