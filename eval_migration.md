# Plano de Melhorias para o Framework de Avaliação

## Objetivo

Refatorar o framework de avaliação (`src/evaluations/core`) para torná-lo mais modular, configurável, extensível e robusto. O objetivo é transformar o conjunto de scripts atual em uma ferramenta de avaliação mais poderosa e flexível, que permita a qualquer usuário definir e executar experimentos complexos sem a necessidade de modificar o código-fonte principal.

---

## Principais Pontos de Melhoria

### 1. Configuração Externalizada (Fim do Hardcoding)

- **Problema Atual**: A configuração do experimento (agente, dataset, métricas, modelo do juiz) está "hardcoded" no script `main.py`. Isso torna a execução de diferentes testes um processo manual e propenso a erros, exigindo a edição direta do código.
- **Proposta**: Mover toda a configuração do experimento para um arquivo externo, como `experiment.yaml` ou `config.json`. O script principal (`main.py`) se tornaria apenas um executor que carrega esse arquivo de configuração.

- **Exemplo de `experiment.yaml`**:
  ```yaml
  experiment_name: "Batman_Unified_Eval_v2"
  experiment_description: "Teste com o novo modelo de agente e métricas de segurança."

  dataset:
    source: "https://docs.google.com/spreadsheets/d/..."
    id_col: "id"
    prompt_col: "initial_prompt"
    metadata_cols: ["persona", "golden_response"]

  agent_to_evaluate:
    model: "google_ai/gemini-3.0-pro"
    system: "Você é o Batman, um herói sombrio e vigilante."
    tools: ["google_search"]
    tags: ["batman", "v2"]

  judge:
    client: "AzureOpenAI"
    model_name: "gpt-4o-mini"

  metrics_to_run:
    - "semantic_correctness"
    - "persona_adherence"
    - "conversational_reasoning"
  ```

### 2. Arquitetura de Plugins para Avaliações

- **Problema Atual**: Para adicionar uma nova métrica de avaliação, é necessário editar o arquivo `evals.py`, adicionar um novo método à classe `Evals` e registrá-lo com o decorador `@eval_method`. Isso centraliza a lógica e dificulta a extensão.
- **Proposta**: Implementar um sistema de plugins. Poderíamos ter um diretório `evaluations/metrics/` onde cada arquivo `.py` define uma ou mais funções de avaliação. O `runner` poderia descobrir e carregar dinamicamente essas funções com base na lista `metrics_to_run` do arquivo de configuração. Isso tornaria a adição de novas métricas um processo de "arrastar e soltar".

### 3. Melhoria na Robustez e Tratamento de Erros

- **Problema Atual**: As chamadas de rede para a EAI Gateway e para os LLMs Juízes podem falhar por motivos transitórios (ex: sobrecarga da API, problemas de rede). Atualmente, uma falha em uma única tarefa pode não ser tratada com resiliência.
- **Proposta**: Implementar um mecanismo de retentativas (retry) com backoff exponencial para todas as chamadas de rede críticas. Bibliotecas como `tenacity` podem ser usadas para adicionar essa funcionalidade de forma limpa e declarativa, aumentando significativamente a robustez do framework.

### 4. Relatórios e Saídas Aprimoradas

- **Problema Atual**: A saída é um único arquivo JSON gigante. Embora seja ótimo para análise programática, é difícil para um humano obter uma visão geral rápida do desempenho.
- **Proposta**: Além do JSON completo, gerar um relatório de resumo em formato Markdown (`summary.md`). Este relatório conteria:
    - Métricas agregadas (média, mediana, desvio padrão para cada score).
    - Uma tabela com os resultados de cada tarefa.
    - Uma seção destacando as tarefas que falharam ou tiveram as piores pontuações.

### 5. Refatoração e Desacoplamento do Código

- **Problema Atual**: A classe `AsyncExperimentRunner` tem muitas responsabilidades, incluindo a lógica de como conduzir uma conversa (`_conduct_conversation`).
- **Proposta**: Extrair a lógica de gerenciamento da conversa para uma classe dedicada, como `ConversationHandler`. O `runner` delegaria a responsabilidade de interagir com o agente para essa classe, focando apenas na orquestração geral do experimento e na coleta de resultados. Isso melhora a separação de conceitos (Separation of Concerns) e a legibilidade.

---

## Plano de Ação Proposto

1.  **Fase 1: Configuração e Desacoplamento**
    - [ ] Definir a estrutura do arquivo `experiment.yaml`.
    - [ ] Modificar `main.py` para ler o arquivo YAML e passar os dicionários de configuração para os componentes.
    - [ ] Adaptar `DataLoader`, `AsyncExperimentRunner` e `Evals` para receberem seus parâmetros a partir da configuração, em vez de tê-los hardcoded.

2.  **Fase 2: Arquitetura de Plugins**
    - [ ] Refatorar a classe `Evals` para ser um carregador de plugins.
    - [ ] Criar um diretório `metrics/` e mover as avaliações existentes para arquivos individuais dentro dele.
    - [ ] Modificar o `runner` para carregar dinamicamente as funções de avaliação necessárias.

3.  **Fase 3: Robustez e Relatórios**
    - [ ] Integrar a biblioteca `tenacity` para adicionar retentativas às chamadas de API em `llm_clients.py`.
    - [ ] Adicionar uma nova função ao `runner` para gerar um `summary.md` após a conclusão de todos os testes.

## Benefícios Esperados

- **Flexibilidade**: Executar qualquer tipo de experimento sem tocar no código.
- **Extensibilidade**: Adicionar novas métricas de avaliação de forma simples e isolada.
- **Robustez**: Maior resiliência a falhas de rede e problemas transitórios.
- **Manutenibilidade**: Código mais limpo, desacoplado e fácil de entender.
- **Melhor Experiência do Usuário**: Relatórios mais claros e úteis para análise humana.
