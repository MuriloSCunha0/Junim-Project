"""
Módulo para construção e estruturação do projeto Java Spring
"""

import os
import re
from typing import Dict, Any, Optional
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JavaBuilder:
    """Classe responsável por construir e estruturar projetos Java Spring"""
    
    def __init__(self):
        """Inicializa o construtor Java"""
        self.project_structure = {}
        self.generated_files = {}
    
    def build_project(self, 
                     generated_code: Dict[str, Any], 
                     project_structure: Dict[str, str],
                     progress_callback: Optional[callable] = None) -> str:
        """
        Constrói projeto Java Spring a partir do código gerado
        
        Args:
            generated_code: Código gerado pelo LLM
            project_structure: Estrutura de diretórios criada
            progress_callback: Callback para progresso
            
        Returns:
            Caminho do projeto construído
        """
        try:
            if progress_callback:
                progress_callback(4, 5, "Estruturando projeto Java Spring...")
            
            logger.info("Iniciando construção do projeto Java")
            
            # Extrai informações do código gerado
            project_name = generated_code.get('project_name', 'modernized_app')
            package_name = generated_code.get('package_name', 'com.example.modernizedapp')
            files = generated_code.get('files', {})
            
            # Atualiza estrutura do projeto
            self.project_structure = project_structure
            base_path = project_structure['base']
            
            # Processa e escreve arquivos
            self._process_and_write_files(files, base_path, package_name)
            
            # Gera arquivos adicionais necessários
            self._generate_additional_files(base_path, package_name, project_name)
            
            # Gera script de validação
            self._generate_validation_script(base_path)
            
            logger.info(f"Projeto Java construído em: {base_path}")
            return base_path
            
        except Exception as e:
            logger.error(f"Erro ao construir projeto Java: {str(e)}")
            raise Exception(f"Falha na construção do projeto Java: {str(e)}")
    
    def _process_and_write_files(self, files: Dict[str, str], base_path: str, package_name: str):
        """Processa e escreve arquivos do projeto"""
        try:
            for file_path, content in files.items():
                # Resolve caminho completo
                full_path = os.path.join(base_path, file_path)
                
                # Cria diretório se necessário
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Processa conteúdo
                processed_content = self._process_file_content(content, package_name, file_path)
                
                # Garante que o conteúdo processado seja uma string
                if not isinstance(processed_content, str):
                    processed_content = str(processed_content)
                
                # Escreve arquivo
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(processed_content)
                
                self.generated_files[file_path] = full_path
                logger.info(f"Arquivo criado: {file_path}")
                
        except Exception as e:
            logger.error(f"Erro ao processar arquivos: {str(e)}")
            raise
    
    def _process_file_content(self, content, package_name: str, file_path: str) -> str:
        """Processa conteúdo de um arquivo específico"""
        try:
            # Se o conteúdo for um dict, extrai o conteúdo da chave 'content'
            if isinstance(content, dict):
                if 'content' in content:
                    content = content['content']
                else:
                    # Se for um dict sem 'content', converte para string
                    content = str(content)
            
            # Garante que o conteúdo seja uma string
            if not isinstance(content, str):
                content = str(content)
            
            # Se o conteúdo não tem package declaration, adiciona
            if file_path.endswith('.java') and 'package ' not in content:
                # Extrai package baseado no caminho
                path_package = self._extract_package_from_path(file_path, package_name)
                if path_package:
                    content = f"package {path_package};\n\n{content}"
            
            # Adiciona imports necessários se não existirem
            if file_path.endswith('.java'):
                content = self._ensure_required_imports(content, file_path)
            
            # Processa arquivos especiais
            if file_path.endswith('pom.xml'):
                content = self._process_pom_xml(content, package_name)
            elif file_path.endswith('application.properties'):
                content = self._process_application_properties(content)
            
            return content
            
        except Exception as e:
            logger.warning(f"Erro ao processar conteúdo do arquivo {file_path}: {str(e)}")
            return str(content) if content else ""
    
    def _extract_package_from_path(self, file_path: str, base_package: str) -> Optional[str]:
        """Extrai nome do package baseado no caminho do arquivo"""
        try:
            # Remove extensão e normaliza separadores
            path_without_ext = file_path.replace('.java', '').replace('\\', '/')
            
            # Procura pela parte java/ no caminho
            java_index = path_without_ext.find('src/main/java/')
            if java_index == -1:
                return base_package
            
            # Extrai caminho após src/main/java/
            package_path = path_without_ext[java_index + len('src/main/java/'):]
            
            # Remove nome do arquivo
            package_parts = package_path.split('/')[:-1]
            
            if package_parts:
                return '.'.join(package_parts)
            else:
                return base_package
                
        except Exception:
            return base_package
    
    def _ensure_required_imports(self, content: str, file_path: str) -> str:
        """Garante que imports necessários estão presentes"""
        try:
            imports_to_add = []
            
            # Identifica tipo de arquivo e imports necessários
            if 'Controller' in file_path:
                required_imports = [
                    'org.springframework.web.bind.annotation.*',
                    'org.springframework.http.ResponseEntity',
                    'org.springframework.beans.factory.annotation.Autowired'
                ]
                imports_to_add.extend(required_imports)
            
            elif 'Service' in file_path:
                required_imports = [
                    'org.springframework.stereotype.Service',
                    'org.springframework.beans.factory.annotation.Autowired'
                ]
                imports_to_add.extend(required_imports)
            
            elif 'Repository' in file_path:
                required_imports = [
                    'org.springframework.data.jpa.repository.JpaRepository',
                    'org.springframework.stereotype.Repository'
                ]
                imports_to_add.extend(required_imports)
            
            elif 'Application' in file_path:
                required_imports = [
                    'org.springframework.boot.SpringApplication',
                    'org.springframework.boot.autoconfigure.SpringBootApplication'
                ]
                imports_to_add.extend(required_imports)
            
            # Adiciona imports que não existem
            for import_stmt in imports_to_add:
                if f'import {import_stmt}' not in content:
                    content = self._add_import(content, import_stmt)
            
            return content
            
        except Exception as e:
            logger.warning(f"Erro ao adicionar imports: {str(e)}")
            return content
    
    def _add_import(self, content: str, import_stmt: str) -> str:
        """Adiciona um import ao arquivo Java"""
        try:
            lines = content.split('\n')
            
            # Encontra posição para inserir import
            package_line = -1
            last_import_line = -1
            
            for i, line in enumerate(lines):
                if line.strip().startswith('package '):
                    package_line = i
                elif line.strip().startswith('import '):
                    last_import_line = i
            
            # Determina onde inserir
            if last_import_line != -1:
                insert_pos = last_import_line + 1
            elif package_line != -1:
                insert_pos = package_line + 2  # Após package e linha em branco
            else:
                insert_pos = 0
            
            # Insere import
            lines.insert(insert_pos, f'import {import_stmt};')
            
            return '\n'.join(lines)
            
        except Exception:
            return content
    
    def _process_pom_xml(self, content: str, package_name: str) -> str:
        """Processa arquivo pom.xml"""
        # Se não há conteúdo de pom.xml, gera um padrão
        if not content or 'pom' not in content.lower():
            return self._generate_default_pom_xml(package_name)
        
        # Verifica se tem dependências essenciais
        essential_deps = [
            'spring-boot-starter-web',
            'spring-boot-starter-data-jpa',
            'spring-boot-starter-validation'
        ]
        
        for dep in essential_deps:
            if dep not in content:
                logger.warning(f"Dependência {dep} não encontrada no pom.xml")
        
        return content
    
    def _process_application_properties(self, content: str) -> str:
        """Processa arquivo application.properties"""
        if not content or 'spring.' not in content:
            return self._generate_default_application_properties()
        
        return content
    
    def _generate_additional_files(self, base_path: str, package_name: str, project_name: str):
        """Gera arquivos adicionais necessários"""
        try:
            # Gera pom.xml se não existir
            pom_path = os.path.join(base_path, 'pom.xml')
            if not os.path.exists(pom_path):
                pom_content = self._generate_default_pom_xml(package_name, project_name)
                with open(pom_path, 'w', encoding='utf-8') as f:
                    f.write(pom_content)
                logger.info("pom.xml padrão gerado")
            
            # Gera application.properties se não existir
            props_path = os.path.join(base_path, 'src/main/resources/application.properties')
            if not os.path.exists(props_path):
                os.makedirs(os.path.dirname(props_path), exist_ok=True)
                props_content = self._generate_default_application_properties()
                with open(props_path, 'w', encoding='utf-8') as f:
                    f.write(props_content)
                logger.info("application.properties padrão gerado")
            
            # Gera README.md
            readme_path = os.path.join(base_path, 'README.md')
            readme_content = self._generate_readme(project_name, package_name)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Gera .gitignore
            gitignore_path = os.path.join(base_path, '.gitignore')
            gitignore_content = self._generate_gitignore()
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
                
        except Exception as e:
            logger.warning(f"Erro ao gerar arquivos adicionais: {str(e)}")
    
    def _generate_default_pom_xml(self, package_name: str, project_name: str = "modernized-app") -> str:
        """Gera pom.xml padrão"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>
    
    <groupId>{package_name}</groupId>
    <artifactId>{project_name}</artifactId>
    <version>1.0.0</version>
    <name>{project_name}</name>
    <description>Projeto modernizado do Delphi para Spring Boot</description>
    
    <properties>
        <java.version>17</java.version>
    </properties>
    
    <dependencies>
        <!-- Spring Boot Starter Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
        <!-- Spring Boot Starter Data JPA -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        
        <!-- Spring Boot Starter Validation -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        
        <!-- H2 Database (para desenvolvimento) -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        
        <!-- SQL Server Driver (se necessário) -->
        <dependency>
            <groupId>com.microsoft.sqlserver</groupId>
            <artifactId>mssql-jdbc</artifactId>
            <scope>runtime</scope>
        </dependency>
        
        <!-- Spring Boot Starter Test -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
"""
    
    def _generate_default_application_properties(self) -> str:
        """Gera application.properties padrão"""
        return """# Application Configuration
spring.application.name=modernized-app

# Server Configuration
server.port=8080

# Database Configuration (H2 - para desenvolvimento)
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA Configuration
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# H2 Console (apenas para desenvolvimento)
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console

# Logging Configuration
logging.level.com.example.modernizedapp=DEBUG
logging.level.org.springframework.web=DEBUG

# Para SQL Server (descomente e configure se necessário)
# spring.datasource.url=jdbc:sqlserver://localhost:1433;databaseName=YourDatabase
# spring.datasource.username=sa
# spring.datasource.password=YourPassword
# spring.datasource.driver-class-name=com.microsoft.sqlserver.jdbc.SQLServerDriver
# spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.SQLServerDialect
"""
    
    def _generate_readme(self, project_name: str, package_name: str) -> str:
        """Gera arquivo README.md"""
        return f"""# {project_name}

Este projeto foi gerado automaticamente pelo **JUNIM** (Java Unified Interoperability Migration), 
uma ferramenta de migração de sistemas Delphi para Java Spring Boot.

## Tecnologias Utilizadas

- Java 17
- Spring Boot 3.2.0
- Spring Data JPA
- Spring Web
- Spring Validation
- Maven
- H2 Database (desenvolvimento)

## Estrutura do Projeto

```
src/
├── main/
│   ├── java/{package_name.replace('.', '/')}/
│   │   ├── controller/     # Controllers REST
│   │   ├── service/        # Lógica de negócio
│   │   ├── repository/     # Acesso a dados
│   │   ├── model/          # Entidades JPA
│   │   └── Application.java
│   └── resources/
│       ├── application.properties
│       └── static/
└── test/
    └── java/
```

## Como Executar

### Pré-requisitos
- Java 17+
- Maven 3.6+

### Executando a aplicação

1. Clone/baixe o projeto
2. Navegue até o diretório do projeto
3. Execute os comandos:

```bash
# Compilar o projeto
mvn clean compile

# Executar testes
mvn test

# Executar a aplicação
mvn spring-boot:run
```

A aplicação estará disponível em: http://localhost:8080

### Console H2 (Desenvolvimento)

Para acessar o console do banco H2 durante o desenvolvimento:
- URL: http://localhost:8080/h2-console
- JDBC URL: jdbc:h2:mem:testdb
- Username: sa
- Password: (deixe em branco)

## Endpoints da API

Os endpoints REST serão listados aqui após a análise do código gerado.

## Configuração de Banco de Dados

Por padrão, o projeto usa H2 em memória para desenvolvimento. 
Para usar SQL Server em produção, edite o arquivo `application.properties`:

```properties
# SQL Server Configuration
spring.datasource.url=jdbc:sqlserver://localhost:1433;databaseName=YourDatabase
spring.datasource.username=sa
spring.datasource.password=YourPassword
spring.datasource.driver-class-name=com.microsoft.sqlserver.jdbc.SQLServerDriver
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.SQLServerDialect
spring.jpa.hibernate.ddl-auto=update
```

## Validação

Execute o script de validação para verificar se o projeto compila corretamente:

- Windows: `validate.bat`
- Linux/Mac: `./validate.sh`

## Observações

- Este projeto foi gerado automaticamente e pode precisar de ajustes manuais
- Verifique a lógica de negócio convertida
- Adapte as configurações de banco conforme necessário
- Execute testes adequados antes de usar em produção

## Suporte

Para questões sobre a migração, consulte a documentação do JUNIM ou 
revise o código Delphi original para entender a lógica de negócio.
"""
    
    def _generate_gitignore(self) -> str:
        """Gera arquivo .gitignore"""
        return """# Compiled class file
*.class

# Log file
*.log

# BlueJ files
*.ctxt

# Mobile Tools for Java (J2ME)
.mtj.tmp/

# Package Files #
*.jar
*.war
*.nar
*.ear
*.zip
*.tar.gz
*.rar

# virtual machine crash logs
hs_err_pid*

# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties
dependency-reduced-pom.xml
buildNumber.properties
.mvn/timing.properties
.mvn/wrapper/maven-wrapper.jar

# IDE
.idea/
*.iws
*.iml
*.ipr
.vscode/
.settings/
.project
.classpath

# OS
.DS_Store
Thumbs.db

# Spring Boot
*.log
/logs/
application-*.properties
!application.properties
"""
    
    def _generate_validation_script(self, base_path: str):
        """Gera scripts de validação"""
        try:
            # Script Windows
            bat_content = """@echo off
echo Validando projeto Java Spring Boot...
echo.

echo Compilando projeto...
mvn clean compile

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✓ Projeto compilado com sucesso!
    echo.
    echo Executando testes...
    mvn test
    
    if %ERRORLEVEL% equ 0 (
        echo.
        echo ✓ Todos os testes passaram!
        echo ✓ Projeto Java validado com sucesso!
    ) else (
        echo.
        echo ✗ Alguns testes falharam. Verifique os logs acima.
    )
) else (
    echo.
    echo ✗ Erro na compilação. Verifique os erros acima.
)

echo.
pause
"""
            
            bat_path = os.path.join(base_path, 'validate.bat')
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            # Script Unix
            sh_content = """#!/bin/bash
echo "Validando projeto Java Spring Boot..."
echo

echo "Compilando projeto..."
mvn clean compile

if [ $? -eq 0 ]; then
    echo
    echo "✓ Projeto compilado com sucesso!"
    echo
    echo "Executando testes..."
    mvn test
    
    if [ $? -eq 0 ]; then
        echo
        echo "✓ Todos os testes passaram!"
        echo "✓ Projeto Java validado com sucesso!"
    else
        echo
        echo "✗ Alguns testes falharam. Verifique os logs acima."
    fi
else
    echo
    echo "✗ Erro na compilação. Verifique os erros acima."
fi

echo
"""
            
            sh_path = os.path.join(base_path, 'validate.sh')
            with open(sh_path, 'w', encoding='utf-8') as f:
                f.write(sh_content)
            
            # Torna executável (Unix)
            try:
                os.chmod(sh_path, 0o755)
            except Exception:
                pass  # Ignora erro no Windows
            
            logger.info("Scripts de validação gerados")
            
        except Exception as e:
            logger.warning(f"Erro ao gerar scripts de validação: {str(e)}")
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Retorna resumo do projeto construído"""
        return {
            'total_files': len(self.generated_files),
            'files': list(self.generated_files.keys()),
            'structure': self.project_structure
        }
