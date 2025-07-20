"""
Pipeline principal de modernização Delphi para Java Spring
"""

import os
import tempfile
from typing import Dict, Any, Optional, Callable
import logging

from utils.file_handler import FileHandler
from core.delphi_parser import DelphiParser
from core.llm_service import LLMService
from core.java_builder import JavaBuilder

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernizationPipeline:
    """Pipeline orquestrador da modernização Delphi → Java Spring"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o pipeline de modernização
        
        Args:
            config: Configuração com chaves de API e modelos
        """
        self.config = config
        self.file_handler = FileHandler()
        self.delphi_parser = DelphiParser()
        self.llm_service = LLMService(config)
        self.java_builder = JavaBuilder()
        
        # Gerenciador de prompts especializado (opcional)
        self.prompt_manager = None
        
        # Estado do pipeline
        self.current_step = 0
        self.total_steps = 5
        self.delphi_structure = None
        self.rag_context = None
        self.generated_code = None
        self.java_project_path = None
    
    def set_prompt_manager(self, prompt_manager):
        """Define o gerenciador de prompts especializados"""
        self.prompt_manager = prompt_manager
        logger.info("✅ Prompt manager configurado para usar prompts especializados")
        
        # Recria o LLMService com o prompt_manager
        self.llm_service = LLMService(self.config, prompt_manager)
        logger.info("✅ LLMService recriado com prompt_manager")
        
        # Verifica se o prompt manager tem os métodos necessários
        essential_methods = [
            'get_spring_conversion_prompt',
            'get_backend_conversion_prompt',
            'get_analysis_prompt',
            'get_testing_prompt',
            'get_documentation_enhanced_prompt'
        ]
        
        available_methods = []
        for method_name in essential_methods:
            if hasattr(prompt_manager, method_name):
                available_methods.append(method_name)
                logger.info(f"✅ Prompt manager possui método {method_name}")
            else:
                logger.warning(f"⚠️ Prompt manager não possui método {method_name}")
        
        if available_methods:
            logger.info(f"Métodos disponíveis: {len(available_methods)}/{len(essential_methods)}")
        else:
            logger.warning("⚠️ Nenhum método essencial encontrado no prompt manager")
    
    def set_analysis_data(self, analysis_results, generated_docs):
        """Define dados da análise prévia para uso na modernização"""
        if analysis_results is None:
            logger.warning("analysis_results é None! Isso pode causar problemas na modernização.")
        else:
            logger.info(f"Dados de análise carregados: {len(analysis_results)} chaves")
        
        if generated_docs is None:
            logger.warning("generated_docs é None! Isso pode causar problemas na documentação.")
        else:
            logger.info(f"Documentação gerada carregada: {len(generated_docs)} chaves")
            
        self.analysis_results = analysis_results
        self.generated_docs = generated_docs
        logger.info("Dados de análise prévia carregados para modernização")
    
    def generate_documentation(self, analysis_results, prompt_type):
        """Gera documentação técnica baseada na análise"""
        try:
            logger.info(f"Gerando documentação do tipo: {prompt_type}")
            
            if not self.prompt_manager:
                raise ValueError("Prompt manager não foi configurado")
            
            # Mapeia tipos de prompt para métodos disponíveis
            prompt_methods = {
                'analysis': 'get_analysis_prompt',
                'functionality_mapping': 'get_functionality_mapping_prompt',
                'backend_analysis': 'get_backend_analysis_prompt',
                'backend_conversion': 'get_backend_conversion_prompt',
                'testing': 'get_testing_prompt',
                'mermaid_diagram': 'get_mermaid_diagram_prompt',
                'spring_conversion': 'get_spring_conversion_prompt',
                'documentation_enhanced': 'get_documentation_enhanced_prompt'
            }
            
            method_name = prompt_methods.get(prompt_type)
            if not method_name or not hasattr(self.prompt_manager, method_name):
                logger.warning(f"Método de prompt não encontrado para tipo: {prompt_type}")
                prompt = f"Gere documentação técnica para o tipo: {prompt_type}"
            else:
                method = getattr(self.prompt_manager, method_name)
                prompt = method()
            
            # Prepara contexto com resultados da análise
            context = f"Análise do projeto:\n{analysis_results}\n\n{prompt}"
            
            # Gera documentação usando o LLM
            documentation = self.llm_service.generate_response(context)
            
            logger.info(f"Documentação gerada com sucesso para tipo: {prompt_type}")
            return documentation
            
        except Exception as e:
            logger.error(f"Erro ao gerar documentação: {str(e)}")
            return f"Erro ao gerar documentação: {str(e)}"

    def run(self, 
            delphi_project_path: Optional[str] = None, 
            progress_callback: Optional[Callable] = None) -> str:
        """
        Executa o pipeline completo de modernização
        
        Args:
            delphi_project_path: Caminho para o arquivo ZIP do projeto Delphi (None se usar análise prévia)
            progress_callback: Função callback para atualizar progresso
            
        Returns:
            Caminho para o arquivo ZIP do projeto Java gerado
        """
        try:
            logger.info("=== INICIANDO PIPELINE DE MODERNIZAÇÃO ===")
            
            # Passo 1: Análise do Sistema Legado (se não houver análise prévia)
            if delphi_project_path:
                if progress_callback:
                    progress_callback(1, self.total_steps, "Analisando projeto Delphi...")
                
                self._step1_analyze_delphi_project(delphi_project_path)
            elif hasattr(self, 'analysis_results') and self.analysis_results:
                if progress_callback:
                    progress_callback(1, self.total_steps, "Usando análise prévia...")
                
                # Usa dados de análise prévia carregados
                logger.info("Usando dados de análise prévia carregados")
                self._use_previous_analysis()
            else:
                raise ValueError("Nenhum projeto Delphi fornecido nem análise prévia disponível")
            
            # Passo 2: Geração Aumentada por Recuperação (RAG)
            if progress_callback:
                progress_callback(2, self.total_steps, "Construindo contexto RAG...")
            
            self._step2_build_rag_context()
            
            # Passo 3: Interação com LLM e Geração de Código
            if progress_callback:
                progress_callback(3, self.total_steps, "Gerando código Java com IA...")
            
            self._step3_generate_java_code(progress_callback)
            
            # Passo 4: Construção e Pós-processamento do Projeto Java
            if progress_callback:
                progress_callback(4, self.total_steps, "Estruturando projeto Java...")
            
            self._step4_build_java_project(progress_callback)
            
            # Passo 5: Empacotamento
            if progress_callback:
                progress_callback(5, self.total_steps, "Empacotando projeto final...")
            
            result_path = self._step5_package_project()
            
            logger.info("=== PIPELINE CONCLUÍDO COM SUCESSO ===")
            return result_path
            
        except Exception as e:
            logger.error(f"Erro no pipeline: {str(e)}")
            self._cleanup()
            raise Exception(f"Falha na modernização: {str(e)}")
    
    def _step1_analyze_delphi_project(self, delphi_project_path: str):
        """Passo 1: Análise do Sistema Legado"""
        try:
            logger.info("PASSO 1: Análise do Sistema Legado")
            
            # Validação do caminho do projeto
            if delphi_project_path is None:
                raise ValueError("Caminho do projeto Delphi não pode ser None")
            
            if not delphi_project_path:
                raise ValueError("Caminho do projeto Delphi está vazio")
            
            logger.info(f"Analisando projeto: {delphi_project_path}")
            
            # Extrai projeto Delphi
            extracted_path = self.file_handler.extract_zip(delphi_project_path)
            logger.info(f"Projeto extraído em: {extracted_path}")
            
            # Encontra arquivos Delphi
            delphi_files = self.file_handler.find_delphi_files(extracted_path)
            logger.info(f"Arquivos encontrados: {sum(len(files) for files in delphi_files.values())}")
            
            # Analisa estrutura do projeto
            self.delphi_structure = self.delphi_parser.parse_project(delphi_files)
            
            # Log do resumo
            summary = self.delphi_structure.get('summary', {})
            logger.info(f"Análise concluída - Units: {summary.get('total_units', 0)}, "
                       f"Forms: {summary.get('total_forms', 0)}, "
                       f"DataModules: {summary.get('total_datamodules', 0)}")
            
        except Exception as e:
            logger.error(f"Erro no Passo 1: {str(e)}")
            raise Exception(f"Falha na análise do projeto Delphi: {str(e)}")
    
    def _step2_build_rag_context(self):
        """Passo 2: Geração Aumentada por Recuperação (RAG)"""
        try:
            logger.info("PASSO 2: Preparação do Contexto")
            
            if not self.delphi_structure:
                raise Exception("Estrutura Delphi não disponível")
            
            # Prepara contexto simples a partir da estrutura
            self.rag_context = self._build_simple_context(self.delphi_structure)
            
            logger.info(f"Contexto preparado: {len(self.rag_context)} caracteres")
            
        except Exception as e:
            logger.error(f"Erro no Passo 2: {str(e)}")
            raise Exception(f"Falha na construção do contexto RAG: {str(e)}")
    
    def _step3_generate_java_code(self, progress_callback: Optional[Callable] = None):
        """Passo 3: Interação com LLM e Geração de Código"""
        try:
            logger.info("PASSO 3: Geração de Código Java")
            
            if not self.delphi_structure or not self.rag_context:
                raise Exception("Dados necessários não disponíveis")
            
            # Configura prompts especializados se disponível
            prompt_config = {}
            if self.prompt_manager:
                logger.info("✅ Usando prompts especializados para geração de código")
                
                # Determina o tipo de prompt baseado na configuração
                modernization_type = self.config.get('type', 'Conversão Completa')
                logger.info(f"Tipo de modernização configurado: {modernization_type}")
                
                # Usa prompt de conversão Spring Boot
                if hasattr(self.prompt_manager, 'get_spring_conversion_prompt'):
                    prompt_config['primary_prompt'] = self.prompt_manager.get_spring_conversion_prompt()
                    logger.info("Usando prompt especializado get_spring_conversion_prompt")
                elif hasattr(self.prompt_manager, 'get_backend_conversion_prompt'):
                    prompt_config['primary_prompt'] = self.prompt_manager.get_backend_conversion_prompt()
                    logger.info("Usando prompt especializado get_backend_conversion_prompt")
                else:
                    logger.warning("Nenhum prompt de conversão específico encontrado")
                
                # Adiciona prompts auxiliares
                if self.config.get('include_tests', False) and hasattr(self.prompt_manager, 'get_testing_prompt'):
                    prompt_config['testing_prompt'] = self.prompt_manager.get_testing_prompt()
                    logger.info("Prompt de testes adicionado à configuração")
                
                # Se há documentação gerada, usa prompt enriquecido
                if (hasattr(self, 'analysis_results') and hasattr(self, 'generated_docs') and 
                    hasattr(self.prompt_manager, 'get_documentation_enhanced_prompt')):
                    prompt_config['enhanced_prompt'] = self.prompt_manager.get_documentation_enhanced_prompt(
                        analysis_results=self.analysis_results,
                        generated_docs=self.generated_docs
                    )
                    logger.info("Prompt enriquecido com documentação configurado")
                
                logger.info(f"Configuração de prompts finalizada. Prompts configurados: {list(prompt_config.keys())}")
            else:
                logger.warning("⚠️ PromptManager não disponível - usando prompts padrão")
            # Gera código Java usando LLM
            self.generated_code = self.llm_service.generate_code(
                self.delphi_structure,
                self.rag_context,
                progress_callback,
                prompt_config=prompt_config
            )
            
            # Valida resultado
            if not self.generated_code or not self.generated_code.get('files'):
                raise Exception("Código Java não foi gerado corretamente")
            
            files_count = len(self.generated_code.get('files', {}))
            logger.info(f"Código Java gerado: {files_count} arquivos")
            
        except Exception as e:
            logger.error(f"Erro no Passo 3: {str(e)}")
            raise Exception(f"Falha na geração de código Java: {str(e)}")
    
    def _step4_build_java_project(self, progress_callback: Optional[Callable] = None):
        """Passo 4: Construção e Pós-processamento do Projeto Java"""
        try:
            logger.info("PASSO 4: Construção do Projeto Java")
            
            if not self.generated_code:
                raise Exception("Código gerado não disponível")
            
            # Cria estrutura do projeto Java
            temp_dir = tempfile.mkdtemp(prefix='junim_java_')
            package_name = self.generated_code.get('package_name', 'com.example.modernizedapp')
            
            java_structure = self.file_handler.create_java_project_structure(
                temp_dir, 
                package_name
            )
            
            # Constrói projeto
            self.java_project_path = self.java_builder.build_project(
                self.generated_code,
                java_structure,
                progress_callback
            )
            
            logger.info(f"Projeto Java construído em: {self.java_project_path}")
            
        except Exception as e:
            logger.error(f"Erro no Passo 4: {str(e)}")
            raise Exception(f"Falha na construção do projeto Java: {str(e)}")
    
    def _step5_package_project(self) -> str:
        """Passo 5: Empacotamento"""
        try:
            logger.info("PASSO 5: Empacotamento do Projeto")
            
            if not self.java_project_path:
                raise Exception("Projeto Java não disponível")
            
            # Cria arquivo ZIP
            output_zip = tempfile.mktemp(suffix='_modernized_project.zip')
            self.file_handler.create_zip(self.java_project_path, output_zip)
            
            logger.info(f"Projeto empacotado: {output_zip}")
            return output_zip
            
        except Exception as e:
            logger.error(f"Erro no Passo 5: {str(e)}")
            raise Exception(f"Falha no empacotamento: {str(e)}")
    
    def _cleanup(self):
        """Limpa recursos temporários"""
        try:
            self.file_handler.cleanup_temp_dirs()
        except Exception as e:
            logger.warning(f"Erro na limpeza: {str(e)}")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Retorna status atual do pipeline"""
        return {
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'delphi_analyzed': self.delphi_structure is not None,
            'rag_built': self.rag_context is not None,
            'code_generated': self.generated_code is not None,
            'project_built': self.java_project_path is not None
        }
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Retorna relatório detalhado da modernização"""
        report = {
            'pipeline_status': self.get_pipeline_status(),
            'timestamp': None,
            'delphi_analysis': None,
            'rag_summary': None,
            'generation_summary': None,
            'java_summary': None
        }
        
        try:
            import datetime
            report['timestamp'] = datetime.datetime.now().isoformat()
            
            # Resumo da análise Delphi
            if self.delphi_structure:
                report['delphi_analysis'] = {
                    'summary': self.delphi_structure.get('summary', {}),
                    'units_count': len(self.delphi_structure.get('units', {})),
                    'forms_count': len(self.delphi_structure.get('forms', {})),
                    'datamodules_count': len(self.delphi_structure.get('data_modules', {}))
                }
            
            # Resumo do contexto
            if self.rag_context:
                report['context_summary'] = {
                    'context_length': len(self.rag_context),
                    'context_type': 'simple_structure'
                }
            
            # Resumo da geração
            if self.generated_code:
                report['generation_summary'] = {
                    'project_name': self.generated_code.get('project_name'),
                    'package_name': self.generated_code.get('package_name'),
                    'files_count': len(self.generated_code.get('files', {})),
                    'files_list': list(self.generated_code.get('files', {}).keys())
                }
            
            # Resumo do projeto Java
            if self.java_project_path:
                report['java_summary'] = self.java_builder.get_project_summary()
            
        except Exception as e:
            logger.warning(f"Erro ao gerar relatório detalhado: {str(e)}")
        
        return report
    
    def test_llm_connectivity(self) -> Dict[str, bool]:
        """Testa conectividade com LLMs"""
        return self.llm_service.test_connection()
    
    def __del__(self):
        """Destructor - limpa recursos"""
        self._cleanup()
    
    def _use_previous_analysis(self):
        """Usa dados de análise prévia carregados"""
        try:
            logger.info("PASSO 1: Usando Análise Prévia")
            
            if not hasattr(self, 'analysis_results') or not self.analysis_results:
                logger.error("Dados de análise prévia não disponíveis")
                raise Exception("Dados de análise prévia não disponíveis")
            
            logger.info(f"Análise prévia disponível com {len(self.analysis_results)} chaves")
            
            # Converte análise prévia para formato do pipeline
            self.delphi_structure = {
                'summary': {
                    'total_units': len(self.analysis_results.get('units_analysis', {})),
                    'total_forms': sum(1 for unit in self.analysis_results.get('units_analysis', {}).values() 
                                     if unit.get('unit_type') == 'form'),
                    'total_datamodules': sum(1 for unit in self.analysis_results.get('units_analysis', {}).values() 
                                           if unit.get('unit_type') == 'datamodule'),
                    'project_name': self.analysis_results.get('project_info', {}).get('name', 'Projeto_Delphi')
                },
                'units': self.analysis_results.get('units_analysis', {}),
                'forms': {name: unit for name, unit in self.analysis_results.get('units_analysis', {}).items() 
                         if unit.get('unit_type') == 'form'},
                'data_modules': {name: unit for name, unit in self.analysis_results.get('units_analysis', {}).items() 
                               if unit.get('unit_type') == 'datamodule'},
                'business_logic': self.analysis_results.get('business_logic', {}),
                'data_flows': self.analysis_results.get('data_flows', {}),
                'execution_flows': self.analysis_results.get('execution_flows', {}),
                'correlations': self.analysis_results.get('correlations', {}),
                'analysis_timestamp': self.analysis_results.get('metadata', {}).get('analysis_timestamp')
            }
            
            # Log do resumo
            summary = self.delphi_structure.get('summary', {})
            logger.info(f"Análise prévia carregada - Units: {summary.get('total_units', 0)}, "
                       f"Forms: {summary.get('total_forms', 0)}, "
                       f"DataModules: {summary.get('total_datamodules', 0)}")
            
        except Exception as e:
            logger.error(f"Erro ao usar análise prévia: {str(e)}")
            raise Exception(f"Falha ao usar análise prévia: {str(e)}")
    
    def _build_simple_context(self, delphi_structure: Dict[str, Any]) -> str:
        """
        Constrói contexto simples a partir da estrutura Delphi
        Substitui a funcionalidade do RAGBuilder removido
        """
        context_parts = []
        
        # Resumo geral
        summary = delphi_structure.get('summary', {})
        context_parts.append(f"PROJETO DELPHI - {summary.get('total_units', 0)} units, {summary.get('total_forms', 0)} forms")
        
        # Units principais
        units = delphi_structure.get('units', {})
        if units:
            unit_names = list(units.keys())[:10]  # Primeiras 10 units
            context_parts.append(f"UNITS: {', '.join(unit_names)}")
        
        # Forms principais  
        forms = delphi_structure.get('forms', {})
        if forms:
            form_names = list(forms.keys())[:5]  # Primeiras 5 forms
            context_parts.append(f"FORMS: {', '.join(form_names)}")
        
        # Data modules
        data_modules = delphi_structure.get('data_modules', {})
        if data_modules:
            dm_names = list(data_modules.keys())[:5]
            context_parts.append(f"DATA_MODULES: {', '.join(dm_names)}")
        
        return "\n".join(context_parts)
