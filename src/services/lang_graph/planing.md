# Plano de Ação: Serviço de Chatbot com Memória Persistente em Cloud SQL e Google GenAI

Este documento detalha os passos para a criação de um serviço de conversação de chatbot utilizando LangGraph, com persistência de memória de curto e longo prazo em um banco de dados Google Cloud SQL (PostgreSQL) e utilizando os modelos do Google GenAI.

## 1. Configuração do Ambiente e Dependências

A base para um software robusto é um ambiente bem configurado.

### 1.1. Gerenciamento de Dependências
Adicionar as seguintes bibliotecas ao `pyproject.toml` (ou `requirements.txt`) e instalar com `uv`:
- `langgraph`: Orquestração do fluxo do chatbot.
- `sqlalchemy`: ORM para interação com o banco de dados.
- `psycopg2-binary` ou `asyncpg`: Driver para PostgreSQL. `asyncpg` é preferível para operações assíncronas.
- `google-cloud-sql-python-connector`: Para conectar de forma segura ao Cloud SQL.
- `pgvector`: Extensão para suporte a dados vetoriais no PostgreSQL.
- `langchain-google-genai`: Para integração com os modelos do Google GenAI.

### 1.2. Variáveis de Ambiente
Configurar um arquivo `.env` na raiz do projeto para armazenar credenciais e configurações.
```
# Cloud SQL - PostgreSQL
DB_USER="<seu_usuario>"
DB_PASS="<sua_senha>"
DB_HOST="<seu_ip_ou_instance_connection_name>"
DB_PORT="5432"
DB_NAME="<nome_do_banco>"

# Google GenAI
GOOGLE_API_KEY="<sua_google_api_key>"

# Nomes dos Modelos
EMBEDDING_MODEL_NAME="models/embedding-001"
CHAT_MODEL_NAME="gemini-pro"
```

## 2. Design e Migração do Banco de Dados (Cloud SQL)

A estrutura do banco de dados é crucial para a performance e escalabilidade da memória do agente.

### 2.1. Definição dos Esquemas (Models)
No diretório `src/services/lang_graph/`, criar um arquivo `models.py`. A base declarativa será importada de `src.db.database`.

**Nota:** É necessário garantir que a extensão `pgvector` esteja habilitada na sua instância do Cloud SQL (`CREATE EXTENSION IF NOT EXISTS vector;`).

```python
# src/services/lang_graph/models.py
from sqlalchemy import String, Text, func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
import datetime
from src.db.database import Base # Importa a Base do database.py

class ShortTermMemory(Base):
    __tablename__ = 'langgraph_memory_short_term'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False) # 'user' ou 'eai'
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

class LongTermMemory(Base):
    __tablename__ = 'langgraph_memory_long_term'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False) # 'user' ou 'eai'
    embedding: Mapped[Vector] = mapped_column(Vector(768)) # Dimensão do models/embedding-001
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
```

### 2.2. Configuração do Banco de Dados Assíncrono
O arquivo `src/db/database.py` será configurado para usar `asyncpg` e fornecer uma sessão assíncrona (`AsyncSession`) para a aplicação.

```python
# src/db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
# ...

ASYNC_DATABASE_URL = env.PG_URI.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession)
Base = declarative_base()

@asynccontextmanager
async def get_async_session():
    # ... implementação ...
```

### 2.3. Criação da Migração com Alembic
Usar o Alembic para versionar o schema do banco.
1. Gerar o script de migração:
   ```bash
   alembic revision --autogenerate -m "create short and long term memory tables for genai"
   ```
2. Revisar e aplicar a migração:
   ```bash
   alembic upgrade head
   ```

## 3. Implementação dos Módulos de Acesso a Dados (Repositórios)

O `Repository Pattern` desacopla a lógica de negócio da manipulação do banco.

### 3.1. Repositório de Memória
O arquivo `src/services/lang_graph/repository.py` conterá a classe `MemoryRepository`.

```python
# src/services/lang_graph/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.services.lang_graph.models import ShortTermMemory, LongTermMemory

class MemoryRepository:
    # ... implementação dos métodos ...
```

## 4. Implementação dos Serviços de LLM

Manter a lógica de instanciação de LLMs isolada facilita a manutenção e a troca de modelos e provedores.

### 4.1. Módulo de LLMs
Criar `src/services/lang_graph/llms.py`. Este arquivo conterá:
- `EmbeddingService`: Classe para gerar embeddings.
- `ChatModelFactory`: Uma factory para criar instâncias de modelos de chat, permitindo fácil troca de provedores.

```python
# src/services/lang_graph/llms.py
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Literal

class EmbeddingService:
    # ... implementação ...

class ChatModelFactory:
    @staticmethod
    def create(provider: Literal["google"], model_name: str, temperature: float = 0) -> BaseChatModel:
        if provider == "google":
            return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        else:
            raise ValueError(f"Provedor '{provider}' não é suportado.")

chat_model = ChatModelFactory.create(provider="google", model_name="gemini-pro")
```

## 5. Integração com LangGraph

Conectando todos os componentes no fluxo do LangGraph.

### 5.1. Construção do Grafo
O arquivo `service.py` orquestrará a construção do grafo, importando os modelos de `llms.py`.

```python
# Exemplo da estrutura em src/services/lang_graph/service.py
from langgraph.graph import StateGraph, END
from src.services.lang_graph.llms import EmbeddingService, chat_model
from src.services.lang_graph.repository import MemoryRepository
from src.db.database import get_async_session
# ... outras importações

# ... Nós do Grafo (load_memory_node, call_llm_node, save_memory_node)

workflow = StateGraph(ConversationState)
# ... adição de nós e arestas ...
app = workflow.compile()
```

## 6. Testes

- **Unitários**: Para `MemoryRepository`, `EmbeddingService` e `ChatModelFactory` com mocks.
- **Integração**: Testar o fluxo completo do grafo com um banco de dados de teste.

## 7. Estrutura de Arquivos Proposta

```
src/services/lang_graph/
├── __init__.py
├── planing.md         # Este arquivo
├── models.py          # Definições dos modelos SQLAlchemy
├── repository.py      # Lógica de acesso ao banco de dados
├── llms.py            # Serviços de LLMs (Embedding e Chat)
└── service.py         # Construção e compilação do grafo LangGraph
```
