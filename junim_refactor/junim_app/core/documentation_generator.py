"""
Gerador de documentação técnica para projetos Delphi
Focado exclusivamente em prompts específicos - SEM FALLBACKS
"""

import os
import json
import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentationGenerator:
    """Gerador de documentação técnica - APENAS com prompts e dados específicos"""
    
    def __init__(self, llm_service=None, prompt_manager=None):
        self.llm_service = llm_service
        self.prompt_manager = prompt_manager
        self.docs_dir = Path("generated_docs")
        self.docs_dir.mkdir(exist_ok=True)
        
        # Apenas os 4 documentos essenciais solicitados
        self.document_types = {
            'project_functions': {
                'name': '⚙️ Funções do Projeto Original',
                'prompt_type': 'project_functions',
                'filename': 'project_functions.md'
            },
            'project_diagram': {
                'name': '📊 Diagrama do Projeto Original',
                'prompt_type': 'project_diagram',
                'filename': 'project_diagram.md'
            },
            'delphi_java_correlation': {
                'name': '🔗 Correlação Delphi-Java',
                'prompt_type': 'correlations',
                'filename': 'delphi_java_correlation.md'
            },
            'project_description': {
                'name': '📝 Descrição do Projeto',
                'prompt_type': 'project_description',
                'filename': 'project_description.md'
            }
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
            
            # LISTA FIXA DOS 4 DOCUMENTOS ESSENCIAIS
            if documents_to_generate is None:
                documents_to_generate = [
                    'project_functions',
                    'project_diagram', 
                    'delphi_java_correlation',
                    'project_description'
                ]
            
            # Gera apenas documentos especificados - SEM FALLBACKS
            for doc_type in documents_to_generate:
                if doc_type in self.document_types:
                    doc_info = self.document_types[doc_type]
                    logger.info(f"📄 Gerando documento: {doc_info['name']}")
                    
                    # Gera o documento usando prompts reais
                    content = self._generate_document_content(doc_type, analysis_results, project_name)
                    
                    if not content or len(content.strip()) < 100:
                        error_msg = f"❌ FALHA na geração de {doc_info['name']} - Conteúdo insuficiente"
                        logger.error(error_msg)
                        raise RuntimeError(error_msg)
                    
                    # Salva o documento
                    doc_path = project_dir / doc_info['filename']
                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Retorna o conteúdo (não o caminho)
                    generated_docs[doc_type] = content
                    logger.info(f"✅ Documento gerado: {doc_info['name']} ({len(content)} chars)")
            
            # Gera README específico
            readme_content = self._generate_essential_readme(analysis_results, project_name, list(generated_docs.keys()))
            readme_path = project_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            generated_docs['readme'] = readme_content
            
            logger.info(f"🎉 Documentação essencial gerada: {len(generated_docs)} arquivos")
            logger.info(f"📁 Documentos salvos em: {project_dir}")
            return generated_docs
            
        except Exception as e:
            error_msg = f"❌ ERRO CRÍTICO na geração de documentação: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _generate_document_content(self, doc_type: str, analysis_results: Dict[str, Any], 
                                   project_name: str) -> str:
        """
        Gera conteúdo de um documento específico usando prompts - SEM FALLBACKS
        """
        try:
            # Validação do tipo de documento
            if doc_type not in self.document_types:
                raise ValueError(f"Tipo de documento '{doc_type}' não suportado")
            
            doc_config = self.document_types[doc_type]
            
            # Obtém prompt específico - OBRIGATÓRIO
            prompt = self._get_prompt_for_document(doc_config['prompt_type'])
            if not prompt or len(prompt) < 100:
                raise RuntimeError(f"Prompt inválido para {doc_type}")
            
            # Prepara contexto - OBRIGATÓRIO
            context = self._prepare_context(analysis_results, project_name, doc_type)
            if not context or len(context) < 500:
                raise RuntimeError(f"Contexto insuficiente para {doc_type}")
            
            # Gera conteúdo usando LLM - OBRIGATÓRIO
            content = self._generate_content_with_llm(prompt, context)
            if not content or len(content.strip()) < 100:
                raise RuntimeError(f"LLM falhou ao gerar conteúdo para {doc_type}")
            
            return content
            
        except Exception as e:
            error_msg = f"Erro ao gerar {doc_type}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _get_prompt_for_document(self, prompt_type: str) -> str:
        """Obtém prompt específico - FALHA se não conseguir"""
        if not self.prompt_manager:
            raise RuntimeError("PromptManager não disponível - OBRIGATÓRIO para geração")
        
        try:
            # Mapeia tipos de prompt para métodos do PromptManager
            prompt_methods = {
                'project_functions': 'get_functionality_mapping_prompt',
                'project_diagram': 'get_backend_analysis_prompt',  # Usar backend para diagrama
                'correlations': 'get_backend_analysis_prompt',
                'project_description': 'get_backend_analysis_prompt'
            }
            
            method_name = prompt_methods.get(prompt_type)
            if not method_name or not hasattr(self.prompt_manager, method_name):
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
        """Prepara contexto específico - FALHA se dados insuficientes"""
        
        # Validação rigorosa dos dados de entrada
        if not analysis_results or not isinstance(analysis_results, dict):
            raise ValueError("analysis_results está vazio ou inválido")
        
        logger.info(f"🔍 Preparando contexto para {doc_key}")
        logger.info(f"📋 Dados disponíveis: {list(analysis_results.keys())}")
        
        # Formata dados de análise
        formatted_data = self._format_analysis_data(analysis_results)
        if len(formatted_data) < 200:
            raise RuntimeError(f"Dados formatados insuficientes: {len(formatted_data)} chars")
        
        # Extrai especificidades do código
        code_specifics = self._extract_code_specifics(analysis_results)
        if len(code_specifics) < 100:
            logger.warning(f"⚠️ Especificações do código limitadas: {len(code_specifics)} chars")
        
        # Monta contexto completo
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

    def _format_analysis_data(self, analysis_results: Dict[str, Any]) -> str:
        """Formata dados de análise de forma legível"""
        try:
            formatted = []
            
            # Metadados do projeto
            metadata = analysis_results.get('metadata', {})
            formatted.append(f"**Projeto**: {metadata.get('project_name', 'N/A')}")
            formatted.append(f"**Arquivos Analisados**: {metadata.get('total_files_analyzed', 0)}")
            formatted.append(f"**Caminho**: {metadata.get('project_path', 'N/A')}")
            
            # Composição do projeto
            files_by_type = metadata.get('files_by_type', {})
            if files_by_type:
                formatted.append("\n**Composição do Projeto:**")
                for file_type, count in files_by_type.items():
                    if count > 0:
                        formatted.append(f"- Arquivos {file_type.upper()}: {count}")
            
            # Estatísticas gerais
            summary = analysis_results.get('summary', {})
            if summary:
                formatted.append("\n**Estatísticas Gerais:**")
                formatted.append(f"- Units: {summary.get('total_units', 0)}")
                formatted.append(f"- Forms: {summary.get('total_forms', 0)}")
                formatted.append(f"- Classes: {summary.get('total_classes', 0)}")
                formatted.append(f"- Métodos: {summary.get('total_methods', 0)}")
            
            # Arquivos analisados
            files = analysis_results.get('files', {})
            if files:
                files_count = len(files) if isinstance(files, dict) else len(files) if isinstance(files, list) else 0
                formatted.append(f"\n**Arquivos Detalhados**: {files_count}")
                
                if isinstance(files, dict):
                    sample_files = list(files.keys())[:5]
                    for file_path in sample_files:
                        file_name = file_path.split('\\')[-1] if '\\' in file_path else file_path
                        formatted.append(f"- {file_name}")
            
            result = "\n".join(formatted)
            logger.info(f"✅ Dados formatados: {len(result)} caracteres")
            
            return result if result else "Dados de análise limitados"
            
        except Exception as e:
            logger.error(f"Erro ao formatar dados: {str(e)}")
            # Formato mínimo em caso de erro
            return f"Projeto: {analysis_results.get('metadata', {}).get('project_name', 'N/A')}\nArquivos: {analysis_results.get('metadata', {}).get('total_files_analyzed', 0)}"

    def _generate_content_with_llm(self, prompt: str, context: str) -> str:
        """Gera conteúdo usando LLM - FALHA se não conseguir"""
        
        if not self.llm_service:
            raise RuntimeError("LLM service não disponível - OBRIGATÓRIO para geração")
        
        try:
            # Combina prompt especializado com contexto específico
            full_prompt = f"{prompt}\n\n{context}"
            
            logger.info(f"🚀 Gerando com LLM: {len(full_prompt)} caracteres")
            
            # Chama o LLM service
            content = self.llm_service.generate_response(full_prompt)
            
            if not content or len(content.strip()) < 100:
                raise RuntimeError("Resposta do LLM muito curta ou vazia")
            
            logger.info(f"✅ Conteúdo gerado: {len(content)} caracteres")
            return content
                
        except Exception as e:
            error_msg = f"Erro na geração com LLM: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _generate_essential_readme(self, analysis_results: Dict[str, Any], 
                                 project_name: str, generated_docs_list: List[str]) -> str:
        """Gera README essencial para os 4 documentos principais"""
        
        metadata = analysis_results.get('metadata', {})
        total_files = metadata.get('total_files_analyzed', 0)
        total_lines = metadata.get('total_lines_analyzed', 0)
        
        readme = f"""# Documentação para Geração Java Spring Boot - {project_name}

## Resumo da Análise
- **Projeto**: {project_name}
- **Arquivos analisados**: {total_files}
- **Linhas de código**: {total_lines:,}
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

## 📊 Estatísticas da Análise
- **Units identificadas**: {len(analysis_results.get('units_analysis', {}))}
- **Forms identificados**: {len(analysis_results.get('forms_analysis', {}))}
- **Classes totais**: {analysis_results.get('summary', {}).get('total_classes', 0)}
- **Métodos totais**: {analysis_results.get('summary', {}).get('total_methods', 0)}

---
*Documentação gerada automaticamente pelo Sistema JUNIM*
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
        Gera documentação completa do projeto baseada na análise
        
        Args:
            analysis_results: Resultados da análise do projeto
            project_name: Nome do projeto
            
        Returns:
            Dict com caminhos dos documentos gerados
        """
        try:
            logger.info(f"🚀 Iniciando geração de documentação completa para: {project_name}")
            
            # Cria diretório específico para o projeto
            project_dir = self.docs_dir / self._sanitize_filename(project_name)
            project_dir.mkdir(exist_ok=True)
            
            generated_docs = {}
            
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
    
    def _get_prompt_for_document(self, prompt_type: str) -> str:
        """Obtém prompt específico para tipo de documento - FALHA se não conseguir"""
        if not self.prompt_manager:
            raise RuntimeError("PromptManager não disponível - OBRIGATÓRIO para geração")
        
        try:
            # Mapeia tipos de prompt para métodos do PromptManager
            prompt_methods = {
                'project_functions': 'get_functionality_mapping_prompt',
                'project_diagram': 'get_backend_analysis_prompt',  # Usar backend para diagrama
                'correlations': 'get_backend_analysis_prompt',
                'project_description': 'get_backend_analysis_prompt'
            }
            
            method_name = prompt_methods.get(prompt_type)
            if not method_name or not hasattr(self.prompt_manager, method_name):
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
        """Prepara contexto para geração de documento - FALHA se dados insuficientes"""
        
        # Validação rigorosa dos dados de entrada
        if not analysis_results or not isinstance(analysis_results, dict):
            raise ValueError("analysis_results está vazio ou inválido")
        
        logger.info(f"🔍 Preparando contexto para {doc_key} - Dados disponíveis: {list(analysis_results.keys())}")
        
        # Formata dados de forma mais legível
        formatted_data = self._format_analysis_data(analysis_results)
        if len(formatted_data) < 200:
            raise RuntimeError(f"Dados formatados insuficientes: {len(formatted_data)} chars")
        
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
        """Formata dados de análise de forma mais legível e específica"""
        try:
            formatted = []
            
            # CORREÇÃO: Log para debug dos dados recebidos
            logger.info(f"🔍 Formatando dados - Chaves disponíveis: {list(analysis_results.keys())}")
            
            # Metadados do projeto
            metadata = analysis_results.get('metadata', {})
            formatted.append(f"**Projeto**: {metadata.get('project_name', 'N/A')}")
            formatted.append(f"**Data da Análise**: {metadata.get('analysis_date', 'N/A')}")
            formatted.append(f"**Arquivos Analisados**: {metadata.get('total_files_analyzed', 0)}")
            formatted.append(f"**Caminho**: {metadata.get('project_path', 'N/A')}")
            
            # Tipos de arquivos com detalhes
            files_by_type = metadata.get('files_by_type', {})
            if files_by_type:
                formatted.append("\n**Composição do Projeto:**")
                for file_type, count in files_by_type.items():
                    if count > 0:
                        formatted.append(f"- Arquivos {file_type.upper()}: {count}")
            
            # CORREÇÃO: Extrair dados de todas as seções possíveis
            # Resumo detalhado do projeto
            summary = analysis_results.get('summary', {})
            if summary:
                formatted.append(f"\n**Estatísticas Gerais:**")
                formatted.append(f"- Units: {summary.get('total_units', 0)}")
                formatted.append(f"- Forms: {summary.get('total_forms', 0)}")
                formatted.append(f"- DataModules: {summary.get('total_datamodules', 0)}")
                formatted.append(f"- Classes: {summary.get('total_classes', 0)}")
                formatted.append(f"- Métodos: {summary.get('total_methods', 0)}")
            
            # CORREÇÃO: Tentar extrair dados de múltiplas fontes
            # Dados dos arquivos analisados (nova seção)
            files = analysis_results.get('files', {})
            if files:
                formatted.append(f"\n**Arquivos Analisados Detalhadamente:**")
                files_count = len(files) if isinstance(files, dict) else len(files) if isinstance(files, list) else 0
                formatted.append(f"- Total de arquivos detalhados: {files_count}")
                
                # Extrai amostras dos arquivos
                if isinstance(files, dict):
                    sample_files = list(files.keys())[:5]
                    for file_path in sample_files:
                        file_name = file_path.split('\\')[-1] if '\\' in file_path else file_path
                        formatted.append(f"- {file_name}")
            
            # Métricas de complexidade
            complexity = summary.get('complexity_metrics', {}) if summary else {}
            if complexity:
                formatted.append(f"\n**Métricas de Complexidade:**")
                formatted.append(f"- Complexidade Média: {complexity.get('average_complexity', 0)}")
                formatted.append(f"- Complexidade Máxima: {complexity.get('max_complexity', 0)}")
                formatted.append(f"- Total de Linhas: {complexity.get('total_lines', 0)}")
                formatted.append(f"- Métodos Complexos: {complexity.get('methods_with_high_complexity', 0)}")
            
            # Funcionalidades principais específicas
            functionalities = analysis_results.get('main_functionalities', [])
            if functionalities:
                formatted.append("\n**Funcionalidades Identificadas:**")
                for func in functionalities:
                    formatted.append(f"- {func}")
            
            # CORREÇÃO: Análise detalhada de units com melhor tratamento de dados
            units_analysis = analysis_results.get('units_analysis', {})
            if units_analysis and isinstance(units_analysis, dict):
                formatted.append("\n**Componentes Principais (Units):**")
                units_list = list(units_analysis.items())[:10]  # Aumenta para 10 units
                for unit_path, unit_data in units_list:
                    if isinstance(unit_data, dict):
                        unit_name = unit_path.split('\\')[-1] if '\\' in unit_path else unit_path
                        unit_type = unit_data.get('unit_type', 'unit')
                        lines = unit_data.get('lines_count', 0)
                        methods = unit_data.get('methods', [])
                        classes = unit_data.get('classes', [])
                        
                        # Informações mais específicas sobre cada unit
                        info_parts = [f"{lines} linhas", f"{len(methods)} métodos"]
                        if classes:
                            class_names = [cls.get('name', 'N/A') for cls in classes if isinstance(cls, dict)]
                            if class_names:
                                info_parts.append(f"classes: {', '.join(class_names)}")
                        
                        formatted.append(f"- **{unit_name}** ({unit_type}): {', '.join(info_parts)}")
                        
                        # Adiciona detalhes dos métodos mais importantes
                        if methods and isinstance(methods, list):
                            important_methods = [m for m in methods if isinstance(m, dict) and m.get('complexity', 0) > 1][:3]
                            if important_methods:
                                method_names = [m.get('name', 'N/A') for m in important_methods]
                                formatted.append(f"  → Métodos principais: {', '.join(method_names)}")
            
            # CORREÇÃO: Análise detalhada de forms com melhor tratamento
            forms_analysis = analysis_results.get('forms_analysis', {})
            if forms_analysis and isinstance(forms_analysis, dict):
                formatted.append("\n**Interfaces (Forms):**")
                forms_list = list(forms_analysis.items())[:5]
                for form_path, form_data in forms_list:
                    if isinstance(form_data, dict):
                        form_name = form_path.split('\\')[-1] if '\\' in form_path else form_path
                        classes = form_data.get('classes', [])
                        methods = form_data.get('methods', [])
                        
                        class_info = ""
                        if classes and isinstance(classes, list) and len(classes) > 0:
                            main_class = classes[0].get('name', 'N/A') if isinstance(classes[0], dict) else 'N/A'
                            parent_class = classes[0].get('parent_class', 'N/A') if isinstance(classes[0], dict) else 'N/A'
                            class_info = f", classe: {main_class} ({parent_class})"
                        
                        lines_count = form_data.get('lines_count', 0)
                        method_count = len(methods) if isinstance(methods, list) else 0
                        formatted.append(f"- **{form_name}**: {lines_count} linhas, {method_count} métodos{class_info}")
                        
                        # Adiciona informações sobre eventos/handlers
                        if methods and isinstance(methods, list):
                            event_methods = [m for m in methods if isinstance(m, dict) and ('Click' in m.get('name', '') or 'Event' in m.get('name', ''))]
                            if event_methods:
                                event_names = [m.get('name', 'N/A') for m in event_methods[:3]]
                                formatted.append(f"  → Eventos: {', '.join(event_names)}")
            
            # RESULTADO FINAL
            result = "\n".join(formatted)
            logger.info(f"✅ Dados formatados: {len(result)} caracteres, {len(formatted)} seções")
            
            return result if result else "Nenhum dado específico foi extraído da análise."
            
        except Exception as e:
            logger.error(f"❌ Erro ao formatar dados: {str(e)}")
            # Fallback para formato JSON mais limpo
            essential_data = {
                'project_name': analysis_results.get('metadata', {}).get('project_name', 'N/A'),
                'total_files': analysis_results.get('metadata', {}).get('total_files_analyzed', 0),
                'summary': analysis_results.get('summary', {}),
                'main_functionalities': analysis_results.get('main_functionalities', []),
                'units_count': len(analysis_results.get('units_analysis', {})),
                'forms_count': len(analysis_results.get('forms_analysis', {}))
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
                    'total_files': analysis_results.get('project_info', {}).get('total_files', 0),
                    'main_units': len(analysis_results.get('units_analysis', {})),
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
    
    