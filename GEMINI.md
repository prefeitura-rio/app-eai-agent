# Plano de Migração para shadcn/ui

Este documento descreve o plano passo a passo para migrar a base de código do frontend existente para usar `shadcn/ui`. O objetivo é melhorar a consistência da UI, a acessibilidade, a experiência do desenvolvedor e a velocidade de implementação de novos recursos.

O objetivo desta fase é revisar cada página individualmente para corrigir problemas de layout, espaçamento, tipografia e garantir que a UI esteja coesa e profissional.

### Checklist da Fase 0:

- [x] **Página de Login (`/login`):**
    - [x] Revisar o layout do formulário, espaçamento dos campos e alinhamento.
    - [x] Garantir que o botão de "Entrar" e a mensagem de erro estejam bem estilizados.
    - [x] Verificar a aparência do botão de troca de tema.

- [x]  **Página Inicial (`/`):**
    - [x] Ajustar o `AppHeader` para garantir que o título e as ações estejam bem alinhados.
    - [x] Estilizar os cards de navegação (`Painel de Experimentos`, etc.) para que tenham uma aparência moderna e um efeito de hover claro.
    - [x] Verificar a tipografia e o espaçamento da seção de descrição.

- [x] **Página de Datasets (`/experiments`):**
    - [x] Garantir que a tabela de datasets esteja bem formatada, com espaçamento adequado nas células e cabeçalhos.
    - [x] Verificar o alinhamento da barra de pesquisa e do botão de download.
    - [x] Ajustar o estilo dos `Badges` para que tenham um bom contraste e legibilidade.
    - [x] Polir o `DropdownMenu` de ordenação.

- [x] **Página de Detalhes do Dataset (`/experiments/[dataset_id]`):**
    - [x] Estilizar as abas (`Tabs`) para que a aba ativa seja claramente destacada.
    - [x] Garantir que as tabelas dentro de cada aba estejam bem formatadas.
    - [x] Revisar o estilo dos blocos de código (`<pre>`) na aba "Exemplos" para garantir a legibilidade.

- [ ] **Página de Detalhes do Experimento (`/experiments/[dataset_id]/[experiment_id]`):**
    - [ ] Ajustar o layout de duas colunas para que seja responsivo e bem espaçado.
    - [ ] Revisar o estilo da lista de "Runs" na barra lateral, incluindo o estado ativo/selecionado.
    - [ ] Polir a aparência dos `Cards` de "Parâmetros", "Métricas" e "Avaliações".
    - [ ] Garantir que o `Accordion` da "Cadeia de Pensamento" esteja visualmente agradável e fácil de usar.
    - [ ] Estilizar a seção de "Comparação de Respostas".



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
```
