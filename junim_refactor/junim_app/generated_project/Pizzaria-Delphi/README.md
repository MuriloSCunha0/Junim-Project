# ProjetoModernizadoModern

## 📋 Descrição

Projeto modernizado de **Projeto Original** (Delphi) para **Java Spring Boot**.

### 🎯 Estatísticas da Modernização

- **Projeto Original:** Projeto Original (Delphi)
- **Projeto Modernizado:** ProjetoModernizadoModern (Java Spring Boot)
- **Entidades Geradas:** 5
- **Services:** 5
- **Controllers REST:** 5

## 🚀 Como Executar

### Pré-requisitos
- Java 17+
- Maven 3.6+

### Executar a aplicação
```bash
mvn spring-boot:run
```

### Compilar para produção
```bash
mvn clean package
```

### Executar testes
```bash
mvn test
```

## 🌐 Endpoints da API

A aplicação estará disponível em: `http://localhost:8080`

### Principais endpoints:
- `/api/base` - CRUD para Base
- `/api/basecadastro` - CRUD para Basecadastro
- `/api/basepesquisa` - CRUD para Basepesquisa
- ... e mais 2 endpoint(s)


## 🗂️ Console do Banco H2

Acesse: `http://localhost:8080/h2-console`
- **JDBC URL:** `jdbc:h2:mem:testdb`
- **User:** `sa`
- **Password:** *(vazio)*

## 📚 Documentação Adicional

- [Arquitetura do Sistema](docs/ARQUITETURA.md)
- [Comparação Delphi ↔ Java](docs/COMPARACAO_DELPHI_JAVA.md)
- [Documentação das APIs](docs/API_DOCUMENTATION.md)
- [Guia de Deployment](docs/DEPLOYMENT.md)

## 🔧 Tecnologias Utilizadas

- **Java 17**
- **Spring Boot 3.2.0**
- **Spring Data JPA**
- **H2 Database** (desenvolvimento)
- **Maven**

---
*Projeto gerado automaticamente pelo JUNIM - Sistema de Modernização Delphi → Java*
