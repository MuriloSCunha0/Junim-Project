"""
Analisador avançado de projeto Delphi para geração de documentação detalhada
"""

import os
import re
import json
import math
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
from pathlib import Path
import time

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import do PromptManager com tratamento de erro
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Versão simplificada sem dependências de performance
PERFORMANCE_AVAILABLE = False

try:
    from prompts.specialized_prompts import PromptManager
    PROMPTS_AVAILABLE = True
    logger.info("✅ PromptManager especializado importado com sucesso")
except ImportError as e:
    logger.error(f"❌ PromptManager não disponível: {e}")
    PROMPTS_AVAILABLE = False
    raise ImportError(f"PromptManager obrigatório não encontrado: {e}")

class LegacyProjectAnalyzer:
    """Analisador avançado de projetos Delphi legados"""
    
    def __init__(self, prompt_manager=None):
        """
        Inicializa o analisador de projetos legados
        
        Args:
            prompt_manager: Gerenciador de prompts especializado (opcional)
        """
        
        # Versão do analisador
        self.version = "1.0.0"
        
    def __init__(self, prompt_manager=None):
        """
        Inicializa o analisador de projetos legados
        
        Args:
            prompt_manager: Gerenciador de prompts especializado (obrigatório)
        """
        
        # Versão do analisador
        self.version = "1.0.0"
        
        # Configura prompt manager (obrigatório)
        if prompt_manager is not None:
            self.prompt_manager = prompt_manager
            logger.info("✅ PromptManager especializado fornecido externamente")
        else:
            # Inicializa prompt manager internamente
            from prompts.specialized_prompts import PromptManager
            self.prompt_manager = PromptManager()
            logger.info("✅ PromptManager especializado inicializado internamente")
        
        # Configuração da API
        self.groq_api_key = None
        self.groq_model = 'llama3-70b-8192'
        
        # Inicializa LLM service
        self.llm_service = None
        self._initialize_llm_service()
        
        # Inicializa gerador de documentação
        from core.documentation_generator import DocumentationGenerator
        self.doc_generator = DocumentationGenerator(
            llm_service=self.llm_service,  # Passa o LLM service
            prompt_manager=self.prompt_manager
        )
        logger.info("✅ DocumentationGenerator inicializado com LLM service e prompt_manager")
    
    def _initialize_llm_service(self):
        """Inicializa o LLM service"""
        from core.llm_service import LLMService
        
        # Cria configuração para o LLM
        config = {
            'groq_api_key': self.groq_api_key,
            'groq_model': self.groq_model
        }
        
        # Cria instância do serviço com prompt_manager
        self.llm_service = LLMService(config, prompt_manager=self.prompt_manager)
        logger.info("✅ LLM Service inicializado")
    
    def update_api_config(self, groq_api_key: str = None, groq_model: str = None):
        """Atualiza configuração da API e reinicializa o LLM service"""
        if groq_api_key:
            self.groq_api_key = groq_api_key
        if groq_model:
            self.groq_model = groq_model
        
        # Reinicializa o LLM service com nova configuração
        self._initialize_llm_service()
        
        # Atualiza o doc_generator também
        if self.doc_generator:
            self.doc_generator.llm_service = self.llm_service
            logger.info("✅ LLM Service atualizado no DocumentationGenerator")

    def _generate_with_ai(self, prompt: str, context: str) -> str:
        """
        Gera análise usando IA com prompt e contexto
        
        Args:
            prompt: Prompt para a IA
            context: Contexto do projeto
            
        Returns:
            Análise gerada pela IA
            
        Raises:
            Exception: Se LLM service não estiver configurado ou falhar
        """
        # Validação obrigatória do LLM service
        if not self.llm_service:
            raise Exception("LLM service não configurado. Configure a API antes de usar análise com IA.")
        
        # Validação de entrada
        if not prompt or not prompt.strip():
            raise Exception("Prompt não pode estar vazio.")
        
        if not context or not context.strip():
            raise Exception("Contexto do projeto não pode estar vazio.")
        
        try:
            # Combina prompt e contexto
            full_prompt = f"{prompt}\n\n## CONTEXTO DO PROJETO:\n{context}"
            
            # Gera resposta com parâmetros corretos
            response = self.llm_service.generate_code(
                delphi_structure={"prompt": full_prompt},  # Usa estrutura correta
                rag_context=context,  # Adiciona o parâmetro obrigatório
                prompt_config={"analysis_prompt": full_prompt}
            )
            
            # Trata diferentes tipos de resposta
            if isinstance(response, dict):
                # Se for dict, extrai o conteúdo relevante
                if 'analysis' in response:
                    return response['analysis']
                elif 'content' in response:
                    return response['content']
                else:
                    return str(response)
            else:
                return str(response)
                
        except ImportError as e:
            raise Exception(f"Módulo LLMService não disponível: {e}")
        except Exception as e:
            raise Exception(f"Erro ao gerar análise com IA: {e}")


    def configure_api(self, api_key: str, model: str = 'llama3-70b-8192'):
        """
        Configura API da IA
        
        Args:
            api_key: Chave da API
            model: Modelo a ser usado
        """
        self.groq_api_key = api_key
        self.groq_model = model
        logger.info(f"✅ API configurada: {model}")

    def analyze_complete_project(self, project_path: str, project_name: str = None) -> Dict[str, Any]:
        """
        Realiza análise completa do projeto Delphi
        
        Args:
            project_path: Caminho do projeto extraído
            project_name: Nome do projeto (opcional)
            
        Returns:
            Análise completa estruturada
        """
        try:
            logger.info(f"Iniciando análise completa do projeto: {project_name or 'Unnamed'}")
            
            # Informações básicas do projeto
            self.project_info = self._extract_project_info(project_path, project_name)
            
            # Análise detalhada por arquivo
            self.units_analysis = self._analyze_units_detailed(project_path)
            
            # Extração de lógica de negócio
            self.business_logic = self._extract_business_logic()
            
            # Análise de fluxos
            self.data_flows = self._analyze_data_flows()
            self.execution_flows = self._analyze_execution_flows()
            
            # Identificação de requisitos
            self.requirements = self._identify_requirements()
            
            # Características do sistema
            self.characteristics = self._analyze_system_characteristics()
            
            # Correlações Delphi → Java
            self.correlations = self._generate_correlations()
            
            # Estrutura final
            complete_analysis = {
                'metadata': {
                    'project_name': project_name or 'Unnamed Project',
                    'analysis_date': datetime.now().isoformat(),
                    'analyzer_version': '1.0.0',
                    'total_files_analyzed': len(self.units_analysis)
                },
                'project_info': self.project_info,
                'units_analysis': self.units_analysis,
                'business_logic': self.business_logic,
                'data_flows': self.data_flows,
                'execution_flows': self.execution_flows,
                'requirements': self.requirements,
                'characteristics': self.characteristics,
                'correlations': self.correlations
            }
            
            logger.info("Análise completa finalizada com sucesso")
            return complete_analysis
            
        except Exception as e:
            logger.error(f"Erro na análise completa: {str(e)}")
            raise Exception(f"Falha na análise do projeto: {str(e)}")
    
    def _extract_project_info(self, project_path: str, project_name: str) -> Dict[str, Any]:
        """Extrai informações básicas do projeto"""
        try:
            delphi_files = self._find_delphi_files(project_path)
            
            # Arquivo de projeto principal (.dpr)
            main_project_file = None
            if delphi_files.get('dpr'):
                main_project_file = delphi_files['dpr'][0]
            
            project_info = {
                'name': project_name,
                'path': project_path,
                'main_project_file': main_project_file,
                'file_counts': {
                    'pascal_units': len(delphi_files.get('pas', [])),
                    'forms': len(delphi_files.get('dfm', [])),
                    'projects': len(delphi_files.get('dpr', [])),
                    'packages': len(delphi_files.get('dpk', [])),
                    'includes': len(delphi_files.get('inc', []))
                },
                'total_files': sum(len(files) for files in delphi_files.values()),
                'estimated_size': self._calculate_project_size(delphi_files),
                'main_units': self._identify_main_units(delphi_files),
                'delphi_version': self._detect_delphi_version(delphi_files),
                'architecture_type': self._detect_architecture_type(delphi_files)
            }
            
            return project_info
            
        except Exception as e:
            logger.warning(f"Erro ao extrair informações do projeto: {str(e)}")
            return {'name': project_name, 'error': str(e)}
    
    def _analyze_units_detailed(self, project_path: str) -> Dict[str, Any]:
        """Análise detalhada de cada unit"""
        units_analysis = {}
        delphi_files = self._find_delphi_files(project_path)
        
        try:
            for pas_file in delphi_files.get('pas', []):
                unit_name = os.path.splitext(os.path.basename(pas_file))[0]
                logger.info(f"Analisando unit: {unit_name}")
                
                content = self._read_file_safe(pas_file)
                if not content:
                    continue
                
                unit_analysis = {
                    'file_path': pas_file,
                    'file_size': len(content),
                    'lines_count': len(content.splitlines()),
                    'unit_type': self._classify_unit_type(content, unit_name),
                    'dependencies': self._extract_dependencies(content),
                    'classes': self._extract_classes_detailed(content),
                    'procedures_functions': self._extract_procedures_functions_detailed(content),
                    'variables': self._extract_variables(content),
                    'constants': self._extract_constants(content),
                    'database_operations': self._extract_database_operations(content),
                    'backend_elements': self._extract_backend_elements(content),
                    'business_rules': self._extract_business_rules(content),
                    'complexity_metrics': self._calculate_complexity_metrics(content)
                }
                
                # Análise do arquivo .dfm correspondente se existir
                dfm_file = pas_file.replace('.pas', '.dfm')
                if os.path.exists(dfm_file):
                    dfm_content = self._read_file_safe(dfm_file)
                    unit_analysis['form_analysis'] = self._analyze_form_file(dfm_content)
                
                units_analysis[unit_name] = unit_analysis
            
            return units_analysis
            
        except Exception as e:
            logger.error(f"Erro na análise detalhada de units: {str(e)}")
            return {}
    
    def _extract_business_logic(self) -> Dict[str, Any]:
        """Extrai e categoriza lógica de negócio"""
        business_logic = {
            'business_rules': [],
            'validations': [],
            'calculations': [],
            'workflows': [],
            'data_processing': [],
            'integrations': []
        }
        
        try:
            for unit_name, unit_data in self.units_analysis.items():
                # Regras de negócio
                for rule in unit_data.get('business_rules', []):
                    business_logic['business_rules'].append({
                        'unit': unit_name,
                        'rule': rule,
                        'type': 'business_rule'
                    })
                
                # Validações
                for proc in unit_data.get('procedures_functions', []):
                    if self._is_validation_function(proc):
                        business_logic['validations'].append({
                            'unit': unit_name,
                            'function': proc['name'],
                            'description': proc.get('description', ''),
                            'parameters': proc.get('parameters', [])
                        })
                
                # Cálculos
                for calc in self._extract_calculations(unit_data):
                    business_logic['calculations'].append({
                        'unit': unit_name,
                        'calculation': calc
                    })
                
                # Processamento de dados
                for db_op in unit_data.get('database_operations', []):
                    business_logic['data_processing'].append({
                        'unit': unit_name,
                        'operation': db_op
                    })
            
            return business_logic
            
        except Exception as e:
            logger.error(f"Erro na extração de lógica de negócio: {str(e)}")
            return business_logic
    
    def _analyze_data_flows(self) -> Dict[str, Any]:
        """Analisa fluxos de dados no sistema"""
        data_flows = {
            'database_flows': [],
            'form_data_flows': [],
            'inter_unit_flows': [],
            'external_flows': []
        }
        
        try:
            for unit_name, unit_data in self.units_analysis.items():
                # Fluxos de banco de dados
                for db_op in unit_data.get('database_operations', []):
                    flow = {
                        'source_unit': unit_name,
                        'operation_type': db_op.get('type'),
                        'tables_involved': db_op.get('tables', []),
                        'data_direction': self._determine_data_direction(db_op),
                        'description': db_op.get('description', '')
                    }
                    data_flows['database_flows'].append(flow)
                
                # Fluxos entre formulários
                if unit_data.get('unit_type') == 'form':
                    form_flows = self._analyze_form_data_flows(unit_data)
                    data_flows['form_data_flows'].extend(form_flows)
                
                # Fluxos entre units
                inter_flows = self._analyze_inter_unit_flows(unit_name, unit_data)
                data_flows['inter_unit_flows'].extend(inter_flows)
            
            return data_flows
            
        except Exception as e:
            logger.error(f"Erro na análise de fluxos de dados: {str(e)}")
            return data_flows
    
    def _analyze_execution_flows(self) -> Dict[str, Any]:
        """Analisa fluxos de execução do sistema"""
        execution_flows = {
            'startup_sequence': [],
            'user_workflows': [],
            'error_handling_flows': [],
            'shutdown_sequence': []
        }
        
        try:
            # Sequência de inicialização
            main_project = self._find_main_project_unit()
            if main_project:
                execution_flows['startup_sequence'] = self._analyze_startup_sequence(main_project)
            
            # Workflows de usuário
            for unit_name, unit_data in self.units_analysis.items():
                if unit_data.get('unit_type') == 'form':
                    workflows = self._extract_user_workflows(unit_name, unit_data)
                    execution_flows['user_workflows'].extend(workflows)
            
            # Tratamento de erros
            error_flows = self._analyze_error_handling()
            execution_flows['error_handling_flows'] = error_flows
            
            return execution_flows
            
        except Exception as e:
            logger.error(f"Erro na análise de fluxos de execução: {str(e)}")
            return execution_flows
    
    def _identify_requirements(self) -> Dict[str, Any]:
        """Identifica requisitos funcionais e não funcionais"""
        requirements = {
            'functional_requirements': [],
            'non_functional_requirements': [],
            'business_requirements': [],
            'technical_requirements': []
        }
        
        try:
            # Requisitos funcionais baseados na análise das units
            for unit_name, unit_data in self.units_analysis.items():
                unit_requirements = self._extract_functional_requirements(unit_name, unit_data)
                requirements['functional_requirements'].extend(unit_requirements)
            
            # Requisitos não funcionais
            requirements['non_functional_requirements'] = self._identify_non_functional_requirements()
            
            # Requisitos de negócio
            requirements['business_requirements'] = self._extract_business_requirements()
            
            # Requisitos técnicos
            requirements['technical_requirements'] = self._identify_technical_requirements()
            
            return requirements
            
        except Exception as e:
            logger.error(f"Erro na identificação de requisitos: {str(e)}")
            return requirements
    
    def _analyze_system_characteristics(self) -> Dict[str, Any]:
        """Analisa características do sistema"""
        characteristics = {
            'architecture_pattern': self._identify_architecture_pattern(),
            'technology_stack': self._identify_technology_stack(),
            'complexity_level': self._assess_complexity_level(),
            'maintainability_score': self._calculate_maintainability_score(),
            'modernization_readiness': self._assess_modernization_readiness(),
            'risk_factors': self._identify_risk_factors(),
            'strengths': self._identify_system_strengths(),
            'weaknesses': self._identify_system_weaknesses()
        }
        
        return characteristics
    
    def _generate_correlations(self) -> Dict[str, Any]:
        """Gera correlações Delphi → Java"""
        correlations = {
            'component_mappings': [],
            'pattern_mappings': [],
            'architecture_mappings': [],
            'technology_mappings': []
        }
        
        try:
            # Mapeamentos de componentes
            for unit_name, unit_data in self.units_analysis.items():
                unit_correlations = self._generate_unit_correlations(unit_name, unit_data)
                correlations['component_mappings'].extend(unit_correlations)
            
            # Mapeamentos de padrões
            correlations['pattern_mappings'] = self._generate_pattern_mappings()
            
            # Mapeamentos de arquitetura
            correlations['architecture_mappings'] = self._generate_architecture_mappings()
            
            # Mapeamentos de tecnologia
            correlations['technology_mappings'] = self._generate_technology_mappings()
            
            return correlations
            
        except Exception as e:
            logger.error(f"Erro na geração de correlações: {str(e)}")
            return correlations
    
    def analyze_project(self, project_path: str, project_name: str = None) -> Dict[str, Any]:
        """Analisa projeto Delphi de forma otimizada"""
        start_time = time.time()
        logger.info(f"🚀 Iniciando análise otimizada do projeto: {project_path}")
        
        # Se project_name não foi fornecido, extrai do caminho
        if project_name is None:
            project_name = Path(project_path).name
        
        try:
            # Otimiza lista de arquivos
            all_files = list(Path(project_path).rglob('*'))
            optimized_files = performance_optimizer.optimize_file_analysis(all_files)
            
            # Processa arquivos em lotes
            results = batch_processor.process_files_in_batches(
                optimized_files, 
                self._analyze_single_file_optimized
            )
            
            # Combina resultados
            combined_results = self._combine_analysis_results(results)
            
            elapsed_time = time.time() - start_time
            logger.info(f"✅ Análise concluída em {elapsed_time:.2f}s")
            
            return combined_results
            
        except Exception as e:
            logger.error(f"❌ Erro na análise otimizada: {str(e)}")
            raise Exception(f"Falha na análise do projeto: {str(e)}")
    
    def _analyze_single_file_optimized(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analisa um único arquivo de forma otimizada"""
        try:
            # Verifica cache primeiro
            cache_key = f"{file_path}_{file_path.stat().st_mtime}"
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Lê arquivo de forma otimizada
            content = streaming_reader.read_file_optimized(file_path)
            if not content:
                return None
            
            # Analisa conteúdo
            analysis = self._analyze_file_content_optimized(content, file_path)
            
            # Salva no cache
            cache_manager.set(cache_key, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro analisando arquivo {file_path}: {str(e)}")
            return None
    
    def _analyze_file_content_optimized(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analisa conteúdo do arquivo de forma otimizada"""
        # Implementação otimizada da análise
        analysis = {
            'file_path': str(file_path),
            'file_size': len(content),
            'classes': self._extract_classes_fast(content),
            'functions': self._extract_functions_fast(content),
            'imports': self._extract_imports_fast(content)
        }
        
        return analysis
    
    def _extract_classes_fast(self, content: str) -> List[Dict[str, Any]]:
        """Extração rápida de classes"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_stripped = line.strip().lower()
            if line_stripped.startswith('type ') and '= class' in line_stripped:
                class_name = self._extract_class_name_fast(line)
                if class_name:
                    classes.append({
                        'name': class_name,
                        'line': i + 1,
                        'type': 'class'
                    })
        
        return classes
    
    def _extract_functions_fast(self, content: str) -> List[Dict[str, Any]]:
        """Extração rápida de funções"""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_stripped = line.strip().lower()
            if (line_stripped.startswith('function ') or 
                line_stripped.startswith('procedure ')):
                func_name = self._extract_function_name_fast(line)
                if func_name:
                    functions.append({
                        'name': func_name,
                        'line': i + 1,
                        'type': 'function' if 'function' in line_stripped else 'procedure'
                    })
        
        return functions
    
    def _extract_imports_fast(self, content: str) -> List[str]:
        """Extração rápida de imports"""
        imports = []
        lines = content.split('\n')
        
        in_uses_section = False
        for line in lines:
            line_stripped = line.strip()
            
            if line_stripped.lower().startswith('uses '):
                in_uses_section = True
                # Extrai unidades da linha uses
                uses_line = line_stripped[5:].replace(';', '').strip()
                imports.extend([u.strip() for u in uses_line.split(',') if u.strip()])
            elif in_uses_section:
                if ';' in line:
                    in_uses_section = False
                else:
                    # Continua coletando unidades
                    uses_line = line_stripped.replace(';', '').strip()
                    imports.extend([u.strip() for u in uses_line.split(',') if u.strip()])
        
        return imports
    
    def _extract_class_name_fast(self, line: str) -> Optional[str]:
        """Extrai nome da classe rapidamente"""
        try:
            # Procura por padrão: type NomeClasse = class
            parts = line.strip().split()
            for i, part in enumerate(parts):
                if part.lower() == 'type' and i + 1 < len(parts):
                    class_name = parts[i + 1]
                    # Remove caracteres especiais
                    class_name = class_name.replace('=', '').strip()
                    if class_name and class_name.isidentifier():
                        return class_name
            return None
        except:
            return None
    
    def _extract_function_name_fast(self, line: str) -> Optional[str]:
        """Extrai nome da função/procedimento rapidamente"""
        try:
            # Procura por padrão: function/procedure NomeFuncao
            line_stripped = line.strip()
            if line_stripped.lower().startswith('function ') or line_stripped.lower().startswith('procedure '):
                # Remove 'function ' ou 'procedure '
                start_pos = 9 if line_stripped.lower().startswith('function ') else 10
                rest = line_stripped[start_pos:].strip()
                
                # Pega o nome até encontrar ( ou :
                func_name = ''
                for char in rest:
                    if char in '(:;':
                        break
                    func_name += char
                
                func_name = func_name.strip()
                if func_name and func_name.replace('_', '').isalnum():
                    return func_name
            return None
        except:
            return None
    
    def _combine_analysis_results(self, results: List[Any]) -> Dict[str, Any]:
        """Combina resultados da análise em lotes"""
        try:
            combined = {
                'files_analyzed': len([r for r in results if r]),
                'total_classes': 0,
                'total_functions': 0,
                'total_imports': 0,
                'files': [],
                'summary': {},
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'analysis_type': 'optimized_batch',
                    'performance_optimized': True
                }
            }
            
            all_classes = []
            all_functions = []
            all_imports = []
            
            for result in results:
                if result and isinstance(result, dict):
                    combined['files'].append(result)
                    
                    # Extrai classes
                    classes = result.get('classes', [])
                    all_classes.extend(classes)
                    
                    # Extrai functions
                    functions = result.get('functions', [])
                    all_functions.extend(functions)
                    
                    # Extrai imports
                    imports = result.get('imports', [])
                    all_imports.extend(imports)
            
            # Contadores
            combined['total_classes'] = len(all_classes)
            combined['total_functions'] = len(all_functions)
            combined['total_imports'] = len(set(all_imports))  # Remove duplicados
            
            # Summary
            combined['summary'] = {
                'files_processed': len(combined['files']),
                'classes_found': combined['total_classes'],
                'functions_found': combined['total_functions'],
                'unique_imports': combined['total_imports'],
                'analysis_method': 'optimized_performance'
            }
            
            logger.info(f"✅ Análise combinada concluída: {combined['total_classes']} classes, {combined['total_functions']} funções")
            return combined
            
        except Exception as e:
            logger.error(f"❌ Erro ao combinar resultados: {str(e)}")
            # Retorna estrutura básica em caso de erro
            return {
                'files_analyzed': len(results),
                'total_classes': 0,
                'total_functions': 0,
                'total_imports': 0,
                'files': [],
                'summary': {'error': str(e)},
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'analysis_type': 'fallback',
                    'error': str(e)
                }
            }
    
 



    def analyze_project_with_prompts(self, project_path: str, project_name: str = None) -> Dict[str, Any]:
        """Analisa projeto usando prompts especializados"""
        try:
            logger.info(f"🔍 Iniciando análise com prompts especializados: {project_path}")
            
            # Verifica se tem prompts especializados
            if not hasattr(self, 'using_specialized_prompts'):
                self.using_specialized_prompts = self.prompt_manager is not None
            
            if not self.using_specialized_prompts:
                logger.warning("⚠️ Prompts especializados não disponíveis, usando análise padrão")
                return self.analyze_project(project_path, project_name)
            
            # Análise estrutural básica
            structural_analysis = self.analyze_project(project_path, project_name)
            
            # Enriquece com análise baseada em prompts
            if self.prompt_manager:
                try:
                    # Gera contexto do projeto
                    project_context = self._generate_project_context(structural_analysis)
                    
                    # Usa prompt de análise especializado
                    analysis_prompt = self.prompt_manager.get_analysis_prompt()
                    
                    # Gera análise com IA
                    enhanced_analysis = self._generate_with_ai(analysis_prompt, project_context)
                    
                    # Combina análises
                    structural_analysis['enhanced_analysis'] = enhanced_analysis
                    structural_analysis['used_specialized_prompts'] = True
                    
                    logger.info("✅ Análise com prompts especializados concluída")
                    
                except Exception as e:
                    logger.error(f"❌ Erro na análise com prompts: {str(e)}")
                    structural_analysis['enhanced_analysis'] = "Erro na análise com prompts especializados"
                    structural_analysis['used_specialized_prompts'] = False
            
            return structural_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise com prompts: {str(e)}")
            # Fallback para análise padrão
            return self.analyze_project(project_path, project_name)

    def _generate_project_context(self, analysis_results: Dict[str, Any]) -> str:
        """Gera contexto do projeto de forma segura"""
        try:
            context_parts = []
            
            # Verifica se analysis_results é válido
            if not isinstance(analysis_results, dict):
                logger.warning(f"⚠️ analysis_results não é dict: {type(analysis_results)}")
                return "Análise básica do projeto concluída."
            
            # Extrai informações seguramente
            files_data = analysis_results.get('files', {})
            if isinstance(files_data, dict):
                total_files = len(files_data)
                context_parts.append(f"Projeto analisado: {total_files} arquivos")
                
                # Conta classes e funções de forma segura
                total_classes = 0
                total_functions = 0
                
                for file_path, file_data in files_data.items():
                    if isinstance(file_data, dict):
                        classes = file_data.get('classes', [])
                        functions = file_data.get('functions', [])
                        
                        if isinstance(classes, list):
                            total_classes += len(classes)
                        if isinstance(functions, list):
                            total_functions += len(functions)
                
                context_parts.append(f"Total: {total_classes} classes, {total_functions} funções")
            
            # Adiciona informações de tecnologia
            context_parts.append("Tecnologia: Delphi/Pascal")
            context_parts.append("Destino: Java Spring Boot")
            
            return " | ".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Erro gerando contexto: {str(e)}")
            return "Projeto Delphi analisado para modernização Spring Boot"
    
    def _collect_delphi_files(self, project_path: str) -> List[str]:
        """Coleta todos os arquivos Delphi do projeto"""
        delphi_files = []
        
        try:
            delphi_extensions = ['.pas', '.dfm', '.dpr', '.dpk', '.inc']
            
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in delphi_extensions):
                        file_path = os.path.join(root, file)
                        delphi_files.append(file_path)
            
            return delphi_files
            
        except Exception as e:
            logger.error(f"Erro ao coletar arquivos Delphi: {str(e)}")
            return []

    def set_analysis_options(self, options: Dict[str, bool]):
        """Define opções de análise"""
        self.analysis_options = options
        logger.info(f"Opções de análise configuradas: {options}")

    def _should_include_comments(self) -> bool:
        """Verifica se deve incluir análise de comentários"""
        return getattr(self, 'analysis_options', {}).get('include_comments', True)

    def _should_analyze_business_logic(self) -> bool:
        """Verifica se deve analisar lógica de negócio"""
        return getattr(self, 'analysis_options', {}).get('analyze_business_logic', True)

    def _should_generate_correlations(self) -> bool:
        """Verifica se deve gerar correlações"""
        return getattr(self, 'analysis_options', {}).get('generate_correlations', True)

    def _count_files_by_type(self, delphi_files: List[str]) -> Dict[str, int]:
        """Conta arquivos por tipo de extensão"""
        file_counts = {
            'pas': 0,
            'dfm': 0,
            'dpr': 0,
            'dpk': 0,
            'inc': 0,
            'others': 0
        }
        
        try:
            for file_path in delphi_files:
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext == '.pas':
                    file_counts['pas'] += 1
                elif ext == '.dfm':
                    file_counts['dfm'] += 1
                elif ext == '.dpr':
                    file_counts['dpr'] += 1
                elif ext == '.dpk':
                    file_counts['dpk'] += 1
                elif ext == '.inc':
                    file_counts['inc'] += 1
                else:
                    file_counts['others'] += 1
            
            return file_counts
            
        except Exception as e:
            logger.error(f"Erro ao contar arquivos: {str(e)}")
            return file_counts

    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analisa um arquivo Delphi individual"""
        try:
            content = self._read_file_safe(file_path)
            
            if not content:
                return {
                    'error': 'Arquivo vazio ou não pôde ser lido',
                    'file_path': file_path
                }
            
            file_analysis = {
                'file_path': file_path,
                'file_size': len(content),
                'lines_count': len(content.splitlines()),
                'unit_type': self._classify_unit_type(content, os.path.basename(file_path)),
                'classes': self._extract_classes(content),
                'methods': self._extract_procedures_functions(content),
                'uses_clauses': self._extract_uses_units(content),
                'complexity_metrics': self._calculate_complexity(content)
            }
            
            return file_analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo {file_path}: {str(e)}")
            return {
                'error': str(e),
                'file_path': file_path
            }

    def _determine_file_type(self, file_analysis: Dict[str, Any]) -> str:
        """Determina o tipo do arquivo baseado na análise"""
        try:
            unit_type = file_analysis.get('unit_type', 'unknown')
            
            if unit_type in ['form', 'datamodule']:
                return unit_type
            elif unit_type in ['class', 'unit']:
                return 'unit'
            else:
                return 'unknown'
                
        except Exception as e:
            logger.error(f"Erro ao determinar tipo do arquivo: {str(e)}")
            return 'unknown'

    def _calculate_complexity_metrics_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de complexidade resumidas para o projeto"""
        try:
            metrics = {
                'average_complexity': 0,
                'max_complexity': 0,
                'total_lines': 0,
                'methods_with_high_complexity': 0
            }
            
            total_complexity = 0
            total_methods = 0
            
            # Analisa todos os arquivos
            for file_path, file_data in analysis_results.get('files', {}).items():
                if isinstance(file_data, dict) and 'complexity_metrics' in file_data:
                    file_complexity = file_data['complexity_metrics']
                    
                    # Soma complexidade
                    if 'cyclomatic_complexity' in file_complexity:
                        complexity = file_complexity['cyclomatic_complexity']
                        total_complexity += complexity
                        total_methods += 1
                        
                        if complexity > metrics['max_complexity']:
                            metrics['max_complexity'] = complexity
                        
                        if complexity > 10:  # Considera alta complexidade
                            metrics['methods_with_high_complexity'] += 1
                    
                    # Soma linhas
                    if 'lines_of_code' in file_complexity:
                        metrics['total_lines'] += file_complexity['lines_of_code']
            
            # Calcula média
            if total_methods > 0:
                metrics['average_complexity'] = round(total_complexity / total_methods, 2)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas: {str(e)}")
            return {'error': 'Métricas não disponíveis'}

    def _identify_main_functionalities(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Identifica as funcionalidades principais do projeto"""
        try:
            functionalities = []
            
            # Analisa forms para identificar funcionalidades
            forms_analysis = analysis_results.get('forms_analysis', {})
            for form_path, form_data in forms_analysis.items():
                if isinstance(form_data, dict):
                    form_name = os.path.basename(form_path).replace('.pas', '')
                    classes = form_data.get('classes', [])
                    
                    for cls in classes:
                        if isinstance(cls, dict):
                            methods = form_data.get('methods', [])
                            event_handlers = [m for m in methods if isinstance(m, dict) and 'click' in m.get('name', '').lower()]
                            
                            if event_handlers:
                                func_name = f"Interface {form_name} com {len(event_handlers)} interações"
                                functionalities.append(func_name)
            
            # Analisa datamodules para operações de dados
            datamodules_analysis = analysis_results.get('datamodules_analysis', {})
            for dm_path, dm_data in datamodules_analysis.items():
                if isinstance(dm_data, dict):
                    dm_name = os.path.basename(dm_path).replace('.pas', '')
                    
                    # Conta métodos e operações
                    methods = dm_data.get('methods', [])
                    if methods:
                        func_name = f"Módulo de dados {dm_name} com {len(methods)} operações"
                        functionalities.append(func_name)
            
            return functionalities[:10]  # Limita a 10 funcionalidades principais
            
        except Exception as e:
            logger.error(f"Erro ao identificar funcionalidades: {str(e)}")
            return ["Funcionalidades não identificadas devido a erro"]

    def _generate_modernization_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Gera recomendações de modernização baseadas na análise"""
        try:
            recommendations = []
            
            summary = analysis_results.get('summary', {})
            
            # Recomendações baseadas na estrutura
            if summary.get('total_forms', 0) > 0:
                recommendations.append("Converter formulários Delphi em APIs REST + frontend moderno")
            
            if summary.get('total_datamodules', 0) > 0:
                recommendations.append("Migrar DataModules para Services e Repositories Spring Boot")
            
            # Recomendações baseadas na complexidade
            complexity = summary.get('complexity_metrics', {})
            if isinstance(complexity, dict) and complexity.get('average_complexity', 0) > 10:
                recommendations.append("Refatorar métodos com alta complexidade ciclomática")
            
            # Recomendações gerais
            recommendations.extend([
                "Implementar arquitetura em camadas (Controller, Service, Repository)",
                "Adicionar validações Bean Validation",
                "Configurar Spring Security para autenticação/autorização",
                "Implementar testes unitários e de integração",
                "Configurar CI/CD para deploy automatizado"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {str(e)}")
            return ["Recomendações não disponíveis devido a erro"]
    
    # Placeholder para métodos adicionais que serão implementados conforme necessário
    def _extract_backend_elements(self, content: str) -> List[Dict]: 
        """Extrai elementos relacionados ao backend (DataModules, validações, etc.)"""
        backend_elements = []
        
        # Procura por componentes de dados
        data_components = re.findall(r'(TQuery|TTable|TDataSet|TClientDataSet|TADOQuery|TADOTable|TFDQuery|TFDTable)\s*:\s*(\w+)', content, re.IGNORECASE)
        for comp_type, comp_name in data_components:
            backend_elements.append({
                'type': 'data_component',
                'component_type': comp_type,
                'name': comp_name,
                'purpose': 'data_access'
            })
        
        # Procura por validações de negócio
        validation_patterns = re.findall(r'(function|procedure)\s+(\w*validat\w*|check\w*|verify\w*)', content, re.IGNORECASE)
        for func_type, func_name in validation_patterns:
            backend_elements.append({
                'type': 'validation',
                'function_type': func_type,
                'name': func_name,
                'purpose': 'business_validation'
            })
        
        return backend_elements
    
    def _extract_business_requirements(self) -> List[Dict]: return []
    def _identify_technical_requirements(self) -> List[Dict]: return []
    def _identify_architecture_pattern(self) -> str: return 'layered'
    def _identify_technology_stack(self) -> List[str]: return []
    def _assess_complexity_level(self) -> str: return 'medium'
    def _calculate_maintainability_score(self) -> float: return 0.7
    def _assess_modernization_readiness(self) -> str: return 'ready'
    def _identify_risk_factors(self) -> List[str]: return []
    def _identify_system_strengths(self) -> List[str]: return []
    def _identify_system_weaknesses(self) -> List[str]: return []
    
    def _calculate_project_size(self, delphi_files: Dict) -> str: return 'medium'
    def _identify_main_units(self, delphi_files: Dict) -> List[str]: return []
    def _detect_delphi_version(self, delphi_files: Dict) -> str: return 'unknown'
    def _detect_architecture_type(self, delphi_files: Dict) -> str: return 'desktop'
    def _extract_visibility_sections(self, content: str, class_name: str) -> Dict: return {}
    def _extract_class_methods_detailed(self, content: str, class_name: str) -> List[Dict]: return []
    def _extract_class_properties(self, content: str, class_name: str) -> List[Dict]: return []
    def _extract_class_fields(self, content: str, class_name: str) -> List[Dict]: return []
    def _extract_class_events(self, content: str, class_name: str) -> List[Dict]: return []
    def _infer_class_purpose(self, class_name: str, parent_class: str) -> str: return 'general'
    def _extract_procedure_body(self, content: str, proc_name: str) -> str: return ''
    def _parse_parameters(self, parameters: str) -> List[Dict]: return []
    def _calculate_function_complexity(self, body: str) -> int: return 1
    def _extract_function_calls(self, body: str) -> List[str]: return []
    def _infer_function_purpose(self, proc_name: str, body: str) -> str: return 'general'
    def _calculate_comment_ratio(self, content: str) -> float: return 0.1
    def _calculate_max_nesting_depth(self, content: str) -> int: return 1
    def extract_system_characteristics(self, units_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai características do sistema baseado na análise das units"""
        try:
            characteristics = {
                'architecture_pattern': 'Traditional VCL',
                'complexity_level': 'Medium',
                'maintainability_score': 0.0,
                'modernization_readiness': 'Requires Assessment',
                'technology_stack': ['Delphi/Object Pascal', 'VCL Components'],
                'strengths': [],
                'weaknesses': [],
                'risk_factors': []
            }
            
            # Calcula métricas agregadas
            total_units = len(units_analysis)
            total_complexity = 0
            high_complexity_units = 0
            
            for unit_name, unit_data in units_analysis.items():
                if 'complexity_metrics' in unit_data:
                    complexity = unit_data['complexity_metrics'].get('cyclomatic_complexity', 0)
                    total_complexity += complexity
                    
                    if complexity > 15:
                        high_complexity_units += 1
            
            # Determina nível de complexidade
            avg_complexity = total_complexity / max(total_units, 1)
            
            if avg_complexity <= 5:
                characteristics['complexity_level'] = 'Low'
                characteristics['modernization_readiness'] = 'Good'
            elif avg_complexity <= 10:
                characteristics['complexity_level'] = 'Medium'
                characteristics['modernization_readiness'] = 'Moderate'
            else:
                characteristics['complexity_level'] = 'High'
                characteristics['modernization_readiness'] = 'Complex'
            
            # Score de manutenibilidade (0-1)
            maintainability = 1.0 - (high_complexity_units / max(total_units, 1))
            characteristics['maintainability_score'] = max(0.0, maintainability)
            
            # Identifica padrões arquiteturais
            form_count = sum(1 for unit in units_analysis.values() 
                           if unit.get('unit_type') == 'form')
            datamodule_count = sum(1 for unit in units_analysis.values() 
                                 if unit.get('unit_type') == 'datamodule')
            
            if datamodule_count > 0:
                characteristics['architecture_pattern'] = 'Data Module Pattern'
                characteristics['strengths'].append('Separation of data access logic')
            
            if form_count > 5:
                characteristics['technology_stack'].append('Multiple Forms Architecture')
            
            # Identifica pontos fortes
            if avg_complexity < 8:
                characteristics['strengths'].append('Moderate complexity')
            if total_units < 50:
                characteristics['strengths'].append('Manageable codebase size')
            
            # Identifica pontos fracos
            if high_complexity_units > total_units * 0.3:
                characteristics['weaknesses'].append('High complexity in some modules')
                characteristics['risk_factors'].append('Complex modules may require refactoring')
            
            if total_units > 100:
                characteristics['weaknesses'].append('Large codebase')
                characteristics['risk_factors'].append('Extended migration timeline')
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Erro ao extrair características: {str(e)}")
            return {'error': str(e)}

    def identify_execution_flows(self, units_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Identifica fluxos de execução do sistema"""
        try:
            execution_flows = {
                'startup_sequence': [],
                'user_workflows': [],
                'error_handling_flows': [],
                'shutdown_sequence': []
            }
            
            # Identifica sequência de inicialização
            for unit_name, unit_data in units_analysis.items():
                if unit_data.get('unit_type') == 'form':
                    procedures = unit_data.get('procedures_functions', [])
                    
                    for proc in procedures:
                        proc_name = proc.get('name', '').lower()
                        
                        if 'create' in proc_name or 'formcreate' in proc_name:
                            execution_flows['startup_sequence'].append({
                                'description': f"Initialize {unit_name}",
                                'unit': unit_name,
                                'procedure': proc.get('name')
                            })
                        
                        elif 'destroy' in proc_name or 'formdestroy' in proc_name:
                            execution_flows['shutdown_sequence'].append({
                                'description': f"Cleanup {unit_name}",
                                'unit': unit_name,
                                'procedure': proc.get('name')
                            })
                        
                        elif 'click' in proc_name or 'execute' in proc_name:
                            execution_flows['user_workflows'].append({
                                'name': f"User Action: {proc.get('name')}",
                                'module': unit_name,
                                'description': f"User interaction in {unit_name}",
                                'steps': [f"User triggers {proc.get('name')}"]
                            })
            
            # Identifica tratamento de erros
            for unit_name, unit_data in units_analysis.items():
                procedures = unit_data.get('procedures_functions', [])
                
                for proc in procedures:
                    proc_name = proc.get('name', '').lower()
                    
                    if 'error' in proc_name or 'exception' in proc_name:
                        execution_flows['error_handling_flows'].append({
                            'type': 'Exception Handler',
                            'handling': f"Error handling in {unit_name}.{proc.get('name')}"
                        })
            
            return execution_flows
            
        except Exception as e:
            logger.error(f"Erro ao identificar fluxos de execução: {str(e)}")
            return {'error': str(e)}

    def map_data_flows(self, units_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia fluxos de dados do sistema"""
        try:
            data_flows = {
                'database_flows': [],
                'form_data_flows': [],
                'component_interactions': [],
                'data_transformations': []
            }
            
            # Analisa fluxos de banco de dados
            for unit_name, unit_data in units_analysis.items():
                if unit_data.get('unit_type') == 'datamodule':
                    datasets = unit_data.get('datasets', [])
                    
                    for dataset in datasets:
                        data_flows['database_flows'].append({
                            'source': 'Database',
                            'target': unit_name,
                            'dataset': dataset.get('name'),
                            'table': dataset.get('table_name', 'Unknown'),
                            'operations': dataset.get('operations', [])
                        })
            
            # Analisa fluxos entre formulários
            for unit_name, unit_data in units_analysis.items():
                if unit_data.get('unit_type') == 'form':
                    # Verifica campos de dados
                    components = unit_data.get('components', [])
                    
                    for component in components:
                        if component.get('type') in ['TEdit', 'TDBEdit', 'TMemo', 'TDBMemo']:
                            data_flows['form_data_flows'].append({
                                'form': unit_name,
                                'component': component.get('name'),
                                'type': component.get('type'),
                                'data_binding': component.get('datasource', None),
                                'flow_type': 'User Input'
                            })
                    
                    # Verifica procedimentos que manipulam dados
                    procedures = unit_data.get('procedures_functions', [])
                    
                    for proc in procedures:
                        proc_name = proc.get('name', '').lower()
                        
                        if any(keyword in proc_name for keyword in ['save', 'insert', 'update', 'delete']):
                            data_flows['data_transformations'].append({
                                'operation': proc.get('name'),
                                'unit': unit_name,
                                'type': 'Data Modification',
                                'description': f"Data operation in {unit_name}"
                            })
            
            # Analisa interações entre componentes
            for unit_name, unit_data in units_analysis.items():
                components = unit_data.get('components', [])
                
                for component in components:
                    if component.get('type') in ['TDataSource', 'TQuery', 'TTable']:
                        data_flows['component_interactions'].append({
                            'component': component.get('name'),
                            'type': component.get('type'),
                            'unit': unit_name,
                            'connections': component.get('properties', {}).get('connected_to', [])
                        })
            
            return data_flows
            
        except Exception as e:
            logger.error(f"Erro ao mapear fluxos de dados: {str(e)}")
            return {'error': str(e)}

    def extract_requirements(self, units_analysis: Dict[str, Any], project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai requisitos funcionais e não funcionais do sistema"""
        try:
            requirements = {
                'functional_requirements': [],
                'non_functional_requirements': [],
                'business_rules': [],
                'data_requirements': [],
                'interface_requirements': []
            }
            
            # Extrai requisitos funcionais baseados em formulários e operações
            for unit_name, unit_data in units_analysis.items():
                if unit_data.get('unit_type') == 'form':
                    # Requisitos baseados em formulários
                    form_caption = unit_data.get('caption', unit_name)
                    requirements['functional_requirements'].append({
                        'id': f"RF-{len(requirements['functional_requirements']) + 1:03d}",
                        'description': f"O sistema deve fornecer interface para {form_caption}",
                        'source': unit_name,
                        'type': 'User Interface',
                        'priority': 'High'
                    })
                    
                    # Requisitos baseados em componentes do formulário
                    components = unit_data.get('components', [])
                    for component in components:
                        comp_type = component.get('type', '')
                        
                        if comp_type in ['TDBGrid', 'TStringGrid']:
                            requirements['functional_requirements'].append({
                                'id': f"RF-{len(requirements['functional_requirements']) + 1:03d}",
                                'description': f"O sistema deve permitir visualização de dados em formato tabular",
                                'source': f"{unit_name}.{component.get('name')}",
                                'type': 'Data Display',
                                'priority': 'Medium'
                            })
                        
                        elif comp_type in ['TButton']:
                            button_name = component.get('name', '').lower()
                            if 'save' in button_name or 'salvar' in button_name:
                                requirements['functional_requirements'].append({
                                    'id': f"RF-{len(requirements['functional_requirements']) + 1:03d}",
                                    'description': f"O sistema deve permitir salvar dados",
                                    'source': f"{unit_name}.{component.get('name')}",
                                    'type': 'Data Persistence',
                                    'priority': 'High'
                                })
                
                elif unit_data.get('unit_type') == 'datamodule':
                    # Requisitos de dados baseados em datasets
                    datasets = unit_data.get('datasets', [])
                    for dataset in datasets:
                        table_name = dataset.get('table_name', 'Unknown')
                        requirements['data_requirements'].append({
                            'id': f"RD-{len(requirements['data_requirements']) + 1:03d}",
                            'description': f"O sistema deve gerenciar dados da entidade {table_name}",
                            'source': f"{unit_name}.{dataset.get('name')}",
                            'entity': table_name,
                            'operations': dataset.get('operations', [])
                        })
            
            # Extrai regras de negócio baseadas em validações
            for unit_name, unit_data in units_analysis.items():
                procedures = unit_data.get('procedures_functions', [])
                
                for proc in procedures:
                    proc_name = proc.get('name', '').lower()
                    
                    if 'validat' in proc_name or 'verif' in proc_name:
                        requirements['business_rules'].append({
                            'id': f"RN-{len(requirements['business_rules']) + 1:03d}",
                            'description': f"Validação de negócio: {proc.get('name')}",
                            'source': f"{unit_name}.{proc.get('name')}",
                            'type': 'Validation Rule',
                            'complexity': proc.get('complexity_metrics', {}).get('cyclomatic_complexity', 1)
                        })
            
            # Requisitos não funcionais baseados na análise do projeto
            total_files = project_info.get('total_files', 0)
            
            requirements['non_functional_requirements'] = [
                {
                    'id': 'RNF-001',
                    'category': 'Performance',
                    'description': 'O sistema deve responder às solicitações em menos de 3 segundos',
                    'metric': 'Response Time < 3s',
                    'priority': 'High'
                },
                {
                    'id': 'RNF-002',
                    'category': 'Scalability',
                    'description': f'O sistema deve suportar expansão baseada em {total_files} módulos originais',
                    'metric': f'Modular architecture for {total_files} modules',
                    'priority': 'Medium'
                },
                {
                    'id': 'RNF-003',
                    'category': 'Maintainability',
                    'description': 'O código deve seguir padrões Spring Boot para facilitar manutenção',
                    'metric': 'Spring Boot best practices compliance',
                    'priority': 'High'
                },
                {
                    'id': 'RNF-004',
                    'category': 'Security',
                    'description': 'O sistema deve implementar autenticação e autorização',
                    'metric': 'Spring Security implementation',
                    'priority': 'High'
                }
            ]
            
            # Requisitos de interface baseados nos formulários
            form_count = sum(1 for unit in units_analysis.values() if unit.get('unit_type') == 'form')
            
            requirements['interface_requirements'] = [
                {
                    'id': 'RI-001',
                    'description': f'Interface web responsiva para {form_count} telas principais',
                    'technology': 'Spring MVC + Thymeleaf ou REST API',
                    'forms_count': form_count
                },
                {
                    'id': 'RI-002',
                    'description': 'Interface deve manter funcionalidades equivalentes ao sistema original',
                    'compatibility': 'Functional equivalent to Delphi forms'
                }
            ]
            
            return requirements
            
        except Exception as e:
            logger.error(f"Erro ao extrair requisitos: {str(e)}")
            return {'error': str(e)}

    def _find_delphi_files(self, project_path: str) -> Dict[str, List[str]]:
        """Encontra todos os arquivos Delphi no projeto"""
        delphi_files = {
            'pas': [],  # Pascal units
            'dfm': [],  # Form files
            'dpr': [],  # Project files
            'dpk': [],  # Package files
            'inc': []   # Include files
        }
        
        try:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext == '.pas':
                        delphi_files['pas'].append(file_path)
                    elif file_ext == '.dfm':
                        delphi_files['dfm'].append(file_path)
                    elif file_ext == '.dpr':
                        delphi_files['dpr'].append(file_path)
                    elif file_ext == '.dpk':
                        delphi_files['dpk'].append(file_path)
                    elif file_ext == '.inc':
                        delphi_files['inc'].append(file_path)
            
            logger.info(f"Arquivos encontrados: {sum(len(files) for files in delphi_files.values())} total")
            return delphi_files
            
        except Exception as e:
            logger.error(f"Erro ao encontrar arquivos Delphi: {str(e)}")
            return delphi_files
    
    def _read_file_safe(self, file_path: str) -> str:
        """Lê arquivo de forma segura com tratamento de encoding"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
            try:
                with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                    return f.read()
            except:
                return ""

    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extrai informações sobre classes do código Delphi"""
        classes = []
        
        try:
            # Padrão para identificar classes
            class_pattern = r'type\s+(\w+)\s*=\s*class\s*(?:\(([^)]+)\))?\s*([^;]+);'
            
            matches = re.finditer(class_pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                class_name = match.group(1)
                parent_class = match.group(2) if match.group(2) else None
                class_body = match.group(3) if match.group(3) else ""
                
                # Extrai métodos da classe
                methods = self._extract_class_methods(class_body)
                
                # Extrai propriedades da classe
                properties = self._extract_class_properties(class_body)
                
                class_info = {
                    'name': class_name,
                    'parent_class': parent_class,
                    'methods': methods,
                    'properties': properties,
                    'is_form': 'TForm' in (parent_class or ''),
                    'is_datamodule': 'TDataModule' in (parent_class or ''),
                    'visibility_sections': self._extract_visibility_sections(class_body)
                }
                
                classes.append(class_info)
            
            return classes
            
        except Exception as e:
            logger.error(f"Erro ao extrair classes: {str(e)}")
            return []

    def _extract_class_methods(self, class_body: str) -> List[Dict[str, Any]]:
        """Extrai métodos de uma classe"""
        methods = []
        
        try:
            # Padrões para procedimentos e funções
            procedure_pattern = r'(?:procedure|function)\s+(\w+)(?:\([^)]*\))?(?:\s*:\s*\w+)?;'
            
            matches = re.finditer(procedure_pattern, class_body, re.IGNORECASE)
            
            for match in matches:
                method_name = match.group(1)
                
                methods.append({
                    'name': method_name,
                    'type': 'procedure' if match.group(0).lower().startswith('procedure') else 'function',
                    'is_event_handler': method_name.lower().startswith('on') or 'click' in method_name.lower(),
                    'visibility': self._determine_method_visibility(match.start(), class_body)
                })
            
            return methods
            
        except Exception as e:
            logger.error(f"Erro ao extrair métodos: {str(e)}")
            return []

    def _extract_class_properties(self, class_body: str) -> List[Dict[str, Any]]:
        """Extrai propriedades de uma classe"""
        properties = []
        
        try:
            # Padrão para propriedades
            property_pattern = r'property\s+(\w+)\s*:\s*(\w+)(?:\s+read\s+(\w+))?(?:\s+write\s+(\w+))?;'
            
            matches = re.finditer(property_pattern, class_body, re.IGNORECASE)
            
            for match in matches:
                prop_name = match.group(1)
                prop_type = match.group(2)
                read_method = match.group(3)
                write_method = match.group(4)
                
                properties.append({
                    'name': prop_name,
                    'type': prop_type,
                    'read_method': read_method,
                    'write_method': write_method,
                    'is_read_only': read_method and not write_method
                })
            
            return properties
            
        except Exception as e:
            logger.error(f"Erro ao extrair propriedades: {str(e)}")
            return []

    def _extract_visibility_sections(self, class_body: str) -> Dict[str, List[str]]:
        """Extrai seções de visibilidade da classe"""
        sections = {
            'private': [],
            'protected': [],
            'public': [],
            'published': []
        }
        
        try:
            # Divide o corpo da classe por seções de visibilidade
            current_section = 'private'  # Padrão Delphi
            
            lines = class_body.split('\n')
            for line in lines:
                line = line.strip().lower()
                
                if line.startswith('private'):
                    current_section = 'private'
                elif line.startswith('protected'):
                    current_section = 'protected'
                elif line.startswith('public'):
                    current_section = 'public'
                elif line.startswith('published'):
                    current_section = 'published'
                elif line and not line.startswith('//'):
                    sections[current_section].append(line)
            
            return sections
            
        except Exception as e:
            logger.error(f"Erro ao extrair seções de visibilidade: {str(e)}")
            return sections

    def _determine_method_visibility(self, method_position: int, class_body: str) -> str:
        """Determina a visibilidade de um método baseado na posição"""
        try:
            # Encontra a seção de visibilidade mais próxima antes do método
            text_before = class_body[:method_position].lower()
            
            visibility_keywords = ['published', 'public', 'protected', 'private']
            
            for keyword in visibility_keywords:
                if keyword in text_before:
                    last_occurrence = text_before.rfind(keyword)
                    if last_occurrence != -1:
                        return keyword
            
            return 'private'  # Padrão Delphi
            
        except Exception as e:
            logger.error(f"Erro ao determinar visibilidade: {str(e)}")
            return 'private'

    def _extract_procedures_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extrai procedimentos e funções globais"""
        procedures = []
        
        try:
            # Padrão para procedimentos e funções globais
            proc_pattern = r'(?:procedure|function)\s+(\w+)(?:\([^)]*\))?(?:\s*:\s*(\w+))?;'
            
            matches = re.finditer(proc_pattern, content, re.IGNORECASE)
            
            for match in matches:
                proc_name = match.group(1)
                return_type = match.group(2)
                
                procedures.append({
                    'name': proc_name,
                    'type': 'function' if return_type else 'procedure',
                    'return_type': return_type,
                    'complexity': self._calculate_method_complexity(match.start(), content)
                })
            
            return procedures
            
        except Exception as e:
            logger.error(f"Erro ao extrair procedimentos/funções: {str(e)}")
            return []

    def _extract_uses_units(self, content: str) -> List[str]:
        """Extrai units usadas no código"""
        uses_units = []
        
        try:
            # Padrão para cláusulas uses
            uses_pattern = r'uses\s+([^;]+);'
            
            matches = re.finditer(uses_pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                units_text = match.group(1)
                # Remove comentários e espaços
                units_text = re.sub(r'\{[^}]*\}', '', units_text)
                units_text = re.sub(r'//.*$', '', units_text, flags=re.MULTILINE)
                
                # Separa por vírgula
                units = [unit.strip() for unit in units_text.split(',')]
                uses_units.extend(units)
            
            return list(set(uses_units))  # Remove duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao extrair uses: {str(e)}")
            return []

    def _calculate_complexity(self, content: str) -> Dict[str, Any]:
        """Calcula métricas de complexidade do código"""
        try:
            lines = content.split('\n')
            
            # Conta estruturas de controle
            control_structures = ['if', 'for', 'while', 'repeat', 'case', 'try']
            complexity_count = 0
            
            for line in lines:
                line_lower = line.lower().strip()
                for structure in control_structures:
                    if line_lower.startswith(structure + ' '):
                        complexity_count += 1
            
            return {
                'lines_of_code': len([line for line in lines if line.strip()]),
                'cyclomatic_complexity': max(1, complexity_count),
                'comment_lines': len([line for line in lines if line.strip().startswith('//')]),
                'blank_lines': len([line for line in lines if not line.strip()])
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular complexidade: {str(e)}")
            return {
                'lines_of_code': 0,
                'cyclomatic_complexity': 1,
                'comment_lines': 0,
                'blank_lines': 0
            }

    def _calculate_method_complexity(self, method_start: int, content: str) -> int:
        """Calcula complexidade de um método específico"""
        try:
            # Encontra o final do método
            method_end = content.find('end;', method_start)
            if method_end == -1:
                return 1
            
            method_content = content[method_start:method_end]
            control_structures = ['if', 'for', 'while', 'repeat', 'case']
            
            complexity = 1  # Complexidade base
            for structure in control_structures:
                complexity += method_content.lower().count(structure + ' ')
            
            return complexity
            
        except Exception as e:
            logger.error(f"Erro ao calcular complexidade do método: {str(e)}")
            return 1
    
    def _classify_unit_type(self, content: str, unit_name: str) -> str:
        """Classifica o tipo da unit baseado no conteúdo"""
        content_lower = content.lower()
        unit_name_lower = unit_name.lower()
        
        if 'tform' in content_lower or 'inherited' in content_lower:
            return 'form'
        elif 'tdatamodule' in content_lower or 'datamodule' in content_lower:
            return 'datamodule'
        elif 'service' in unit_name_lower or 'manager' in unit_name_lower:
            return 'service'
        elif 'util' in unit_name_lower or 'helper' in unit_name_lower:
            return 'utility'
        elif 'class(' in content_lower or 'class ' in content_lower:
            return 'class'
        elif 'interface' in content_lower and 'implementation' in content_lower:
            return 'unit'
        else:
            return 'unknown'

    def extract_business_logic(self, units_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai lógica de negócio das unidades analisadas
        
        Args:
            units_analysis: Análise das unidades do projeto
            
        Returns:
            Análise da lógica de negócio
        """
        try:
            # Verifica se tem prompts especializados
            if not hasattr(self, 'using_specialized_prompts'):
                self.using_specialized_prompts = self.prompt_manager is not None
            
            # Análise básica da lógica de negócio
            business_logic = {
                'services': [],
                'entities': [],
                'utilities': [],
                'forms': [],
                'data_modules': []
            }
            
            # Processa cada unidade
            for unit_name, unit_data in units_analysis.items():
                if isinstance(unit_data, dict):
                    unit_type = unit_data.get('type', 'unknown')
                    
                    if unit_type == 'service':
                        business_logic['services'].append({
                            'name': unit_name,
                            'methods': unit_data.get('methods', []),
                            'properties': unit_data.get('properties', [])
                        })
                    elif unit_type == 'form':
                        business_logic['forms'].append({
                            'name': unit_name,
                            'controls': unit_data.get('controls', []),
                            'events': unit_data.get('events', [])
                        })
                    elif unit_type == 'datamodule':
                        business_logic['data_modules'].append({
                            'name': unit_name,
                            'components': unit_data.get('components', []),
                            'connections': unit_data.get('connections', [])
                        })
                    elif unit_type == 'class':
                        business_logic['entities'].append({
                            'name': unit_name,
                            'properties': unit_data.get('properties', []),
                            'methods': unit_data.get('methods', [])
                        })
                    elif unit_type == 'utility':
                        business_logic['utilities'].append({
                            'name': unit_name,
                            'functions': unit_data.get('functions', [])
                        })
            
            # Enriquece com análise baseada em prompts se disponível
            if self.using_specialized_prompts and self.prompt_manager:
                try:
                    # Usa prompt de análise de backend (substituindo business_analysis)
                    backend_prompt = self.prompt_manager.get_backend_analysis_prompt()
                    
                    # Gera contexto da análise
                    context = f"Análise de unidades: {str(units_analysis)[:1000]}..."
                    
                    # Gera análise com IA
                    enhanced_analysis = self._generate_with_ai(backend_prompt, context)
                    business_logic['enhanced_analysis'] = enhanced_analysis
                    business_logic['used_specialized_prompts'] = True
                    
                    logger.info("✅ Análise de negócio com prompts especializados concluída")
                    
                except Exception as e:
                    logger.error(f"❌ Erro na análise de negócio com prompts: {str(e)}")
                    business_logic['enhanced_analysis'] = "Erro na análise com prompts especializados"
                    business_logic['used_specialized_prompts'] = False
            else:
                business_logic['used_specialized_prompts'] = False
            
            return business_logic
            
        except Exception as e:
            logger.error(f"❌ Erro na extração de lógica de negócio: {str(e)}")
            return {
                'error': str(e),
                'services': [],
                'entities': [],
                'utilities': [],
                'forms': [],
                'data_modules': []
            }