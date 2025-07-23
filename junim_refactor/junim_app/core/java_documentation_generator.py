"""
Gerador de Documentação para Projetos Java - Documenta projetos modernizados
Gera documentação estruturada similar ao DocumentationGenerator, mas focado em Java Spring Boot
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class JavaDocumentationGenerator:
    """
    Gera documentação estruturada para projetos Java Spring Boot
    Permite comparação com documentação do projeto Delphi original
    """
    
    def __init__(self, prompt_manager=None, llm_client=None):
        self.prompt_manager = prompt_manager
        self.llm_client = llm_client
        
        # Tipos de documentação específicos para Java
        self.java_document_types = {
            'api_documentation': {
                'title': 'Documentação da API REST',
                'description': 'Endpoints, DTOs e contratos da API',
                'use_llm': True,
                'prompt_type': 'api_documentation'
            },
            'architecture_overview': {
                'title': 'Visão Geral da Arquitetura',
                'description': 'Estrutura em camadas e componentes Spring',
                'use_llm': True,
                'prompt_type': 'architecture_analysis'
            },
            'component_catalog': {
                'title': 'Catálogo de Componentes',
                'description': 'Controllers, Services, Repositories e Entities',
                'use_llm': True,
                'prompt_type': 'component_catalog'
            },
            'database_schema': {
                'title': 'Esquema de Banco de Dados',
                'description': 'Entidades JPA e relacionamentos',
                'use_llm': True,
                'prompt_type': 'database_schema'
            },
            'spring_configuration': {
                'title': 'Configurações Spring',
                'description': 'Beans, propriedades e perfis',
                'use_llm': True,
                'prompt_type': 'spring_configuration'
            },
            'system_diagram': {
                'title': 'Diagrama do Sistema',
                'description': 'Arquitetura visual em Mermaid',
                'use_llm': True,
                'prompt_type': 'java_system_diagram'
            },
            'deployment_guide': {
                'title': 'Guia de Deploy',
                'description': 'Instruções de configuração e implantação',
                'use_llm': True,
                'prompt_type': 'deployment_guide'
            },
            'comparison_analysis': {
                'title': 'Análise Comparativa',
                'description': 'Comparação com o projeto Delphi original',
                'use_llm': True,
                'prompt_type': 'comparison_analysis'
            }
        }
    
    def generate_java_documentation(self, java_analysis: Dict[str, Any], 
                                  comparison_data: Optional[Dict[str, Any]] = None,
                                  output_dir: str = "output") -> Dict[str, str]:
        """
        Gera documentação completa para projeto Java
        
        Args:
            java_analysis: Resultado do JavaProjectAnalyzer
            comparison_data: Dados de comparação com projeto Delphi (opcional)
            output_dir: Diretório de saída
            
        Returns:
            Dict com documentos gerados {tipo: conteúdo}
        """
        logger.info(f"📝 Iniciando geração de documentação Java para {java_analysis['metadata']['project_name']}")
        
        try:
            generated_docs = {}
            
            # Cria diretório de saída se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Gera cada tipo de documento
            for doc_type, config in self.java_document_types.items():
                logger.info(f"📄 Gerando: {config['title']}")
                
                if doc_type == 'comparison_analysis' and not comparison_data:
                    logger.info("⏭️ Pulando análise comparativa (dados não fornecidos)")
                    continue
                
                try:
                    if config['use_llm'] and self.llm_client and self.prompt_manager:
                        content = self._generate_llm_documentation(
                            doc_type, java_analysis, comparison_data
                        )
                    else:
                        content = self._generate_fallback_documentation(
                            doc_type, java_analysis, comparison_data
                        )
                    
                    if content and self._validate_java_content(content, java_analysis['metadata']['project_name']):
                        generated_docs[doc_type] = content
                        
                        # Salva arquivo individual
                        filename = f"{doc_type}_{java_analysis['metadata']['project_name']}.md"
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"✅ Salvo: {filepath}")
                    else:
                        logger.warning(f"⚠️ Conteúdo inválido para {doc_type}")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao gerar {doc_type}: {str(e)}")
                    # Gera fallback em caso de erro
                    fallback_content = self._generate_error_fallback(doc_type, java_analysis)
                    generated_docs[doc_type] = fallback_content
            
            logger.info(f"✅ Documentação Java completa: {len(generated_docs)} documentos gerados")
            return generated_docs
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de documentação Java: {str(e)}")
            raise Exception(f"Falha na geração de documentação Java: {str(e)}")
    
    def _generate_llm_documentation(self, doc_type: str, java_analysis: Dict[str, Any], 
                                  comparison_data: Optional[Dict[str, Any]]) -> str:
        """Gera documentação usando LLM"""
        try:
            # Obtém prompt específico
            prompt = self._get_java_prompt(doc_type)
            
            # Prepara contexto
            context = self._prepare_java_context(java_analysis, comparison_data, doc_type)
            
            # Chama LLM
            full_prompt = f"{prompt}\n\n=== CONTEXTO DO PROJETO ===\n{context}"
            response = self.llm_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=4000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            if not content or len(content.strip()) < 100:
                raise ValueError("Resposta LLM muito curta ou vazia")
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro LLM para {doc_type}: {str(e)}")
            raise
    
    def _get_java_prompt(self, doc_type: str) -> str:
        """Obtém prompt específico para documentação Java"""
        java_prompts = {
            'api_documentation': """
Gere documentação completa da API REST deste projeto Java Spring Boot.

INSTRUÇÕES:
- Documente todos os endpoints encontrados
- Inclua métodos HTTP, paths e parâmetros
- Descreva DTOs e contratos de dados
- Adicione exemplos de request/response quando possível
- Use formato Markdown estruturado
- Seja específico ao projeto analisado

ESTRUTURA ESPERADA:
# Documentação da API REST - [Nome do Projeto]

## Visão Geral
[Descrição geral da API]

## Controllers e Endpoints
### [Controller Name]
- **GET** `/path` - Descrição
- **POST** `/path` - Descrição

## DTOs e Modelos de Dados
[Estruturas de dados utilizadas]

## Códigos de Resposta
[Status codes e significados]
""",
            
            'architecture_overview': """
Gere visão geral da arquitetura deste projeto Java Spring Boot.

INSTRUÇÕES:
- Descreva a arquitetura em camadas utilizada
- Explique o padrão MVC implementado
- Detalhe a organização de pacotes
- Mencione frameworks e bibliotecas principais
- Use diagramas em texto quando útil
- Seja específico ao projeto analisado

ESTRUTURA ESPERADA:
# Arquitetura do Sistema - [Nome do Projeto]

## Visão Geral
[Descrição da arquitetura]

## Camadas da Aplicação
### Camada de Apresentação (Controllers)
### Camada de Negócio (Services)
### Camada de Persistência (Repositories)

## Organização de Pacotes
[Estrutura de diretórios]

## Tecnologias Utilizadas
[Stack tecnológico]
""",
            
            'component_catalog': """
Gere catálogo completo dos componentes Spring deste projeto.

INSTRUÇÕES:
- Liste todos os Controllers, Services, Repositories e Entities
- Descreva a responsabilidade de cada componente
- Mencione dependências entre componentes
- Inclua anotações Spring utilizadas
- Seja específico ao projeto analisado

ESTRUTURA ESPERADA:
# Catálogo de Componentes - [Nome do Projeto]

## Controllers
### [Nome do Controller]
- **Responsabilidade:** [descrição]
- **Endpoints:** [lista]
- **Dependências:** [services utilizados]

## Services
### [Nome do Service]
- **Responsabilidade:** [descrição]
- **Métodos principais:** [lista]

## Repositories
### [Nome do Repository]
- **Entidade:** [entidade gerenciada]
- **Queries customizadas:** [se houver]

## Entities
### [Nome da Entity]
- **Tabela:** [nome da tabela]
- **Relacionamentos:** [se houver]
""",
            
            'database_schema': """
Gere documentação do esquema de banco de dados baseado nas entidades JPA.

INSTRUÇÕES:
- Documente todas as entidades encontradas
- Descreva campos e tipos de dados
- Explique relacionamentos entre entidades
- Inclua constraints e índices quando visíveis
- Seja específico ao projeto analisado

ESTRUTURA ESPERADA:
# Esquema de Banco de Dados - [Nome do Projeto]

## Entidades
### [Nome da Entidade]
- **Tabela:** `nome_tabela`
- **Campos:**
  - `id` (Long) - Chave primária
  - `campo` (String) - Descrição

## Relacionamentos
[Diagramas de relacionamento em texto]

## Índices e Constraints
[Se identificados]
""",
            
            'spring_configuration': """
Gere documentação das configurações Spring do projeto.

INSTRUÇÕES:
- Documente arquivos de configuração encontrados
- Explique propriedades principais
- Mencione perfis (profiles) se existirem
- Descreva beans customizados
- Seja específico ao projeto analisado

ESTRUTURA ESPERADA:
# Configurações Spring - [Nome do Projeto]

## Arquivos de Configuração
### application.properties/yml
[Propriedades principais]

## Perfis de Execução
[Se houver profiles]

## Beans Customizados
[Configurações especiais]

## Dependências
[Spring Boot starters utilizados]
""",
            
            'java_system_diagram': """
Gere diagrama Mermaid da arquitetura do sistema Java Spring Boot.

INSTRUÇÕES CRÍTICAS:
- Use APENAS sintaxe Mermaid válida
- Represente Controllers, Services, Repositories e Entities
- Mostre fluxo de dados entre camadas
- Inclua banco de dados se houver entities
- Seja específico ao projeto analisado
- VALIDAR sintaxe Mermaid antes de retornar

EXEMPLO DE ESTRUTURA:
```mermaid
graph TD
    subgraph "Presentation Layer"
        Controller1[UserController]
        Controller2[ProductController]
    end
    
    subgraph "Business Layer"
        Service1[UserService]
        Service2[ProductService]
    end
    
    subgraph "Data Layer"
        Repo1[UserRepository]
        Repo2[ProductRepository]
        Entity1[User]
        Entity2[Product]
    end
    
    subgraph "Database"
        DB[(Database)]
    end
    
    Controller1 --> Service1
    Controller2 --> Service2
    Service1 --> Repo1
    Service2 --> Repo2
    Repo1 --> Entity1
    Repo2 --> Entity2
    Entity1 --> DB
    Entity2 --> DB
```

IMPORTANTE: Adapte o diagrama aos componentes REAIS encontrados no projeto.
""",
            
            'deployment_guide': """
Gere guia de deployment para este projeto Java Spring Boot.

INSTRUÇÕES:
- Inclua pré-requisitos (Java, banco, etc.)
- Descreva processo de build
- Explique configurações de ambiente
- Mencione opções de deployment (JAR, Docker, etc.)
- Seja específico ao projeto analisado

ESTRUTURA ESPERADA:
# Guia de Deploy - [Nome do Projeto]

## Pré-requisitos
- Java [versão]
- Banco de dados [tipo]
- Maven/Gradle

## Build do Projeto
```bash
# Comandos de build
```

## Configuração de Ambiente
[Variáveis de ambiente necessárias]

## Deployment
### Execução Local
### Docker
### Produção
""",
            
            'comparison_analysis': """
Gere análise comparativa entre o projeto Java modernizado e o projeto Delphi original.

INSTRUÇÕES:
- Compare funcionalidades implementadas
- Destaque melhorias arquiteturais
- Identifique gaps ou funcionalidades perdidas
- Explique benefícios da modernização
- Use dados de comparação fornecidos
- Seja específico aos projetos analisados

ESTRUTURA ESPERADA:
# Análise Comparativa - Delphi vs Java

## Resumo da Migração
[Status geral da migração]

## Mapeamento de Funcionalidades
[Comparação função a função]

## Melhorias Arquiteturais
[Benefícios da nova arquitetura]

## Gaps Identificados
[Funcionalidades não migradas]

## Recomendações
[Próximos passos]
"""
        }
        
        return java_prompts.get(doc_type, "Gere documentação para este projeto Java Spring Boot.")
    
    def _prepare_java_context(self, java_analysis: Dict[str, Any], 
                            comparison_data: Optional[Dict[str, Any]], 
                            doc_type: str) -> str:
        """Prepara contexto específico para cada tipo de documento"""
        context_parts = []
        
        # Metadados do projeto
        metadata = java_analysis['metadata']
        context_parts.append(f"PROJETO: {metadata['project_name']}")
        context_parts.append(f"TIPO: {metadata['project_type']}")
        context_parts.append(f"ARQUIVOS ANALISADOS: {metadata['total_files']}")
        
        # Contexto específico por tipo de documento
        if doc_type == 'api_documentation':
            # Endpoints e controllers
            endpoints = java_analysis.get('api_endpoints', [])
            controllers = java_analysis['spring_components']['controllers']
            
            context_parts.append("\n=== ENDPOINTS DA API ===")
            for endpoint in endpoints:
                context_parts.append(f"- {endpoint['http_method']} {endpoint.get('base_path', '')}/{endpoint['method_name']}")
            
            context_parts.append("\n=== CONTROLLERS ===")
            for controller in controllers:
                context_parts.append(f"- {controller['name']}: {len(controller['endpoints'])} endpoints")
        
        elif doc_type == 'architecture_overview':
            # Estrutura geral e componentes
            components = java_analysis['spring_components']['component_summary']
            packages = java_analysis['project_structure']['packages']
            
            context_parts.append(f"\n=== COMPONENTES ===")
            context_parts.append(f"Controllers: {components['total_controllers']}")
            context_parts.append(f"Services: {components['total_services']}")
            context_parts.append(f"Repositories: {components['total_repositories']}")
            context_parts.append(f"Entities: {components['total_entities']}")
            
            context_parts.append(f"\n=== PACOTES ===")
            for package in packages[:10]:  # Primeiros 10 pacotes
                context_parts.append(f"- {package}")
        
        elif doc_type == 'component_catalog':
            # Detalhes de todos os componentes
            spring_components = java_analysis['spring_components']
            
            context_parts.append("\n=== CONTROLLERS ===")
            for controller in spring_components['controllers']:
                context_parts.append(f"- {controller['name']}")
                for endpoint in controller['endpoints']:
                    context_parts.append(f"  - {endpoint['http_method']} {endpoint['method_name']}")
            
            context_parts.append("\n=== SERVICES ===")
            for service in spring_components['services']:
                context_parts.append(f"- {service['name']}")
                for method in service['public_methods'][:5]:  # Primeiros 5 métodos
                    context_parts.append(f"  - {method}")
            
            context_parts.append("\n=== ENTITIES ===")
            for entity in spring_components['entities']:
                context_parts.append(f"- {entity['name']} (tabela: {entity.get('table_name', 'N/A')})")
        
        elif doc_type == 'database_schema':
            # Entidades JPA e relacionamentos
            entities = java_analysis['spring_components']['entities']
            
            context_parts.append("\n=== ENTIDADES JPA ===")
            for entity in entities:
                context_parts.append(f"- {entity['name']}")
                context_parts.append(f"  Tabela: {entity.get('table_name', 'N/A')}")
                
                fields = entity.get('fields', [])
                if fields:
                    context_parts.append("  Campos:")
                    for field in fields[:10]:  # Primeiros 10 campos
                        context_parts.append(f"    - {field['name']} ({field['type']})")
                
                relationships = entity.get('relationships', [])
                if relationships:
                    context_parts.append("  Relacionamentos:")
                    for rel in relationships:
                        context_parts.append(f"    - {rel['type']} com {rel['target_entity']}")
        
        elif doc_type == 'spring_configuration':
            # Configurações e dependências
            dependencies = java_analysis.get('dependencies', {})
            
            if dependencies.get('spring_boot_starters'):
                context_parts.append("\n=== SPRING BOOT STARTERS ===")
                for starter in dependencies['spring_boot_starters']:
                    context_parts.append(f"- {starter}")
            
            if dependencies.get('maven_dependencies'):
                context_parts.append("\n=== DEPENDÊNCIAS MAVEN ===")
                for dep in dependencies['maven_dependencies'][:10]:  # Primeiras 10
                    context_parts.append(f"- {dep['groupId']}:{dep['artifactId']}")
        
        elif doc_type == 'java_system_diagram':
            # Componentes para diagrama
            components = java_analysis['spring_components']
            
            context_parts.append("\n=== COMPONENTES PARA DIAGRAMA ===")
            context_parts.append("Controllers:")
            for controller in components['controllers']:
                context_parts.append(f"- {controller['name']}")
            
            context_parts.append("Services:")
            for service in components['services']:
                context_parts.append(f"- {service['name']}")
            
            context_parts.append("Repositories:")
            for repo in components['repositories']:
                context_parts.append(f"- {repo['name']}")
            
            context_parts.append("Entities:")
            for entity in components['entities']:
                context_parts.append(f"- {entity['name']}")
        
        elif doc_type == 'comparison_analysis' and comparison_data:
            # Dados de comparação
            context_parts.append("\n=== DADOS DE COMPARAÇÃO ===")
            
            mapping = comparison_data.get('functionality_mapping', {})
            if mapping.get('mapping_summary'):
                summary = mapping['mapping_summary']
                context_parts.append(f"Funções Delphi: {summary['total_delphi_functions']}")
                context_parts.append(f"Métodos Java: {summary['total_java_methods']}")
                context_parts.append(f"Mapeadas: {summary['mapped_functions']}")
                context_parts.append(f"Não mapeadas: {summary['unmapped_functions']}")
            
            coverage = comparison_data.get('migration_coverage', {})
            if coverage:
                context_parts.append(f"Cobertura geral: {coverage.get('overall_coverage_percent', 0):.1f}%")
            
            validation = comparison_data.get('validation_results', {})
            if validation.get('overall_status'):
                context_parts.append(f"Status validação: {validation['overall_status']}")
        
        return "\n".join(context_parts)
    
    def _generate_fallback_documentation(self, doc_type: str, java_analysis: Dict[str, Any], 
                                       comparison_data: Optional[Dict[str, Any]]) -> str:
        """Gera documentação fallback sem LLM"""
        project_name = java_analysis['metadata']['project_name']
        
        if doc_type == 'api_documentation':
            return self._create_api_fallback(project_name, java_analysis)
        elif doc_type == 'architecture_overview':
            return self._create_architecture_fallback(project_name, java_analysis)
        elif doc_type == 'component_catalog':
            return self._create_component_fallback(project_name, java_analysis)
        elif doc_type == 'database_schema':
            return self._create_database_fallback(project_name, java_analysis)
        elif doc_type == 'spring_configuration':
            return self._create_configuration_fallback(project_name, java_analysis)
        elif doc_type == 'java_system_diagram':
            return self._create_diagram_fallback(project_name, java_analysis)
        elif doc_type == 'deployment_guide':
            return self._create_deployment_fallback(project_name, java_analysis)
        elif doc_type == 'comparison_analysis' and comparison_data:
            return self._create_comparison_fallback(project_name, comparison_data)
        else:
            return self._create_generic_java_fallback(project_name, doc_type, java_analysis)
    
    def _create_api_fallback(self, project_name: str, java_analysis: Dict[str, Any]) -> str:
        """Cria documentação fallback da API"""
        content = [
            f"# 📡 Documentação da API REST - {project_name}",
            f"\n**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\n## 🎯 Visão Geral",
            f"API REST desenvolvida em Java Spring Boot para o projeto {project_name}.",
        ]
        
        # Controllers e endpoints
        controllers = java_analysis['spring_components']['controllers']
        if controllers:
            content.append("\n## 🎮 Controllers e Endpoints")
            for controller in controllers:
                content.append(f"\n### {controller['name']}")
                
                if controller.get('base_mapping'):
                    content.append(f"**Base Path:** `{controller['base_mapping']}`")
                
                endpoints = controller.get('endpoints', [])
                if endpoints:
                    content.append("\n**Endpoints:**")
                    for endpoint in endpoints:
                        http_method = endpoint.get('http_method', 'GET')
                        method_name = endpoint.get('method_name', 'unknown')
                        content.append(f"- **{http_method}** `/{method_name}` - {method_name}")
                else:
                    content.append("- Nenhum endpoint específico identificado")
        else:
            content.append("\n## ⚠️ Controllers")
            content.append("Nenhum controller REST identificado no projeto.")
        
        # Resumo de endpoints
        all_endpoints = java_analysis.get('api_endpoints', [])
        if all_endpoints:
            content.append(f"\n## 📊 Resumo")
            content.append(f"- **Total de Controllers:** {len(controllers)}")
            content.append(f"- **Total de Endpoints:** {len(all_endpoints)}")
            
            # Agrupa por método HTTP
            http_methods = {}
            for endpoint in all_endpoints:
                method = endpoint.get('http_method', 'UNKNOWN')
                http_methods[method] = http_methods.get(method, 0) + 1
            
            content.append("\n**Distribuição por Método HTTP:**")
            for method, count in http_methods.items():
                content.append(f"- {method}: {count} endpoints")
        
        return "\n".join(content)
    
    def _create_architecture_fallback(self, project_name: str, java_analysis: Dict[str, Any]) -> str:
        """Cria documentação fallback da arquitetura"""
        content = [
            f"# 🏗️ Arquitetura do Sistema - {project_name}",
            f"\n**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\n## 🎯 Visão Geral",
            f"Arquitetura do sistema {project_name} baseada em Spring Boot com padrão MVC em camadas.",
        ]
        
        # Componentes por camada
        components = java_analysis['spring_components']['component_summary']
        content.extend([
            "\n## 📋 Camadas da Aplicação",
            "\n### 🎮 Camada de Apresentação (Controllers)",
            f"- **Total:** {components['total_controllers']} controllers",
            "- **Responsabilidade:** Exposição de APIs REST e controle de fluxo",
            
            "\n### ⚙️ Camada de Negócio (Services)",
            f"- **Total:** {components['total_services']} services",
            "- **Responsabilidade:** Lógica de negócio e processamento",
            
            "\n### 🗄️ Camada de Persistência (Repositories)",
            f"- **Total:** {components['total_repositories']} repositories",
            "- **Responsabilidade:** Acesso a dados e persistência",
            
            "\n### 📦 Camada de Dados (Entities)",
            f"- **Total:** {components['total_entities']} entities",
            "- **Responsabilidade:** Mapeamento objeto-relacional"
        ])
        
        # Organização de pacotes
        packages = java_analysis['project_structure']['packages']
        if packages:
            content.append("\n## 📁 Organização de Pacotes")
            main_package = java_analysis['project_structure'].get('main_package', 'N/A')
            content.append(f"**Pacote Principal:** `{main_package}`")
            content.append("\n**Estrutura de Pacotes:**")
            for package in packages[:10]:
                content.append(f"- `{package}`")
            if len(packages) > 10:
                content.append(f"- ... e mais {len(packages) - 10} pacotes")
        
        # Tecnologias
        dependencies = java_analysis.get('dependencies', {})
        starters = dependencies.get('spring_boot_starters', [])
        if starters:
            content.append("\n## 💻 Tecnologias Utilizadas")
            content.append("**Spring Boot Starters:**")
            for starter in starters:
                content.append(f"- {starter}")
        
        return "\n".join(content)
    
    def _create_component_fallback(self, project_name: str, java_analysis: Dict[str, Any]) -> str:
        """Cria catálogo fallback de componentes"""
        content = [
            f"# 📋 Catálogo de Componentes - {project_name}",
            f"\n**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\n## 🎯 Visão Geral",
            f"Catálogo completo dos componentes Spring do projeto {project_name}.",
        ]
        
        spring_components = java_analysis['spring_components']
        
        # Controllers
        controllers = spring_components['controllers']
        content.append(f"\n## 🎮 Controllers ({len(controllers)})")
        if controllers:
            for controller in controllers:
                content.append(f"\n### {controller['name']}")
                content.append(f"- **Arquivo:** `{controller['file']}`")
                
                if controller.get('base_mapping'):
                    content.append(f"- **Base Path:** `{controller['base_mapping']}`")
                
                endpoints = controller.get('endpoints', [])
                if endpoints:
                    content.append(f"- **Endpoints:** {len(endpoints)} identificados")
                    for endpoint in endpoints[:5]:  # Primeiros 5
                        content.append(f"  - {endpoint['http_method']} {endpoint['method_name']}")
                    if len(endpoints) > 5:
                        content.append(f"  - ... e mais {len(endpoints) - 5} endpoints")
        else:
            content.append("Nenhum controller identificado.")
        
        # Services
        services = spring_components['services']
        content.append(f"\n## ⚙️ Services ({len(services)})")
        if services:
            for service in services:
                content.append(f"\n### {service['name']}")
                content.append(f"- **Arquivo:** `{service['file']}`")
                
                methods = service.get('public_methods', [])
                if methods:
                    content.append(f"- **Métodos Públicos:** {len(methods)}")
                    for method in methods[:5]:  # Primeiros 5
                        content.append(f"  - {method}")
                    if len(methods) > 5:
                        content.append(f"  - ... e mais {len(methods) - 5} métodos")
        else:
            content.append("Nenhum service identificado.")
        
        # Repositories
        repositories = spring_components['repositories']
        content.append(f"\n## 🗄️ Repositories ({len(repositories)})")
        if repositories:
            for repo in repositories:
                content.append(f"\n### {repo['name']}")
                content.append(f"- **Arquivo:** `{repo['file']}`")
                
                if repo.get('entity_type'):
                    content.append(f"- **Entidade:** {repo['entity_type']}")
                
                queries = repo.get('custom_queries', [])
                if queries:
                    content.append(f"- **Queries Customizadas:** {len(queries)}")
        else:
            content.append("Nenhum repository identificado.")
        
        # Entities
        entities = spring_components['entities']
        content.append(f"\n## 📦 Entities ({len(entities)})")
        if entities:
            for entity in entities:
                content.append(f"\n### {entity['name']}")
                content.append(f"- **Arquivo:** `{entity['file']}`")
                
                if entity.get('table_name'):
                    content.append(f"- **Tabela:** `{entity['table_name']}`")
                
                fields = entity.get('fields', [])
                if fields:
                    content.append(f"- **Campos:** {len(fields)}")
                
                relationships = entity.get('relationships', [])
                if relationships:
                    content.append(f"- **Relacionamentos:** {len(relationships)}")
        else:
            content.append("Nenhuma entity identificada.")
        
        return "\n".join(content)
    
    def _create_database_fallback(self, project_name: str, java_analysis: Dict[str, Any]) -> str:
        """Cria documentação fallback do banco"""
        content = [
            f"# 🗄️ Esquema de Banco de Dados - {project_name}",
            f"\n**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\n## 🎯 Visão Geral",
            f"Esquema de banco de dados baseado nas entidades JPA do projeto {project_name}.",
        ]
        
        entities = java_analysis['spring_components']['entities']
        
        if entities:
            content.append(f"\n## 📦 Entidades ({len(entities)})")
            
            for entity in entities:
                content.append(f"\n### {entity['name']}")
                
                if entity.get('table_name'):
                    content.append(f"- **Tabela:** `{entity['table_name']}`")
                else:
                    content.append(f"- **Tabela:** `{entity['name'].lower()}`")
                
                # Campos
                fields = entity.get('fields', [])
                if fields:
                    content.append("\n**Campos:**")
                    for field in fields:
                        field_name = field.get('name', 'unknown')
                        field_type = field.get('type', 'unknown')
                        annotation = field.get('annotation', '')
                        
                        field_desc = f"- `{field_name}` ({field_type})"
                        if annotation == 'Id':
                            field_desc += " - Chave primária"
                        elif annotation == 'Column':
                            field_desc += " - Coluna"
                        
                        content.append(field_desc)
                
                # Relacionamentos
                relationships = entity.get('relationships', [])
                if relationships:
                    content.append("\n**Relacionamentos:**")
                    for rel in relationships:
                        rel_type = rel.get('type', 'unknown')
                        target_entity = rel.get('target_entity', 'unknown')
                        field_name = rel.get('field_name', 'unknown')
                        content.append(f"- `{field_name}` - {rel_type} com {target_entity}")
            
            # Resumo do banco
            content.append(f"\n## 📊 Resumo do Banco")
            content.append(f"- **Total de Entidades:** {len(entities)}")
            
            tables = [e.get('table_name', e['name'].lower()) for e in entities]
            content.append(f"- **Total de Tabelas:** {len(tables)}")
            
            total_relationships = sum(len(e.get('relationships', [])) for e in entities)
            content.append(f"- **Total de Relacionamentos:** {total_relationships}")
            
        else:
            content.append("\n## ⚠️ Entidades")
            content.append("Nenhuma entidade JPA identificada no projeto.")
            content.append("Verifique se o projeto utiliza persistência de dados.")
        
        return "\n".join(content)
    
    def _create_configuration_fallback(self, project_name: str, java_analysis: Dict[str, Any]) -> str:
        """Cria documentação fallback de configurações"""
        content = [
            f"# ⚙️ Configurações Spring - {project_name}",
            f"\n**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\n## 🎯 Visão Geral",
            f"Configurações Spring Boot identificadas no projeto {project_name}.",
        ]
        
        dependencies = java_analysis.get('dependencies', {})
        
        # Spring Boot Starters
        starters = dependencies.get('spring_boot_starters', [])
        if starters:
            content.append(f"\n## 🚀 Spring Boot Starters ({len(starters)})")
            for starter in starters:
                content.append(f"- `{starter}`")
        
        # Dependências Maven
        maven_deps = dependencies.get('maven_dependencies', [])
        if maven_deps:
            content.append(f"\n## 📦 Dependências Maven ({len(maven_deps)})")
            for dep in maven_deps[:10]:  # Primeiras 10
                group_id = dep.get('groupId', 'unknown')
                artifact_id = dep.get('artifactId', 'unknown')
                version = dep.get('version', 'managed')
                content.append(f"- `{group_id}:{artifact_id}` (v{version})")
            
            if len(maven_deps) > 10:
                content.append(f"- ... e mais {len(maven_deps) - 10} dependências")
        
        # Dependências Gradle
        gradle_deps = dependencies.get('gradle_dependencies', [])
        if gradle_deps:
            content.append(f"\n## 🐘 Dependências Gradle ({len(gradle_deps)})")
            for dep in gradle_deps[:10]:  # Primeiras 10
                content.append(f"- `{dep}`")
            
            if len(gradle_deps) > 10:
                content.append(f"- ... e mais {len(gradle_deps) - 10} dependências")
        
        # Padrões arquiteturais
        patterns = java_analysis.get('architecture_analysis', {})
        if patterns:
            content.append("\n## 🏗️ Padrões Arquiteturais Identificados")
            
            pattern_names = {
                'mvc_pattern': 'Padrão MVC',
                'repository_pattern': 'Padrão Repository',
                'service_layer': 'Camada de Serviços',
                'dependency_injection': 'Injeção de Dependência',
                'rest_api': 'API REST',
                'jpa_orm': 'ORM JPA/Hibernate'
            }
            
            for pattern_key, pattern_name in pattern_names.items():
                if patterns.get(pattern_key):
                    content.append(f"- ✅ {pattern_name}")
            
            config_classes = patterns.get('configuration_classes', [])
            if config_classes:
                content.append(f"\n**Classes de Configuração:**")
                for config_class in config_classes:
                    content.append(f"- {config_class}")
        
        return "\n".join(content)
    
    def _create_diagram_fallback(self, project_name: str, java_analysis: Dict[str, Any]) -> str:
        """Cria diagrama fallback do sistema"""
        content = [
            f"# 📊 Diagrama do Sistema - {project_name}",
            f"\n**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\n## 🎯 Arquitetura do Sistema",
            f"Diagrama arquitetural do projeto {project_name} em Spring Boot.",
        ]
        
        # Gera diagrama Mermaid básico
        components = java_analysis['spring_components']
        controllers = components['controllers']
        services = components['services']
        repositories = components['repositories']
        entities = components['entities']
        
        content.append("\n```mermaid")
        content.append("graph TD")
        content.append("    subgraph \"🎮 Presentation Layer\"")
        
        if controllers:
            for i, controller in enumerate(controllers):
                controller_id = f"C{i+1}"
                controller_name = controller['name']
                content.append(f"        {controller_id}[{controller_name}]")
        else:
            content.append("        C1[Nenhum Controller]")
        
        content.append("    end")
        content.append("")
        content.append("    subgraph \"⚙️ Business Layer\"")
        
        if services:
            for i, service in enumerate(services):
                service_id = f"S{i+1}"
                service_name = service['name']
                content.append(f"        {service_id}[{service_name}]")
        else:
            content.append("        S1[Nenhum Service]")
        
        content.append("    end")
        content.append("")
        content.append("    subgraph \"🗄️ Data Layer\"")
        
        if repositories:
            for i, repo in enumerate(repositories):
                repo_id = f"R{i+1}"
                repo_name = repo['name']
                content.append(f"        {repo_id}[{repo_name}]")
        else:
            content.append("        R1[Nenhum Repository]")
        
        if entities:
            for i, entity in enumerate(entities):
                entity_id = f"E{i+1}"
                entity_name = entity['name']
                content.append(f"        {entity_id}[{entity_name}]")
        
        content.append("    end")
        content.append("")
        
        if entities:
            content.append("    subgraph \"💾 Database\"")
            content.append("        DB[(Database)]")
            content.append("    end")
            content.append("")
        
        # Conexões
        if controllers and services:
            for i in range(min(len(controllers), len(services))):
                content.append(f"    C{i+1} --> S{i+1}")
        
        if services and repositories:
            for i in range(min(len(services), len(repositories))):
                content.append(f"    S{i+1} --> R{i+1}")
        
        if repositories and entities:
            for i in range(min(len(repositories), len(entities))):
                content.append(f"    R{i+1} --> E{i+1}")
        
        if entities:
            for i in range(len(entities)):
                content.append(f"    E{i+1} --> DB")
        
        content.append("```")
        
        # Legenda
        content.append("\n## 📋 Legenda")
        content.append("- **Controllers:** Camada de apresentação (APIs REST)")
        content.append("- **Services:** Camada de negócio (lógica da aplicação)")
        content.append("- **Repositories:** Camada de acesso a dados")
        content.append("- **Entities:** Modelos de dados (JPA)")
        content.append("- **Database:** Banco de dados relacional")
        
        return "\n".join(content)
    
    def _create_deployment_fallback(self, project_name: str, java_analysis: Dict[str, Any]) -> str:
        """Cria guia fallback de deployment"""
        content = [
            f"# 🚀 Guia de Deploy - {project_name}",
            f"\n**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\n## 🎯 Visão Geral",
            f"Guia de deployment para o projeto {project_name} desenvolvido em Java Spring Boot.",
        ]
        
        # Pré-requisitos
        content.extend([
            "\n## 📋 Pré-requisitos",
            "- **Java:** 11 ou superior (recomendado Java 17 LTS)",
            "- **Maven:** 3.6+ ou Gradle 7.0+",
            "- **Banco de Dados:** Conforme configurado no projeto"
        ])
        
        # Verifica se há dependências específicas
        dependencies = java_analysis.get('dependencies', {})
        starters = dependencies.get('spring_boot_starters', [])
        
        if any('jpa' in starter.lower() for starter in starters):
            content.append("- **Banco de Dados:** PostgreSQL, MySQL ou H2")
        
        if any('security' in starter.lower() for starter in starters):
            content.append("- **Configuração de Segurança:** Certificados SSL (produção)")
        
        # Build do projeto
        content.append("\n## 🔨 Build do Projeto")
        
        # Verifica se é Maven ou Gradle baseado nas dependências
        if dependencies.get('maven_dependencies'):
            content.extend([
                "### Maven",
                "```bash",
                "# Limpar e compilar",
                "mvn clean compile",
                "",
                "# Executar testes",
                "mvn test",
                "",
                "# Gerar JAR executável",
                "mvn clean package",
                "",
                "# Pular testes (se necessário)",
                "mvn clean package -DskipTests",
                "```"
            ])
        elif dependencies.get('gradle_dependencies'):
            content.extend([
                "### Gradle",
                "```bash",
                "# Limpar e compilar",
                "./gradlew clean build",
                "",
                "# Executar testes",
                "./gradlew test",
                "",
                "# Gerar JAR executável",
                "./gradlew bootJar",
                "```"
            ])
        
        # Configuração de ambiente
        content.extend([
            "\n## ⚙️ Configuração de Ambiente",
            "### Variáveis de Ambiente",
            "```bash",
            "# Configuração de banco (exemplo)",
            "export SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/database",
            "export SPRING_DATASOURCE_USERNAME=user",
            "export SPRING_DATASOURCE_PASSWORD=password",
            "",
            "# Configuração de perfil",
            "export SPRING_PROFILES_ACTIVE=production",
            "```"
        ])
        
        # Deployment
        content.extend([
            "\n## 🚀 Deployment",
            "### Execução Local",
            "```bash",
            "# Via Maven",
            "mvn spring-boot:run",
            "",
            "# Via JAR",
            f"java -jar target/{project_name}-1.0.0.jar",
            "```",
            "",
            "### Docker (Recomendado)",
            "```dockerfile",
            "# Dockerfile sugerido",
            "FROM openjdk:17-jre-slim",
            "COPY target/*.jar app.jar",
            "EXPOSE 8080",
            "ENTRYPOINT [\"java\", \"-jar\", \"/app.jar\"]",
            "```",
            "",
            "```bash",
            "# Build da imagem",
            f"docker build -t {project_name} .",
            "",
            "# Execução",
            f"docker run -p 8080:8080 {project_name}",
            "```"
        ])
        
        # Health check
        if any('actuator' in starter.lower() for starter in starters):
            content.extend([
                "\n## 🏥 Health Check",
                "```bash",
                "# Verificar saúde da aplicação",
                "curl http://localhost:8080/actuator/health",
                "",
                "# Métricas (se habilitado)",
                "curl http://localhost:8080/actuator/metrics",
                "```"
            ])
        
        return "\n".join(content)
    
    def _create_comparison_fallback(self, project_name: str, comparison_data: Dict[str, Any]) -> str:
        """Cria análise comparativa fallback"""
        content = [
            f"# 🔄 Análise Comparativa - {project_name}",
            f"\n**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\n## 🎯 Resumo da Migração",
        ]
        
        # Status da migração
        coverage = comparison_data.get('migration_coverage', {})
        if coverage:
            overall_coverage = coverage.get('overall_coverage_percent', 0)
            status = coverage.get('coverage_status', 'Desconhecido')
            
            content.append(f"- **Cobertura Geral:** {overall_coverage:.1f}%")
            content.append(f"- **Status:** {status}")
            
            if coverage.get('function_coverage_percent'):
                content.append(f"- **Cobertura de Funcionalidades:** {coverage['function_coverage_percent']:.1f}%")
            
            if coverage.get('class_coverage_percent'):
                content.append(f"- **Cobertura de Classes:** {coverage['class_coverage_percent']:.1f}%")
        
        # Mapeamento de funcionalidades
        mapping = comparison_data.get('functionality_mapping', {})
        if mapping.get('mapping_summary'):
            summary = mapping['mapping_summary']
            content.extend([
                "\n## 🗺️ Mapeamento de Funcionalidades",
                f"- **Funções Delphi:** {summary['total_delphi_functions']}",
                f"- **Métodos Java:** {summary['total_java_methods']}",
                f"- **Mapeadas:** {summary['mapped_functions']}",
                f"- **Não Mapeadas:** {summary['unmapped_functions']}"
            ])
        
        # Comparação arquitetural
        arch_comparison = comparison_data.get('architecture_comparison', {})
        if arch_comparison:
            content.append("\n## 🏗️ Evolução Arquitetural")
            
            delphi_arch = arch_comparison.get('delphi_architecture', {})
            java_arch = arch_comparison.get('java_architecture', {})
            
            if delphi_arch and java_arch:
                content.extend([
                    "### Delphi (Original)",
                    f"- **Padrão:** {delphi_arch.get('pattern', 'N/A')}",
                    f"- **Interface:** {delphi_arch.get('ui_technology', 'N/A')}",
                    f"- **Dados:** {delphi_arch.get('data_access', 'N/A')}",
                    "",
                    "### Java Spring Boot (Modernizado)",
                    f"- **Padrão:** {java_arch.get('pattern', 'N/A')}",
                    f"- **Interface:** {java_arch.get('ui_technology', 'N/A')}",
                    f"- **Dados:** {java_arch.get('data_access', 'N/A')}"
                ])
            
            improvements = arch_comparison.get('architectural_improvements', [])
            if improvements:
                content.append("\n### 🎯 Melhorias Implementadas")
                for improvement in improvements:
                    content.append(f"- {improvement}")
        
        # Validação da migração
        validation = comparison_data.get('validation_results', {})
        if validation:
            overall_status = validation.get('overall_status', 'UNKNOWN')
            content.append(f"\n## ✅ Resultado da Validação: {overall_status}")
            
            validations = validation.get('validations', [])
            if validations:
                for val in validations:
                    status_icon = {'PASS': '✅', 'WARNING': '⚠️', 'FAIL': '❌'}.get(val['status'], '❓')
                    content.append(f"- {status_icon} **{val['aspect']}:** {val['message']}")
            
            summary = validation.get('summary', {})
            if summary:
                content.extend([
                    f"\n**Resumo:** {summary['passed']} passou, {summary['warnings']} avisos, {summary['failed']} falhas"
                ])
        
        # Recomendações
        recommendations = comparison_data.get('recommendations', [])
        if recommendations:
            content.append("\n## 💡 Recomendações")
            
            for rec in recommendations:
                priority = rec.get('priority', 'MEDIUM')
                category = rec.get('category', 'Geral')
                recommendation = rec.get('recommendation', 'N/A')
                rationale = rec.get('rationale', '')
                
                priority_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢', 'CRITICAL': '🚨'}.get(priority, '⚪')
                
                content.append(f"### {priority_icon} {category} ({priority})")
                content.append(f"**Recomendação:** {recommendation}")
                if rationale:
                    content.append(f"**Justificativa:** {rationale}")
                content.append("")
        
        return "\n".join(content)
    
    def _create_generic_java_fallback(self, project_name: str, doc_type: str, 
                                    java_analysis: Dict[str, Any]) -> str:
        """Cria documentação fallback genérica"""
        return f"""# 📄 {doc_type.replace('_', ' ').title()} - {project_name}

**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 🎯 Resumo
Documento {doc_type} para o projeto Java Spring Boot {project_name}.

## 📊 Estatísticas do Projeto
- **Total de Arquivos:** {java_analysis['metadata']['total_files']}
- **Controllers:** {java_analysis['spring_components']['component_summary']['total_controllers']}
- **Services:** {java_analysis['spring_components']['component_summary']['total_services']}
- **Repositories:** {java_analysis['spring_components']['component_summary']['total_repositories']}
- **Entities:** {java_analysis['spring_components']['component_summary']['total_entities']}

## ⚠️ Aviso
Esta documentação foi gerada automaticamente como fallback.
Para informações mais detalhadas, execute o sistema com LLM configurado.
"""
    
    def _create_error_fallback(self, doc_type: str, java_analysis: Dict[str, Any]) -> str:
        """Cria conteúdo de erro para documentação"""
        project_name = java_analysis['metadata']['project_name']
        doc_title = self.java_document_types[doc_type]['title']
        
        return f"""# ❌ Erro - {doc_title}

**Projeto:** {project_name}  
**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 🚨 Erro na Geração
Ocorreu um erro durante a geração deste documento.

## 📊 Informações Básicas
- **Tipo de Documento:** {doc_title}
- **Total de Arquivos:** {java_analysis['metadata']['total_files']}
- **Componentes Spring:** {sum(java_analysis['spring_components']['component_summary'].values())}

## 🔧 Solução
1. Verifique se o LLM está configurado corretamente
2. Confirme se os dados de análise estão completos
3. Tente gerar novamente o documento
"""
    
    def _validate_java_content(self, content: str, project_name: str) -> bool:
        """Valida se o conteúdo gerado é específico ao projeto Java"""
        if not content or len(content.strip()) < 50:
            return False
        
        # Verifica se contém o nome do projeto
        if project_name.lower() not in content.lower():
            logger.warning(f"⚠️ Conteúdo não menciona o projeto {project_name}")
            return False
        
        # Verifica se contém termos relacionados a Java/Spring
        java_terms = ['java', 'spring', 'controller', 'service', 'repository', 'entity', 'api', 'rest']
        if not any(term in content.lower() for term in java_terms):
            logger.warning("⚠️ Conteúdo não contém termos específicos de Java/Spring")
            return False
        
        # Verifica se não é muito genérico
        generic_phrases = [
            'este é um projeto genérico',
            'projeto de exemplo',
            'template padrão',
            'documentação genérica'
        ]
        
        if any(phrase in content.lower() for phrase in generic_phrases):
            logger.warning("⚠️ Conteúdo parece genérico")
            return False
        
        return True
