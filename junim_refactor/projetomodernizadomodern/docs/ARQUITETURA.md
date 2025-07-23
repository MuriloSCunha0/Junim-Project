# 🏗️ Arquitetura do Sistema - ProjetoModernizadoModern

## Visão Geral

Este documento descreve a arquitetura do sistema modernizado **ProjetoModernizadoModern**, convertido de Delphi para Java Spring Boot.

## 📐 Diagrama de Arquitetura

```mermaid
flowchart TD
    Client[Cliente/Frontend] --> API[API Gateway]
    API --> Controllers{Controllers}
    
    %% Controllers
    Controllers --> C0[ClientesController]
    C0 --> S0[ClientesService]
    S0 --> R0[ClientesRepository]
    R0 --> E0[Clientes]
    Controllers --> C1[ProdutosController]
    C1 --> S1[ProdutosService]
    S1 --> R1[ProdutosRepository]
    R1 --> E1[Produtos]

    %% Database
    E0 --> DB[(H2 Database)]
    E1 --> DB
    E2 --> DB
    
    %% Styling
    classDef controller fill:#e1f5fe
    classDef service fill:#f3e5f5
    classDef repository fill:#e8f5e8
    classDef entity fill:#fff3e0
    
    class C0,C1,C2 controller
    class S0,S1,S2 service
    class R0,R1,R2 repository
    class E0,E1,E2 entity

```

## 🏛️ Padrões Arquiteturais

### 1. **Arquitetura em Camadas (Layered Architecture)**

O sistema segue o padrão de arquitetura em camadas do Spring Boot:

- **Camada de Apresentação (Controllers):** 2 endpoints REST
- **Camada de Negócio (Services):** 2 services de domínio
- **Camada de Dados (Repositories):** 2 repositórios JPA
- **Camada de Persistência (Entities):** 2 entidades de domínio

### 2. **Injeção de Dependência**
Utiliza o container IoC do Spring para gerenciar dependências.

### 3. **Repository Pattern**
Abstração da camada de dados através de interfaces JPA Repository.

### 4. **REST API**
Endpoints RESTful para comunicação cliente-servidor.

## 📦 Estrutura de Pacotes

```
src/main/java/com/empresa/sistema/
├── entity/          # Entidades JPA (2 classes)
├── repository/      # Repositórios (2 interfaces)
├── service/         # Services de negócio (2 classes)
├── controller/      # Controllers REST (2 classes)
└── Application.java # Classe principal
```

## 🔄 Fluxo de Dados

1. **Client** → REST Request → **Controller**
2. **Controller** → Business Logic → **Service**
3. **Service** → Data Access → **Repository**
4. **Repository** → Database → **Entity**
5. **Entity** → **Repository** → **Service** → **Controller** → **Client**

## 📊 Componentes do Sistema

### Entidades

**Entidades JPA:**
- `Clientes.java`
- `Produtos.java`


### Services

**Services de Negócio:**
- `ClientesService.java`
- `ProdutosService.java`


### Controllers

**Controllers REST:**
- `ClientesController.java`
- `ProdutosController.java`


## 🛡️ Segurança

- Configuração básica do Spring Security (pode ser expandida)
- Validação de dados com Bean Validation
- CORS habilitado para desenvolvimento

## 📈 Escalabilidade

- Arquitetura stateless permite escalabilidade horizontal
- Pool de conexões configurável
- Cache de primeiro nível do Hibernate

---
*Gerado automaticamente pelo JUNIM*
