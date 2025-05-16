# Agentic Search API

API que gerencia os fluxos e ferramentas dos agentes de IA da Prefeitura do Rio de Janeiro.

## Recursos Principais

### Atualização de System Prompt

A API oferece funcionalidades para gerenciar os system prompts dos agentes:

- **Obter System Prompt Atual**: Permite visualizar o conteúdo atual do system prompt de um tipo de agente.
- **Atualizar System Prompt**: Permite atualizar o system prompt tanto no template quanto em todos os agentes existentes.

#### Endpoints

- `GET /api/v1/system-prompt` - Retorna o system prompt atual
- `POST /api/v1/system-prompt` - Atualiza o system prompt

Exemplo de requisição para atualizar o system prompt:

```json
{
  "new_prompt": "Novo conteúdo do system prompt...",
  "agent_type": "agentic_search",
  "update_template": true,
  "update_agents": true,
  "tags": ["agentic_search", "user_123456"]
}
```

#### Backup Automático

O serviço realiza backup automático dos system prompts antes de qualquer alteração, armazenando-os no diretório:

```
src/services/letta/agents/system_prompts/cache/
```

## Executando o Projeto

1. Clone o repositório
2. Configure as variáveis de ambiente conforme necessário
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