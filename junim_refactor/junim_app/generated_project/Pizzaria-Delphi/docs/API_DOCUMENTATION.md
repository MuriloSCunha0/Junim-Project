# 🌐 Documentação das APIs REST

## 📋 Visão Geral

Esta documentação descreve as APIs REST disponíveis no sistema.

**Base URL:** `http://localhost:8080/api`

## 📚 Endpoints Disponíveis

Total de Controllers: **5**


### Base

**Base Path:** `/api/base`

| Método | Endpoint | Descrição | Parâmetros |
|--------|----------|-----------|------------|
| GET | `/api/base` | Listar todos | - |
| GET | `/api/base/{id}` | Buscar por ID | `id` (Long) |
| POST | `/api/base` | Criar novo | Body: Base JSON |
| PUT | `/api/base/{id}` | Atualizar | `id` (Long), Body: Base JSON |
| DELETE | `/api/base/{id}` | Deletar | `id` (Long) |

#### Exemplo de Payload (Base):
```json
{
  "nome": "string",
  "descricao": "string",
  "ativo": true
}
```

#### Respostas:
- **200 OK:** Operação bem-sucedida
- **201 Created:** Recurso criado
- **404 Not Found:** Recurso não encontrado
- **400 Bad Request:** Dados inválidos


### Basecadastro

**Base Path:** `/api/basecadastro`

| Método | Endpoint | Descrição | Parâmetros |
|--------|----------|-----------|------------|
| GET | `/api/basecadastro` | Listar todos | - |
| GET | `/api/basecadastro/{id}` | Buscar por ID | `id` (Long) |
| POST | `/api/basecadastro` | Criar novo | Body: Basecadastro JSON |
| PUT | `/api/basecadastro/{id}` | Atualizar | `id` (Long), Body: Basecadastro JSON |
| DELETE | `/api/basecadastro/{id}` | Deletar | `id` (Long) |

#### Exemplo de Payload (Basecadastro):
```json
{
  "nome": "string",
  "descricao": "string",
  "ativo": true
}
```

#### Respostas:
- **200 OK:** Operação bem-sucedida
- **201 Created:** Recurso criado
- **404 Not Found:** Recurso não encontrado
- **400 Bad Request:** Dados inválidos


### Basepesquisa

**Base Path:** `/api/basepesquisa`

| Método | Endpoint | Descrição | Parâmetros |
|--------|----------|-----------|------------|
| GET | `/api/basepesquisa` | Listar todos | - |
| GET | `/api/basepesquisa/{id}` | Buscar por ID | `id` (Long) |
| POST | `/api/basepesquisa` | Criar novo | Body: Basepesquisa JSON |
| PUT | `/api/basepesquisa/{id}` | Atualizar | `id` (Long), Body: Basepesquisa JSON |
| DELETE | `/api/basepesquisa/{id}` | Deletar | `id` (Long) |

#### Exemplo de Payload (Basepesquisa):
```json
{
  "nome": "string",
  "descricao": "string",
  "ativo": true
}
```

#### Respostas:
- **200 OK:** Operação bem-sucedida
- **201 Created:** Recurso criado
- **404 Not Found:** Recurso não encontrado
- **400 Bad Request:** Dados inválidos


### Close

**Base Path:** `/api/close`

| Método | Endpoint | Descrição | Parâmetros |
|--------|----------|-----------|------------|
| GET | `/api/close` | Listar todos | - |
| GET | `/api/close/{id}` | Buscar por ID | `id` (Long) |
| POST | `/api/close` | Criar novo | Body: Close JSON |
| PUT | `/api/close/{id}` | Atualizar | `id` (Long), Body: Close JSON |
| DELETE | `/api/close/{id}` | Deletar | `id` (Long) |

#### Exemplo de Payload (Close):
```json
{
  "nome": "string",
  "descricao": "string",
  "ativo": true
}
```

#### Respostas:
- **200 OK:** Operação bem-sucedida
- **201 Created:** Recurso criado
- **404 Not Found:** Recurso não encontrado
- **400 Bad Request:** Dados inválidos


### Show

**Base Path:** `/api/show`

| Método | Endpoint | Descrição | Parâmetros |
|--------|----------|-----------|------------|
| GET | `/api/show` | Listar todos | - |
| GET | `/api/show/{id}` | Buscar por ID | `id` (Long) |
| POST | `/api/show` | Criar novo | Body: Show JSON |
| PUT | `/api/show/{id}` | Atualizar | `id` (Long), Body: Show JSON |
| DELETE | `/api/show/{id}` | Deletar | `id` (Long) |

#### Exemplo de Payload (Show):
```json
{
  "nome": "string",
  "descricao": "string",
  "ativo": true
}
```

#### Respostas:
- **200 OK:** Operação bem-sucedida
- **201 Created:** Recurso criado
- **404 Not Found:** Recurso não encontrado
- **400 Bad Request:** Dados inválidos


## 🔧 Como Testar

### Usando curl:

```bash
# Listar todos
curl -X GET http://localhost:8080/api/[entity]

# Buscar por ID
curl -X GET http://localhost:8080/api/[entity]/1

# Criar novo
curl -X POST http://localhost:8080/api/[entity] \
  -H "Content-Type: application/json" \
  -d '{"nome": "Teste", "descricao": "Descrição teste", "ativo": true}'

# Atualizar
curl -X PUT http://localhost:8080/api/[entity]/1 \
  -H "Content-Type: application/json" \
  -d '{"nome": "Teste Atualizado", "descricao": "Nova descrição", "ativo": true}'

# Deletar
curl -X DELETE http://localhost:8080/api/[entity]/1
```

### Usando Postman:
1. Importe a collection (se disponível)
2. Configure a base URL: `http://localhost:8080`
3. Teste os endpoints conforme documentado

---
*Documentação gerada automaticamente pelo JUNIM*
