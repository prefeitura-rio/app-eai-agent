leia todos os arquivos da pasta @src/evaluations/core/ crie um resumo da estrutura dos arquivos e detalhe o que cada arquivo faz,, ssuas classes seus metodos e funcoes, save o resumo em evals.md  

# Plano de Migração para shadcn/ui

Este documento descreve o plano passo a passo para migrar a base de código do frontend existente para usar `shadcn/ui`. O objetivo é melhorar a consistência da UI, a acessibilidade, a experiência do desenvolvedor e a velocidade de implementação de novos recursos.

**É de EXTREMA IMPORTANCIA que as modificacoes em uma determinada pagina NAO AFETE as demais paginas!!!!!**

# Frontend Development Knowledge Base & Best Practices

## Introduction

This document serves as a comprehensive knowledge base and best practices guide for developing modern frontend applications. It is the result of an extensive migration and debugging process, capturing critical lessons learned to prevent common pitfalls and accelerate future development. The primary goal is to provide a canonical reference for AI and human developers working on this project, ensuring consistency, quality, and adherence to modern standards.

The core technology stack discussed is **Next.js 15 (with App Router)**, **Tailwind CSS v4**, and **shadcn/ui**. This combination represents a significant shift in frontend development, moving towards a "CSS-first" configuration and a more declarative, component-based architecture. This guide will detail the intricacies of this new paradigm, which proved to be a major source of errors and misunderstandings during the initial migration.

This is a living document. It should be updated as the project evolves and as new best practices emerge.

---

## 1. Core Philosophy & Final Configuration

After a lengthy and complex debugging process, a stable and correct configuration was achieved. The root cause of most issues was a misunderstanding of the new "CSS-first" paradigm introduced in Tailwind CSS v4 and how it interacts with `shadcn/ui`. This section presents the final, canonical configuration.

### 1.1. The Great Deception: `tailwind.config.ts` vs. `globals.css`

The most critical lesson is that for a modern Next.js 15 + Tailwind v4 project, the configuration strategy is fundamentally different from Tailwind v3.

-   **`tailwind.config.ts` is DEPRECATED for Theming:** In v3, this file was the heart of all configuration. In v4, its role is drastically reduced. For a `shadcn/ui` project, it is **NOT USED** for defining colors, fonts, or other theme values. Deleting it is the correct step.
-   **`globals.css` is the NEW Source of Truth:** All theme and design token configuration now lives inside `app/globals.css`.

### 1.2. The Correct `globals.css` Structure for Tailwind v4 + shadcn/ui

The structure of this file is precise and unforgiving. Errors in this structure will lead to build failures or a completely unstyled application. The correct structure follows a three-part pattern:

**Part 1: Define Raw CSS Variables (`:root` and `.dark`)**
First, you define all your theme variables as standard CSS custom properties. Crucially, the color values **must be wrapped in `hsl()`**.

```css
:root {
  --background: hsl(210 40% 98%);
  --foreground: hsl(222.2 84% 4.9%);
  --card: hsl(0 0% 100%);
  /* ... all other light theme variables ... */
}
 
.dark {
  --background: hsl(222.2 84% 4.9%);
  --foreground: hsl(210 40% 98%);
  --card: hsl(222.2 47.4% 11.2%);
  /* ... all other dark theme variables ... */
}
```

**Part 2: Bridge Variables to Tailwind (`@theme inline`)**
This is the "magic" step that was missed during debugging. The `@theme inline` directive tells Tailwind to take the existing CSS variables you defined in Part 1 and create utility classes from them.

-   Inside this block, you map Tailwind's conceptual theme colors (like `--color-background`) to your raw CSS variables (like `var(--background)`).
-   Crucially, you **do not** wrap the `var()` in `hsl()` here.

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-destructive: var(--destructive);
  /* ... and so on for all theme variables ... */
}
```
Without this block, classes like `bg-background` or `text-destructive` have no meaning to Tailwind, and styles will not be applied.

**Part 3: Apply Base Styles**
Finally, you apply your base styles to global elements like `body`.

```css
body {
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  background-color: var(--color-background);
  color: var(--color-foreground);
}
```

**The Complete, Correct `globals.css`:**
```css
@import "tailwindcss";
@import "tw-animate-css";

/* PART 1: Define raw HSL variables */
:root {
  --background: hsl(210 40% 98%);
  --foreground: hsl(222.2 84% 4.9%);
  --card: hsl(0 0% 100%);
  --card-foreground: hsl(222.2 84% 4.9%);
  --popover: hsl(0 0% 100%);
  --popover-foreground: hsl(222.2 84% 4.9%);
  --primary: hsl(221.2 83.2% 53.3%);
  --primary-foreground: hsl(210 40% 98%);
  --secondary: hsl(210 40% 96.1%);
  --secondary-foreground: hsl(222.2 47.4% 11.2%);
  --muted: hsl(210 40% 96.1%);
  --muted-foreground: hsl(215.4 16.3% 46.9%);
  --accent: hsl(210 40% 96.1%);
  --accent-foreground: hsl(222.2 47.4% 11.2%);
  --destructive: hsl(0 84.2% 60.2%);
  --destructive-foreground: hsl(210 40% 98%);
  --border: hsl(214.3 31.8% 91.4%);
  --input: hsl(214.3 31.8% 91.4%);
  --ring: hsl(222.2 84% 4.9%);
  --radius: 0.5rem;
}

.dark {
  --background: hsl(222.2 84% 4.9%);
  --foreground: hsl(210 40% 98%);
  --card: hsl(222.2 47.4% 11.2%);
  --card-foreground: hsl(210 40% 98%);
  --popover: hsl(222.2 84% 4.9%);
  --popover-foreground: hsl(210 40% 98%);
  --primary: hsl(210 40% 98%);
  --primary-foreground: hsl(222.2 47.4% 11.2%);
  --secondary: hsl(217.2 32.6% 17.5%);
  --secondary-foreground: hsl(210 40% 98%);
  --muted: hsl(217.2 32.6% 17.5%);
  --muted-foreground: hsl(215 20.2% 65.1%);
  --accent: hsl(217.2 32.6% 17.5%);
  --accent-foreground: hsl(210 40% 98%);
  --destructive: hsl(0 72% 51%);
  --destructive-foreground: hsl(210 40% 98%);
  --border: hsl(217.2 32.6% 17.5%);
  --input: hsl(217.2 32.6% 17.5%);
  --ring: hsl(212.7 26.8% 83.9%);
}

/* PART 2: Bridge variables to Tailwind's theme system */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --radius: var(--radius);
}

/* PART 3: Apply base styles */
body {
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  background-color: var(--color-background);
  color: var(--color-foreground);
}

a {
  color: var(--color-primary);
}
a:hover {
  text-decoration: underline;
  text-underline-offset: 4px;
}

---
## 2. Estrutura do Repositório Frontend

Esta seção detalha a estrutura de pastas e arquivos do frontend, construído com Next.js (App Router), e descreve a responsabilidade de cada página e componente principal.

### 2.1. Visão Geral da Estrutura de Arquivos

```
src/frontend/app/
├─── page.tsx                 # Página inicial (/)
├─── layout.tsx               # Layout principal da aplicação
├─── globals.css              # Estilos globais e variáveis de tema Tailwind
├─── components/              # Componentes React reutilizáveis
│    ├─── AppHeader.tsx        # Cabeçalho da página (título, subtítulo, ações)
│    ├─── ConditionalLayout.tsx# Renderiza o layout principal (com sidebar) condicionalmente
│    ├─── sidebar.tsx          # Barra de navegação lateral
│    └─── ui/                  # Componentes base do shadcn/ui
├─── contexts/                # Contextos React para gerenciamento de estado global
│    ├─── AuthContext.tsx      # Gerencia o estado de autenticação (token)
│    ├─── HeaderContext.tsx    # Gerencia o conteúdo do AppHeader
│    └─── SidebarContext.tsx   # Gerencia o estado da sidebar (expandido/recolhido)
├─── login/
│    └─── page.tsx             # Página de login (/login)
├─── experiments/             # Seção de visualização de experimentos
│    ├─── page.tsx             # Página principal de datasets (/experiments)
│    ├─── layout.tsx           # Layout da seção de experimentos
│    └─── [dataset_id]/
│         ├─── page.tsx         # Página de um dataset específico (/experiments/[dataset_id])
│         └─── [experiment_id]/
│              ├─── page.tsx     # Página de detalhes de um experimento
│              └─── components/  # Componentes específicos da página de detalhes
│                   ├─── experiment-details-client.tsx
│                   ├─── RunDetails.tsx
│                   ├─── Comparison.tsx
│                   ├─── Evaluations.tsx
│                   └─── ReasoningTimeline.tsx
└─── eai_settings/            # Seção para configuração dos agentes EAI
     ├─── page.tsx             # Página principal de configurações (/eai_settings)
     ├─── layout.tsx           # Layout da seção de configurações
     └─── components/          # Componentes específicos da página de configurações
          ├─── settings-client.tsx
          ├─── AgentSelector.tsx
          ├─── PromptEditor.tsx
          ├─── AgentConfiguration.tsx
          └─── VersionHistory.tsx
```

### 2.2. Descrição das Páginas e Componentes

#### Estrutura Principal

*   **`app/layout.tsx`**: O layout raiz que envolve toda a aplicação. É responsável por configurar os providers essenciais: `ThemeProvider` (para temas claro/escuro), `AuthProvider` (para autenticação), `HeaderProvider` (para o cabeçalho dinâmico), e `TooltipProvider`. Inclui o `ConditionalLayout` para aplicar a estrutura de navegação principal.
*   **`app/page.tsx`**: A página inicial (`/`). Apresenta uma visão geral e cartões de navegação que direcionam o usuário para as seções principais, como "Painel de Experimentos" e "Configurações EAI".
*   **`app/login/page.tsx`**: A página de login (`/login`). Contém um formulário simples para que o usuário insira seu Bearer Token de autenticação. É a única página que não utiliza o `ConditionalLayout` com a `Sidebar`.
*   **`app/components/AppHeader.tsx`**: Um componente de cabeçalho reutilizável. Seu conteúdo (título, subtítulo e botões de ação) é controlado dinamicamente através do `HeaderContext`, permitindo que cada página defina seu próprio cabeçalho.
*   **`app/components/sidebar.tsx`**: A barra de navegação lateral persistente. Oferece links para as seções principais, um botão para alternar o tema e a funcionalidade de logout. Seu estado (expandido ou recolhido) é gerenciado pelo `SidebarContext`.

#### Seção de Experimentos (`/experiments`)

*   **`experiments/layout.tsx`**: O layout específico para a seção de experimentos. Ele utiliza o `HeaderProvider` para garantir que o `AppHeader` reflita o contexto de navegação (seja na lista de datasets, na lista de experimentos ou nos detalhes de um experimento).
*   **`experiments/page.tsx`**: A página de listagem de datasets (`/experiments`). Busca e exibe todos os datasets disponíveis em uma tabela que pode ser ordenada e filtrada. Clicar em um dataset navega para a página de detalhes do mesmo.
*   **`experiments/[dataset_id]/page.tsx`**: Esta página (`/experiments/[dataset_id]`) exibe os detalhes de um dataset específico. Ela contém duas abas: uma para listar todos os experimentos associados àquele dataset e outra para listar todos os exemplos de dados.
*   **`experiments/[dataset_id]/[experiment_id]/page.tsx`**: O coração da análise de dados. Esta página exibe todos os detalhes de uma única execução de experimento.
    *   **`components/experiment-details-client.tsx`**: O componente cliente que organiza a UI. Possui um layout de duas colunas:
        1.  **Barra Lateral**: Lista todas as "runs" (execuções individuais) do experimento. Clicar em uma run atualiza a área de conteúdo principal.
        2.  **Conteúdo Principal**: Exibe os detalhes da run selecionada.
    *   **`components/RunDetails.tsx`**: Agrega vários sub-componentes para mostrar uma visão completa da run, incluindo a mensagem do usuário, comparação de respostas, avaliações e a cadeia de pensamento.
    *   **`components/Comparison.tsx`**: Mostra uma comparação lado a lado entre a resposta gerada pelo agente e a resposta de referência ("golden answer").
    *   **`components/Evaluations.tsx`**: Apresenta as métricas de avaliação (anotações) para a run, como "Answer Completeness" e "Answer Similarity", dentro de um acordeão.
    *   **`components/ReasoningTimeline.tsx`**: Visualiza a "cadeia de pensamento" do agente, mostrando cada passo lógico, chamada de ferramenta e retorno que levou à resposta final.

#### Seção de Configurações EAI (`/eai_settings`)

*   **`eai_settings/layout.tsx`**: O layout para a seção de configurações, que fornece o `AppHeader` para esta área.
*   **`eai_settings/page.tsx`**: A página principal para gerenciar as configurações dos agentes (`/eai_settings`). Ela busca os tipos de agentes disponíveis e os dados de configuração do agente atualmente selecionado.
    *   **`components/settings-client.tsx`**: O componente cliente central que gerencia toda a interatividade da página. Ele possui um layout de duas colunas:
        1.  **Configuração Principal (Esquerda)**: Contém os controles para selecionar o tipo de agente, editar o system prompt e ajustar as configurações do agente.
        2.  **Histórico de Versões (Direita)**: Lista todas as versões salvas para o agente selecionado.
    *   **`components/AgentSelector.tsx`**: Um seletor que permite ao usuário escolher qual tipo de agente deseja configurar.
    *   **`components/PromptEditor.tsx`**: Uma área de texto para visualizar e editar o system prompt do agente.
    *   **`components/AgentConfiguration.tsx`**: Campos de formulário para definir parâmetros do agente, como `memory_blocks`, `tools`, `model_name`, etc.
    *   **`components/VersionHistory.tsx`**: Exibe o histórico de versões. Clicar em uma versão carrega seu respectivo prompt e configuração nos campos de edição, permitindo a visualização ou reutilização de configurações passadas.