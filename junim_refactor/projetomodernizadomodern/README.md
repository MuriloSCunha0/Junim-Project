# 🚀 ProjetoModernizadoModern - Spring Boot

## 📋 Sobre este projeto
Projeto Java Spring Boot modernizado automaticamente pelo **JUNIM** a partir de um projeto Delphi.

## ⚙️ Pré-requisitos
- **Java 17** ou superior
- **Maven 3.6** ou superior
- **Git** (opcional)

## � Como executar

### 1. Preparar o ambiente
```bash
# Verificar versão do Java
java -version

# Verificar versão do Maven  
mvn -version
```

### 2. Executar a aplicação
```bash
# Navegar para o diretório do projeto
cd projetomodernizadomodern

# Executar a aplicação
mvn spring-boot:run
```

### 3. Acessar a aplicação
- **API REST:** http://localhost:8080/api
- **Console H2:** http://localhost:8080/h2-console
  - URL: `jdbc:h2:mem:testdb`
  - Usuário: `sa`
  - Senha: *(vazio)*

## 📚 Documentação incluída
- `README.md` - Visão geral do projeto
- `docs/ARQUITETURA.md` - Diagramas e arquitetura
- `docs/COMPARACAO_DELPHI_JAVA.md` - Mapeamento Delphi → Java
- `docs/API_DOCUMENTATION.md` - Documentação das APIs REST
- `docs/DEPLOYMENT.md` - Guia de deployment
- `docs/original/` - Documentação do projeto Delphi original

## 🛠️ Comandos úteis
```bash
# Compilar o projeto
mvn clean compile

# Executar testes
mvn test

# Gerar JAR para produção
mvn clean package

# Executar o JAR gerado
java -jar target/projetomodernizadomodern-1.0.0.jar
```

## 📁 Estrutura do projeto
```
projetomodernizadomodern/
├── src/main/java/com/empresa/sistema/
│   ├── entity/          # Entidades JPA
│   ├── repository/      # Repositórios de dados
│   ├── service/         # Lógica de negócio
│   ├── controller/      # Controllers REST
│   └── Application.java # Classe principal
├── src/main/resources/
│   └── application.yml  # Configurações
├── docs/                # Documentação
├── pom.xml             # Configuração Maven
└── README.md           # Este arquivo
```

## 🆘 Suporte
- **Sistema:** JUNIM - Modernização Delphi → Java
- **Versão:** 2.0
- **Gerado em:** 22/07/2025 às 21:28

Para dúvidas técnicas, consulte a documentação na pasta `docs/`.
