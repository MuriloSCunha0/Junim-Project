# 🚀 Guia de Deployment - ProjetoModernizadoModern

## 📋 Pré-requisitos

### Desenvolvimento
- **Java 17** ou superior
- **Maven 3.6+**
- **Git**

### Produção
- **Java 17** Runtime
- **Banco de dados** (PostgreSQL, MySQL, etc.)
- **Servidor de aplicação** (opcional)

## 🔧 Configuração

### 1. Banco de Dados

#### H2 (Desenvolvimento)
```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    username: sa
    password: ""
```

#### PostgreSQL (Produção)
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/projetomodernizadomodern
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
```

### 2. Variáveis de Ambiente

```bash
# Banco de dados
DB_USERNAME=usuario_db
DB_PASSWORD=senha_db
DB_URL=jdbc:postgresql://localhost:5432/database

# Aplicação
SERVER_PORT=8080
SPRING_PROFILES_ACTIVE=prod
```

## 🐳 Docker

### Dockerfile
```dockerfile
FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/projetomodernizadomodern-1.0.0.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - DB_URL=jdbc:postgresql://db:5432/projetomodernizadomodern
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: projetomodernizadomodern
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🔄 CI/CD Pipeline

### GitHub Actions (.github/workflows/deploy.yml)
```yaml
name: Deploy Application

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Build with Maven
      run: mvn clean package
    
    - name: Build Docker image
      run: docker build -t projetomodernizadomodern:latest .
    
    - name: Deploy to production
      run: |
        # Seus comandos de deploy aqui
```

## ☁️ Deploy na Cloud

### Heroku
```bash
# 1. Login no Heroku
heroku login

# 2. Criar aplicação
heroku create projetomodernizadomodern

# 3. Configurar variáveis
heroku config:set SPRING_PROFILES_ACTIVE=heroku

# 4. Deploy
git push heroku main
```

### AWS ECS
1. Criar cluster ECS
2. Configurar task definition
3. Criar service
4. Configurar load balancer

### Google Cloud Run
```bash
# 1. Build da imagem
gcloud builds submit --tag gcr.io/PROJECT_ID/projetomodernizadomodern

# 2. Deploy
gcloud run deploy --image gcr.io/PROJECT_ID/projetomodernizadomodern --platform managed
```

## 📊 Monitoramento

### Health Check
- **Endpoint:** `/actuator/health`
- **Status:** Verificar se retorna 200 OK

### Métricas
- **Endpoint:** `/actuator/metrics`
- **Prometheus:** Configurar se necessário

### Logs
```bash
# Ver logs da aplicação
docker logs container_name

# Logs em tempo real
docker logs -f container_name
```

## 🔧 Troubleshooting

### Problemas Comuns

1. **Porta já em uso**
   ```bash
   # Verificar processo na porta 8080
   netstat -tulpn | grep 8080
   
   # Matar processo
   kill -9 PID
   ```

2. **Erro de conexão com banco**
   - Verificar variáveis de ambiente
   - Confirmar se banco está rodando
   - Validar credenciais

3. **Memória insuficiente**
   ```bash
   # Aumentar heap size
   java -Xmx2g -jar app.jar
   ```

## 📝 Checklist de Deploy

- [ ] ✅ Aplicação compila sem erros
- [ ] ✅ Testes passando
- [ ] ✅ Banco de dados configurado
- [ ] ✅ Variáveis de ambiente definidas
- [ ] ✅ Health check funcionando
- [ ] ✅ Logs configurados
- [ ] ✅ Backup dos dados
- [ ] ✅ Plano de rollback definido

---
*Guia gerado automaticamente pelo JUNIM*
