# Agentic Search API

Uma API avançada de chatbot com memória de longo prazo, construída com LangGraph, Google Generative AI e PostgreSQL com pgvector para busca semântica.

## 🎯 Descrição

O Agentic Search API é um sistema de chatbot inteligente que combina:
- **Conversação natural** com modelos de linguagem avançados
- **Memória de longo prazo** persistente em banco de dados
- **Memória de curto prazo** persistente dentro de uma sessão (usando `checkpoint` do `LangChain`)
- **Busca semântica** usando embeddings e pgvector
- **Ferramentas dinâmicas** para operações de memória
- **Arquitetura modular** baseada em LangGraph

O sistema é projetado para manter conversas contextuais e personalizadas, lembrando informações importantes sobre os usuários ao longo do tempo.

## 📁 Estrutura do Repositório

```
app-agentic-search/
├── src/
│   ├── services/
│   │   └── lang_graph/           # 🧠 Core do chatbot
│   │       ├── service.py        # Serviço principal
│   │       ├── graph.py          # Definição do grafo LangGraph
│   │       ├── models.py         # Modelos Pydantic
│   │       ├── tools.py          # Ferramentas de memória
│   │       ├── database.py       # Gerenciamento do banco
│   │       ├── repository.py     # Camada de acesso a dados
│   │       ├── memory.py         # Gerenciador de memória
│   │       ├── llms.py           # Configuração dos LLMs
│   │       ├── chat.py           # Interface de chat CLI
│   │       └── tests/            # Testes automatizados
│   ├── api/                      # 🚀 Endpoints da API
│   ├── admin/                    # 📊 Interface administrativa
│   ├── config/                   # ⚙️ Configurações
│   ├── db/                       # 🗄️ Configuração do banco
│   └── utils/                    # 🛠️ Utilitários
└── logs/                         # 📋 Logs da aplicação
```

## 🧪 Testes

### **Executando Testes**
```bash
# Teste específico
uv run python src/services/lang_graph/test_service.py conversation

# Todos os testes
uv run python src/services/lang_graph/test_service.py all
```

### Testando o Chatbot

```bash
# Teste via CLI
echo "Olá, meu nome é João" | uv run python src/services/lang_graph/chat.py

# Testes automatizados
uv run python src/services/lang_graph/test_service.py conversation
uv run python src/services/lang_graph/test_service.py memory
uv run python src/services/lang_graph/test_service.py all_tools
```

## 🧠 Funcionamento em Alto Nível

### 1. **Fluxo de Conversação**

```
Usuário → LangGraph → Memória → LLM → Resposta
   ↓         ↓         ↓        ↓       ↓
Mensagem → Grafo → Busca → Processamento → Resposta
```

### 2. **Componentes Principais**

#### **LangGraph Service** (`service.py`)
- Gerencia sessões de conversa
- Processa mensagens de forma assíncrona
- Coordena memória e ferramentas

#### **Graph** (`graph.py`)
- Define o fluxo de execução
- Gerencia estados da conversa
- Coordena recuperação de memórias

#### **Memory System** (`memory.py`, `repository.py`)
- Armazena informações em PostgreSQL
- Busca semântica com pgvector
- Tipos de memória: `user_profile`, `preference`, `fact` ...

#### **Tools** (`tools.py`)
- `get_memory_tool`: Busca informações
- `save_memory_tool`: Salva novas informações
- `update_memory_tool`: Atualiza informações existentes
- `delete_memory_tool`: Remove informações

