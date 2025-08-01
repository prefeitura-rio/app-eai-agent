# Plano de Migração do Frontend de Visualização de Experimentos

## 1. Introdução e Objetivo

Este documento descreve o plano de refatoração para a interface de visualização de experimentos, localizada em `src/frontend/app/experiments/**`. O objetivo principal é atualizar os componentes React e as definições de tipo para serem compatíveis com a nova estrutura de dados de saída (schema) gerada pelo framework de avaliação.

A nova estrutura organiza os resultados de forma mais lógica, separando as análises de turno único (`one_turn_analysis`) das de múltiplos turnos (`multi_turn_analysis`), e enriquece os dados com mais detalhes, como `reasoning_trace` e informações de erro explícitas.

---

## 2. Análise da Incompatibilidade de Dados

A principal fonte de problemas é a incompatibilidade entre a estrutura de dados que o frontend espera (`types.ts`) e a que o backend agora fornece.

#### Estrutura Antiga (Inferida do Frontend)

```typescript
// O que o frontend espera atualmente
interface ExperimentRun {
  // ...
  agent_response: {
    one_turn: string | null;
    multi_turn_final: string | null;
  };
  reasoning_trace: {
    one_turn: Step[] | null;
    multi_turn: Turn[] | null; // Também usado como transcrição
  };
  evaluations: Evaluation[]; // Lista plana com um campo 'eval_type'
}
```

#### Nova Estrutura (Fornecida pelo Backend)

```typescript
// O que o backend fornece agora
interface ExperimentRun { // Corresponde ao TaskOutput do backend
  // ...
  task_data: object;
  one_turn_analysis: {
    agent_message: string | null;
    agent_reasoning_trace: ReasoningStep[] | null;
    evaluations: Evaluation[] | [];
    has_error: boolean;
    error_message: string | null;
  };
  multi_turn_analysis: {
    final_agent_message: string | null;
    transcript: ConversationTurn[] | null;
    evaluations: Evaluation[] | [];
    has_error: boolean;
    error_message: string | null;
  };
}
```

---

## 3. Plano de Refatoração Detalhado

A migração será dividida em etapas, começando pela base (tipos) e subindo para os componentes.

### Etapa 1: Atualização das Definições de Tipo (`src/frontend/app/experiments/types.ts`)

Esta é a base para todas as outras mudanças.

1.  **Redefinir `ExperimentRun`**: Alterar a interface `ExperimentRun` para espelhar o schema `TaskOutput` do backend.
2.  **Criar Novas Interfaces**:
    -   `OneTurnAnalysis`
    -   `MultiTurnAnalysis`
    -   `ReasoningStep` (para a cadeia de pensamento)
    -   `ConversationTurn` (para a transcrição da conversa)
    -   Atualizar a interface `Evaluation` para corresponder aos campos `score`, `annotations`, `has_error`, etc.

### Etapa 2: Refatoração dos Componentes de Visualização

#### A. `RunDetails.tsx` (Componente Principal)

Este componente sofrerá as maiores mudanças, pois orquestra a exibição dos dados de um `run`.

1.  **Fonte de Dados**: A lógica do `viewMode` ('one_turn' vs 'multi_turn') será mantida, mas as fontes de dados mudarão:
    -   **Se `viewMode === 'one_turn'`**:
        -   A resposta do agente virá de `run.one_turn_analysis.agent_message`.
        -   Os dados para `ReasoningTimeline` virão de `run.one_turn_analysis.agent_reasoning_trace`.
        -   Os dados para `Evaluations` virão de `run.one_turn_analysis.evaluations`.
    -   **Se `viewMode === 'multi_turn'`**:
        -   A resposta final do agente virá de `run.multi_turn_analysis.final_agent_message`.
        -   Os dados para `ConversationTranscript` virão de `run.multi_turn_analysis.transcript`.
        -   Os dados para `Evaluations` virão de `run.multi_turn_analysis.evaluations`.

2.  **Tratamento de Erros**: O componente deve verificar os campos `has_error` e `error_message` em `one_turn_analysis` e `multi_turn_analysis`. Se `has_error` for `true`, ele deve exibir uma mensagem de erro clara (usando o `error_message`) em vez de tentar renderizar os componentes filhos para aquela visão.

#### B. Componentes Filhos

1.  **`Evaluations.tsx`**:
    -   Atualizar a assinatura do componente para receber `evaluations: OneTurnAnalysis['evaluations']`.
    -   Alterar a referência de `ev.judge_annotations` para `ev.annotations`.
    -   Adicionar lógica para exibir um estado de erro se `ev.has_error` for `true`.

2.  **`ReasoningTimeline.tsx`**:
    -   Atualizar a assinatura para receber `reasoningTrace: OneTurnAnalysis['agent_reasoning_trace']`.
    -   A lógica interna parece ser compatível, mas precisa receber os dados corretos.

3.  **`ConversationTranscript.tsx`**:
    -   Atualizar a assinatura para receber `transcript: MultiTurnAnalysis['transcript']`.
    -   Mapear os campos do objeto `ConversationTurn` para a exibição: `turn.user_message` (em vez de `judge_message`) e `turn.agent_message` (em vez de `agent_response`).
    -   **Melhoria Sugerida**: Adicionar um `Accordion` dentro de cada resposta do agente para mostrar o `agent_reasoning_trace` daquele turno específico, se disponível.

### Etapa 3: Refatoração da Lógica de Filtragem e Exportação

1.  **`Filters.tsx`**:
    -   A lógica de `filterOptions` está quebrada, pois depende de uma lista plana de avaliações.
    -   **Novo Plano**: O `useMemo` para `filterOptions` deve agora iterar sobre todos os `runs` e, para cada `run`, agregar as avaliações de `run.one_turn_analysis.evaluations` e `run.multi_turn_analysis.evaluations`.
    -   A função `applyFilters` também precisará ser atualizada para verificar as métricas em ambos os locais (`one_turn_analysis` e `multi_turn_analysis`) ao decidir se um `run` corresponde aos filtros.

2.  **`experiment-details-client.tsx` (Exportação de JSON)**:
    -   A função `handleDownloadCleanJson` e a interface `LlmJsonFilters` estão simplistas demais.
    -   **Novo Plano**:
        -   Atualizar `LlmJsonFilters` para refletir a nova estrutura, permitindo ao usuário escolher se quer incluir `one_turn_analysis` e/ou `multi_turn_analysis`.
        -   A função `handleDownloadCleanJson` deve construir o objeto `cleanedRuns` com base na nova estrutura, incluindo ou omitindo os objetos `one_turn_analysis` e `multi_turn_analysis` inteiros com base nos filtros.

### Etapa 4: Melhoria Geral da UI e Tratamento de Erros

1.  **Criar um Componente `ErrorDisplay`**:
    -   Sugerimos criar um componente reutilizável, por exemplo, `ErrorDisplay.tsx`, que receba um `message` e exiba um alerta de erro padronizado.
    -   Este componente será usado em `RunDetails.tsx` e outros locais onde `has_error` for `true`.

2.  **Atualizar `Metadata.tsx`**:
    -   A função `fillTemplate` que processa os prompts do juiz precisa ser atualizada. Ela atualmente busca `run.agent_response.one_turn` e `run.reasoning_trace.multi_turn`, que não existem mais.
    -   Ela deve ser modificada para buscar `run.one_turn_analysis.agent_message` e `run.multi_turn_analysis.transcript`, respectivamente.

## 4. Conclusão

A execução deste plano de refatoração irá sincronizar o frontend com as capacidades do backend, resultando em uma ferramenta de visualização mais robusta, precisa e informativa. A mudança mais significativa será a adaptação à estrutura aninhada de `one_turn_analysis` e `multi_turn_analysis`, que afetará a exibição, filtragem e exportação de dados.
