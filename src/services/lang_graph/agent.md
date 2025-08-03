### Plano de Elaboração de Chatbot

**Objetivo:** Criar um chatbot com memória de longo prazo persistente, onde a gestão dessa memória é uma habilidade intrínseca do agente conversacional. Prioridade em custos e simplicidade para a V1, permitindo que o agente decida *quando* e *o que* buscar e memorizar. Utilizar ChatGoogleGenerativeAI e GoogleGenerativeAIEmbeddings


src/services/lang_graph/
├── __init__.py
├── models.py         # Definições de todos os modelos Pydantic.
├── database.py       # definicao das funcoes de banco de dados (Google Cloud SQL Postgres).
├── repository.py     # Lógica de acesso e manipulação do banco de dados utilizando database.
├── memory.py         # definicao da classe de gerenciamento de memoria.
├── tools.py          # Implementação das ferramentas do agente (get, save, update, delete).
├── llms.py           # definicao de modelos a serem utilizados
├── graph.py          # Definição do estado, nós e montagem do grafo LangGraph.
└── service.py        # Ponto de entrada para interagir com o chatbot.
└── test_service.py   # Configuracao de um script que chama o service para testagem

---

#### 1. Arquitetura da Memória (Onde a informação fica)

A única fonte de verdade para a memória de longo prazo será a tabela no Google Cloud SQL.

*   **Tabela:** `long_term_memory`
*   **Colunas:**
    *   `memory_id`: `UUID` ou `INT AUTO_INCREMENT`. Chave primária para permitir updates e deletes precisos.
    *   `user_id`: `VARCHAR`. Essencial para garantir que a memória de um usuário não se misture com a de outro.
    *   `creation_datetime`: `TIMESTAMP`. Para buscas cronológicas e para entender quando um fato foi aprendido.
    *   `last_accessed`: `TIMESTAMP`. Para rastrear quando a memória foi utilizada pela última vez, permitindo identificar memórias obsoletas ou não utilizadas.
    *   `memory_type` **`ENUM('user_profile', 'preference', 'goal', 'constraint', 'critical_info')`**. O campo agora é um tipo enumerado, aceitando apenas os valores predefinidos.
    *   `content`: `TEXT`. O conteúdo da memória em si. Deve ser uma informação concisa e atômica.
    *   `embedding`: `VECTOR`. O vetor de embedding do campo `content`, usado para a busca semântica.

### Definição dos `memory_types` via Pydantic

A tipologia de memória será definida através de um modelo Pydantic, permitindo flexibilidade na configuração de diferentes tipos de agentes:

```python
from enum import Enum
from pydantic import BaseModel
from typing import Literal

class MemoryType(str, Enum):
    USER_PROFILE = "user_profile"
    PREFERENCE = "preference"
    GOAL = "goal"
    CONSTRAINT = "constraint"
    CRITICAL_INFO = "critical_info"

class MemoryTypeConfig(BaseModel):
    """Configuração dos tipos de memória com descrições que serão injetadas no prompt do agente."""
    user_profile: str = "Fatos estáveis sobre o usuário (Ex: 'O nome do usuário é Carlos', 'O usuário mora em São Paulo')."
    preference: str = "Preferências subjetivas e gostos do usuário (Ex: 'Prefere hotéis com academia', 'Gosta de comida italiana')."
    goal: str = "Um objetivo ou tarefa que o usuário deseja alcançar (Ex: 'Está planejando uma viagem de 10 dias para a Itália em dezembro')."
    constraint: str = "Uma restrição ou condição que deve ser respeitada (Ex: 'É alérgico a amendoim', 'Tem um orçamento máximo de R$ 5.000 para a viagem')."
    critical_info: str = "Informação crítica e pontual, geralmente de curto prazo (Ex: 'O número da reserva do voo é ABC123', 'O protocolo do último atendimento foi 987654')."
```

---

#### 2. Curadoria Integrada & Interação com a Memória (Como a informação é salva e acessada)

O agente será o único responsável por gerenciar a memória de longo prazo. Isso é feito através de ferramentas que ele pode chamar com base em seu raciocínio.

**As Ferramentas (Tools) do Agente:**

*   **`get_memory(mode: str, query: str = None, memory_type: MemoryType = None)`:**
    *   **Função:** Permite que o agente recupere memórias.
    *   **`mode`**: `semantic` (busca por similaridade de `query`) ou `chronological` (últimas N memórias).
    *   **`query`**: Texto para busca semântica (se `mode='semantic'`).
    *   **`memory_type`**: Opcional, para filtrar por `memory_type` usando o modelo Pydantic.
    *   **Configurações da Sessão:** A ferramenta usa os valores de `memory_limit` e `memory_min_relevance` da configuração da sessão.
    *   **Importante:** A ferramenta internamente adiciona o `user_id` da sessão para garantir que o agente só acesse memórias do usuário correto. Também atualiza automaticamente o campo `last_accessed` para todas as memórias retornadas.
    *   **Retorno:** Lista de objetos contendo `memory_id`, `content`, `memory_type`, `creation_datetime`, e `relevance_score` (apenas para busca semântica).
    **Comportamento Interno:**
    - Filtra automaticamente por `user_id` da sessão
    - Respeita `memory_limit` e `memory_min_relevance` da configuração
    - Atualiza `last_accessed` automaticamente
    - Retorna lista com `memory_id`, `content`, `memory_type`, `creation_datetime`, `relevance_score`

*   **`save_memory(content: str, memory_type: MemoryType)`:**
    *   **Função:** O agente usa essa ferramenta quando identifica um fato novo e importante que deve ser persistido. Ele mesmo formula o `content` para ser uma declaração clara e concisa. A ferramenta internamente adiciona o `user_id`, gera o `embedding`, e define `creation_datetime` e `last_accessed` com o timestamp atual.
    *   **Parâmetros validados via Pydantic:** O `memory_type` é automaticamente validado contra o modelo `MemoryType` definido via Pydantic.
    *   **Retorno:** Objeto contendo `memory_id`, `content`, `memory_type`, e `success: true` se salvo com sucesso, ou `success: false` com `error_message` se houver falha.
    **Comportamento Interno:**
    - Adiciona `user_id`, `embedding`, timestamps automaticamente
    - Valida `memory_type` contra enum definido
    - Retorna confirmação com `memory_id` ou erro
*   **`update_memory(memory_id: str, new_content: str)`:**
    *   **Função:** Se o usuário corrige uma informação ou um fato muda. O agente precisa ter obtido o `memory_id` previamente (provavelmente via `get_memory`). A ferramenta internamente verifica o `user_id`, atualiza o `content`, regenera o `embedding`, e atualiza o `last_accessed`.
    *   **Retorno:** Objeto contendo `memory_id`, `old_content`, `new_content`, e `success: true` se atualizado com sucesso, ou `success: false` com `error_message` se houver falha (ex: memory_id não encontrado ou não pertence ao usuário).
    **Comportamento Interno:**
    - Verifica ownership (user_id)
    - Regenera embedding
    - Atualiza `last_accessed`
    
*   **`delete_memory(memory_id: str)`:**
    *   **Função:** Para informações que se tornaram obsoletas ou irrelevantes. Requer o `memory_id`. A ferramenta internamente verifica o `user_id`.
    *   **Retorno:** Objeto contendo `memory_id`, `deleted_content`, e `success: true` se deletado com sucesso, ou `success: false` com `error_message` se houver falha (ex: memory_id não encontrado ou não pertence ao usuário).
    **Comportamento Interno:**
    - Verifica ownership antes da exclusão
    - Retorna confirmação ou erro

**Instruções para o Agente (via System Prompt Configurável):**

O comportamento do agente é guiado por um `system_prompt` configurável que é passado no início da sessão. O prompt é construído dinamicamente incluindo as definições dos tipos de memória do modelo Pydantic.

**Estrutura de Configuração da Sessão:**

```python
from pydantic import BaseModel
from typing import Optional

class SessionConfig(BaseModel):
    thread_id: str
    user_id: str
    chat_model: str  # Nome do modelo (ex: "gpt-4", "claude-3")
    system_prompt: str = "Você é um assistente útil com capacidade de memória."
    memory_limit: int = 20
    memory_min_relevance: float = 0.6
    memory_types_config: MemoryTypeConfig = MemoryTypeConfig()

# Exemplo de uso:
config = {
    "configurable": {
        "thread_id": f"{user_id}",
        "user_id": user_id,
        "chat_model": chat_model_instance,
        "system_prompt": agent_config.get(
            "system_prompt", 
            "Você é um assistente útil com capacidade de memória de longo prazo."
        ),
        "memory_limit": agent_config.get("memory_limit", 20),
        "use_pre_memory_load": agent_config.get("use_pre_memory_load", True),
        "memory_min_relevance": agent_config.get("memory_min_relevance", 0.6),
        "memory_types_config": MemoryTypeConfig()
    }
}
```

---

#### 3. O Cérebro da Operação: Fluxo de Conversa no LangGraph

O LangGraph orquestra o fluxo, gerenciando o estado (memória de curto prazo) e decidindo qual nó executar a seguir.

1.  **Início (Recebimento da Mensagem do Usuário):**
    *   A mensagem do usuário é recebida e adicionada ao estado da conversa (ex: `state['messages']`).

2.  **Nó de Recuperação Inicial (Opcional):**
    *   **Objetivo:** Proativamente fornecer contexto ao agente antes que ele decida o que fazer.
    *   **Ativação:** Controlado por um flag na configuração da sessão (ex: `enable_proactive_memory_retrieval`).
    *   **Ação:** Se ativado, chama a ferramenta `get_memory` usando a mensagem do usuário como `query`. Os resultados são adicionados ao estado (`state['retrieved_memories']`) e incluídos no primeiro prompt do agente.

3.  **Nó do Agente (Raciocínio):**
    *   **Entrada:** Recebe todo o estado da conversa: histórico de mensagens, memórias recuperadas (se houver) e o `system_prompt` dinâmico.
    *   **System Prompt Dinâmico (Exemplo):**
        > "Você é um assistente pessoal com memória. Para lembrar informações entre conversas, use estas ferramentas: `get_memory`, `save_memory`, `update_memory`, `delete_memory`.
        >
        > **Tipos de Memória Disponíveis:**
        > *   **user_profile:** Fatos estáveis sobre o usuário (Ex: 'O nome do usuário é Carlos').
        > *   **preference:** Preferências subjetivas do usuário (Ex: 'Prefere hotéis com academia').
        > *   **goal:** Um objetivo que o usuário deseja alcançar (Ex: 'Está planejando uma viagem').
        > *   **constraint:** Uma restrição a ser respeitada (Ex: 'É alérgico a amendoim').
        > *   **critical_info:** Informação crítica e pontual (Ex: 'O número da reserva é ABC123').
        >
        > **Diretrizes:**
        > 1.  **Pense Passo a Passo:** Antes de responder, considere se buscar na memória (`get_memory`) pode enriquecer sua resposta.
        > 2.  **Seja Proativo:** Se o usuário fornecer uma informação nova e reutilizável, salve-a com `save_memory`.
        > 3.  **Mantenha a Qualidade:** Se notar que uma memória está errada, use `update_memory`. Se for irrelevante, use `delete_memory`."
    *   **Decisão:** O agente decide qual o próximo passo:
        *   **Chamar uma Ferramenta:** Se precisar de mais informações ou precisar gerenciar a memória.
        *   **Responder ao Usuário:** Se já tiver todas as informações necessárias.

4.  **Nó de Execução de Ferramentas:**
    *   Executa a ferramenta chamada pelo agente.
    *   O resultado da execução (ex: a lista de memórias ou o status de sucesso de uma operação) é adicionado ao estado (`state['tool_outputs']`).

5.  **Aresta Condicional (Router):**
    *   Após a execução de uma ferramenta, este "roteador" decide para onde o fluxo deve ir.
    *   **Se o agente chamou outra ferramenta:** Volta para o **Nó de Execução de Ferramentas**.
    *   **Se o agente finalizou o uso de ferramentas:** Volta para o **Nó do Agente (Raciocínio)** para que ele possa usar o resultado da ferramenta e formular sua resposta final.
    *   **Se o agente decidiu responder:** Vai para o **Nó de Resposta Final**.

6.  **Fim:**
    * O sistema retorna uma lista completa do tracing de menssagens, permitindo rastreabilidade total do fluxo de conversação.


Fluxo de Operação (LangGraph):
    
graph TD
    A[Usuário envia mensagem] --> B{Pré-busca ativada?}
    B -->|Sim| C[Busca inicial: semantic/chronological]
    B -->|Não| D[Agente processa contexto atual]
    C --> D
    D --> E[Agente decide ação]
    E -->|Usar ferramenta| F[Executa ferramenta]
    F --> G[Atualiza estado]
    G --> E
    E -->|Responder| H[Gera resposta final]
---

