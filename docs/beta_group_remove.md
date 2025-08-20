# Beta Group Remove Script

Este script permite remover números de telefone da whitelist beta, seja removendo grupos inteiros ou números específicos.

## 🚀 **Funcionalidades**

1. **Listar grupos**: Mostra todos os grupos e quantos números cada um tem
2. **Remover grupo completo**: Remove todos os números de um grupo específico
3. **Remover números específicos**: Remove uma lista específica de números
4. **Suporte a ambientes**: Funciona tanto em staging quanto em produção

## 📋 **Como usar**

### 1. Listar todos os grupos disponíveis

```bash
# Staging
uv run src/utils/beta_group_remove.py --list-groups

# Produção  
uv run src/utils/beta_group_remove.py --env production --list-groups
```

### 2. Remover grupo completo

```bash
# Staging
uv run src/utils/beta_group_remove.py --group "nome_do_grupo"

# Produção
uv run src/utils/beta_group_remove.py --env production --group "nome_do_grupo"
```

### 3. Remover números específicos

```bash
# Staging
uv run src/utils/beta_group_remove.py --numbers "21999999999,21888888888"

# Produção
uv run src/utils/beta_group_remove.py --env production --numbers "21999999999,21888888888"
```

## 📝 **Exemplos práticos**

### Listar grupos
```bash
uv run src/utils/beta_group_remove.py --list-groups
```
**Saída:**
```
📋 Grupos encontrados na whitelist:
  📱 prefeitura_interno: 368 números
  📱 iplan_whatsapp_devs: 30 números
  📱 focus_group_presencial: 15 números

📊 Total: 413 números em 3 grupos
```

### Remover grupo completo
```bash
uv run src/utils/beta_group_remove.py --group "test_group"
```
**Saída:**
```
📱 Encontrados 25 números no grupo 'test_group':
  - +5521999999999
  - +5521888888888
  ...

⚠️ ATENÇÃO: Você está prestes a remover 25 números do grupo 'test_group' no ambiente STAGING!
Digite 'CONFIRMAR' para prosseguir: CONFIRMAR
✅ 25 números removidos da whitelist com sucesso
🎉 Grupo 'test_group' removido com sucesso!
```

### Remover números específicos
```bash
uv run src/utils/beta_group_remove.py --numbers "21999999999, 21888888888, 11777777777"
```
**Saída:**
```
📱 Números que serão removidos (6):
  - 552199999999
  - 5521999999999
  - 552188888888
  - 5521888888888
  - 551177777777
  - 5511977777777

⚠️ ATENÇÃO: Você está prentes a remover 6 números no ambiente STAGING!
Digite 'CONFIRMAR' para prosseguir: CONFIRMAR
✅ 6 números removidos da whitelist com sucesso!
```

## 🔧 **Opções da linha de comando**

```bash
uv run src/utils/beta_group_remove.py --help
```

**Parâmetros:**
- `--env {staging,production}`: Ambiente (padrão: staging)
- `--group NOME`: Remove todos os números de um grupo
- `--numbers LISTA`: Remove números específicos (separados por vírgula/espaço)
- `--list-groups`: Lista todos os grupos com contagens

## ⚠️ **Medidas de segurança**

### 1. Confirmação obrigatória
O script **sempre** pede confirmação antes de remover números:
```
⚠️ ATENÇÃO: Você está prestes a remover X números no ambiente PRODUCTION!
Digite 'CONFIRMAR' para prosseguir:
```

### 2. Preview dos números
Sempre mostra quais números serão removidos antes da confirmação.

### 3. Normalização de números
- Automaticamente normaliza números brasileiros
- Gera variações com/sem '9' após DDD
- Remove formatações (parênteses, hífens, espaços)

### 4. Logs detalhados
- Mostra ambiente sendo usado
- Confirma autenticação
- Relatório de quantos números foram removidos

## 🛡️ **Configuração de ambiente**

O script usa as mesmas variáveis de ambiente do script de inserção:

```bash
# Staging
WHITELIST_API_BASE_URL_STAGING=https://services.staging.app.dados.rio/rmi/v1/admin/beta
WHITELIST_ISSUER_STAGING=https://auth-idriohom.apps.rio.gov.br/auth/realms/idrio_cidadao
WHITELIST_CLIENT_ID_STAGING=superapp.apps.rio.gov.br
WHITELIST_CLIENT_SECRET_STAGING=seu_client_secret_staging

# Production
WHITELIST_API_BASE_URL_PROD=https://services.pref.rio/rmi/v1/admin/beta
WHITELIST_ISSUER_PROD=https://auth-idrio.apps.rio.gov.br/auth/realms/idrio_cidadao
WHITELIST_CLIENT_ID_PROD=superapp.apps.rio.gov.br
WHITELIST_CLIENT_SECRET_PROD=seu_client_secret_production
```

## 🚨 **CUIDADOS IMPORTANTES**

1. **Operação irreversível**: Uma vez removidos, os números precisam ser re-adicionados manualmente
2. **Ambiente correto**: Sempre verifique se está usando o ambiente correto (staging vs production)
3. **Backup**: Considere fazer backup dos grupos antes de remover
4. **Teste primeiro**: Teste sempre em staging antes de usar em produção

## 💡 **Casos de uso**

### Limpeza de grupos de teste
```bash
uv run src/utils/beta_group_remove.py --group "test_group_temporario"
```

### Remoção de números específicos
```bash
uv run src/utils/beta_group_remove.py --numbers "21999999999,11888888888"
```

### Auditoria de grupos
```bash
uv run src/utils/beta_group_remove.py --list-groups
```

### Migração entre ambientes
1. Liste grupos em staging: `--list-groups`
2. Remova grupo específico: `--group "nome"`
3. Re-adicione em produção usando o script de inserção
