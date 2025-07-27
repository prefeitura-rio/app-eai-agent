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

- [x] **Verificar Configuração:** Confirmar que o `tailwind.config.js` e o `globals.css` estão configurados conforme a documentação do `shadcn/ui`.
- [x] **Definir Tema:** Customizar as variáveis CSS no `globals.css` para alinhar com a identidade visual do projeto (cores primárias, secundárias, fontes, bordas, etc.).
- [x] **Criar Diretório de UI:** Garantir que todos os novos componentes `shadcn/ui` sejam adicionados ao diretório `src/frontend/app/components/ui`.
- [x] **Adicionar Componentes Atômicos:** Adicionar os primeiros componentes que servirão de base para todos os outros.
    - `npx shadcn-ui@latest add button`
    - `npx shadcn-ui@latest add card`
    - `npx shadcn-ui@latest add input`
    - `npx shadcn-ui@latest add label`

---

## Fase 2: Migração de Componentes Comuns

Agora, vamos substituir os componentes personalizados mais usados por suas contrapartes do `shadcn/ui`.

### Checklist da Fase 2:

- [x] **Substituir Botões:**
    - [x] Identificar todos os elementos `<button>` e `<a>` estilizados como botões no projeto.
    - [x] Substituí-los pelo componente `<Button>` do `shadcn/ui`.
    - [x] Aplicar as variantes corretas (`default`, `destructive`, `outline`, `ghost`, `link`).

- [x] **Substituir Cards:**
    - [x] Encontrar todos os contêineres que funcionam como "cards" ou painéis.
    - [x] Refatorá-los para usar a composição de `<Card>`, `<CardHeader>`, `<CardTitle>`, `<CardDescription>` e `<CardContent>`.
    - [x] Aplicar isso primeiro em componentes de baixo nível e, em seguida, nas visualizações de página.

- [x] **Substituir `JsonViewerModal.tsx`:**
    - [x] Adicionar o componente `Dialog` do `shadcn/ui`: `npx shadcn-ui@latest add dialog`.
    - [x] Refatorar `JsonViewerModal.tsx` para usar `<Dialog>`, `<DialogTrigger>`, `<DialogContent>`, `<DialogHeader>`, `<DialogTitle>` e `<DialogDescription>`.
    - [x] Garantir que o conteúdo JSON ainda seja renderizado corretamente dentro do novo modal.

---

## Fase 3: Migração Página por Página

Com os blocos de construção no lugar, podemos começar a migrar páginas inteiras.

### Checklist da Fase 3:

- [x] **Página de Datasets (`/experiments`):**
    - [x] Adicionar o componente `Table`: `npx shadcn-ui@latest add table`.
    - [x] Substituir a tabela HTML existente pela composição de `<Table>`, `<TableHeader>`, `<TableBody>`, etc.
    - [x] Adicionar o componente `Dropdown Menu`: `npx shadcn-ui@latest add dropdown-menu`.
    - [x] Usar o `DropdownMenu` para as opções de ordenação e filtro da tabela.
    - [x] Substituir a barra de pesquisa pelo componente `<Input>` do `shadcn/ui`.

- [x] **Página de Detalhes do Dataset (`/experiments/[dataset_id]`):**
    - [x] Adicionar o componente `Tabs`: `npx shadcn-ui@latest add tabs`.
    - [x] Substituir a navegação por abas ("Experimentos", "Exemplos") pelo componente `<Tabs>`.
    - [x] Garantir que as tabelas dentro de cada aba também sejam migradas para o componente `Table`.

- [x] **Página de Detalhes do Experimento (`/experiments/[dataset_id]/[experiment_id]`):**
    - [x] Usar componentes `<Card>` para exibir os metadados e parâmetros do experimento.
    - [x] Adicionar e usar o componente `Accordion`: `npx shadcn-ui@latest add accordion`.
    - [x] Refatorar a "Cadeia de Pensamento" (timeline) para usar o `Accordion` para cada passo (Raciocínio, Chamada de Ferramenta), permitindo que o usuário expanda e recolha os detalhes.
    - [x] Garantir que qualquer botão ou link nesta página use o componente `<Button>`.

---

## Fase 4: Limpeza e Revisão Final

A etapa final para garantir que o projeto permaneça limpo e consistente.

### Checklist da Fase 4:

- [x] **Remover CSS Legado:**
    - [x] Procurar por arquivos `.module.css` que se tornaram redundantes após a migração dos componentes.
    - [x] Excluir os arquivos de estilo antigos e remover suas importações.

- [x] **Remover Componentes Legados:**
    - [x] Excluir os arquivos de componentes personalizados que foram totalmente substituídos (ex: o antigo `JsonViewerModal.tsx` se o novo for criado em um local diferente).

- [ ] **Revisão da UI:**
    - [ ] Navegar por todo o aplicativo para garantir a consistência visual (espaçamento, cores, tipografia).
    - [ ] Testar a responsividade em diferentes tamanhos de tela.

- [x] **Executar Linter:**
    - [x] Rodar `npm run lint` (ou comando equivalente) para garantir que todo o novo código siga as diretrizes de estilo do projeto.

---

## Fase 5: Migração Final para Tailwind CSS

O objetivo desta fase é eliminar completamente a dependência de arquivos `.module.css`, substituindo todos os estilos restantes por classes de utilitários do Tailwind CSS.

### Checklist da Fase 5:

- [x] **Refatorar `AppHeader.tsx`:**
    - [x] Substituir as classes de layout de `AppHeader.module.css` (ex: `.header`, `.header_content`) por classes de utilitários do Tailwind diretamente no JSX.
    - [x] Excluir o arquivo `AppHeader.module.css` após a refatoração.

- [x] **Refatorar `datasets-client.tsx`:**
    - [x] Substituir as classes restantes de `page.module.css` (ex: `.container`, `.table_responsive`) por classes do Tailwind.
    - [x] Remover a importação do `page.module.css`.

- [x] **Refatorar `dataset-experiments-client.tsx`:**
    - [x] Substituir a classe `.preformatted` de `page.module.css` por classes do Tailwind.
    - [x] Remover a importação do `page.module.css`.

- [x] **Limpeza Geral de CSS Modules:**
    - [x] Fazer uma busca global por `*.module.css` no projeto.
    - [x] Analisar cada arquivo restante e refatorar o componente que o utiliza.
    - [x] Excluir todos os arquivos `.module.css` que se tornaram obsoletos.

---

## Fase 6: Polimento da UI e Estilo

O objetivo desta fase é revisar cada página individualmente para corrigir problemas de layout, espaçamento, tipografia e garantir que a UI esteja coesa e profissional.

### Checklist da Fase 6:

- [x] **Página de Login (`/login`):**
    - [x] Revisar o layout do formulário, espaçamento dos campos e alinhamento.
    - [x] Garantir que o botão de "Entrar" e a mensagem de erro estejam bem estilizados.
    - [x] Verificar a aparência do botão de troca de tema.

- [ ] **Página Inicial (`/`):**
    - [ ] Ajustar o `AppHeader` para garantir que o título e as ações estejam bem alinhados.
    - [ ] Estilizar os cards de navegação (`Painel de Experimentos`, etc.) para que tenham uma aparência moderna e um efeito de hover claro.
    - [ ] Verificar a tipografia e o espaçamento da seção de descrição.

- [ ] **Página de Datasets (`/experiments`):**
    - [ ] Garantir que a tabela de datasets esteja bem formatada, com espaçamento adequado nas células e cabeçalhos.
    - [ ] Verificar o alinhamento da barra de pesquisa e do botão de download.
    - [ ] Ajustar o estilo dos `Badges` para que tenham um bom contraste e legibilidade.
    - [ ] Polir o `DropdownMenu` de ordenação.

- [ ] **Página de Detalhes do Dataset (`/experiments/[dataset_id]`):**
    - [ ] Estilizar as abas (`Tabs`) para que a aba ativa seja claramente destacada.
    - [ ] Garantir que as tabelas dentro de cada aba estejam bem formatadas.
    - [ ] Revisar o estilo dos blocos de código (`<pre>`) na aba "Exemplos" para garantir a legibilidade.

- [ ] **Página de Detalhes do Experimento (`/experiments/[dataset_id]/[experiment_id]`):**
    - [ ] Ajustar o layout de duas colunas para que seja responsivo e bem espaçado.
    - [ ] Revisar o estilo da lista de "Runs" na barra lateral, incluindo o estado ativo/selecionado.
    - [ ] Polir a aparência dos `Cards` de "Parâmetros", "Métricas" e "Avaliações".
    - [ ] Garantir que o `Accordion` da "Cadeia de Pensamento" esteja visualmente agradável e fácil de usar.
    - [ ] Estilizar a seção de "Comparação de Respostas".
