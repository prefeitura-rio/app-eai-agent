# Plano de Implementação: EAI Gateway (Abordagem com Banco de Dados)

Este documento descreve o plano para construir um gateway de API (`eai_gateway`) robusto. A nova abordagem utilizará um banco de dados SQL para gerenciar o mapeamento entre usuários e agentes, garantindo a persistência do contexto da conversa.

## Arquitetura Proposta

A solução será dividida em três componentes principais:

1.  **Agent ID Manager (`src/services/eai_gateway/agent_id_manager.py`):** Uma camada de serviço responsável por toda a interação com o banco de dados para obter, armazenar e deletar o mapeamento `user_number` -> `agent_id`.
2.  **EAI Client (`src/services/eai_gateway/api.py`):** O cliente de baixo nível, refatorado e robusto, responsável exclusivamente pela comunicação com a API externa do Letta.
3.  **API Gateway (`src/api/v1/eai_gateway.py`):** O ponto de entrada para o frontend. Ele orquestra as chamadas, utilizando o `AgentIdManager` para encontrar o agente correto e o `EAIClient` para se comunicar com ele.

---

## Fase 1: Implementação do Agent ID Manager

Esta é a base da nova lógica. Criaremos um serviço para gerenciar o estado dos agentes no banco de dados.

### 1.1. Modelo de Dados (SQLAlchemy)

Em um arquivo de modelos apropriado (ex: `src/models/user_agent_model.py`), definiremos a tabela para o mapeamento.

```python
from sqlalchemy import Column, String
from src.db.database import Base

class UserAgent(Base):
    __tablename__ = "user_agents"

    user_number = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, unique=True)
```

### 1.2. Lógica do Manager (`src/services/eai_gateway/agent_id_manager.py`)

Esta classe conterá toda a lógica de banco de dados.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db_session
from src.models.user_agent_model import UserAgent
from sqlalchemy.future import select

class AgentIdManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_agent_id(self, user_number: str) -> str | None:
        """Busca o agent_id para um user_number no banco de dados."""
        result = await self.session.execute(
            select(UserAgent).filter(UserAgent.user_number == user_number)
        )
        user_agent = result.scalars().first()
        return user_agent.agent_id if user_agent else None

    async def store_agent_id(self, user_number: str, agent_id: str) -> None:
        """Salva ou atualiza o mapeamento user_number -> agent_id."""
        user_agent = UserAgent(user_number=user_number, agent_id=agent_id)
        await self.session.merge(user_agent)
        await self.session.commit()

    async def delete_agent_id(self, user_number: str) -> bool:
        """Deleta o mapeamento para um user_number."""
        result = await self.session.execute(
            select(UserAgent).filter(UserAgent.user_number == user_number)
        )
        user_agent = result.scalars().first()
        if user_agent:
            await self.session.delete(user_agent)
            await self.session.commit()
            return True
        return False

# Função de dependência para o FastAPI
async def get_agent_id_manager(session: AsyncSession = Depends(get_db_session)) -> AgentIdManager:
    return AgentIdManager(session)
```

---

## Fase 2: Refatoração do EAI Client

O cliente será atualizado para ser mais robusto, conforme o plano anterior, mas agora com o caminho do arquivo corrigido.

### 2.1. Modelos Pydantic e Configuração (`src/services/eai_gateway/api.py`)

Usaremos Pydantic para validar os dados de entrada e saída da API do Letta e centralizaremos a configuração.

### 2.2. Classe do Cliente (`src/services/eai_gateway/api.py`)

A classe `EAIClient` será uma representação limpa da API externa, sem qualquer lógica de banco de dados.

```python
# Em src/services/eai_gateway/api.py
# (Estrutura similar à do plano anterior, com Pydantic e tratamento de erros)

class EAIClient:
    # ... inicialização com httpx e configuração ...

    async def create_agent(self, request: CreateAgentRequest) -> Dict[str, Any]:
        # ... implementação ...

    async def send_message_and_get_response(...) -> MessageResponse:
        # ... implementação do polling ...
```

---

## Fase 3: Implementação do API Gateway

O gateway irá orquestrar a lógica, combinando o gerenciamento de agentes com a comunicação com a API do Letta.

### 3.1. Schemas da API do Gateway (`src/api/v1/eai_gateway.py`)

```python
from pydantic import BaseModel
from typing import Dict, Any

class ChatRequest(BaseModel):
    user_number: str
    message: str

class ChatResponse(BaseModel):
    response: Dict[str, Any]
```

### 3.2. Endpoints (`src/api/v1/eai_gateway.py`)

Criaremos os três endpoints solicitados: um para o chat, um para buscar e outro para deletar o agente associado.

```python
from fastapi import APIRouter, Depends, HTTPException
from .agent_id_manager import AgentIdManager, get_agent_id_manager
from .api import EAIClient, CreateAgentRequest, EAIClientError

router = APIRouter(prefix="/eai-gateway", tags=["EAI Gateway"])
eai_client = EAIClient() # Instância única

@router.post("/chat", response_model=ChatResponse)
async def handle_chat(
    request: ChatRequest,
    agent_manager: AgentIdManager = Depends(get_agent_id_manager)
):
    try:
        # 1. Verificar se já existe um agente para o usuário
        agent_id = await agent_manager.get_agent_id(request.user_number)

        # 2. Se não existir, criar um novo e salvá-lo no DB
        if not agent_id:
            create_req = CreateAgentRequest(user_number=request.user_number)
            create_resp = await eai_client.create_agent(create_req)
            agent_id = create_resp.get("agent_id")
            if not agent_id:
                raise HTTPException(status_code=500, detail="Falha ao obter agent_id da API EAI.")
            await agent_manager.store_agent_id(request.user_number, agent_id)

        # 3. Enviar a mensagem e obter a resposta
        response = await eai_client.send_message_and_get_response(
            agent_id=agent_id,
            message=request.message
        )
        return ChatResponse(response=response.model_dump())

    except EAIClientError as e:
        raise HTTPException(status_code=502, detail=f"Erro de comunicação com o serviço EAI: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")


@router.get("/agent/{user_number}", response_model=Dict[str, str | None])
async def get_agent(
    user_number: str,
    agent_manager: AgentIdManager = Depends(get_agent_id_manager)
):
    """Retorna o agent_id associado a um user_number, se existir."""
    agent_id = await agent_manager.get_agent_id(user_number)
    return {"agent_id": agent_id}


@router.delete("/agent/{user_number}", status_code=204)
async def delete_agent_association(
    user_number: str,
    agent_manager: AgentIdManager = Depends(get_agent_id_manager)
):
    """Deleta a associação entre user_number e agent_id."""
    success = await agent_manager.delete_agent_id(user_number)
    if not success:
        raise HTTPException(status_code=404, detail="Nenhuma associação encontrada para este usuário.")
    return None
```

### 3.3. Integração

O novo `router` do `eai_gateway` será incluído no `main.py` da aplicação para que os endpoints fiquem acessíveis.
