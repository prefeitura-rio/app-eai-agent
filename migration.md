# Plano de Migração para shadcn/ui

Este documento descreve o plano passo a passo para migrar a base de código do frontend existente para usar `shadcn/ui`. O objetivo é melhorar a consistência da UI, a acessibilidade, a experiência do desenvolvedor e a velocidade de implementação de novos recursos.

## Estratégia Geral

A migração será realizada em fases, seguindo uma abordagem "bottom-up" (de baixo para cima):

1.  **Fundação:** Configurar o tema base e os componentes mais atômicos.
2.  **Componentes Comuns:** Substituir componentes personalizados que são usados em todo o aplicativo.
3.  **Página por Página:** Migrar páginas inteiras, uma de cada vez, compondo os novos componentes `shadcn/ui`.
4.  **Limpeza:** Remover estilos e componentes legados que não são mais necessários.

---

## Fase 1: Fundação e Configuração

O objetivo desta fase é garantir que o ambiente esteja corretamente configurado para `shadcn/ui` e estabelecer as bases do nosso sistema de design.

### Checklist da Fase 1:

- [ ] **Verificar Configuração:** Confirmar que o `tailwind.config.js` e o `globals.css` estão configurados conforme a documentação do `shadcn/ui`.
- [ ] **Definir Tema:** Customizar as variáveis CSS no `globals.css` para alinhar com a identidade visual do projeto (cores primárias, secundárias, fontes, bordas, etc.).
- [ ] **Criar Diretório de UI:** Garantir que todos os novos componentes `shadcn/ui` sejam adicionados ao diretório `src/frontend/app/components/ui`.
- [ ] **Adicionar Componentes Atômicos:** Adicionar os primeiros componentes que servirão de base para todos os outros.
    - `npx shadcn-ui@latest add button`
    - `npx shadcn-ui@latest add card`
    - `npx shadcn-ui@latest add input`
    - `npx shadcn-ui@latest add label`

---

## Fase 2: Migração de Componentes Comuns

Agora, vamos substituir os componentes personalizados mais usados por suas contrapartes do `shadcn/ui`.

### Checklist da Fase 2:

- [ ] **Substituir Botões:**
    - [ ] Identificar todos os elementos `<button>` e `<a>` estilizados como botões no projeto.
    - [ ] Substituí-los pelo componente `<Button>` do `shadcn/ui`.
    - [ ] Aplicar as variantes corretas (`default`, `destructive`, `outline`, `ghost`, `link`).

- [ ] **Substituir Cards:**
    - [ ] Encontrar todos os contêineres que funcionam como "cards" ou painéis.
    - [ ] Refatorá-los para usar a composição de `<Card>`, `<CardHeader>`, `<CardTitle>`, `<CardDescription>` e `<CardContent>`.
    - [ ] Aplicar isso primeiro em componentes de baixo nível e, em seguida, nas visualizações de página.

- [ ] **Substituir `JsonViewerModal.tsx`:**
    - [ ] Adicionar o componente `Dialog` do `shadcn/ui`: `npx shadcn-ui@latest add dialog`.
    - [ ] Refatorar `JsonViewerModal.tsx` para usar `<Dialog>`, `<DialogTrigger>`, `<DialogContent>`, `<DialogHeader>`, `<DialogTitle>` e `<DialogDescription>`.
    - [ ] Garantir que o conteúdo JSON ainda seja renderizado corretamente dentro do novo modal.

---

## Fase 3: Migração Página por Página

Com os blocos de construção no lugar, podemos começar a migrar páginas inteiras.

### Checklist da Fase 3:

- [ ] **Página de Datasets (`/experiments`):**
    - [ ] Adicionar o componente `Table`: `npx shadcn-ui@latest add table`.
    - [ ] Substituir a tabela HTML existente pela composição de `<Table>`, `<TableHeader>`, `<TableBody>`, etc.
    - [ ] Adicionar o componente `Dropdown Menu`: `npx shadcn-ui@latest add dropdown-menu`.
    - [ ] Usar o `DropdownMenu` para as opções de ordenação e filtro da tabela.
    - [ ] Substituir a barra de pesquisa pelo componente `<Input>` do `shadcn/ui`.

- [ ] **Página de Detalhes do Dataset (`/experiments/[dataset_id]`):**
    - [ ] Adicionar o componente `Tabs`: `npx shadcn-ui@latest add tabs`.
    - [ ] Substituir a navegação por abas ("Experimentos", "Exemplos") pelo componente `<Tabs>`.
    - [ ] Garantir que as tabelas dentro de cada aba também sejam migradas para o componente `Table`.

- [ ] **Página de Detalhes do Experimento (`/experiments/[dataset_id]/[experiment_id]`):**
    - [ ] Usar componentes `<Card>` para exibir os metadados e parâmetros do experimento.
    - [ ] Adicionar e usar o componente `Accordion`: `npx shadcn-ui@latest add accordion`.
    - [ ] Refatorar a "Cadeia de Pensamento" (timeline) para usar o `Accordion` para cada passo (Raciocínio, Chamada de Ferramenta), permitindo que o usuário expanda e recolha os detalhes.
    - [ ] Garantir que qualquer botão ou link nesta página use o componente `<Button>`.

---

## Fase 4: Limpeza e Revisão Final

A etapa final para garantir que o projeto permaneça limpo e consistente.

### Checklist da Fase 4:

- [ ] **Remover CSS Legado:**
    - [ ] Procurar por arquivos `.module.css` que se tornaram redundantes após a migração dos componentes.
    - [ ] Excluir os arquivos de estilo antigos e remover suas importações.

- [ ] **Remover Componentes Legados:**
    - [ ] Excluir os arquivos de componentes personalizados que foram totalmente substituídos (ex: o antigo `JsonViewerModal.tsx` se o novo for criado em um local diferente).

- [ ] **Revisão da UI:**
    - [ ] Navegar por todo o aplicativo para garantir a consistência visual (espaçamento, cores, tipografia).
    - [ ] Testar a responsividade em diferentes tamanhos de tela.

- [ ] **Executar Linter:**
    - [ ] Rodar `npm run lint` (ou comando equivalente) para garantir que todo o novo código siga as diretrizes de estilo do projeto.
