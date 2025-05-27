# Agentic Search API

API que gerencia os fluxos e ferramentas dos agentes de IA da Prefeitura do Rio de Janeiro.

## Recursos Principais

### Atualização de System Prompt

A API oferece funcionalidades para gerenciar os system prompts dos agentes:

- **Obter System Prompt Atual**: Permite visualizar o conteúdo atual do system prompt de um tipo de agente.
- **Atualizar System Prompt**: Permite atualizar o system prompt no banco de dados e em todos os agentes existentes.
- **Histórico de Versões**: Permite visualizar o histórico de alterações nos system prompts.

#### Endpoints

- `GET /api/v1/system-prompt` - Retorna o system prompt atual
- `POST /api/v1/system-prompt` - Atualiza o system prompt
- `GET /api/v1/system-prompt/history` - Retorna o histórico de versões dos prompts

Exemplo de requisição para atualizar o system prompt:

```json
{
  "new_prompt": "Novo conteúdo do system prompt...",
  "agent_type": "agentic_search",
  "update_agents": true,
  "tags": ["agentic_search", "user_123456"],
  "metadata": {
    "author": "admin",
    "reason": "Melhoria na resposta de emergência"
  }
}
```

#### Persistência em Banco de Dados

O sistema armazena todos os system prompts em um banco de dados PostgreSQL, mantendo um histórico completo de versões e implantações:

- **Versionamento automático**: Cada alteração cria uma nova versão do prompt
- **Controle de status**: Apenas uma versão ativa por tipo de agente
- **Rastreamento de implantações**: Registro detalhado de cada implantação em agentes
- **Metadados personalizáveis**: Permite adicionar informações como autor, motivo da alteração, etc.

## Banco de Dados

A aplicação utiliza PostgreSQL para armazenamento de dados. Configure a conexão através da variável de ambiente:

```
PG_URI=postgresql://usuario:senha@localhost:5432/nome_do_banco
```

### Migrações

Para gerenciar o esquema do banco de dados, utilizamos Alembic:

```bash
# Inicializar o banco de dados (cria as tabelas)
# Isso acontece automaticamente ao iniciar a aplicação, mas você pode executar manualmente:
python -c "from src.db import Base, engine; Base.metadata.create_all(bind=engine)"

# Criar uma nova migração
alembic revision --autogenerate -m "descrição da migração"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1
```

## Executando o Projeto

1. Clone o repositório
2. Configure as variáveis de ambiente (incluindo `PG_URI`)
3. Execute os comandos:

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor localmente
uvicorn src.main:app --reload
```

## Documentação da API

Acesse a documentação em:

```
http://localhost:8000/docs
```