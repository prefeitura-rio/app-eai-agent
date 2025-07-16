Excelente. Assumir o papel de planejador de execução é a abordagem correta para um projeto dessa complexidade. Um bom plano garante que todos os componentes sejam construídos na ordem certa e se encaixem perfeitamente.

Aqui está um plano de execução elaborado e detalhado para implementar a arquitetura do agente de IA no Google Cloud Platform.

---

### **Visão Geral da Arquitetura (O Alvo Final)**

Nosso objetivo é construir um sistema de agente de IA serverless, escalável e orientado a eventos. O fluxo de dados será o seguinte: uma mensagem de um cidadão aciona uma Cloud Function, que por sua vez utiliza o LangGraph para orquestrar o raciocínio, a memória e o uso de ferramentas, com todo o estado persistido no Memorystore for Redis e o conhecimento específico no Vertex AI Vector Search.

```mermaid
graph TD
    subgraph Cidadão (Fase 5)
        A[WhatsApp]
    end

    subgraph Provedor de API (Fase 5)
        B[Twilio API]
    end

    subgraph Nuvem GCP (Fases 2-3)
        C[Cloud API Gateway]
        D[Cloud Function <br> (Python + LangGraph)]
        E[Memorystore for Redis <br> (Estado da Conversa)]
        F[Vertex AI Vector Search <br> (Conhecimento do Rio)]
        G[Vertex AI <br> (Modelos Gemini)]
    end

    subgraph Monitoramento (Fase 4)
        H[Cloud Logging/Trace]
        I[LangSmith]
    end
    
    A --> B --> C --> D
    
    D <--> E
    D <--> F
    D <--> G
    
    D --> H
    D --> I
```

---

### **Plano de Execução Detalhado**

Dividimos o projeto em fases, começando com o desenvolvimento local do cérebro do agente e progredindo para a implantação na infraestrutura em nuvem.

### **Fase 0: Fundação e Configuração do Ambiente**

*Objetivo: Preparar o terreno para o desenvolvimento, tanto localmente quanto na nuvem.*

1.  **Criar Projeto GCP:**
    *   Crie um novo projeto no Google Cloud Console.
    *   Associe uma conta de faturamento.
2.  **Habilitar APIs Necessárias:**
    *   No console do GCP, habilite: `Vertex AI API`, `Cloud Functions API`, `API Gateway API`, `Memorystore for Redis API`, `Cloud Build API`.
3.  **Configurar Ambiente de Desenvolvimento Local:**
    *   Instale o Python (3.11+).
    *   Instale a CLI do Google Cloud (`gcloud`).
    *   Autentique a CLI: `gcloud auth application-default login`.
    *   Configure o projeto padrão: `gcloud config set project SEU_ID_DE_PROJETO`.
    *   Instale o Terraform para gerenciamento de infraestrutura.

### **Fase 1: Desenvolvimento do Core do Agente (Local)**

*Objetivo: Construir e testar a lógica completa do agente em um ambiente local controlado, usando um checkpointer na memória.*

**Pseudocódigo e Estrutura:**

1.  **Definir o Estado do Agente (`state.py`):**
    ```python
    # Usando TypedDict para definir a estrutura do estado que flui pelo grafo
    class AgentState(TypedDict):
        messages: Annotated[list[AnyMessage], operator.add]
        user_id: str
        next_node: str # Campo para controle de fluxo
        tool_outputs: list
    ```

2.  **Implementar as Ferramentas (`tools.py`):**
    ```python
    @tool
    def consultar_status_protocolo(protocolo_id: str) -> str:
        """Consulta o status de um protocolo nos sistemas da prefeitura."""
        # Lógica de mentira para teste local
        if protocolo_id == "123":
            return "Status: Em análise."
        else:
            return "Status: Protocolo não encontrado."
    ```

3.  **Construir o Grafo do Agente (`graph.py`):**
    ```python
    # 1. Inicializar o modelo LLM
    model = VertexAI(model_name="gemini-1.5-pro-001")
    tools = [consultar_status_protocolo]
    model_with_tools = model.bind_tools(tools)

    # 2. Definir o Nó do Agente (o "cérebro")
    def agent_node(state: AgentState):
        response = model_with_tools.invoke(state['messages'])
        return {"messages": [response]}

    # 3. Definir o Nó de Ação (o "músculo")
    def action_node(state: AgentState):
        # Lógica para executar a ferramenta chamada pelo 'agent_node'
        # e retornar o resultado.
        tool_call = state['messages'][-1].tool_calls[0]
        tool_output = ... # Executar a ferramenta
        return {"tool_outputs": [tool_output]}
    
    # 4. Definir as Arestas Condicionais (a "lógica")
    def should_continue(state: AgentState):
        if state['messages'][-1].tool_calls:
            return "action_node"
        else:
            return END

    # 5. Montar o Grafo
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("action", action_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("action", "agent")
    
    # 6. Adicionar Memória (Checkpointer na Memória para teste local)
    memory = MemorySaver()
    agent_graph = workflow.compile(checkpointer=memory)
    ```

4.  **Criar um Teste Interativo (`main.py`):**
    ```python
    def main():
        thread_id = "conversa-teste-local-123"
        config = {"configurable": {"thread_id": thread_id}}

        while True:
            user_input = input("Você: ")
            if user_input.lower() == "sair":
                break
            
            # Invoca o grafo com a entrada do usuário
            response = agent_graph.invoke({"messages": [("user", user_input)]}, config)
            
            # Imprime a resposta final do agente
            print("Agente:", response['messages'][-1].content)
    ```

### **Fase 2: Provisionamento da Infraestrutura em Nuvem (IaC)**

*Objetivo: Usar o Terraform para criar todos os recursos de nuvem necessários de forma automatizada e reprodutível.*

**Arquivo `main.tf` (Pseudocódigo Terraform):**
```terraform
# Configura o provedor Google Cloud
provider "google" {
  project = "SEU_ID_DE_PROJETO"
  region  = "us-central1"
}

# 1. Memorystore for Redis para o Checkpointer
resource "google_redis_instance" "conversation_memory" {
  name           = "redis-agente-rio"
  tier           = "BASIC" # ou STANDARD_HA para produção
  memory_size_gb = 10      # Começar com um tamanho e escalar conforme necessário
}

# 2. Vertex AI Vector Search para RAG
resource "google_vertex_ai_index" "knowledge_base" {
  display_name = "kb-agente-rio"
  # Configuração de dimensões, tipo de índice (ex: ANN), etc.
}

resource "google_vertex_ai_index_endpoint" "knowledge_base_endpoint" {
  display_name = "kb-endpoint-agente-rio"
  public_endpoint_enabled = false # Acesso via rede privada
}

# 3. Conta de Serviço para a Cloud Function (Boas práticas de segurança)
resource "google_service_account" "function_identity" {
  account_id   = "agente-rio-function-sa"
  display_name = "Service Account for Rio Agent Cloud Function"
}

# (Opcional: Adicionar permissões IAM para a conta de serviço acessar Vertex AI, etc.)
```

### **Fase 3: Implantação e Integração na Nuvem**

*Objetivo: Adaptar o código do agente para usar a infraestrutura da nuvem e implantá-lo como uma Cloud Function.*

1.  **Adaptar Código do Agente:**
    *   No `graph.py`, troque o checkpointer de memória pelo checkpointer do Redis.
    ```python
    # Substituir o MemorySaver pelo RedisSaver
    from langgraph.prebuilt import RedisSaver

    # Obter o IP do Redis a partir do Terraform ou variáveis de ambiente
    redis_host = "IP_DO_MEMROYSTORE"
    redis_port = 6379
    
    checkpointer = RedisSaver.from_conn_string(f"redis://{redis_host}:{redis_port}")
    agent_graph = workflow.compile(checkpointer=checkpointer)
    ```

2.  **Criar o Entrypoint da Cloud Function:**
    *   Crie um arquivo `main_cloud.py` que será o ponto de entrada da função. Ele irá lidar com requisições HTTP.
    ```python
    # main_cloud.py
    import functions_framework
    from graph import agent_graph # Importa o grafo compilado

    @functions_framework.http
    def handle_chat_message(request):
        request_json = request.get_json(silent=True)
        user_id = request_json['user_id']
        message = request_json['message']

        config = {"configurable": {"thread_id": user_id}}
        response = agent_graph.invoke({"messages": [("user", message)]}, config)
        
        return {"response": response['messages'][-1].content}
    ```

3.  **Implantar a Cloud Function:**
    *   Use o comando `gcloud` para implantar.
    ```bash
    gcloud functions deploy agente-rio-http \
      --gen2 \
      --runtime=python312 \
      --region=us-central1 \
      --source=. \
      --entry-point=handle_chat_message \
      --trigger-http \
      --allow-unauthenticated \
      --service-account=agente-rio-function-sa@...
    ```

4.  **Configurar o API Gateway:**
    *   Crie uma especificação OpenAPI (`api_spec.yaml`) que define um caminho (ex: `/chat`) e o mapeia para a URL da sua Cloud Function.
    *   Implante a especificação no API Gateway para obter uma URL pública estável e segura.

### **Fase 4: Teste, Monitoramento e Otimização**

*Objetivo: Garantir que a solução implantada funcione corretamente, identificar gargalos e otimizar custos.*

1.  **Teste de Integração:** Use uma ferramenta como Postman ou `curl` para enviar requisições para a URL do API Gateway e verificar as respostas.
2.  **Monitoramento:**
    *   Use o **Cloud Logging** para ver os logs de execução da sua Cloud Function.
    *   Use o **LangSmith** (configurado no código do agente) para rastrear o fluxo de pensamento do agente, ver as chamadas de ferramentas e depurar o comportamento do LLM.
3.  **Otimização de Custos (Planejamento):**
    *   **Redis:** Planeje uma estratégia de TTL (Time-To-Live) para as chaves de conversas para evitar que o Memorystore cresça indefinidamente.
    *   **LLM:** Implemente o roteamento para modelos mais baratos/rápidos para tarefas simples.
    *   **Cache:** Planeje uma camada de cache para perguntas frequentes.

### **Fase 5: Rollout de Produção (Conexão com WhatsApp)**

*Objetivo: Conectar o sistema ao mundo real.*

1.  **Configurar o Broker do WhatsApp (Twilio):**
    *   Na sua conta Twilio, configure o número do WhatsApp.
    *   No campo "A MESSAGE COMES IN", configure o webhook para apontar para a **URL pública do seu Cloud API Gateway**.
    *   Adapte a Cloud Function para receber o formato de requisição da Twilio e enviar respostas no formato esperado por ela.
    