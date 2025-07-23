# 🌐 Documentação das APIs REST

## 📋 Visão Geral

Esta documentação descreve as APIs REST disponíveis no sistema.

**Base URL:** `http://localhost:8080/api`

## 📚 Endpoints Disponíveis

Total de Controllers: **2**


### Clientes

**Base Path:** `/api/clientes`

| Método | Endpoint | Descrição | Parâmetros |
|--------|----------|-----------|------------|
| GET | `/api/clientes` | Listar todos | - |
| GET | `/api/clientes/{id}` | Buscar por ID | `id` (Long) |
| POST | `/api/clientes` | Criar novo | Body: Clientes JSON |
| PUT | `/api/clientes/{id}` | Atualizar | `id` (Long), Body: Clientes JSON |
| DELETE | `/api/clientes/{id}` | Deletar | `id` (Long) |

#### Exemplo de Payload (Clientes):
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


### Produtos

**Base Path:** `/api/produtos`

| Método | Endpoint | Descrição | Parâmetros |
|--------|----------|-----------|------------|
| GET | `/api/produtos` | Listar todos | - |
| GET | `/api/produtos/{id}` | Buscar por ID | `id` (Long) |
| POST | `/api/produtos` | Criar novo | Body: Produtos JSON |
| PUT | `/api/produtos/{id}` | Atualizar | `id` (Long), Body: Produtos JSON |
| DELETE | `/api/produtos/{id}` | Deletar | `id` (Long) |

#### Exemplo de Payload (Produtos):
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
