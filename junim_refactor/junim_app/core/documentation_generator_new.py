"""
Gerador de documentação técnica completa para projetos Delphi
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentationGenerator:
    """Gerador de documentação técnica abrangente"""
    
    def __init__(self, llm_service=None, prompt_manager=None):
        self.llm_service = llm_service
        self.prompt_manager = prompt_manager
        self.docs_dir = Path("generated_docs")
        self.docs_dir.mkdir(exist_ok=True)
        
        # Tipos de documentos que serão gerados
        self.document_types = {
            'backend_analysis': {
                'name': '🔧 Análise de Backend',
                'prompt_type': 'analysis',
                'filename': 'backend_analysis.md'
            },
            'functionality_mapping': {
                'name': '🔗 Mapeamento de Funcionalidades',
                'prompt_type': 'functionality_mapping',
                'filename': 'functionality_mapping.md'
            },
            'requirements_analysis': {
                'name': '📋 Análise de Requisitos',
                'prompt_type': 'requirements',
                'filename': 'requirements_analysis.md'
            },
            'system_characteristics': {
                'name': '⚙️ Características do Sistema',
                'prompt_type': 'characteristics',
                'filename': 'system_characteristics.md'
            },
            'execution_flows': {
                'name': '🔄 Fluxos de Execução',
                'prompt_type': 'execution_flows',
                'filename': 'execution_flows.md'
            },
            'data_flows': {
                'name': '📊 Fluxos de Dados',
                'prompt_type': 'data_flows',
                'filename': 'data_flows.md'
            },
            'correlations': {
                'name': '🔗 Correlações Delphi→Java',
                'prompt_type': 'correlations',
                'filename': 'correlations.md'
            },
            'quality_metrics': {
                'name': '📈 Métricas de Qualidade',
                'prompt_type': 'quality_metrics',
                'filename': 'quality_metrics.md'
            },
            'testing_strategy': {
                'name': '🧪 Estratégia de Testes',
                'prompt_type': 'testing',
                'filename': 'testing_strategy.md'
            }
        }
    
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
            
            # Gera índice da documentação
            self._generate_documentation_index(generated_docs, project_dir, project_name)
            
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
            
            # Gera conteúdo
            content = self._generate_content(prompt, context)
            
            if not content:
                return None
            
            # Salva documento
            doc_path = project_dir / doc_config['filename']
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return doc_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar documento {doc_key}: {str(e)}")
            return None
    
    def _get_prompt_for_document(self, prompt_type: str) -> str:
        """Obtém prompt específico para tipo de documento"""
        if not self.prompt_manager:
            return self._get_fallback_prompt(prompt_type)
        
        try:
            # Mapeia tipos de prompt para métodos do PromptManager
            prompt_methods = {
                'analysis': 'get_backend_analysis_prompt',
                'functionality_mapping': 'get_functionality_mapping_prompt',
                'requirements': 'get_requirements_analysis_prompt',
                'characteristics': 'get_system_characteristics_prompt',
                'execution_flows': 'get_execution_flows_prompt',
                'data_flows': 'get_data_flows_prompt',
                'correlations': 'get_correlations_prompt',
                'quality_metrics': 'get_quality_metrics_prompt',
                'testing': 'get_testing_prompt'
            }
            
            method_name = prompt_methods.get(prompt_type)
            if method_name and hasattr(self.prompt_manager, method_name):
                method = getattr(self.prompt_manager, method_name)
                return method()
            else:
                return self._get_fallback_prompt(prompt_type)
                
        except Exception as e:
            logger.warning(f"Erro ao obter prompt especializado: {str(e)}")
            return self._get_fallback_prompt(prompt_type)
    
    def _get_fallback_prompt(self, prompt_type: str) -> str:
        """Prompts de fallback para cada tipo de documento"""
        prompts = {
            'analysis': """
Analise o projeto Delphi fornecido e gere uma documentação técnica detalhada focada no backend.

Considere:
- Estrutura do projeto
- Funcionalidades principais
- Lógica de negócio
- Integração com banco de dados
- Arquitetura geral

Forneça insights técnicos precisos para modernização para Java Spring Boot.
            """,
            'functionality_mapping': """
Mapeie todas as funcionalidades do sistema Delphi fornecido.

Para cada funcionalidade identifique:
- Nome e propósito
- Entrada e saída de dados
- Regras de negócio
- Dependências
- Equivalente em Java Spring Boot

Foque em funcionalidades de backend.
            """,
            'requirements': """
Extraia e documente todos os requisitos do sistema baseado no código Delphi.

Inclua:
- Requisitos funcionais
- Requisitos não funcionais
- Regras de negócio
- Integrações necessárias
- Validações e constraints
            """,
            'characteristics': """
Analise as características técnicas do sistema Delphi.

Documente:
- Arquitetura atual
- Padrões utilizados
- Complexidade técnica
- Pontos fortes e fracos
- Métricas de qualidade
            """,
            'execution_flows': """
Documente os fluxos de execução do sistema.

Inclua:
- Fluxo de inicialização
- Fluxos de trabalho principais
- Tratamento de erros
- Sequências de finalização
            """,
            'data_flows': """
Mapeie todos os fluxos de dados do sistema.

Documente:
- Fluxos de banco de dados
- Fluxos entre módulos
- Fluxos de entrada/saída
- Transformações de dados
            """,
            'correlations': """
Gere correlações entre componentes Delphi e equivalentes Java Spring Boot.

Mapeie:
- Classes Delphi → Classes Java
- Formulários → Controllers REST
- Módulos → Services
- Acesso a dados → Repositories
            """,
            'quality_metrics': """
Avalie métricas de qualidade do código Delphi.

Analise:
- Complexidade ciclomática
- Cobertura de testes
- Manutenibilidade
- Padrões de código
- Dívida técnica
            """,
            'testing': """
Desenvolva estratégia de testes para o sistema modernizado.

Inclua:
- Testes unitários
- Testes de integração
- Testes de API
- Cenários de teste
- Cobertura esperada
            """
        }
        
        return prompts.get(prompt_type, "Analise o projeto fornecido e gere documentação técnica detalhada.")
    
    def _prepare_context(self, analysis_results: Dict[str, Any], project_name: str, doc_key: str) -> str:
        """Prepara contexto para geração de documento"""
        context = f"""
PROJETO: {project_name}
DOCUMENTO: {doc_key}

ANÁLISE DO PROJETO:
{json.dumps(analysis_results, indent=2, ensure_ascii=False)}

INSTRUÇÕES:
- Gere documentação técnica detalhada e específica
- Foque em aspectos de backend
- Use markdown para formatação
- Seja preciso e objetivo
- Inclua exemplos quando necessário
        """
        return context
    
    def _generate_content(self, prompt: str, context: str) -> str:
        """Gera conteúdo usando LLM ou fallback"""
        if self.llm_service:
            try:
                full_prompt = f"{prompt}\n\n{context}"
                content = self.llm_service.generate_response(full_prompt)
                return content if content else self._generate_fallback_content(context)
            except Exception as e:
                logger.warning(f"Erro ao gerar conteúdo com LLM: {str(e)}")
                return self._generate_fallback_content(context)
        else:
            return self._generate_fallback_content(context)
    
    def _generate_fallback_content(self, context: str) -> str:
        """Gera conteúdo de fallback quando LLM não está disponível"""
        return f"""
# Documentação Técnica

## Contexto
{context}

## Análise
Esta documentação foi gerada automaticamente baseada na análise do projeto.

## Próximos Passos
- Revisar e ajustar documentação
- Validar informações técnicas
- Complementar com detalhes específicos

*Nota: Este documento foi gerado automaticamente e deve ser revisado.*
        """
    
    def _generate_documentation_index(self, generated_docs: Dict[str, str], 
                                    project_dir: Path, project_name: str):
        """Gera índice da documentação"""
        try:
            index_content = f"""# Documentação Técnica - {project_name}

## Índice de Documentos

"""
            
            for doc_key, doc_path in generated_docs.items():
                doc_config = self.document_types.get(doc_key, {})
                doc_name = doc_config.get('name', doc_key)
                filename = Path(doc_path).name
                
                index_content += f"- [{doc_name}](./{filename})\n"
            
            index_content += f"""

## Informações de Geração

- **Data**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
- **Documentos**: {len(generated_docs)}
- **Projeto**: {project_name}

## Como Usar

1. Comece pelo **Resumo Executivo** para visão geral
2. Consulte **Análise de Backend** para detalhes técnicos
3. Use **Mapeamento de Funcionalidades** para entender recursos
4. Revise **Fluxos** para compreender operações
5. Consulte **Correlações** para modernização

---
*Documentação gerada automaticamente pelo JUNIM*
"""
            
            index_path = project_dir / "README.md"
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
                
            logger.info("✅ Índice da documentação gerado")
            
        except Exception as e:
            logger.error(f"Erro ao gerar índice: {str(e)}")
    
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
            new_content = self._generate_content(feedback_prompt, context)
            
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
    
    def get_document_content(self, doc_key: str, project_name: str = "Projeto") -> str:
        """Obtém conteúdo de um documento específico"""
        try:
            doc_config = self.document_types.get(doc_key, {})
            filename = doc_config.get('filename', f'{doc_key}.md')
            
            project_dir = self.docs_dir / self._sanitize_filename(project_name)
            doc_path = project_dir / filename
            
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Erro ao ler documento {doc_key}: {str(e)}")
            return ""
    
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
