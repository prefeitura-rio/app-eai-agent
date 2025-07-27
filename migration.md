# Plano de Migração: Página de Configurações EAI

Este documento descreve o plano para migrar a página de administração de "Configurações EAI" de uma implementação estática (HTML, CSS, JS) para uma aplicação moderna usando Next.js, Tailwind CSS 4 e shadcn/ui, seguindo as diretrizes do `GEMINI.md`.

## Fase 1: Estrutura da Página e Rota

- [ ] Criar a nova rota da página em `app/settings/page.tsx`.
- [ ] Desenvolver o layout principal da página, dividindo-a em duas colunas: a coluna da esquerda para o editor e configurações, e a da direita para o histórico.
- [ ] Garantir que o layout seja responsivo e se adapte a diferentes tamanhos de tela.

## Fase 2: Lógica de Dados e Estado Principal

- [ ] No componente `page.tsx`, criar os estados (`useState`) para gerenciar:
    - A lista de tipos de agente.
    - O tipo de agente selecionado.
    - O conteúdo do prompt do sistema.
    - Os valores dos campos de configuração (memory blocks, tools, etc.).
    - A lista do histórico de versões.
    - O estado de carregamento (`loading`).
- [ ] Implementar os `useEffect` hooks para buscar os dados iniciais da API quando o componente for montado ou quando o tipo de agente mudar:
    - Buscar tipos de agente de `/api/v1/system-prompt/agent-types`.
    - Buscar os dados do agente selecionado (prompt, config, histórico) de `/api/v1/unified-history` e `/api/v1/system-prompt`.

## Fase 3: Componentes da Coluna Esquerda (Editor e Configurações)

- [ ] **Componente `AgentSelector`:**
    - [ ] Criar um componente para buscar e exibir os tipos de agente em um `Select` do shadcn/ui.
    - [ ] Ao selecionar um novo agente, o estado principal da página deve ser atualizado.

- [ ] **Componente `PromptEditor`:**
    - [ ] Criar um componente que contenha uma `Textarea` para o prompt do sistema.
    - [ ] Adicionar um botão de "Copiar" (`Clipboard`) com feedback visual.

- [ ] **Componente `AgentConfiguration`:**
    - [ ] Criar um componente para os campos de configuração:
        - `Textarea` para os `memory_blocks` (com validação de JSON).
        - `Input` para `tools`.
        - `Input` para `model_name`.
        - `Input` para `embedding_name`.
    - [ ] Adicionar um `Switch` para a opção "Atualizar agentes existentes".

- [ ] **Componente `ActionButtons`:**
    - [ ] Criar um componente para os botões de ação principais:
        - Botão "Salvar Alterações" que abre um modal de confirmação.
        - Botão "Resetar Tudo" que abre um modal de confirmação.
    - [ ] Implementar a lógica de salvamento (`/api/v1/unified-save`) e reset (`/api/v1/unified-reset`) que é disparada a partir dos modais.

## Fase 4: Componente da Coluna Direita (Histórico)

- [ ] **Componente `VersionHistory`:**
    - [ ] Criar um componente para exibir a lista de versões do histórico.
    - [ ] Cada item da lista deve mostrar a versão, data, autor, motivo e um preview do conteúdo.
    - [ ] Adicionar badges para indicar o tipo de alteração (Prompt, Config, Ambos) e o status "Ativo".
    - [ ] Implementar a funcionalidade de clique em um item do histórico para carregar os dados daquela versão nos campos de edição.
    - [ ] O item selecionado/ativo deve ter um destaque visual.

## Fase 5: Estilização e Polimento Final

- [ ] Substituir todo o CSS customizado de `style.css` por classes de utilitário do Tailwind CSS.
- [ ] Usar componentes `Card` do shadcn/ui para agrupar as seções de forma visualmente coesa.
- [ ] Garantir que todos os elementos interativos (botões, inputs, selects) sigam a identidade visual do `shadcn/ui`.
- [ ] Adicionar feedback de carregamento (skeletons ou spinners) enquanto os dados da API são buscados.
- [ ] Implementar notificações (`Toast`) para dar feedback sobre o sucesso ou falha das operações de salvar e resetar.
