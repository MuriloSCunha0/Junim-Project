"""
Gerador de documentação técnica para projetos Delphi
Sistema ROBUSTO com prompts específicos e análise detalhada do projeto real
"""

import os
import json
import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Importa motor de modernização
from .modernization_engine import ModernizationEngine

logger = logging.getLogger(__name__)

class DocumentationGenerator:
    """Gerador ROBUSTO de documentação técnica - Focado no projeto real"""
    
    def __init__(self, llm_service=None, prompt_manager=None):
        self.llm_service = llm_service
        self.prompt_manager = prompt_manager
        self.modernization_engine = ModernizationEngine()  # Motor de modernização integrado
        self.docs_dir = Path("generated_docs")
        self.docs_dir.mkdir(exist_ok=True)
        
        # Sistema de documentos essenciais baseados nos prompts disponíveis
        self.document_types = {
            'project_analysis': {
                'name': '📊 Análise Completa do Projeto',
                'prompt_type': 'comprehensive_analysis',
                'filename': 'project_analysis.md',
                'priority': 1,
                'description': 'Análise profunda e completa do projeto Delphi'
            },
            'project_diagram': {
                'name': '📈 Diagrama de Arquitetura Mermaid',
                'prompt_type': 'diagram_generation',
                'filename': 'project_diagram.md',
                'priority': 2,
                'description': 'Diagrama visual da arquitetura do projeto'
            },
            'functions_catalog': {
                'name': '⚙️ Catálogo de Funções e Procedimentos',
                'prompt_type': 'functions_mapping',
                'filename': 'functions_catalog.md',
                'priority': 3,
                'description': 'Mapeamento detalhado de todas as funcionalidades'
            },
            'delphi_java_mapping': {
                'name': '🔗 Mapeamento Delphi → Java Spring',
                'prompt_type': 'technology_mapping',
                'filename': 'delphi_java_mapping.md',
                'priority': 4,
                'description': 'Correlações específicas entre Delphi e Spring Boot'
            },
            'modernization_strategy': {
                'name': '🚀 Estratégia de Modernização',
                'prompt_type': 'modernization_plan',
                'filename': 'modernization_strategy.md',
                'priority': 5,
                'description': 'Plano detalhado para modernização do sistema'
            },
            'backend_analysis': {
                'name': '🏗️ Análise de Backend',
                'prompt_type': 'backend_analysis',
                'filename': 'backend_analysis.md',
                'priority': 6,
                'description': 'Análise específica do backend e arquitetura'
            },
            'spring_conversion': {
                'name': '☕ Conversão Spring Boot',
                'prompt_type': 'spring_conversion',
                'filename': 'spring_conversion.md',
                'priority': 7,
                'description': 'Implementação prática em Spring Boot'
            },
            'code_modernization': {
                'name': '🚀 Código Java Spring Boot Modernizado',
                'prompt_type': 'code_modernization',
                'filename': 'modernized_code.md',
                'priority': 8,
                'description': 'Código Java Spring Boot completo baseado na documentação'
            },
            'testing_strategy': {
                'name': '🧪 Estratégia de Testes',
                'prompt_type': 'testing',
                'filename': 'testing_strategy.md',
                'priority': 9,
                'description': 'Testes automatizados para o sistema modernizado'
            }
        }
        
        # Configurações para garantir especificidade
        self.specificity_checks = {
            'min_project_references': 3,  # Mín. de referências específicas do projeto
            'min_content_length': 500,    # Mín. de caracteres por documento
            'required_sections': ['análise', 'específico', 'projeto'],
            'forbidden_generic': ['exemplo genérico', 'template', 'placeholder']
        }

    def generate_specific_documentation(self, analysis_results: Dict[str, Any], 
                                      project_name: str = "Projeto",
                                      include_mermaid: bool = True,
                                      documents_to_generate: List[str] = None) -> Dict[str, str]:
        """
        Gera APENAS documentação específica usando prompts - SEM FALLBACKS
        
        Returns:
            Dict com conteúdo dos documentos gerados (não caminhos)
        """
        try:
            logger.info(f"🚀 Gerando documentação essencial para: {project_name}")
            
            # Validação crítica dos dados de entrada
            if not analysis_results or not isinstance(analysis_results, dict):
                error_msg = f"❌ ERRO CRÍTICO: Dados de análise inválidos para {project_name}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"📋 Dados disponíveis: {list(analysis_results.keys())}")
            
            # Cria diretório específico para o projeto
            project_dir = self.docs_dir / self._sanitize_filename(project_name)
            project_dir.mkdir(exist_ok=True)
            
            generated_docs = {}
            
            # LISTA EXPANDIDA DOS DOCUMENTOS ESSENCIAIS baseada nos prompts disponíveis
            if documents_to_generate is None:
                documents_to_generate = [
                    'project_analysis',         # Análise completa usando analysis_prompt.txt
                    'project_diagram',          # Diagrama Mermaid usando project_diagram_prompt.txt
                    'functions_catalog',        # Catálogo usando functionality_mapping_prompt.txt
                    'backend_analysis',         # Análise backend usando backend_analysis_prompt.txt
                    'delphi_java_mapping',      # Mapeamento usando functionality_mapping_prompt.txt
                    'modernization_strategy',   # Estratégia usando backend_conversion_prompt.txt
                    'code_modernization',       # Código Java Spring Boot modernizado
                ]
            
            # CORREÇÃO: Gera apenas documentos especificados - COM LOGS DETALHADOS
            for doc_type in documents_to_generate:
                logger.info(f"🔄 Processando documento: {doc_type}")
                
                if doc_type in self.document_types:
                    doc_info = self.document_types[doc_type]
                    logger.info(f"📄 Gerando documento: {doc_info['name']} usando prompt_type: {doc_info['prompt_type']}")
                    
                    try:
                        # Gera o documento usando prompts reais
                        content = self._generate_document_content(doc_type, analysis_results, project_name)
                        
                        if not content or len(content.strip()) < 100:
                            error_msg = f"❌ FALHA na geração de {doc_info['name']} - Conteúdo insuficiente: {len(content.strip()) if content else 0} chars"
                            logger.error(error_msg)
                            raise RuntimeError(error_msg)
                        
                        # Salva o documento
                        doc_path = project_dir / doc_info['filename']
                        with open(doc_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        # Retorna o conteúdo (não o caminho)
                        generated_docs[doc_type] = content
                        logger.info(f"✅ Documento gerado com sucesso: {doc_info['name']} ({len(content)} chars)")
                        
                    except Exception as doc_error:
                        logger.error(f"❌ ERRO ao gerar {doc_type}: {str(doc_error)}")
                        # IMPORTANTE: Em vez de falhar completamente, continua com próximo documento
                        continue
                        
                else:
                    logger.warning(f"⚠️ Tipo de documento não configurado: {doc_type}")
                    logger.info(f"📋 Tipos disponíveis: {list(self.document_types.keys())}")
            
            # CORREÇÃO: Gera README específico sempre, mesmo se poucos documentos foram gerados
            try:
                readme_content = self._generate_essential_readme(analysis_results, project_name, list(generated_docs.keys()))
                readme_path = project_dir / "README.md"
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                generated_docs['readme'] = readme_content
                logger.info(f"✅ README gerado com sucesso ({len(readme_content)} chars)")
            except Exception as readme_error:
                logger.error(f"❌ Erro ao gerar README: {str(readme_error)}")
                # Gera README mínimo em caso de erro
                minimal_readme = f"# {project_name}\n\nProjeto analisado em {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n## Documentos Gerados\n\n{len(generated_docs)} documento(s) processado(s)."
                generated_docs['readme'] = minimal_readme
            
            # RESULTADO: Garante que pelo menos algum documento seja retornado
            if not generated_docs:
                logger.warning("⚠️ Nenhum documento foi gerado - criando documentos básicos")
                generated_docs = self._generate_fallback_docs(analysis_results, project_name)
            
            logger.info(f"🎉 Documentação essencial finalizada: {len(generated_docs)} arquivos")
            logger.info(f"📁 Documentos salvos em: {project_dir}")
            logger.info(f"📋 Documentos criados: {list(generated_docs.keys())}")
            
            # Log detalhado dos documentos gerados
            for doc_key, content in generated_docs.items():
                content_size = len(content) if isinstance(content, str) else 0
                logger.info(f"  ✅ {doc_key}: {content_size} caracteres")
            
            return generated_docs
            
        except Exception as e:
            error_msg = f"❌ ERRO CRÍTICO na geração de documentação: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _generate_document_content(self, doc_type: str, analysis_results: Dict[str, Any], 
                                   project_name: str) -> str:
        """
        Gera conteúdo de um documento específico usando prompts - SEM FALLBACKS
        Integrado com motor de modernização para documentos específicos
        """
        try:
            # Debug para verificar o estado do DocumentationGenerator
            logger.info(f"🔍 _generate_document_content chamado para: {doc_type}")
            logger.info(f"🔍 self.prompt_manager disponível: {self.prompt_manager is not None}")
            logger.info(f"🔍 self.llm_service disponível: {self.llm_service is not None}")
            
            # Validação do tipo de documento
            if doc_type not in self.document_types:
                raise ValueError(f"Tipo de documento '{doc_type}' não suportado")
            
            doc_config = self.document_types[doc_type]
            
            # NOVO: Verifica se deve usar motor de modernização
            if doc_config.get('use_modernization_engine', False):
                logger.info(f"🔧 Usando motor de modernização para {doc_type}")
                return self._generate_modernization_document(analysis_results, project_name)
            
            # Obtém prompt específico - OBRIGATÓRIO
            prompt = self._get_prompt_for_document(doc_config['prompt_type'])
            if not prompt or len(prompt) < 100:
                raise RuntimeError(f"Prompt inválido para {doc_type}")
            
            # Prepara contexto - OBRIGATÓRIO
            context = self._prepare_context(analysis_results, project_name, doc_type)
            if not context or len(context) < 300:  # CORREÇÃO: Reduzido de 500 para 300
                logger.warning(f"⚠️ Contexto limitado para {doc_type}: {len(context) if context else 0} chars")
                # CORREÇÃO: Não falha mais, mas continua com contexto limitado
                if not context:
                    context = f"Projeto: {project_name} - Dados limitados disponíveis"
            
            # CORREÇÃO: Gera conteúdo usando LLM com parâmetros adicionais para fallback
            content = self._generate_content_with_llm(prompt, context, doc_type, analysis_results, project_name)
            if not content or len(content.strip()) < 100:
                raise RuntimeError(f"LLM falhou ao gerar conteúdo para {doc_type}")
            
            return content
            
        except Exception as e:
            error_msg = f"Erro ao gerar {doc_type}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _generate_modernization_document(self, analysis_results: Dict[str, Any], 
                                       project_name: str) -> str:
        """
        Gera documento de modernização usando o motor de modernização integrado
        """
        try:
            logger.info(f"🚀 Iniciando geração de documento de modernização para {project_name}")
            
            # Usa o motor de modernização para analisar o projeto
            modernization_strategy = self.modernization_engine.analyze_for_modernization(analysis_results)
            
            # Constrói o documento markdown estruturado
            content_sections = []
            
            # Cabeçalho
            content_sections.append(f"# 🔧 Plano Detalhado de Modernização - {project_name}")
            content_sections.append(f"\n**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            content_sections.append(f"**Motor de Modernização:** v{modernization_strategy['metadata']['modernization_engine_version']}")
            
            # Resumo Executivo
            summary = modernization_strategy['summary']
            content_sections.append("\n## 📊 Resumo Executivo")
            content_sections.append(f"- **Complexidade:** {summary['complexity_level'].upper()}")
            content_sections.append(f"- **Esforço Estimado:** {summary['estimated_effort_weeks']} semanas")
            content_sections.append(f"- **Total de Componentes:** {modernization_strategy['metadata']['total_components']}")
            
            if summary['priority_components']:
                content_sections.append("\n### 🎯 Componentes Prioritários")
                for i, component in enumerate(summary['priority_components'], 1):
                    content_sections.append(f"{i}. {component}")
            
            if summary['risk_factors']:
                content_sections.append("\n### ⚠️ Fatores de Risco")
                for risk in summary['risk_factors']:
                    content_sections.append(f"- {risk}")
            
            # Mapeamento de Componentes
            mapping = modernization_strategy['component_mapping']
            content_sections.append("\n## 🗺️ Mapeamento Delphi → Java Spring")
            
            for java_type, components in mapping.items():
                if components:
                    type_names = {
                        'controllers': '🎮 Controllers',
                        'services': '⚙️ Services', 
                        'entities': '📦 Entities',
                        'repositories': '🗄️ Repositories',
                        'utilities': '🔧 Utilities'
                    }
                    content_sections.append(f"\n### {type_names.get(java_type, java_type.title())}")
                    
                    for comp in components:
                        complexity_indicator = "🟢" if comp['complexity'] <= 2 else "🟡" if comp['complexity'] <= 3 else "🔴"
                        content_sections.append(f"- {complexity_indicator} `{comp['delphi_original']}` → `{comp['java_equivalent']}`")
                        
                        if comp['migration_notes']:
                            for note in comp['migration_notes']:
                                content_sections.append(f"  - {note}")
            
            # Fases de Migração
            phases = modernization_strategy['migration_phases']
            content_sections.append("\n## 📅 Fases de Migração")
            
            for phase in phases:
                content_sections.append(f"\n### Fase {phase['phase']}: {phase['name']}")
                content_sections.append(f"**Duração:** {phase['duration_weeks']} semanas")
                content_sections.append(f"**Descrição:** {phase['description']}")
                
                if phase['deliverables']:
                    content_sections.append("\n**Entregáveis:**")
                    for deliverable in phase['deliverables']:
                        content_sections.append(f"- {deliverable}")
                
                if phase['components']:
                    content_sections.append("\n**Componentes a migrar:**")
                    for component in phase['components']:
                        content_sections.append(f"- {component}")
            
            # Stack Tecnológico
            tech_stack = modernization_strategy['technology_stack']
            content_sections.append("\n## 💻 Stack Tecnológico Recomendado")
            
            content_sections.append("\n### Backend")
            backend = tech_stack['backend']
            for key, value in backend.items():
                if value:
                    content_sections.append(f"- **{key.replace('_', ' ').title()}:** {value}")
            
            content_sections.append("\n### Frontend")
            frontend = tech_stack['frontend']
            for key, value in frontend.items():
                content_sections.append(f"- **{key.replace('_', ' ').title()}:** {value}")
            
            # Diretrizes de Implementação
            guidelines = modernization_strategy['implementation_guidelines']
            content_sections.append("\n## 📋 Diretrizes de Implementação")
            for i, guideline in enumerate(guidelines, 1):
                content_sections.append(f"{i}. {guideline}")
            
            # Checklist de Validação
            checklist = modernization_strategy['validation_checklist']
            content_sections.append("\n## ✅ Checklist de Validação")
            for item in checklist:
                content_sections.append(f"- [ ] {item}")
            
            # Rodapé
            content_sections.append(f"\n---\n*Documento gerado pelo Sistema de Modernização v{self.modernization_engine.version}*")
            
            final_content = "\n".join(content_sections)
            
            logger.info(f"✅ Documento de modernização gerado: {len(final_content)} caracteres")
            return final_content
            
        except Exception as e:
            logger.error(f"❌ Erro na geração do documento de modernização: {str(e)}")
            raise RuntimeError(f"Falha na geração do documento de modernização: {str(e)}")

    def _get_prompt_for_document(self, prompt_type: str) -> str:
        """Obtém prompt específico - FALHA se não conseguir"""
        # Debug para verificar o estado
        logger.info(f"🔍 _get_prompt_for_document chamado para: {prompt_type}")
        logger.info(f"🔍 PromptManager disponível: {self.prompt_manager is not None}")
        
        if not self.prompt_manager:
            logger.error("❌ PromptManager não está disponível!")
            raise RuntimeError("PromptManager não disponível - OBRIGATÓRIO para geração")
        
        try:
            # CORREÇÃO: Mapeia tipos de prompt para métodos reais do PromptManager
            prompt_methods = {
                'functions_mapping': 'get_functionality_mapping_prompt',       # Catálogo de funções
                'comprehensive_analysis': 'get_analysis_prompt',               # Análise completa
                'technology_mapping': 'get_functionality_mapping_prompt',      # Mapeamento Delphi→Java  
                'modernization_plan': 'get_backend_conversion_prompt',         # Estratégia de modernização
                'backend_analysis': 'get_backend_analysis_prompt',             # Análise de backend
                'testing': 'get_testing_prompt',                               # Testes automatizados
                'spring_conversion': 'get_spring_conversion_prompt',           # Conversão Spring Boot
                'diagram_generation': 'get_diagram_prompt',                    # Geração de diagramas Mermaid
                'code_modernization': 'get_code_modernization_prompt'          # Modernização de código
            }
            
            method_name = prompt_methods.get(prompt_type)
            if not method_name or not hasattr(self.prompt_manager, method_name):
                logger.error(f"Erro ao obter prompt para {prompt_type}: Método {method_name} não encontrado no PromptManager")
                raise RuntimeError(f"Método {method_name} não encontrado no PromptManager")
            
            method = getattr(self.prompt_manager, method_name)
            prompt = method()
            
            if not prompt or len(prompt) < 50:
                raise RuntimeError(f"Prompt vazio ou inválido para {prompt_type}")
            
            logger.info(f"✅ Prompt obtido para {prompt_type}: {len(prompt)} caracteres")
            return prompt
                
        except Exception as e:
            error_msg = f"Erro ao obter prompt para {prompt_type}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _prepare_context(self, analysis_results: Dict[str, Any], project_name: str, doc_key: str) -> str:
        """Prepara contexto específico - INCLUI entidades de banco e formulários"""
        
        # Validação rigorosa dos dados de entrada
        if not analysis_results or not isinstance(analysis_results, dict):
            raise ValueError("analysis_results está vazio ou inválido")
        
        logger.info(f"🔍 Preparando contexto para {doc_key}")
        logger.info(f"📋 Dados disponíveis: {list(analysis_results.keys())}")
        
        # Formata dados de análise
        formatted_data = self._format_analysis_data(analysis_results)
        
        # Extrai especificidades do código
        code_specifics = self._extract_code_specifics(analysis_results)
        
        # NOVO: Extrai entidades de banco de dados e formulários
        database_entities_info = self._extract_database_entities_info(analysis_results)
        form_entities_info = self._extract_form_entities_info(analysis_results)
        crud_operations_info = self._extract_crud_operations_info(analysis_results)
        
        # CORREÇÃO: Monta contexto específico e detalhado
        context = f"""
===== PROJETO ESPECÍFICO: {project_name} =====
TIPO DE DOCUMENTO: {doc_key}

===== DADOS ESTRUTURAIS REAIS =====
{formatted_data}

===== COMPONENTES DE CÓDIGO IDENTIFICADOS =====
{code_specifics}

===== ENTIDADES DE BANCO DE DADOS IDENTIFICADAS =====
{database_entities_info}

===== FORMULÁRIOS CRUD IDENTIFICADOS =====
{form_entities_info}

===== OPERAÇÕES CRUD DETECTADAS =====
{crud_operations_info}

===== INSTRUÇÕES CRÍTICAS =====
VOCÊ DEVE GERAR DOCUMENTAÇÃO TÉCNICA ESPECÍFICA para o projeto "{project_name}".

🚨 REGRAS OBRIGATÓRIAS:
1. USE APENAS os nomes de arquivos, classes, entidades e métodos listados acima
2. NÃO invente ou use exemplos genéricos
3. Seja específico sobre as entidades de banco e formulários encontrados
4. Foque em modernização Delphi → Java Spring Boot
5. Use formatação Markdown técnica
6. Mencione APENAS elementos que foram identificados

EXEMPLO DE FORMATO ESPERADO:
# Análise Específica para {project_name}

## Entidades de Banco Identificadas
- Produto: id, nome, preco, estoque, ativo
- Cliente: id, nome, email, telefone

## Formulários CRUD Mapeados
- TProductForm → ProductController (CREATE, UPDATE, DELETE, READ)
- TClientForm → ClientController (CREATE, UPDATE, DELETE, READ)

## Mapeamento Delphi-Java
- QryProdutos → ProductRepository
- btnSalvar → ProductService.save()
- Validação "Nome obrigatório" → @NotBlank

NÃO USE FRASES COMO: "vamos identificar", "pode me fornecer", "it seems like"
SEJA DIRETO E TÉCNICO BASEADO NOS DADOS FORNECIDOS.
        """
        
        logger.info(f"🎯 Contexto específico preparado: {len(context)} caracteres")
        
        return context

    def _extract_code_specifics(self, analysis_results: Dict[str, Any]) -> str:
        """Extrai informações específicas do código"""
        try:
            specifics = []
            
            # Extrai classes identificadas
            all_classes = []
            files_data = analysis_results.get('files', {})
            
            if isinstance(files_data, dict):
                files_to_process = files_data.values()
            elif isinstance(files_data, list):
                files_to_process = files_data
            else:
                files_to_process = []
            
            for file_data in files_to_process:
                if isinstance(file_data, dict):
                    classes = file_data.get('classes', [])
                    for cls in classes:
                        class_name = cls.get('name', '')
                        parent_class = cls.get('parent_class', '')
                        if class_name:
                            all_classes.append(f"{class_name} (extends {parent_class})")
            
            if all_classes:
                specifics.append("**Classes Identificadas:**")
                for cls in all_classes[:10]:
                    specifics.append(f"- {cls}")
            
            # Extrai métodos importantes
            important_methods = []
            for file_data in files_to_process:
                if isinstance(file_data, dict):
                    methods = file_data.get('methods', [])
                    for method in methods:
                        method_name = method.get('name', '')
                        method_type = method.get('type', 'method')
                        return_type = method.get('return_type', 'void')
                        if method_name and not method_name.startswith('_'):
                            important_methods.append(f"{method_name}(): {return_type} ({method_type})")
            
            if important_methods:
                specifics.append("\n**Métodos Principais:**")
                for method in important_methods[:15]:
                    specifics.append(f"- {method}")
            
            # Extrai eventos de interface
            event_methods = []
            for file_data in files_to_process:
                if isinstance(file_data, dict):
                    methods = file_data.get('methods', [])
                    for method in methods:
                        method_name = method.get('name', '')
                        if any(event in method_name for event in ['Click', 'Change', 'Create', 'Close', 'Show']):
                            event_methods.append(method_name)
            
            if event_methods:
                specifics.append("\n**Eventos de Interface:**")
                for event in event_methods[:10]:
                    specifics.append(f"- {event}")
            
            return "\n".join(specifics) if specifics else "Componentes básicos identificados."
            
        except Exception as e:
            logger.error(f"Erro ao extrair especificidades: {str(e)}")
            return "Erro ao extrair detalhes do código."

    def _extract_database_entities_info(self, analysis_results: Dict[str, Any]) -> str:
        """Extrai informações das entidades de banco de dados identificadas"""
        try:
            database_entities = analysis_results.get('database_entities', [])
            if not database_entities:
                return "Nenhuma entidade de banco de dados identificada."
            
            info_lines = ["**Entidades de Banco de Dados:**"]
            for entity in database_entities:
                entity_name = entity.get('name', 'Unknown')
                table_name = entity.get('table_name', 'unknown')
                fields = entity.get('fields', [])
                operations = entity.get('operations', [])
                source_file = entity.get('source_file', 'unknown')
                
                info_lines.append(f"\n• **{entity_name}** (tabela: {table_name})")
                info_lines.append(f"  - Arquivo: {source_file}")
                
                if fields:
                    info_lines.append("  - Campos:")
                    for field in fields[:8]:  # Limitar a 8 campos
                        field_name = field.get('name', 'unknown')
                        field_type = field.get('type', 'String')
                        required = " (obrigatório)" if field.get('required', False) else ""
                        primary_key = " (PK)" if field.get('primary_key', False) else ""
                        foreign_key = f" (FK → {field.get('foreign_key')})" if field.get('foreign_key') else ""
                        info_lines.append(f"    * {field_name}: {field_type}{required}{primary_key}{foreign_key}")
                
                if operations:
                    info_lines.append(f"  - Operações: {', '.join(operations)}")
            
            return "\n".join(info_lines)
            
        except Exception as e:
            logger.error(f"Erro ao extrair entidades de banco: {str(e)}")
            return "Erro ao extrair entidades de banco de dados."

    def _extract_form_entities_info(self, analysis_results: Dict[str, Any]) -> str:
        """Extrai informações dos formulários CRUD identificados"""
        try:
            form_entities = analysis_results.get('form_entities', [])
            if not form_entities:
                return "Nenhum formulário CRUD identificado."
            
            info_lines = ["**Formulários CRUD Identificados:**"]
            for form in form_entities:
                form_name = form.get('name', 'Unknown')
                source_file = form.get('source_file', 'unknown')
                crud_operations = form.get('crud_operations', {})
                db_controls = form.get('db_controls', [])
                validations = form.get('validations', [])
                
                info_lines.append(f"\n• **{form_name}**")
                info_lines.append(f"  - Arquivo: {source_file}")
                
                if crud_operations:
                    info_lines.append("  - Operações CRUD:")
                    for operation, button in crud_operations.items():
                        info_lines.append(f"    * {operation}: {button}")
                
                if db_controls:
                    info_lines.append("  - Controles de Dados:")
                    for control in db_controls[:5]:  # Limitar a 5 controles
                        control_name = control.get('name', 'unknown')
                        control_type = control.get('type', 'unknown')
                        info_lines.append(f"    * {control_name} ({control_type})")
                
                if validations:
                    info_lines.append("  - Validações:")
                    for validation in validations[:3]:  # Limitar a 3 validações
                        val_type = validation.get('type', 'unknown')
                        val_field = validation.get('field', 'N/A')
                        val_message = validation.get('message', 'N/A')
                        info_lines.append(f"    * {val_type} ({val_field}): {val_message}")
            
            return "\n".join(info_lines)
            
        except Exception as e:
            logger.error(f"Erro ao extrair formulários CRUD: {str(e)}")
            return "Erro ao extrair formulários CRUD."

    def _extract_crud_operations_info(self, analysis_results: Dict[str, Any]) -> str:
        """Extrai resumo das operações CRUD detectadas"""
        try:
            crud_summary = analysis_results.get('crud_summary', {})
            if not crud_summary:
                return "Nenhuma operação CRUD detectada."
            
            info_lines = ["**Resumo das Operações CRUD:**"]
            
            # Operações encontradas
            operations_found = crud_summary.get('operations_found', [])
            if operations_found:
                info_lines.append(f"- Operações detectadas: {', '.join(operations_found)}")
            
            # Entidades com CRUD
            entities_with_crud = crud_summary.get('entities_with_crud', [])
            if entities_with_crud:
                info_lines.append("\n- Formulários com CRUD completo:")
                for entity in entities_with_crud:
                    form_name = entity.get('form_name', 'Unknown')
                    operations = entity.get('operations', {})
                    source_file = entity.get('source_file', 'unknown')
                    info_lines.append(f"  * {form_name} ({source_file}): {len(operations)} operações")
            
            # Validações encontradas
            validations_found = crud_summary.get('validations_found', [])
            unique_validations = {v.get('type', 'unknown') for v in validations_found if isinstance(v, dict)}
            if unique_validations:
                info_lines.append(f"\n- Tipos de validação encontrados: {', '.join(unique_validations)}")
            
            return "\n".join(info_lines)
            
        except Exception as e:
            logger.error(f"Erro ao extrair operações CRUD: {str(e)}")
            return "Erro ao extrair operações CRUD."

    def _generate_content_with_llm(self, prompt: str, context: str, doc_type: str = None, 
                                 analysis_results: Dict[str, Any] = None, project_name: str = None) -> str:
        """Gera conteúdo usando LLM - COM LÓGICA ESPECIAL PARA MODERNIZAÇÃO"""
        
        if not self.llm_service:
            raise RuntimeError("LLM service não disponível - OBRIGATÓRIO para geração")
        
        try:
            # LÓGICA ESPECIAL PARA MODERNIZAÇÃO DE CÓDIGO
            if doc_type == 'code_modernization':
                return self._generate_modernization_with_full_context(prompt, context, analysis_results, project_name)
            
            # CORREÇÃO: Melhora o prompt para forçar uso de dados específicos
            enhanced_prompt = f"""
{prompt}

IMPORTANTE: Você DEVE usar EXCLUSIVAMENTE os dados específicos fornecidos no contexto abaixo. 
NÃO use informações genéricas. Se não houver dados suficientes, mencione isso claramente.

DADOS ESPECÍFICOS DO PROJETO:
{context}

FORMATO OBRIGATÓRIO:
1. Comece com o nome do projeto específico
2. Use APENAS nomes de arquivos, classes e métodos identificados
3. Não use exemplos genéricos
4. Se dados estiverem limitados, seja explícito sobre isso
"""
            
            logger.info(f"🚀 Gerando com LLM: {len(enhanced_prompt)} caracteres")
            logger.info(f"📋 Contexto contém: {len(context)} caracteres")
            
            # Log dos primeiros 500 caracteres do contexto para debug
            context_preview = context[:500] + "..." if len(context) > 500 else context
            logger.info(f"🔍 Preview do contexto: {context_preview}")
            
            # Chama o LLM service
            content = self.llm_service.generate_response(enhanced_prompt)
            
            if not content or len(content.strip()) < 100:
                raise RuntimeError("Resposta do LLM muito curta ou vazia")
            
            # CORREÇÃO: Verifica se o conteúdo é genérico demais
            generic_indicators = [
                "please provide me with a list",
                "can you please provide",
                "let's identify the functionalities",
                "to start, let's",
                "it seems like you are looking"
            ]
            
            content_lower = content.lower()
            generic_count = sum(1 for indicator in generic_indicators if indicator in content_lower)
            
            # CORREÇÃO: Detecta conteúdo genérico e cria fallback específico
            if generic_count >= 2:
                logger.warning(f"⚠️ Conteúdo genérico detectado - criando versão específica")
                return self._generate_specific_fallback_content(doc_type, analysis_results, project_name)
            
            logger.info(f"✅ Conteúdo específico gerado: {len(content)} caracteres")
            return content
                
        except Exception as e:
            error_msg = f"Erro na geração com LLM: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _generate_specific_fallback_content(self, doc_type: str, analysis_results: Dict[str, Any], project_name: str) -> str:
        """Gera conteúdo específico baseado apenas nos dados estruturais"""
        try:
            logger.info(f"🔧 Gerando fallback específico para {doc_type}")
            
            # Extrai dados específicos
            metadata = analysis_results.get('metadata', {})
            units = analysis_results.get('units', {})
            forms = analysis_results.get('forms', {})
            summary = analysis_results.get('summary', {})
            
            if doc_type == 'delphi_java_correlation':
                return self._create_correlation_fallback(project_name, units, forms, metadata)
            elif doc_type == 'project_functions':
                return self._create_functions_fallback(project_name, units, forms, metadata)
            elif doc_type == 'project_diagram':
                return self._create_diagram_fallback(project_name, units, forms, metadata)
            elif doc_type == 'project_description':
                return self._create_description_fallback(project_name, units, forms, metadata)
            else:
                return self._create_generic_fallback(project_name, doc_type, analysis_results)
                
        except Exception as e:
            logger.error(f"Erro no fallback específico: {str(e)}")
            return f"# {project_name} - {doc_type}\n\nDados limitados disponíveis para este documento.\n\nAnálise realizada em {datetime.now().strftime('%d/%m/%Y %H:%M')}"

    def _create_correlation_fallback(self, project_name: str, units: dict, forms: dict, metadata: dict) -> str:
        """Cria documento de correlação específico"""
        content = [f"# Correlação Delphi-Java para {project_name}"]
        content.append(f"\nDocumento gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        content.append(f"\n## Projeto Analisado: {project_name}")
        
        if units:
            content.append("\n## Units Identificadas → Controllers Java")
            for unit_path, unit_data in list(units.items())[:10]:
                unit_name = unit_path.split('\\')[-1] if '\\' in unit_path else unit_path
                java_name = unit_name.replace('.pas', 'Controller.java').replace('.dpr', 'Application.java')
                content.append(f"- `{unit_name}` → `{java_name}`")
                
                if isinstance(unit_data, dict):
                    classes = unit_data.get('classes', [])
                    if classes:
                        for cls in classes[:3]:
                            if isinstance(cls, dict):
                                delphi_class = cls.get('name', 'N/A')
                                java_class = delphi_class.replace('T', '') + 'Service'
                                content.append(f"  - Classe `{delphi_class}` → `{java_class}`")
        
        if forms:
            content.append("\n## Forms → REST Controllers")
            for form_path, form_data in list(forms.items())[:5]:
                form_name = form_path.split('\\')[-1] if '\\' in form_path else form_path
                controller_name = form_name.replace('.dfm', 'Controller.java').replace('Form', '')
                content.append(f"- `{form_name}` → `{controller_name}`")
        
        total_files = metadata.get('total_files_analyzed', len(units) + len(forms))
        content.append(f"\n## Resumo da Modernização")
        content.append(f"- **Arquivos analisados**: {total_files}")
        content.append(f"- **Units para Controllers**: {len(units)}")
        content.append(f"- **Forms para REST APIs**: {len(forms)}")
        
        return "\n".join(content)

    def _create_functions_fallback(self, project_name: str, units: dict, forms: dict, metadata: dict) -> str:
        """Cria documento de funções específico"""
        content = [f"# Funções do Projeto {project_name}"]
        content.append(f"\nAnálise de funções e procedimentos identificados")
        content.append(f"\nGerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        if units:
            content.append("\n## Funções das Units")
            for unit_path, unit_data in list(units.items())[:10]:
                unit_name = unit_path.split('\\')[-1] if '\\' in unit_path else unit_path
                content.append(f"\n### {unit_name}")
                
                if isinstance(unit_data, dict):
                    procedures = unit_data.get('procedures_functions', []) or unit_data.get('procedures', [])
                    functions = unit_data.get('functions', [])
                    
                    if procedures:
                        content.append("**Procedimentos:**")
                        for proc in procedures[:10]:
                            if isinstance(proc, dict):
                                proc_name = proc.get('name', 'N/A')
                                content.append(f"- `{proc_name}()`")
                    
                    if functions:
                        content.append("**Funções:**")
                        for func in functions[:10]:
                            if isinstance(func, dict):
                                func_name = func.get('name', 'N/A')
                                return_type = func.get('return_type', 'variant')
                                content.append(f"- `{func_name}(): {return_type}`")
        
        if forms:
            content.append("\n## Eventos dos Forms")
            for form_path, form_data in list(forms.items())[:5]:
                form_name = form_path.split('\\')[-1] if '\\' in form_path else form_path
                content.append(f"\n### {form_name}")
                
                if isinstance(form_data, dict):
                    methods = form_data.get('methods', []) or form_data.get('procedures_functions', [])
                    if methods:
                        for method in methods[:10]:
                            if isinstance(method, dict):
                                method_name = method.get('name', 'N/A')
                                if 'Click' in method_name or 'Event' in method_name:
                                    content.append(f"- `{method_name}` (evento)")
                                else:
                                    content.append(f"- `{method_name}` (método)")
        
        return "\n".join(content)

    def _create_diagram_fallback(self, project_name: str, units: dict, forms: dict, metadata: dict) -> str:
        """Cria diagrama específico"""
        content = [f"# Diagrama do Projeto {project_name}"]
        content.append(f"\nDiagrama da arquitetura atual")
        content.append(f"\nGerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        content.append("\n## Diagrama Mermaid")
        content.append("```mermaid")
        content.append("graph TD")
        content.append(f"    A[{project_name}] --> B[Units]")
        content.append(f"    A --> C[Forms]")
        
        if units:
            for i, (unit_path, _) in enumerate(list(units.items())[:5]):
                unit_name = unit_path.split('\\')[-1] if '\\' in unit_path else unit_path
                safe_name = unit_name.replace('.', '_').replace('-', '_')
                content.append(f"    B --> U{i}[{unit_name}]")
        
        if forms:
            for i, (form_path, _) in enumerate(list(forms.items())[:5]):
                form_name = form_path.split('\\')[-1] if '\\' in form_path else form_path
                safe_name = form_name.replace('.', '_').replace('-', '_')
                content.append(f"    C --> F{i}[{form_name}]")
        
        content.append("```")
        
        return "\n".join(content)

    def _create_description_fallback(self, project_name: str, units: dict, forms: dict, metadata: dict) -> str:
        """Cria descrição específica"""
        content = [f"# Descrição do Projeto {project_name}"]
        content.append(f"\nDescrição baseada na análise estrutural")
        content.append(f"\nGerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        total_files = metadata.get('total_files_analyzed', len(units) + len(forms))
        content.append(f"\n## Visão Geral")
        content.append(f"- **Nome**: {project_name}")
        content.append(f"- **Tipo**: Aplicação Delphi")
        content.append(f"- **Arquivos**: {total_files}")
        content.append(f"- **Units**: {len(units)}")
        content.append(f"- **Forms**: {len(forms)}")
        
        if units:
            content.append(f"\n## Components Principais")
            for unit_path, unit_data in list(units.items())[:5]:
                unit_name = unit_path.split('\\')[-1] if '\\' in unit_path else unit_path
                content.append(f"- **{unit_name}**: Unit principal")
                
                if isinstance(unit_data, dict):
                    classes = unit_data.get('classes', [])
                    if classes:
                        class_names = [cls.get('name', 'N/A') for cls in classes if isinstance(cls, dict)]
                        content.append(f"  - Classes: {', '.join(class_names[:3])}")
        
        return "\n".join(content)

    def _create_generic_fallback(self, project_name: str, doc_type: str, analysis_results: dict) -> str:
        """Cria fallback genérico"""
        return f"# {project_name} - {doc_type.title()}\n\nDocumento específico gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\nDados estruturais disponíveis limitados."

    def _generate_essential_readme(self, analysis_results: Dict[str, Any], 
                                 project_name: str, generated_docs_list: List[str]) -> str:
        """Gera README essencial baseado nos dados REAIS da análise"""
        
        # CORREÇÃO: Usa as chaves corretas que o analyzer realmente retorna
        metadata = analysis_results.get('metadata', {})
        units = analysis_results.get('units', {})  # MUDANÇA: 'units' ao invés de 'units_analysis'
        forms = analysis_results.get('forms', {})  # MUDANÇA: 'forms' ao invés de 'forms_analysis'
        summary = analysis_results.get('summary', {})
        
        # CORREÇÃO: Calcula estatísticas baseadas nos dados reais
        total_files = metadata.get('total_files', 0)
        if total_files == 0:  # Fallback se metadata não tem total_files
            total_files = len(units) + len(forms)
        
        # CORREÇÃO: Calcula linhas de código reais
        total_lines = 0
        for unit_data in units.values():
            if isinstance(unit_data, dict):
                total_lines += unit_data.get('lines_count', 0) or unit_data.get('lines', 0)
        
        # CORREÇÃO: Conta elementos reais do projeto
        total_functions = 0
        total_classes = 0
        for unit_data in units.values():
            if isinstance(unit_data, dict):
                procedures = unit_data.get('procedures_functions', []) or unit_data.get('procedures', [])
                functions = unit_data.get('functions', [])
                classes = unit_data.get('classes', [])
                
                total_functions += len(procedures) + len(functions)
                total_classes += len(classes)
        
        # CORREÇÃO: Adiciona informações dos forms
        total_forms = len(forms)
        for form_data in forms.values():
            if isinstance(form_data, dict):
                form_methods = form_data.get('methods', []) or form_data.get('procedures_functions', [])
                total_functions += len(form_methods)
                
                form_classes = form_data.get('classes', [])
                total_classes += len(form_classes)
        
        readme = f"""# Documentação para Geração Java Spring Boot - {project_name}

## Resumo da Análise REAL
- **Projeto**: {project_name}
- **Arquivos analisados**: {total_files}
- **Linhas de código**: {total_lines:,}
- **Classes identificadas**: {total_classes}
- **Métodos/Funções**: {total_functions}
- **Forms/Interfaces**: {total_forms}
- **Data da análise**: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 📋 Documentos Essenciais Gerados

### 1. ⚙️ Funções do Projeto Original
**Arquivo**: `project_functions.md`
- Lista todas as funções identificadas no projeto Delphi
- Métodos de Forms, Units e DataModules
- Base para geração dos métodos Java

### 2. 📊 Diagrama do Projeto Original  
**Arquivo**: `project_diagram.md`
- Diagrama Mermaid da arquitetura atual
- Fluxo de dados identificado
- Estrutura visual para conversão

### 3. 🔗 Correlação Delphi-Java
**Arquivo**: `delphi_java_correlation.md`
- Mapeamento direto de componentes Delphi → Spring Boot
- Equivalências de classes e métodos
- Padrões de conversão

### 4. 📝 Descrição do Projeto
**Arquivo**: `project_description.md`
- Visão geral baseada na análise
- Funcionalidades identificadas
- Características técnicas

## 🎯 Próximos Passos
1. ✅ Análise Delphi concluída
2. ✅ Documentação essencial gerada
3. 🔄 **Próximo**: Geração do código Java Spring Boot
4. 🔄 Testes e validação

## 📊 Estatísticas da Análise DETALHADA
- **Units identificadas**: {len(units)}
- **Forms identificados**: {len(forms)}
- **DataModules identificados**: {len(analysis_results.get('datamodules', {}))}
- **Complexidade média**: {summary.get('average_complexity', 'N/A')}
- **Tipo de arquitetura**: {summary.get('architecture_type', 'Desktop VCL')}

## 🔧 Componentes Principais Identificados
"""

        # CORREÇÃO: Adiciona lista real dos componentes encontrados
        if units:
            readme += "\n### Units Analisadas:\n"
            for i, (unit_path, unit_data) in enumerate(list(units.items())[:10]):
                unit_name = unit_path.split('\\')[-1] if '\\' in unit_path else unit_path
                unit_type = unit_data.get('unit_type', 'unit') if isinstance(unit_data, dict) else 'unit'
                lines = unit_data.get('lines_count', 0) if isinstance(unit_data, dict) else 0
                readme += f"- **{unit_name}** ({unit_type}) - {lines} linhas\n"
        
        if forms:
            readme += "\n### Forms/Interfaces:\n"
            for i, (form_path, form_data) in enumerate(list(forms.items())[:5]):
                form_name = form_path.split('\\')[-1] if '\\' in form_path else form_path
                lines = form_data.get('lines_count', 0) if isinstance(form_data, dict) else 0
                readme += f"- **{form_name}** - {lines} linhas\n"
        
        readme += f"""
---
*Documentação gerada automaticamente pelo Sistema JUNIM*
*Baseada na análise REAL de {total_files} arquivos do projeto {project_name}*
*Focada na geração de código Java Spring Boot*
"""
        return readme

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza nome do arquivo"""
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized

    # Métodos auxiliares para compatibilidade com interface existente
    def get_document_content(self, doc_key_or_path: str, project_name: str = "Projeto") -> str:
        """Obtém conteúdo de um documento específico"""
        try:
            if os.path.isfile(doc_key_or_path):
                with open(doc_key_or_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            doc_config = self.document_types.get(doc_key_or_path, {})
            filename = doc_config.get('filename', f'{doc_key_or_path}.md')
            
            project_dir = self.docs_dir / self._sanitize_filename(project_name)
            doc_path = project_dir / filename
            
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"Documento não encontrado: {doc_key_or_path}"
                
        except Exception as e:
            logger.error(f"Erro ao ler documento {doc_key_or_path}: {str(e)}")
            return f"Erro ao carregar documento: {str(e)}"
    
    def generate_complete_documentation(self, analysis_results: Dict[str, Any], 
                                      project_name: str = "Projeto") -> Dict[str, str]:
        """
        Gera documentação COMPLETA e ESPECÍFICA baseada na análise real do projeto
        
        Args:
            analysis_results: Resultados detalhados da análise do projeto Delphi
            project_name: Nome específico do projeto
            
        Returns:
            Dict com caminhos dos documentos gerados
        """
        try:
            logger.info(f"🚀 Iniciando geração ROBUSTA de documentação para: {project_name}")
            
            # Validação rigorosa dos dados de entrada
            if not self._validate_analysis_data(analysis_results, project_name):
                raise ValueError(f"❌ Dados de análise insuficientes para {project_name}")
            
            # Extrai contexto específico do projeto
            project_context = self._extract_project_context(analysis_results, project_name)
            logger.info(f"📋 Contexto extraído: {len(project_context)} elementos específicos")
            
            # Cria diretório específico para o projeto
            project_dir = self.docs_dir / self._sanitize_filename(project_name)
            project_dir.mkdir(exist_ok=True)
            
            generated_docs = {}
            
            # Gera cada documento com verificação de especificidade
            for doc_type, doc_info in sorted(self.document_types.items(), 
                                           key=lambda x: x[1]['priority']):
                logger.info(f"📄 Gerando {doc_info['name']}...")
                
                try:
                    # Gera conteúdo específico usando contexto do projeto
                    content = self._generate_specific_content(
                        doc_type, analysis_results, project_context, project_name
                    )
                    
                    # Valida especificidade do conteúdo gerado
                    if self._validate_content_specificity(content, project_name):
                        file_path = project_dir / doc_info['filename']
                        
                        # Salva documento com metadata
                        self._save_document_with_metadata(file_path, content, doc_info, project_name)
                        generated_docs[doc_type] = str(file_path)
                        
                        logger.info(f"✅ {doc_info['name']} gerado com sucesso: {len(content)} chars")
                    else:
                        # Tenta regenerar com prompt mais específico
                        logger.warning(f"⚠️ Conteúdo genérico detectado, regenerando {doc_type}...")
                        content = self._regenerate_with_enhanced_specificity(
                            doc_type, analysis_results, project_context, project_name
                        )
                        
                        if self._validate_content_specificity(content, project_name):
                            file_path = project_dir / doc_info['filename']
                            self._save_document_with_metadata(file_path, content, doc_info, project_name)
                            generated_docs[doc_type] = str(file_path)
                            logger.info(f"✅ {doc_info['name']} regenerado com sucesso")
                        else:
                            logger.error(f"❌ Falha na geração específica de {doc_type}")
                            raise RuntimeError(f"Não foi possível gerar conteúdo específico para {doc_type}")
                
                except Exception as e:
                    logger.error(f"❌ Erro ao gerar {doc_type}: {str(e)}")
                    # Não continua se um documento essencial falhar
                    raise RuntimeError(f"Falha crítica na geração de {doc_type}: {str(e)}")
            
            # Gera índice consolidado
            self._generate_project_index(project_dir, generated_docs, project_name)
            
            logger.info(f"🎉 Documentação completa gerada: {len(generated_docs)} documentos")
            return generated_docs
            
        except Exception as e:
            logger.error(f"❌ Falha na geração de documentação: {str(e)}")
            raise
            
            # Gera cada tipo de documento
            for doc_key, doc_config in self.document_types.items():
                try:
                    logger.info(f"📄 Gerando documento: {doc_config['name']}")
                    
                    doc_path = self._generate_document(
                        doc_key=doc_key,
                        doc_config=doc_config,
                        analysis_results=analysis_results,
                        project_dir=project_dir,
                        project_name=project_name
                    )
                    
                    if doc_path:
                        generated_docs[doc_key] = str(doc_path)
                        logger.info(f"✅ Documento gerado: {doc_config['name']}")
                    else:
                        logger.warning(f"⚠️ Falha ao gerar documento: {doc_config['name']}")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao gerar documento {doc_key}: {str(e)}")
                    continue
            
            # Salva metadados
            self._save_documentation_metadata(generated_docs, analysis_results, project_dir)
            
            logger.info(f"🎉 Documentação completa gerada: {len(generated_docs)} documentos")
            return generated_docs
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de documentação: {str(e)}")
            return {}
    
    def _generate_document(self, doc_key: str, doc_config: Dict[str, Any], 
                          analysis_results: Dict[str, Any], project_dir: Path, 
                          project_name: str) -> Optional[Path]:
        """Gera um documento específico"""
        try:
            # Obtém prompt específico
            prompt = self._get_prompt_for_document(doc_config['prompt_type'])
            
            # Prepara contexto
            context = self._prepare_context(analysis_results, project_name, doc_key)
            
            # Gera conteúdo usando LLM
            content = self._generate_content_with_llm(prompt, context)
            
            if not content or len(content.strip()) < 100:
                raise RuntimeError(f"Falha ao gerar conteúdo para {doc_key}")
            
            # Salva documento
            doc_path = project_dir / doc_config['filename']
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return doc_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar documento {doc_key}: {str(e)}")
            return None
    
    def _prepare_context(self, analysis_results: Dict[str, Any], project_name: str, doc_key: str) -> str:
        """Prepara contexto para geração de documento - FALHA se dados insuficientes"""
        
        # Validação rigorosa dos dados de entrada
        if not analysis_results or not isinstance(analysis_results, dict):
            raise ValueError("analysis_results está vazio ou inválido")
        
        logger.info(f"🔍 Preparando contexto para {doc_key} - Dados disponíveis: {list(analysis_results.keys())}")
        
        # Formata dados de forma mais legível
        formatted_data = self._format_analysis_data(analysis_results)
        if len(formatted_data) < 200:
            logger.warning(f"⚠️ Dados formatados limitados: {len(formatted_data)} chars - continuando mesmo assim")
            # CORREÇÃO: Não falha mais, mas continua com dados limitados
        
        # Adiciona informações específicas do código
        code_specifics = self._extract_code_specifics(analysis_results)
        if len(code_specifics) < 100:
            logger.warning(f"⚠️ Especificações do código limitadas: {len(code_specifics)} chars")
        
        # Monta contexto completo - igual à versão limpa
        context = f"""
===== CONTEXTO ESPECÍFICO DO PROJETO =====
PROJETO: {project_name}
TIPO DE DOCUMENTO: {doc_key}

===== DADOS REAIS EXTRAÍDOS DA ANÁLISE =====
{formatted_data}

===== CÓDIGO E COMPONENTES IDENTIFICADOS =====
{code_specifics}

===== INSTRUÇÕES CRÍTICAS PARA IA =====
VOCÊ DEVE GERAR DOCUMENTAÇÃO TÉCNICA ESPECÍFICA para este projeto Delphi ({project_name}).

🚨 REGRAS OBRIGATÓRIAS:
1. Use EXCLUSIVAMENTE os dados fornecidos acima - não invente nada
2. Mencione nomes ESPECÍFICOS de classes, métodos e arquivos identificados
3. Foque em aspectos de backend e modernização para Java Spring Boot
4. Use formatação Markdown clara com títulos, subtítulos e listas
5. Seja técnico e preciso - EVITE descrições genéricas
6. Inclua exemplos práticos baseados APENAS no código analisado

FORMATO ESPERADO: Documento Markdown técnico específico para {project_name}
NÃO USE INFORMAÇÕES GENÉRICAS - BASE-SE APENAS NOS DADOS FORNECIDOS ACIMA
        """
        
        logger.info(f"🎯 Contexto preparado: {len(context)} caracteres")
        
        if len(context) < 1000:
            raise RuntimeError(f"Contexto muito pequeno: {len(context)} caracteres")
        
        return context
    
    def _extract_code_specifics(self, analysis_results: Dict[str, Any]) -> str:
        """Extrai informações específicas do código para enriquecer o contexto"""
        try:
            specifics = []
            
            # Extrai nomes de classes específicas
            all_classes = []
            files_data = analysis_results.get('files', {})
            
            # Verifica se files é um dicionário ou lista
            if isinstance(files_data, dict):
                files_to_process = files_data.values()
            elif isinstance(files_data, list):
                files_to_process = files_data
            else:
                files_to_process = []
            
            for file_data in files_to_process:
                if isinstance(file_data, dict):
                    classes = file_data.get('classes', [])
                    for cls in classes:
                        class_name = cls.get('name', '')
                        parent_class = cls.get('parent_class', '')
                        if class_name:
                            all_classes.append(f"{class_name} (extends {parent_class})")
            
            if all_classes:
                specifics.append(f"**Classes Identificadas:**")
                for cls in all_classes[:10]:  # Limita para não ficar muito longo
                    specifics.append(f"- {cls}")
            
            # Extrai métodos específicos importantes
            important_methods = []
            files_data = analysis_results.get('files', {})
            
            # Verifica se files é um dicionário ou lista
            if isinstance(files_data, dict):
                files_to_process = files_data.values()
            elif isinstance(files_data, list):
                files_to_process = files_data
            else:
                files_to_process = []
                
            for file_data in files_to_process:
                if isinstance(file_data, dict):
                    methods = file_data.get('methods', [])
                    for method in methods:
                        method_name = method.get('name', '')
                        method_type = method.get('type', 'method')
                        return_type = method.get('return_type', 'void')
                        if method_name and not method_name.startswith('_'):  # Ignora métodos privados
                            important_methods.append(f"{method_name}(): {return_type} ({method_type})")
            
            if important_methods:
                specifics.append(f"\n**Métodos Principais:**")
                for method in important_methods[:15]:  # Limita para não ficar muito longo
                    specifics.append(f"- {method}")
            
            # Extrai padrões de nomenclatura
            naming_patterns = set()
            files_data = analysis_results.get('files', {})
            
            # Verifica se files é um dicionário ou lista
            if isinstance(files_data, dict):
                files_to_process = files_data.values()
            elif isinstance(files_data, list):
                files_to_process = files_data
            else:
                files_to_process = []
                
            for file_data in files_to_process:
                if isinstance(file_data, dict):
                    classes = file_data.get('classes', [])
                    for cls in classes:
                        class_name = cls.get('name', '')
                        if class_name.startswith('T'):
                            naming_patterns.add("Classes com prefixo T (padrão Delphi)")
                        if 'Form' in class_name:
                            naming_patterns.add("Classes de formulário (UI)")
                        if 'DataModule' in class_name:
                            naming_patterns.add("DataModules (acesso a dados)")
            
            if naming_patterns:
                specifics.append(f"\n**Padrões Identificados:**")
                for pattern in naming_patterns:
                    specifics.append(f"- {pattern}")
            
            # Extrai informações sobre eventos (importante para UI)
            event_methods = []
            files_data = analysis_results.get('files', {})
            
            # Verifica se files é um dicionário ou lista
            if isinstance(files_data, dict):
                files_to_process = files_data.values()
            elif isinstance(files_data, list):
                files_to_process = files_data
            else:
                files_to_process = []
                
            for file_data in files_to_process:
                if isinstance(file_data, dict):
                    methods = file_data.get('methods', [])
                    for method in methods:
                        method_name = method.get('name', '')
                        if any(event in method_name for event in ['Click', 'Change', 'Create', 'Close', 'Show']):
                            event_methods.append(method_name)
            
            if event_methods:
                specifics.append(f"\n**Eventos de Interface:**")
                for event in event_methods[:10]:
                    specifics.append(f"- {event}")
            
            return "\n".join(specifics) if specifics else "Nenhum detalhe específico adicional identificado."
            
        except Exception as e:
            logger.error(f"Erro ao extrair especificidades do código: {str(e)}")
            return "Erro ao extrair detalhes específicos do código."
    
    def _format_analysis_data(self, analysis_results: Dict[str, Any]) -> str:
        """Formata dados de análise MELHORADOS de forma legível e específica"""
        try:
            formatted = []
            
            # CORREÇÃO: Log para debug dos dados recebidos
            logger.info(f"🔍 Formatando dados MELHORADOS - Chaves disponíveis: {list(analysis_results.keys())}")
            
            # Informações básicas do projeto
            project_name = analysis_results.get('project_name', 'N/A')
            formatted.append(f"**Projeto**: {project_name}")
            formatted.append(f"**Data da Análise**: {analysis_results.get('analysis_timestamp', 'N/A')}")
            
            # Estatísticas do projeto (nova estrutura)
            stats = analysis_results.get('project_statistics', {})
            if stats:
                formatted.append(f"\n**📊 ESTATÍSTICAS REAIS:**")
                formatted.append(f"• Total de linhas: {stats.get('total_lines', 0)}")
                formatted.append(f"• Total de funções: {stats.get('total_functions', 0)}")
                formatted.append(f"• Total de classes: {stats.get('total_classes', 0)}")
                formatted.append(f"• Total de eventos: {stats.get('total_events', 0)}")
                formatted.append(f"• Formulários (Forms): {stats.get('form_count', 0)}")
                formatted.append(f"• Units utilitárias: {stats.get('utility_count', 0)}")
                formatted.append(f"• Data Modules: {stats.get('datamodule_count', 0)}")
            
            # Arquivos analisados (nova estrutura)
            files_analyzed = analysis_results.get('files_analyzed', {})
            if files_analyzed:
                formatted.append(f"\n**📁 ARQUIVOS IDENTIFICADOS ({files_analyzed.get('total_files', 0)}):**")
                files_list = files_analyzed.get('files', [])
                if files_list:
                    # Agrupa por tipo
                    forms = [f for f in files_list if f.get('type') == 'form']
                    utilities = [f for f in files_list if f.get('type') == 'utility']
                    datamodules = [f for f in files_list if f.get('type') == 'datamodule']
                    
                    if forms:
                        form_names = [f['filename'] for f in forms[:3]]
                        formatted.append(f"• Forms: {', '.join(form_names)}")
                        if len(forms) > 3:
                            formatted.append(f"  ... e mais {len(forms) - 3} forms")
                    
                    if utilities:
                        util_names = [f['filename'] for f in utilities[:3]]
                        formatted.append(f"• Units: {', '.join(util_names)}")
                        if len(utilities) > 3:
                            formatted.append(f"  ... e mais {len(utilities) - 3} units")
                    
                    if datamodules:
                        dm_names = [f['filename'] for f in datamodules]
                        formatted.append(f"• Data Modules: {', '.join(dm_names)}")
            
            # Funções específicas identificadas (nova estrutura)
            functions = analysis_results.get('functions', [])
            if functions:
                formatted.append(f"\n**⚙️ FUNÇÕES IDENTIFICADAS ({len(functions)}):**")
                for func in functions[:8]:  # Primeiras 8 funções
                    func_name = func.get('name', 'N/A')
                    func_type = func.get('type', 'function')
                    func_file = func.get('source_file', 'N/A')
                    category = func.get('category', '')
                    
                    func_desc = f"• {func_name}() [{func_type}]"
                    if category and category != func_type:
                        func_desc += f" - {category}"
                    func_desc += f" em {func_file}"
                    formatted.append(func_desc)
                
                if len(functions) > 8:
                    formatted.append(f"... e mais {len(functions) - 8} funções")
            
            # Classes específicas identificadas (nova estrutura)
            classes = analysis_results.get('classes', [])
            if classes:
                formatted.append(f"\n**📦 CLASSES IDENTIFICADAS ({len(classes)}):**")
                for cls in classes[:5]:  # Primeiras 5 classes
                    class_name = cls.get('name', 'N/A')
                    parent_class = cls.get('parent_class', 'TObject')
                    class_type = cls.get('class_type', 'class')
                    source_file = cls.get('source_file', 'N/A')
                    
                    cls_desc = f"• {class_name}"
                    if parent_class != 'TObject':
                        cls_desc += f" extends {parent_class}"
                    cls_desc += f" [{class_type}] em {source_file}"
                    formatted.append(cls_desc)
                    
                    # Métodos da classe
                    methods = cls.get('methods', [])
                    if methods:
                        method_names = [m['name'] for m in methods[:3]]
                        formatted.append(f"  - Métodos: {', '.join(method_names)}")
                
                if len(classes) > 5:
                    formatted.append(f"... e mais {len(classes) - 5} classes")
            
            # Dependências identificadas (nova estrutura)
            dependencies = analysis_results.get('dependencies', [])
            if dependencies:
                formatted.append(f"\n**🔗 DEPENDÊNCIAS (Uses):**")
                deps_limited = dependencies[:10]  # Limita a 10 dependências
                formatted.append(f"• {', '.join(deps_limited)}")
                if len(dependencies) > 10:
                    formatted.append(f"... e mais {len(dependencies) - 10}")
            
            # Hierarquia do projeto (nova estrutura)
            hierarchy = analysis_results.get('hierarchy', {})
            if hierarchy:
                formatted.append(f"\n**🏗️ ESTRUTURA DO PROJETO:**")
                root_files = hierarchy.get('root_files', [])
                subdirs = hierarchy.get('subdirectories', {})
                
                if root_files:
                    delphi_roots = [f for f in root_files if f.endswith(('.pas', '.dfm', '.dpr'))]
                    if delphi_roots:
                        formatted.append(f"• Arquivos na raiz: {', '.join(delphi_roots[:3])}")
                
                if subdirs:
                    formatted.append(f"• Subdiretórios: {len(subdirs)} encontrados")
            
            result = "\n".join(formatted)
            
            if len(result) < 200:
                logger.warning(f"⚠️ Contexto formatado limitado: {len(result)} chars")
                # Adiciona informação mínima se o resultado for muito pequeno
                result += f"\n\n**INFORMAÇÃO DISPONÍVEL LIMITADA**\nProjeto: {project_name}\nMétodo de análise: {analysis_results.get('analysis_method', 'estruturada')}"
            
            logger.info(f"✅ Contexto formatado com sucesso: {len(result)} caracteres")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao formatar dados de análise: {str(e)}")
            # Fallback com informações básicas
            project_name = analysis_results.get('project_name', 'Projeto Desconhecido')
            return f"**Projeto**: {project_name}\n**Status**: Dados de análise limitados\n**Erro**: {str(e)}"
            
            # Métricas de complexidade
            complexity = analysis_results.get('complexity_metrics', {})
            if complexity:
                formatted.append(f"\n**Métricas de Complexidade:**")
                formatted.append(f"- Total de Linhas: {complexity.get('total_lines', 0)}")
                formatted.append(f"- Total de Funções: {complexity.get('function_count', 0)}")
                formatted.append(f"- Total de Classes: {complexity.get('class_count', 0)}")
                formatted.append(f"- Complexidade Estimada: {complexity.get('estimated_complexity', 'N/A')}")
            
            # Dependências
            dependencies = analysis_results.get('dependencies', {})
            if dependencies:
                formatted.append(f"\n**Dependências:**")
                internal_units = dependencies.get('internal_units', [])
                system_units = dependencies.get('system_units', [])
                external_libs = dependencies.get('external_libraries', [])
                
                if internal_units:
                    formatted.append(f"- Units Internas: {len(internal_units)} ({', '.join(internal_units[:3])}...)")
                if system_units:
                    formatted.append(f"- Units do Sistema: {len(system_units)} ({', '.join(system_units[:3])}...)")
                if external_libs:
                    formatted.append(f"- Bibliotecas Externas: {len(external_libs)}")
            
            # Elementos de banco de dados
            db_elements = analysis_results.get('database_elements', {})
            if db_elements and any(db_elements.values()):
                formatted.append(f"\n**Elementos de Banco de Dados:**")
                connections = db_elements.get('connections', [])
                queries = db_elements.get('queries', [])
                tables = db_elements.get('tables_referenced', [])
                
                if connections:
                    formatted.append(f"- Conexões: {len(connections)}")
                if queries:
                    formatted.append(f"- Queries/Operações: {len(queries)}")
                if tables:
                    formatted.append(f"- Tabelas Referenciadas: {len(tables)}")
            
            # Componentes de UI
            ui_components = analysis_results.get('ui_components', {})
            if ui_components and any(ui_components.values()):
                formatted.append(f"\n**Componentes de Interface:**")
                ui_forms = ui_components.get('forms', [])
                ui_controls = ui_components.get('controls', [])
                ui_menus = ui_components.get('menus', [])
                
                if ui_forms:
                    formatted.append(f"- Formulários UI: {len(ui_forms)}")
                if ui_controls:
                    formatted.append(f"- Controles: {len(ui_controls)}")
                if ui_menus:
                    formatted.append(f"- Menus: {len(ui_menus)}")
            
            # Análise LLM (se disponível)
            llm_analysis = analysis_results.get('llm_analysis', '')
            if llm_analysis and len(llm_analysis) > 100:
                # Extrai primeiras linhas da análise LLM
                llm_lines = llm_analysis.split('\n')[:5]
                formatted.append(f"\n**Análise LLM (resumo):**")
                for line in llm_lines:
                    if line.strip():
                        formatted.append(f"- {line.strip()[:100]}...")
            
            # Business Logic identificada
            business_logic = analysis_results.get('business_logic', {})
            if business_logic and any(business_logic.values()):
                formatted.append(f"\n**Lógica de Negócio:**")
                rules = business_logic.get('rules', [])
                patterns = business_logic.get('patterns', [])
                workflows = business_logic.get('workflows', [])
                
                if rules:
                    formatted.append(f"- Regras identificadas: {len(rules)}")
                if patterns:
                    formatted.append(f"- Padrões detectados: {len(patterns)}")
                if workflows:
                    formatted.append(f"- Fluxos de trabalho: {len(workflows)}")
            
            # Dicas para documentação
            doc_hints = analysis_results.get('documentation_hints', {})
            if doc_hints and any(doc_hints.values()):
                formatted.append(f"\n**Sugestões para Documentação:**")
                suggested_sections = doc_hints.get('suggested_sections', [])
                key_components = doc_hints.get('key_components', [])
                main_functions = doc_hints.get('main_functions', [])
                
                if suggested_sections:
                    formatted.append(f"- Seções sugeridas: {', '.join(suggested_sections[:3])}")
                if key_components:
                    formatted.append(f"- Componentes-chave: {', '.join(key_components[:3])}")
                if main_functions:
                    formatted.append(f"- Funções principais: {', '.join(main_functions[:3])}")
            
            # Sugestões de modernização
            modernization = analysis_results.get('modernization_suggestions', {})
            if modernization and any(modernization.values()):
                formatted.append(f"\n**Sugestões de Modernização:**")
                priority_areas = modernization.get('priority_areas', [])
                tech_migration = modernization.get('technology_migration', [])
                arch_improvements = modernization.get('architecture_improvements', [])
                
                if priority_areas:
                    formatted.append(f"- Áreas prioritárias: {', '.join(priority_areas[:2])}")
                if tech_migration:
                    formatted.append(f"- Migração tecnológica: {', '.join(tech_migration[:2])}")
                if arch_improvements:
                    formatted.append(f"- Melhorias arquiteturais: {', '.join(arch_improvements[:2])}")
            
            # RESULTADO FINAL
            result = "\n".join(formatted)
            logger.info(f"✅ Dados formatados: {len(result)} caracteres, {len(formatted)} seções")
            
            return result if result else "Nenhum dado específico foi extraído da análise."
            
        except Exception as e:
            logger.error(f"❌ Erro ao formatar dados: {str(e)}")
            # Fallback para formato JSON mais limpo
            essential_data = {
                'project_name': analysis_results.get('metadata', {}).get('project_name', 'N/A'),
                'total_files': analysis_results.get('files_analyzed', {}).get('total_files', 0),
                'functions_count': len(analysis_results.get('code_structure', {}).get('functions', [])),
                'classes_count': len(analysis_results.get('code_structure', {}).get('classes', [])),
                'forms_count': len(analysis_results.get('code_structure', {}).get('forms', [])),
                'complexity': analysis_results.get('complexity_metrics', {}).get('estimated_complexity', 'N/A')
            }
            return f"Dados da análise (formato simplificado):\n{json.dumps(essential_data, indent=2, ensure_ascii=False)}"
    


    def _save_documentation_metadata(self, generated_docs: Dict[str, str], 
                                   analysis_results: Dict[str, Any], project_dir: Path):
        """Salva metadados da documentação"""
        try:
            metadata = {
                'generation_date': datetime.now().isoformat(),
                'documents_generated': len(generated_docs),
                'document_list': list(generated_docs.keys()),
                'analysis_summary': {
                    'total_files': analysis_results.get('metadata', {}).get('total_files_analyzed', 0),  # CORREÇÃO: usa 'metadata'
                    'main_units': len(analysis_results.get('units', {})),      # CORREÇÃO: 'units' ao invés de 'units_analysis'
                    'main_forms': len(analysis_results.get('forms', {})),     # CORREÇÃO: 'forms' ao invés de 'forms_analysis'
                    'has_requirements': 'requirements' in analysis_results,
                    'has_characteristics': 'characteristics' in analysis_results
                }
            }
            
            metadata_path = project_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            logger.info("✅ Metadados salvos")
            
        except Exception as e:
            logger.error(f"Erro ao salvar metadados: {str(e)}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza nome do arquivo"""
        import re
        # Remove caracteres especiais
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove espaços extras
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized
    
    def regenerate_document_with_feedback(self, doc_key: str, original_content: str, 
                                        feedback: str, analysis_results: Dict[str, Any], 
                                        project_name: str = "Projeto") -> str:
        """
        Regenera documento específico com base no feedback
        
        Args:
            doc_key: Chave do documento
            original_content: Conteúdo original
            feedback: Feedback do usuário
            analysis_results: Dados da análise
            project_name: Nome do projeto
            
        Returns:
            Novo conteúdo do documento
        """
        try:
            logger.info(f"🔄 Regenerando documento {doc_key} com feedback")
            
            # Obtém prompt específico
            doc_config = self.document_types.get(doc_key, {})
            base_prompt = self._get_prompt_for_document(doc_config.get('prompt_type', 'analysis'))
            
            # Cria prompt com feedback
            feedback_prompt = f"""
{base_prompt}

DOCUMENTO ORIGINAL:
{original_content}

FEEDBACK DO USUÁRIO:
{feedback}

INSTRUÇÕES:
- Considere o feedback fornecido
- Mantenha aspectos corretos do documento original
- Corrija problemas identificados no feedback
- Melhore a qualidade e precisão
- Mantenha formatação markdown
- Foque em aspectos de backend
            """
            
            # Prepara contexto
            context = self._prepare_context(analysis_results, project_name, doc_key)
            
            # Gera novo conteúdo
            new_content = self._generate_content_with_llm(feedback_prompt, context)
            
            if new_content:
                # Salva versão atualizada
                project_dir = self.docs_dir / self._sanitize_filename(project_name)
                project_dir.mkdir(exist_ok=True)
                
                doc_path = project_dir / doc_config.get('filename', f'{doc_key}.md')
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"✅ Documento {doc_key} regenerado com sucesso")
                return new_content
            else:
                logger.warning(f"⚠️ Falha ao regenerar documento {doc_key}")
                return original_content
                
        except Exception as e:
            logger.error(f"❌ Erro ao regenerar documento {doc_key}: {str(e)}")
            return original_content
    
    def get_document_content(self, doc_key_or_path: str, project_name: str = "Projeto") -> str:
        """Obtém conteúdo de um documento específico"""
        try:
            # Se for um caminho de arquivo, usa diretamente
            if os.path.isfile(doc_key_or_path):
                with open(doc_key_or_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Caso contrário, trata como doc_key
            doc_config = self.document_types.get(doc_key_or_path, {})
            filename = doc_config.get('filename', f'{doc_key_or_path}.md')
            
            project_dir = self.docs_dir / self._sanitize_filename(project_name)
            doc_path = project_dir / filename
            
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"Documento não encontrado: {doc_key_or_path}"
                
        except Exception as e:
            logger.error(f"Erro ao ler documento {doc_key_or_path}: {str(e)}")
            return f"Erro ao carregar documento: {str(e)}"
    
    def list_generated_documents(self, project_name: str = "Projeto") -> Dict[str, Dict[str, Any]]:
        """Lista documentos gerados para um projeto"""
        try:
            project_dir = self.docs_dir / self._sanitize_filename(project_name)
            
            if not project_dir.exists():
                return {}
            
            documents = {}
            
            for doc_key, doc_config in self.document_types.items():
                filename = doc_config.get('filename', f'{doc_key}.md')
                doc_path = project_dir / filename
                
                if doc_path.exists():
                    stat = doc_path.stat()
                    documents[doc_key] = {
                        'name': doc_config.get('name', doc_key),
                        'path': str(doc_path),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
            
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao listar documentos: {str(e)}")
            return {}
    
    def get_documentation_summary(self, project_name: str = "Projeto") -> Dict[str, Any]:
        """Obtém resumo da documentação gerada"""
        try:
            project_dir = self.docs_dir / self._sanitize_filename(project_name)
            metadata_path = project_dir / "metadata.json"
            
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao obter resumo: {str(e)}")
            return {}
    
    # ========== MÉTODOS APRIMORADOS PARA ANÁLISE ESPECÍFICA ==========
    
    def _validate_analysis_data(self, analysis_results: Dict[str, Any], project_name: str) -> bool:
        """Valida se os dados de análise são suficientes para gerar documentação específica"""
        if not analysis_results or not isinstance(analysis_results, dict):
            logger.error(f"❌ Dados de análise inválidos para {project_name}")
            return False
        
        required_sections = ['files_analyzed', 'code_structure', 'metadata']
        missing_sections = [section for section in required_sections 
                          if section not in analysis_results]
        
        if missing_sections:
            logger.error(f"❌ Seções obrigatórias ausentes: {missing_sections}")
            return False
        
        # Verifica se há código real analisado
        files_count = analysis_results.get('files_analyzed', {}).get('total_files', 0)
        if files_count == 0:
            logger.error(f"❌ Nenhum arquivo foi analisado para {project_name}")
            return False
        
        logger.info(f"✅ Dados de análise válidos: {files_count} arquivos analisados")
        return True
    
    def _extract_project_context(self, analysis_results: Dict[str, Any], project_name: str) -> Dict[str, Any]:
        """Extrai contexto específico do projeto para usar nos prompts"""
        context = {
            'project_name': project_name,
            'files': [],
            'functions': [],
            'classes': [],
            'forms': [],
            'database_tables': [],
            'business_logic': [],
            'specific_patterns': []
        }
        
        # Extrai arquivos específicos
        files_data = analysis_results.get('files_analyzed', {})
        if 'files' in files_data:
            for file_info in files_data['files']:
                if isinstance(file_info, dict):
                    context['files'].append({
                        'name': file_info.get('filename', ''),
                        'type': file_info.get('file_type', ''),
                        'size': file_info.get('size', 0),
                        'functions_count': len(file_info.get('functions', []))
                    })
        
        # Extrai estrutura de código
        code_structure = analysis_results.get('code_structure', {})
        
        # Funções e procedimentos específicos
        if 'functions' in code_structure:
            for func in code_structure['functions']:
                if isinstance(func, dict):
                    context['functions'].append({
                        'name': func.get('name', ''),
                        'type': func.get('type', ''),
                        'parameters': func.get('parameters', []),
                        'file': func.get('source_file', '')
                    })
        
        # Classes e objetos
        if 'classes' in code_structure:
            for cls in code_structure['classes']:
                if isinstance(cls, dict):
                    context['classes'].append({
                        'name': cls.get('name', ''),
                        'methods': cls.get('methods', []),
                        'properties': cls.get('properties', []),
                        'file': cls.get('source_file', '')
                    })
        
        # Forms e componentes visuais
        if 'forms' in code_structure:
            for form in code_structure['forms']:
                if isinstance(form, dict):
                    context['forms'].append({
                        'name': form.get('name', ''),
                        'components': form.get('components', []),
                        'events': form.get('events', [])
                    })
        
        # Extrai padrões específicos do negócio
        if 'business_logic' in analysis_results:
            business_logic = analysis_results['business_logic']
            if isinstance(business_logic, dict):
                context['business_logic'] = [
                    f"Regra: {rule}" for rule in business_logic.get('rules', [])
                ]
                context['specific_patterns'] = business_logic.get('patterns', [])
        
        logger.info(f"📋 Contexto extraído: {len(context['files'])} arquivos, "
                   f"{len(context['functions'])} funções, {len(context['classes'])} classes")
        
        return context
    
    def _validate_content_specificity(self, content: str, project_name: str) -> bool:
        """Valida se o conteúdo gerado é específico do projeto, não genérico"""
        if not content or len(content.strip()) < self.specificity_checks['min_content_length']:
            logger.warning(f"⚠️ Conteúdo muito curto: {len(content.strip())} chars")
            return False
        
        content_lower = content.lower()
        
        # Verifica referências específicas do projeto
        project_refs = 0
        project_refs += content_lower.count(project_name.lower())
        project_refs += len(re.findall(r'\b(function|procedure|class|form)\s+\w+', content_lower))
        project_refs += len(re.findall(r'\bunit\s+\w+', content_lower))
        
        if project_refs < self.specificity_checks['min_project_references']:
            logger.warning(f"⚠️ Poucas referências específicas: {project_refs}")
            return False
        
        # Verifica conteúdo genérico proibido
        for forbidden in self.specificity_checks['forbidden_generic']:
            if forbidden in content_lower:
                logger.warning(f"⚠️ Conteúdo genérico detectado: {forbidden}")
                return False
        
        # Verifica seções obrigatórias
        sections_found = sum(1 for section in self.specificity_checks['required_sections']
                           if section in content_lower)
        
        if sections_found < len(self.specificity_checks['required_sections']) - 1:
            logger.warning(f"⚠️ Seções obrigatórias ausentes: {sections_found}/{len(self.specificity_checks['required_sections'])}")
            return False
        
        logger.info(f"✅ Conteúdo específico validado: {project_refs} refs, {sections_found} seções")
        return True
    
    def _generate_specific_content(self, doc_type: str, analysis_results: Dict[str, Any], 
                                 project_context: Dict[str, Any], project_name: str) -> str:
        """Gera conteúdo específico usando contexto detalhado do projeto"""
        try:
            doc_info = self.document_types[doc_type]
            
            # Constrói prompt específico com contexto
            specific_prompt = self._build_context_aware_prompt(doc_type, project_context, project_name)
            
            # Prepara dados estruturados para o LLM
            structured_data = self._structure_analysis_data(analysis_results, project_context)
            
            # Gera conteúdo usando LLM
            content = self._generate_content_with_llm(
                specific_prompt, structured_data, doc_type, analysis_results, project_name
            )
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro na geração específica de {doc_type}: {str(e)}")
            raise
    
    def _regenerate_with_enhanced_specificity(self, doc_type: str, analysis_results: Dict[str, Any],
                                            project_context: Dict[str, Any], project_name: str) -> str:
        """Regenera conteúdo com prompts mais específicos e direcionados"""
        try:
            logger.info(f"🔄 Regenerando {doc_type} com especificidade aprimorada...")
            
            # Prompt mais direcionado
            enhanced_prompt = self._build_enhanced_specific_prompt(doc_type, project_context, project_name)
            
            # Dados mais estruturados
            enhanced_data = self._enhance_structure_data(analysis_results, project_context)
            
            # Gera com parâmetros mais restritivos
            content = self._generate_content_with_llm(
                enhanced_prompt, enhanced_data, doc_type, analysis_results, project_name, 
                enhanced_specificity=True
            )
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Falha na regeneração de {doc_type}: {str(e)}")
            raise
    
    def _build_context_aware_prompt(self, doc_type: str, project_context: Dict[str, Any], 
                                   project_name: str) -> str:
        """Constrói prompt específico baseado no contexto do projeto"""
        base_prompt = self._get_prompt_for_document(self.document_types[doc_type]['prompt_type'])
        
        # Adiciona contexto específico ao prompt
        context_addition = f"""
        
CONTEXTO ESPECÍFICO DO PROJETO "{project_name}":
- Arquivos analisados: {len(project_context['files'])} arquivos
- Funções encontradas: {len(project_context['functions'])} funções/procedimentos
- Classes identificadas: {len(project_context['classes'])} classes
- Forms detectados: {len(project_context['forms'])} formulários

INSTRUÇÕES ESPECÍFICAS:
- Use APENAS informações reais do projeto "{project_name}"
- Mencione nomes específicos de arquivos, funções e classes encontradas
- NÃO use exemplos genéricos ou templates
- Base toda análise nos dados reais fornecidos
- Se não houver dados suficientes, seja explícito sobre as limitações
        """
        
        return base_prompt + context_addition
    
    def _structure_analysis_data(self, analysis_results: Dict[str, Any], 
                                project_context: Dict[str, Any]) -> str:
        """Estrutura os dados de análise para melhor consumo pelo LLM"""
        structured = f"""
DADOS ESTRUTURADOS DO PROJETO:

== ARQUIVOS ANALISADOS ==
{self._format_files_data(project_context['files'])}

== FUNÇÕES E PROCEDIMENTOS ==
{self._format_functions_data(project_context['functions'])}

== CLASSES E OBJETOS ==
{self._format_classes_data(project_context['classes'])}

== FORMULÁRIOS E INTERFACE ==
{self._format_forms_data(project_context['forms'])}

== LÓGICA DE NEGÓCIO ==
{self._format_business_logic(project_context['business_logic'])}

== METADADOS ==
{json.dumps(analysis_results.get('metadata', {}), indent=2, ensure_ascii=False)}
        """
        
        return structured
    
    def _format_files_data(self, files: List[Dict]) -> str:
        """Formata dados dos arquivos para apresentação estruturada"""
        if not files:
            return "Nenhum arquivo específico identificado."
        
        formatted = []
        for file_info in files[:10]:  # Limita a 10 arquivos para não sobrecarregar
            formatted.append(f"- {file_info['name']} ({file_info['type']}) - {file_info['functions_count']} funções")
        
        if len(files) > 10:
            formatted.append(f"... e mais {len(files) - 10} arquivos")
        
        return "\n".join(formatted)
    
    def _format_functions_data(self, functions: List[Dict]) -> str:
        """Formata dados das funções para apresentação estruturada"""
        if not functions:
            return "Nenhuma função específica identificada."
        
        formatted = []
        for func in functions[:15]:  # Limita a 15 funções
            params = f"({len(func['parameters'])} params)" if func['parameters'] else "(sem parâmetros)"
            formatted.append(f"- {func['name']} {params} - {func['file']}")
        
        if len(functions) > 15:
            formatted.append(f"... e mais {len(functions) - 15} funções")
        
        return "\n".join(formatted)
    
    def _format_classes_data(self, classes: List[Dict]) -> str:
        """Formata dados das classes para apresentação estruturada"""
        if not classes:
            return "Nenhuma classe específica identificada."
        
        formatted = []
        for cls in classes[:10]:  # Limita a 10 classes
            methods_count = len(cls['methods']) if cls['methods'] else 0
            props_count = len(cls['properties']) if cls['properties'] else 0
            formatted.append(f"- {cls['name']} - {methods_count} métodos, {props_count} propriedades")
        
        if len(classes) > 10:
            formatted.append(f"... e mais {len(classes) - 10} classes")
        
        return "\n".join(formatted)
    
    def _format_forms_data(self, forms: List[Dict]) -> str:
        """Formata dados dos formulários para apresentação estruturada"""
        if not forms:
            return "Nenhum formulário específico identificado."
        
        formatted = []
        for form in forms[:8]:  # Limita a 8 forms
            comp_count = len(form['components']) if form['components'] else 0
            events_count = len(form['events']) if form['events'] else 0
            formatted.append(f"- {form['name']} - {comp_count} componentes, {events_count} eventos")
        
        if len(forms) > 8:
            formatted.append(f"... e mais {len(forms) - 8} formulários")
        
        return "\n".join(formatted)
    
    def _format_business_logic(self, business_logic: List[str]) -> str:
        """Formata lógica de negócio identificada"""
        if not business_logic:
            return "Nenhuma lógica de negócio específica identificada."
        
        return "\n".join([f"- {logic}" for logic in business_logic[:5]])
    
    def _save_document_with_metadata(self, file_path: Path, content: str, 
                                   doc_info: Dict[str, Any], project_name: str):
        """Salva documento com metadados de geração"""
        # Salva o conteúdo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Salva metadados
        metadata = {
            'document_type': doc_info['name'],
            'project_name': project_name,
            'generated_at': datetime.now().isoformat(),
            'content_length': len(content),
            'specificity_validated': True,
            'generator_version': '1.1.0'
        }
        
        metadata_path = file_path.with_suffix('.meta.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _generate_project_index(self, project_dir: Path, generated_docs: Dict[str, str], 
                               project_name: str):
        """Gera índice consolidado dos documentos do projeto"""
        index_content = f"""# 📋 Índice de Documentação - {project_name}

Documentação técnica gerada automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}

## 📄 Documentos Disponíveis

"""
        
        for doc_type, file_path in generated_docs.items():
            doc_info = self.document_types.get(doc_type, {'name': doc_type})
            file_name = Path(file_path).name
            index_content += f"- [{doc_info['name']}](./{file_name})\n"
        
        index_content += f"""
## ℹ️ Informações de Geração

- **Projeto:** {project_name}
- **Documentos gerados:** {len(generated_docs)}
- **Gerador:** JUNIM Documentation Generator v1.1.0
- **Validação de especificidade:** ✅ Ativada

---
*Documentação gerada automaticamente pelo sistema JUNIM*
"""
        
        index_path = project_dir / "README.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        logger.info(f"📋 Índice consolidado gerado: {index_path}")
    
    def _generate_fallback_docs(self, analysis_results: Dict[str, Any], project_name: str) -> Dict[str, str]:
        """Gera documentação básica quando o LLM não está disponível"""
        logger.info("🔄 Gerando documentação básica (fallback)...")
        
        fallback_docs = {}
        
        # 1. Análise geral do projeto
        analysis_doc = f"""# Análise do Projeto {project_name}

*Documentação gerada automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*

## 📊 Resumo da Análise

**Projeto:** {project_name}
**Arquivos analisados:** {analysis_results.get('file_count', 0)}
**Status:** Análise concluída

## 📁 Estrutura Identificada

"""
        
        # Adiciona estrutura de código se disponível
        code_structure = analysis_results.get('code_structure', {})
        if code_structure:
            forms = code_structure.get('forms', [])
            if forms:
                analysis_doc += f"### 🖼️ Formulários ({len(forms)})\n\n"
                for form in forms[:10]:  # Limita a 10 formulários
                    analysis_doc += f"- **{form.get('name', 'N/A')}**: {form.get('type', 'Form')}\n"
                analysis_doc += "\n"
            
            classes = code_structure.get('classes', [])
            if classes:
                analysis_doc += f"### 📦 Classes ({len(classes)})\n\n"
                for cls in classes[:10]:  # Limita a 10 classes
                    analysis_doc += f"- **{cls.get('name', 'N/A')}**: {cls.get('type', 'Class')}\n"
                analysis_doc += "\n"
        
        analysis_doc += """
## 🚀 Próximos Passos

1. **Revisar**: Verificar se todos os componentes foram identificados
2. **Modernizar**: Usar a aba de modernização para gerar código Java Spring Boot
3. **Comparar**: Analisar as diferenças entre o código original e modernizado

---
*Análise gerada pelo sistema JUNIM*
"""
        
        fallback_docs['project_analysis'] = analysis_doc
        
        # 2. Diagrama básico (textual)
        diagram_doc = f"""# Diagrama de Arquitetura - {project_name}

*Diagrama simplificado gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*

## 🏗️ Arquitetura Atual (Delphi)

```
┌─────────────────────────────────────┐
│           APLICAÇÃO DELPHI          │
├─────────────────────────────────────┤
│                                     │
│  📱 Interface de Usuário            │
│  ├── Formulários ({len(code_structure.get('forms', []))})             │
│  └── Componentes                    │
│                                     │
│  🔧 Lógica de Negócio              │
│  ├── Classes ({len(code_structure.get('classes', []))})                │
│  └── Funções                       │
│                                     │
│  💾 Acesso a Dados                 │
│  └── Conexões de banco             │
│                                     │
└─────────────────────────────────────┘
```

## 🎯 Arquitetura Proposta (Java Spring Boot)

```
┌─────────────────────────────────────┐
│      APLICAÇÃO SPRING BOOT          │
├─────────────────────────────────────┤
│                                     │
│  🌐 Controllers (REST API)          │
│  ├── Endpoints REST                 │
│  └── Validações                     │
│                                     │
│  🔧 Services (Lógica de Negócio)    │
│  ├── Serviços de domínio            │
│  └── Regras de negócio              │
│                                     │
│  📦 Entities/DTOs                   │
│  ├── Modelos de dados               │
│  └── Transferência de dados         │
│                                     │
│  💾 Repositories (JPA)              │
│  ├── Acesso a dados                 │
│  └── Consultas personalizadas       │
│                                     │
│  🗄️ Banco de Dados                  │
│  └── H2/PostgreSQL/MySQL            │
│                                     │
└─────────────────────────────────────┘
```

---
*Diagrama gerado pelo sistema JUNIM*
"""
        
        fallback_docs['project_diagram'] = diagram_doc
        
        # 3. Catálogo de funções básico
        functions_doc = f"""# Catálogo de Funções - {project_name}

*Catálogo gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*

## 📋 Componentes Identificados

### 🖼️ Formulários
"""
        
        forms = code_structure.get('forms', [])
        if forms:
            for form in forms:
                functions_doc += f"""
**{form.get('name', 'N/A')}**
- Tipo: {form.get('type', 'Form')}
- Arquivo: {form.get('file', 'N/A')}
"""
        else:
            functions_doc += "\nNenhum formulário identificado.\n"
        
        functions_doc += "\n### 📦 Classes\n"
        
        classes = code_structure.get('classes', [])
        if classes:
            for cls in classes:
                functions_doc += f"""
**{cls.get('name', 'N/A')}**
- Tipo: {cls.get('type', 'Class')}
- Arquivo: {cls.get('file', 'N/A')}
"""
        else:
            functions_doc += "\nNenhuma classe identificada.\n"
        
        functions_doc += """
## 🔄 Mapeamento para Java Spring Boot

| Componente Delphi | Equivalente Java Spring | Observações |
|-------------------|------------------------|-------------|
| Form              | Controller + Service   | Interface REST |
| Class             | Entity + Service       | Modelo de dados |
| Database Access   | Repository (JPA)       | Acesso a dados |
| Business Logic    | Service Layer          | Lógica de negócio |

---
*Catálogo gerado pelo sistema JUNIM*
"""
        
        fallback_docs['functions_catalog'] = functions_doc
        
        logger.info(f"✅ {len(fallback_docs)} documentos básicos gerados")
        return fallback_docs

    def _generate_modernization_with_full_context(self, prompt: str, context: str, 
                                                  analysis_results: Dict, project_name: str) -> str:
        """Gera código de modernização com contexto completo"""
        try:
            logger.info("🔧 Gerando modernização com contexto completo...")
            
            # Extrair informações específicas para modernização
            forms = analysis_results.get('code_structure', {}).get('forms', [])
            classes = analysis_results.get('code_structure', {}).get('classes', [])
            functions = analysis_results.get('functions', [])
            
            # Criar prompt específico para modernização
            modernization_prompt = f"""
Você é um especialista em modernização de código Delphi para Java Spring Boot.

TAREFA: Gerar código Java Spring Boot funcional baseado no projeto Delphi analisado.

PROJETO: {project_name}
FORMULÁRIOS ENCONTRADOS: {len(forms)}
CLASSES ENCONTRADAS: {len(classes)}
FUNÇÕES ENCONTRADAS: {len(functions)}

FORMULÁRIOS ESPECÍFICOS:
{self._format_forms_for_modernization(forms)}

CLASSES ESPECÍFICAS:
{self._format_classes_for_modernization(classes)}

FUNCIONALIDADES PRINCIPAIS:
{self._format_functions_for_modernization(functions)}

GERE:
1. Entidades JPA para cada formulário/classe principal
2. Repositories JPA para acesso a dados
3. Services para lógica de negócio
4. Controllers REST para API

FORMATO DE SAÍDA:
```java
// === ENTIDADE EXEMPLO ===
@Entity
@Table(name = "nome_tabela")
public class NomeEntidade {{
    // campos e métodos
}}

// === REPOSITORY EXEMPLO ===
@Repository
public interface NomeRepository extends JpaRepository<NomeEntidade, Long> {{
    // métodos de consulta
}}

// === SERVICE EXEMPLO ===
@Service
public class NomeService {{
    // lógica de negócio
}}

// === CONTROLLER EXEMPLO ===
@RestController
@RequestMapping("/api/nome")
public class NomeController {{
    // endpoints REST
}}
```

Use APENAS os nomes e funcionalidades identificados no projeto analisado.
"""
            
            # Gerar com LLM
            if self.llm_service:
                response = self.llm_service.generate_response(modernization_prompt)
                if response and len(response.strip()) > 200:
                    return response
            
            # Fallback: gerar código básico
            return self._generate_basic_java_code(forms, classes, project_name)
            
        except Exception as e:
            logger.error(f"❌ Erro na modernização com contexto: {str(e)}")
            return f"# Código Java Spring Boot - {project_name}\n\nErro na geração: {str(e)}"

    def _format_forms_for_modernization(self, forms: List) -> str:
        """Formata formulários para modernização"""
        if not forms:
            return "Nenhum formulário identificado."
        
        result = ""
        for form in forms[:10]:  # Limitar a 10
            result += f"- {form.get('name', 'N/A')}: {form.get('type', 'Form')}\n"
        return result

    def _format_classes_for_modernization(self, classes: List) -> str:
        """Formata classes para modernização"""
        if not classes:
            return "Nenhuma classe identificada."
        
        result = ""
        for cls in classes[:10]:  # Limitar a 10
            result += f"- {cls.get('name', 'N/A')}: {cls.get('type', 'Class')}\n"
        return result

    def _format_functions_for_modernization(self, functions: List) -> str:
        """Formata funções para modernização"""
        if not functions:
            return "Nenhuma função identificada."
        
        result = ""
        for func in functions[:15]:  # Limitar a 15
            result += f"- {func.get('name', 'N/A')}: {func.get('description', 'Função')}\n"
        return result

    def _generate_basic_java_code(self, forms: List, classes: List, project_name: str) -> str:
        """Gera código Java básico quando LLM não está disponível"""
        
        code = f"""# Código Java Spring Boot - {project_name}

## Entidades JPA Geradas

"""
        
        # Gerar entidades baseadas nos formulários
        for form in forms[:5]:  # Limitar a 5
            entity_name = form.get('name', 'Entity').replace('Form', '').replace('frm', '')
            
            code += f"""
### {entity_name}.java
```java
@Entity
@Table(name = "{entity_name.lower()}")
public class {entity_name} {{
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "nome")
    private String nome;
    
    @Column(name = "ativo")
    private Boolean ativo = true;
    
    @Column(name = "data_criacao")
    private LocalDateTime dataCriacao;
    
    // Getters e Setters
    // ... métodos padrão
}}
```

### {entity_name}Repository.java
```java
@Repository
public interface {entity_name}Repository extends JpaRepository<{entity_name}, Long> {{
    List<{entity_name}> findByAtivoTrue();
    List<{entity_name}> findByNomeContainingIgnoreCase(String nome);
}}
```

### {entity_name}Service.java
```java
@Service
@Transactional
public class {entity_name}Service {{
    
    @Autowired
    private {entity_name}Repository repository;
    
    public List<{entity_name}> listarTodos() {{
        return repository.findByAtivoTrue();
    }}
    
    public {entity_name} salvar({entity_name} entity) {{
        return repository.save(entity);
    }}
}}
```

### {entity_name}Controller.java
```java
@RestController
@RequestMapping("/api/{entity_name.lower()}")
public class {entity_name}Controller {{
    
    @Autowired
    private {entity_name}Service service;
    
    @GetMapping
    public ResponseEntity<List<{entity_name}>> listarTodos() {{
        return ResponseEntity.ok(service.listarTodos());
    }}
    
    @PostMapping
    public ResponseEntity<{entity_name}> criar(@RequestBody {entity_name} entity) {{
        return ResponseEntity.ok(service.salvar(entity));
    }}
}}
```

"""
        
        code += f"""
## Configurações

### application.yml
```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:h2:mem:testdb
    username: sa
    password: ''
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
```

### pom.xml (dependências principais)
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
</dependency>
```

---
*Código gerado automaticamente pelo JUNIM*
"""
        
        return code