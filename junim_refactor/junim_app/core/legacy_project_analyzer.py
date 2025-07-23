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
            'groq_model': self.groq_model,
            'ollama_model': 'codellama:7b',  # Modelo padrão Ollama
            'ollama_url': 'http://localhost:11434'
        }
        
        # Cria instância do serviço com prompt_manager
        self.llm_service = LLMService(config, prompt_manager=self.prompt_manager)
        logger.info("✅ LLM Service inicializado com codellama:7b")
    
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
        """
        Analisa projeto Delphi com foco em estrutura e especificidade para documentação
        VERSÃO MELHORADA: Análise hierárquica + extração específica + LLM contextual
        """
        start_time = time.time()
        logger.info(f"🚀 Iniciando análise MELHORADA do projeto: {project_path}")
        
        # Se project_name não foi fornecido, extrai do caminho
        if project_name is None:
            project_name = Path(project_path).stem
        
        try:
            # 1. ANÁLISE HIERÁRQUICA DO PROJETO
            hierarchy = self._analyze_project_hierarchy(project_path)
            logger.info(f"📁 Hierarquia analisada: {hierarchy['total_files']} arquivos, {len(hierarchy['form_units'])} forms, {len(hierarchy['utility_units'])} units")
            
            # 2. COLETA E ANÁLISE DETALHADA DOS ARQUIVOS
            detailed_analysis = self._collect_and_analyze_files_detailed(project_path, hierarchy)
            
            if not detailed_analysis['files']:
                logger.warning("⚠️ Nenhum arquivo Delphi encontrado no projeto extraído")
                return self._create_empty_analysis_result(project_name, project_path)
            
            logger.info(f"� Analisados {len(detailed_analysis['files'])} arquivos em detalhes")
            
            # 3. SÍNTESE DOS RESULTADOS DA ANÁLISE
            synthesis = self._synthesize_analysis_results(detailed_analysis, hierarchy, project_name)
            
            # 4. CONTEXTO MELHORADO PARA LLM
            enhanced_context = self._prepare_enhanced_context_for_llm(synthesis, project_name)
            
            # 5. ANÁLISE LLM COM CONTEXTO ESPECÍFICO
            if self.llm_service and PROMPTS_AVAILABLE:
                llm_analysis = self._analyze_with_enhanced_llm_context(enhanced_context, project_name)
                synthesis['llm_analysis'] = llm_analysis
                synthesis['analysis_method'] = 'enhanced_llm'
            else:
                synthesis['analysis_method'] = 'structured_only'
            
            elapsed_time = time.time() - start_time
            logger.info(f"✅ Análise melhorada concluída em {elapsed_time:.2f}s")
            logger.info(f"📊 Resultados: {len(synthesis['functions'])} funções, {len(synthesis['classes'])} classes identificadas")
            
            return synthesis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise melhorada: {str(e)}")
            # Fallback para análise estruturada tradicional
            logger.info("🔄 Tentando análise estruturada como fallback...")
            return self._fallback_to_structured_analysis(project_path, project_name)
    
    def _collect_and_analyze_files_detailed(self, project_path: str, hierarchy: Dict[str, Any]) -> Dict[str, Any]:
        """Coleta e analisa arquivos de forma detalhada"""
        detailed_files = []
        summary = {
            'total_functions': 0,
            'total_classes': 0,
            'total_events': 0,
            'total_lines': 0
        }
        
        # Analisa todos os arquivos identificados na hierarquia
        all_units = (hierarchy['form_units'] + hierarchy['datamodule_units'] + 
                    hierarchy['main_units'] + hierarchy['utility_units'])
        
        for unit_info in all_units:
            file_path = os.path.join(project_path, unit_info['path'], unit_info['name'])
            if unit_info['path'] == '.':
                file_path = os.path.join(project_path, unit_info['name'])
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Análise estruturada do arquivo
                file_analysis = {
                    'filename': unit_info['name'],
                    'path': unit_info['path'],
                    'type': unit_info['type'],
                    'content_preview': content[:500],
                    'line_count': len(content.splitlines()),
                    'functions': [],
                    'classes': [],
                    'dependencies': []
                }
                
                # Extração estruturada
                self._analyze_pascal_unit_structured(content, file_analysis, unit_info['name'])
                
                # NOVA: Extração específica de entidades de banco de dados
                database_entities = self._extract_database_entities_from_unit(content, unit_info['name'])
                file_analysis['database_entities'] = database_entities
                
                # NOVA: Extração específica de formulários CRUD
                form_entities = self._extract_form_crud_entities(content, unit_info['name'])
                file_analysis['form_entities'] = form_entities
                
                # Atualiza estatísticas
                summary['total_functions'] += len(file_analysis.get('functions', []))
                summary['total_classes'] += len(file_analysis.get('classes', []))
                summary['total_events'] += len([f for f in file_analysis.get('functions', []) if f.get('is_event_handler', False)])
                summary['total_lines'] += file_analysis['line_count']
                
                detailed_files.append(file_analysis)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao analisar {unit_info['name']}: {e}")
        
        return {
            'files': detailed_files,
            'summary': summary
        }
    
    def _extract_database_entities_from_unit(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Extrai entidades de banco de dados de uma unit Delphi"""
        entities = []
        
        # Procurar por SQL statements para identificar tabelas
        sql_patterns = [
            r'(?:SELECT|FROM|INSERT\s+INTO|UPDATE)\s+[*\w\s,]+\s+FROM\s+(\w+)',
            r'(?:INSERT\s+INTO|UPDATE)\s+(\w+)',
            r'(?:DELETE\s+FROM)\s+(\w+)'
        ]
        
        table_names = set()
        for pattern in sql_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    table_names.update([t for t in match if t and len(t) > 2])
                elif match and len(match) > 2:
                    table_names.add(match)
        
        # Procurar por DataSet assignments (ex: DataSet := DataModule1.QryProdutos)
        dataset_pattern = r'DataSet\s*:=\s*\w+\.(\w+)'
        dataset_matches = re.findall(dataset_pattern, content, re.IGNORECASE)
        
        for dataset in dataset_matches:
            if 'qry' in dataset.lower() or 'query' in dataset.lower():
                # Extrair nome da tabela do nome da query
                table_name = dataset.replace('Qry', '').replace('Query', '').replace('qry', '')
                if table_name and len(table_name) > 2:
                    table_names.add(table_name)
        
        # Procurar por FieldByName para identificar campos
        field_pattern = r'FieldByName\([\'"](\w+)[\'"]\)'
        field_matches = re.findall(field_pattern, content, re.IGNORECASE)
        
        # Criar entidades para cada tabela identificada
        for table_name in table_names:
            entity_fields = self._extract_entity_fields_from_content(content, table_name, field_matches)
            operations = self._extract_crud_operations_from_content(content)
            validations = self._extract_validations_from_content(content)
            
            entities.append({
                'name': table_name.capitalize(),
                'table_name': table_name.lower(),
                'type': 'database_entity',
                'source_file': filename,
                'fields': entity_fields,
                'operations': operations,
                'validations': validations
            })
        
        return entities
    
    def _extract_form_crud_entities(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Extrai informações de formulários CRUD"""
        entities = []
        
        # Procurar por declaração de classe de formulário
        form_pattern = r'type\s+(\w*Form\w*)\s*=\s*class\s*\(TForm\)'
        form_matches = re.findall(form_pattern, content, re.IGNORECASE)
        
        for form_name in form_matches:
            # Extrair controles de dados do formulário
            db_controls = self._extract_db_controls_from_content(content)
            buttons = self._extract_form_buttons_from_content(content)
            validations = self._extract_validations_from_content(content)
            
            # Determinar se é um form CRUD baseado nos botões
            is_crud_form = any(btn.lower() in ['btnnovo', 'btnsalvar', 'btnexcluir'] for btn in buttons)
            
            if is_crud_form:
                entities.append({
                    'name': form_name,
                    'type': 'crud_form',
                    'source_file': filename,
                    'db_controls': db_controls,
                    'crud_buttons': buttons,
                    'validations': validations,
                    'crud_operations': self._map_buttons_to_operations(buttons)
                })
        
        return entities
    
    def _extract_entity_fields_from_content(self, content: str, table_name: str, all_fields: List[str]) -> List[Dict[str, Any]]:
        """Extrai campos específicos de uma entidade baseado no contexto"""
        fields = []
        
        # Campos padrão baseado no nome da tabela
        if 'produto' in table_name.lower():
            standard_fields = [
                {'name': 'id', 'type': 'Long', 'required': True, 'primary_key': True},
                {'name': 'nome', 'type': 'String', 'required': True},
                {'name': 'descricao', 'type': 'String', 'required': False},
                {'name': 'preco', 'type': 'BigDecimal', 'required': True, 'validation': 'positive'},
                {'name': 'estoque', 'type': 'Integer', 'required': False, 'default': 0},
                {'name': 'ativo', 'type': 'Boolean', 'required': False, 'default': True}
            ]
        elif 'client' in table_name.lower():
            standard_fields = [
                {'name': 'id', 'type': 'Long', 'required': True, 'primary_key': True},
                {'name': 'nome', 'type': 'String', 'required': True},
                {'name': 'email', 'type': 'String', 'required': False, 'validation': 'email'},
                {'name': 'telefone', 'type': 'String', 'required': False},
                {'name': 'endereco', 'type': 'String', 'required': False},
                {'name': 'dataCadastro', 'type': 'LocalDate', 'required': False}
            ]
        elif 'venda' in table_name.lower() or 'pedido' in table_name.lower():
            standard_fields = [
                {'name': 'id', 'type': 'Long', 'required': True, 'primary_key': True},
                {'name': 'clienteId', 'type': 'Long', 'required': True, 'foreign_key': 'Cliente'},
                {'name': 'produtoId', 'type': 'Long', 'required': True, 'foreign_key': 'Produto'},
                {'name': 'quantidade', 'type': 'Integer', 'required': True, 'validation': 'positive'},
                {'name': 'precoTotal', 'type': 'BigDecimal', 'required': True},
                {'name': 'dataVenda', 'type': 'LocalDate', 'required': False}
            ]
        else:
            standard_fields = [
                {'name': 'id', 'type': 'Long', 'required': True, 'primary_key': True},
                {'name': 'nome', 'type': 'String', 'required': True},
                {'name': 'ativo', 'type': 'Boolean', 'required': False, 'default': True}
            ]
        
        # Marcar campos que foram encontrados no código
        found_fields = {field.lower() for field in all_fields}
        for field in standard_fields:
            field['found_in_code'] = field['name'].lower() in found_fields
        
        return standard_fields
    
    def _extract_crud_operations_from_content(self, content: str) -> List[str]:
        """Extrai operações CRUD identificadas no código"""
        operations = []
        
        content_lower = content.lower()
        if 'append' in content_lower or 'insert' in content_lower:
            operations.append('CREATE')
        if 'post' in content_lower or 'update' in content_lower:
            operations.append('UPDATE')
        if 'delete' in content_lower:
            operations.append('DELETE')
        if 'open' in content_lower or 'select' in content_lower:
            operations.append('READ')
        
        return operations
    
    def _extract_validations_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extrai validações do código Delphi"""
        validations = []
        
        validation_patterns = [
            {
                'pattern': r'if\s+.*\.Text\s*=\s*[\'\']\s*then.*obrigatório',
                'type': 'required_field',
                'field': 'nome',
                'message': 'Campo obrigatório'
            },
            {
                'pattern': r'if\s+.*\.AsFloat\s*<=\s*0.*maior.*zero',
                'type': 'positive_number', 
                'field': 'preco',
                'message': 'Deve ser maior que zero'
            },
            {
                'pattern': r'MessageDlg.*Confirma.*exclusão',
                'type': 'delete_confirmation',
                'field': None,
                'message': 'Confirmação de exclusão'
            }
        ]
        
        for validation_def in validation_patterns:
            if re.search(validation_def['pattern'], content, re.IGNORECASE):
                validations.append({
                    'type': validation_def['type'],
                    'field': validation_def['field'],
                    'message': validation_def['message'],
                    'found': True
                })
        
        return validations
    
    def _extract_db_controls_from_content(self, content: str) -> List[Dict[str, str]]:
        """Extrai controles de banco de dados do formulário"""
        controls = []
        
        db_patterns = [
            (r'(DBEdit\d*)\s*:\s*TDBEdit', 'text_input'),
            (r'(DBCheckBox\d*)\s*:\s*TDBCheckBox', 'checkbox'),
            (r'(DBGrid\d*)\s*:\s*TDBGrid', 'grid'),
            (r'(DBNavigator\d*)\s*:\s*TDBNavigator', 'navigator'),
            (r'(DataSource\d*)\s*:\s*TDataSource', 'datasource')
        ]
        
        for pattern, control_type in db_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                controls.append({
                    'name': match,
                    'type': control_type
                })
        
        return controls
    
    def _extract_form_buttons_from_content(self, content: str) -> List[str]:
        """Extrai botões do formulário"""
        button_pattern = r'(btn\w+)\s*:\s*TButton'
        return re.findall(button_pattern, content, re.IGNORECASE)
    
    def _map_buttons_to_operations(self, buttons: List[str]) -> Dict[str, str]:
        """Mapeia botões para operações CRUD"""
        operations = {}
        
        for button in buttons:
            button_lower = button.lower()
            if 'novo' in button_lower or 'add' in button_lower or 'create' in button_lower:
                operations['CREATE'] = button
            elif 'salvar' in button_lower or 'save' in button_lower or 'update' in button_lower:
                operations['UPDATE'] = button
            elif 'excluir' in button_lower or 'delete' in button_lower or 'remove' in button_lower:
                operations['DELETE'] = button
            elif 'pesquisar' in button_lower or 'search' in button_lower or 'find' in button_lower:
                operations['SEARCH'] = button
            elif 'cancelar' in button_lower or 'cancel' in button_lower:
                operations['CANCEL'] = button
        
        return operations
    
    def _synthesize_analysis_results(self, detailed_analysis: Dict[str, Any], hierarchy: Dict[str, Any], project_name: str) -> Dict[str, Any]:
        """Sintetiza os resultados da análise em formato estruturado"""
        synthesis = {
            'project_name': project_name,
            'analysis_timestamp': datetime.now().isoformat(),
            'hierarchy': hierarchy,
            'files_analyzed': {
                'total_files': len(detailed_analysis['files']),
                'files': detailed_analysis['files']
            },
            'functions': [],
            'classes': [],
            'events': [],
            'dependencies': set(),
            'database_entities': [],
            'form_entities': [],
            'crud_summary': {
                'entities_with_crud': [],
                'operations_found': set(),
                'validations_found': []
            },
            'project_statistics': {
                'total_lines': detailed_analysis['summary']['total_lines'],
                'total_functions': detailed_analysis['summary']['total_functions'],
                'total_classes': detailed_analysis['summary']['total_classes'],
                'total_events': detailed_analysis['summary']['total_events'],
                'form_count': len(hierarchy['form_units']),
                'utility_count': len(hierarchy['utility_units']),
                'datamodule_count': len(hierarchy['datamodule_units'])
            }
        }
        
        # Consolida funções, classes e dependências
        for file_data in detailed_analysis['files']:
            # Funções
            for func in file_data.get('functions', []):
                func['source_file'] = file_data['filename']
                synthesis['functions'].append(func)
            
            # Classes
            for cls in file_data.get('classes', []):
                cls['source_file'] = file_data['filename']
                synthesis['classes'].append(cls)
            
            # Eventos
            for func in file_data.get('functions', []):
                if func.get('is_event_handler', False):
                    func['source_file'] = file_data['filename']
                    synthesis['events'].append(func)
            
            # Dependências
            for dep in file_data.get('dependencies', []):
                synthesis['dependencies'].add(dep)
            
            # NOVO: Entidades de banco de dados
            for entity in file_data.get('database_entities', []):
                synthesis['database_entities'].append(entity)
                # Adicionar operações encontradas ao resumo
                for op in entity.get('operations', []):
                    synthesis['crud_summary']['operations_found'].add(op)
                # Adicionar validações encontradas
                synthesis['crud_summary']['validations_found'].extend(entity.get('validations', []))
            
            # NOVO: Entidades de formulários
            for form_entity in file_data.get('form_entities', []):
                synthesis['form_entities'].append(form_entity)
                # Se tem operações CRUD, adicionar à lista
                if form_entity.get('crud_operations'):
                    synthesis['crud_summary']['entities_with_crud'].append({
                        'form_name': form_entity['name'],
                        'operations': form_entity['crud_operations'],
                        'source_file': form_entity['source_file']
                    })
        
        synthesis['dependencies'] = list(synthesis['dependencies'])
        synthesis['crud_summary']['operations_found'] = list(synthesis['crud_summary']['operations_found'])
        
        # Adicionar estatísticas de entidades
        synthesis['project_statistics']['database_entities_count'] = len(synthesis['database_entities'])
        synthesis['project_statistics']['form_entities_count'] = len(synthesis['form_entities'])
        synthesis['project_statistics']['crud_forms_count'] = len(synthesis['crud_summary']['entities_with_crud'])
        
        return synthesis
    
    def _prepare_enhanced_context_for_llm(self, synthesis: Dict[str, Any], project_name: str) -> str:
        """Prepara contexto rico e específico para o LLM"""
        context_parts = []
        
        # Cabeçalho específico do projeto
        context_parts.append(f"=== ANÁLISE ESPECÍFICA: {project_name} ===")
        context_parts.append(f"Data: {synthesis['analysis_timestamp']}")
        
        # Estatísticas gerais
        stats = synthesis['project_statistics']
        context_parts.append(f"\n📊 ESTATÍSTICAS DO PROJETO:")
        context_parts.append(f"• Total de linhas: {stats['total_lines']}")
        context_parts.append(f"• Total de funções: {stats['total_functions']}")
        context_parts.append(f"• Total de classes: {stats['total_classes']}")
        context_parts.append(f"• Total de eventos: {stats['total_events']}")
        context_parts.append(f"• Formulários: {stats['form_count']}")
        context_parts.append(f"• Units utilitárias: {stats['utility_count']}")
        context_parts.append(f"• Data Modules: {stats['datamodule_count']}")
        
        # Funções específicas identificadas
        if synthesis['functions']:
            context_parts.append(f"\n⚙️ FUNÇÕES IDENTIFICADAS ({len(synthesis['functions'])}):")
            for i, func in enumerate(synthesis['functions'][:10]):  # Limita a 10 para não sobrecarregar
                func_desc = f"• {func['name']}({len(func.get('parameters', []))} params)"
                if func.get('return_type'):
                    func_desc += f" -> {func['return_type']}"
                if func.get('category'):
                    func_desc += f" [{func['category']}]"
                context_parts.append(func_desc)
            if len(synthesis['functions']) > 10:
                context_parts.append(f"... e mais {len(synthesis['functions']) - 10} funções")
        
        # Classes específicas identificadas
        if synthesis['classes']:
            context_parts.append(f"\n📦 CLASSES IDENTIFICADAS ({len(synthesis['classes'])}):")
            for cls in synthesis['classes'][:5]:  # Limita a 5
                cls_desc = f"• {cls['name']}"
                if cls.get('parent_class'):
                    cls_desc += f" extends {cls['parent_class']}"
                if cls.get('class_type'):
                    cls_desc += f" [{cls['class_type']}]"
                context_parts.append(cls_desc)
                
                # Métodos da classe
                if cls.get('methods'):
                    methods = [m['name'] for m in cls['methods'][:3]]
                    context_parts.append(f"  - Métodos: {', '.join(methods)}")
                
                # Propriedades da classe
                if cls.get('properties'):
                    props = [p['name'] for p in cls['properties'][:3]]
                    context_parts.append(f"  - Propriedades: {', '.join(props)}")
        
        # Dependências identificadas
        if synthesis['dependencies']:
            context_parts.append(f"\n🔗 DEPENDÊNCIAS IDENTIFICADAS:")
            deps = synthesis['dependencies'][:8]  # Limita a 8
            context_parts.append(f"• Uses: {', '.join(deps)}")
        
        # Arquitetura identificada
        context_parts.append(f"\n🏗️ ARQUITETURA IDENTIFICADA:")
        hierarchy = synthesis['hierarchy']
        if hierarchy['form_units']:
            form_names = [f['name'] for f in hierarchy['form_units'][:3]]
            context_parts.append(f"• Forms principais: {', '.join(form_names)}")
        if hierarchy['datamodule_units']:
            dm_names = [f['name'] for f in hierarchy['datamodule_units']]
            context_parts.append(f"• Data Modules: {', '.join(dm_names)}")
        
        # Instruções para o LLM
        context_parts.append(f"\n🎯 INSTRUÇÕES PARA ANÁLISE:")
        context_parts.append("• Use APENAS os dados específicos fornecidos acima")
        context_parts.append("• Mencione nomes reais de classes, funções e arquivos identificados")
        context_parts.append("• Identifique a funcionalidade principal baseada nos nomes das funções")
        context_parts.append("• Sugira mapeamentos específicos para Spring Boot baseado na arquitetura identificada")
        context_parts.append("• Foque em informações técnicas precisas e evite generalidades")
        
        return "\n".join(context_parts)
    
    def _analyze_with_enhanced_llm_context(self, enhanced_context: str, project_name: str) -> str:
        """Análise LLM com contexto melhorado"""
        try:
            if not self.prompt_manager:
                logger.warning("⚠️ PromptManager não disponível para análise LLM")
                return "Análise LLM não realizada - PromptManager indisponível"
            
            # Obtém prompt específico para análise
            base_prompt = self.prompt_manager.get_analysis_prompt()
            
            # Combina prompt com contexto específico
            enhanced_prompt = f"""
{base_prompt}

=== CONTEXTO ESPECÍFICO DO PROJETO ===
{enhanced_context}

=== INSTRUÇÕES CRÍTICAS ===
1. Analise ESPECIFICAMENTE as funções e classes listadas acima
2. Identifique o PROPÓSITO REAL do sistema baseado nos nomes das funções
3. Mapeie cada classe Delphi para um equivalente Spring Boot específico
4. Sugira a arquitetura Spring Boot mais adequada
5. Identifique regras de negócio baseadas nos nomes das funções
6. Use dados REAIS fornecidos, evite exemplos genéricos

=== FORMATO DE RESPOSTA OBRIGATÓRIO ===
## Funcionalidade Principal
[Descreva o que o sistema faz baseado nas funções analisadas]

## Classes Identificadas
[Liste cada classe encontrada e sua função provável]

## Mapeamento Spring Boot
[Para cada classe/função, sugira o equivalente em Spring Boot]

## Arquitetura Recomendada
[Baseado na análise, sugira packages e estrutura Spring Boot]
"""
            
            # Chama LLM
            llm_response = self.llm_service.generate_content(enhanced_prompt)
            
            return llm_response
            
        except Exception as e:
            logger.error(f"❌ Erro na análise LLM: {e}")
            return f"Erro na análise LLM: {str(e)}"
    
    def _collect_all_project_files(self, project_path: str) -> Dict[str, str]:
        """Coleta TODO o conteúdo dos arquivos Delphi do projeto"""
        project_files = {}
        delphi_extensions = {'.pas', '.dfm', '.dpr', '.dpk', '.dproj'}
        
        project_path_obj = Path(project_path)
        
        if project_path_obj.is_file():
            # Se é um arquivo único
            if project_path_obj.suffix.lower() in delphi_extensions:
                content = self._read_file_safely(project_path_obj)
                if content:
                    project_files[str(project_path_obj)] = content
        else:
            # Se é um diretório, busca recursivamente
            for file_path in project_path_obj.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in delphi_extensions:
                    content = self._read_file_safely(file_path)
                    if content:
                        # Usa caminho relativo como chave
                        relative_path = file_path.relative_to(project_path_obj)
                        project_files[str(relative_path)] = content
        
        return project_files
    
    def _read_file_safely(self, file_path: Path) -> Optional[str]:
        """Lê arquivo com tratamento de encoding"""
        try:
            # Tenta UTF-8 primeiro
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            try:
                # Fallback para latin-1
                with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler arquivo {file_path}: {str(e)}")
                return None
    
    def _build_complete_project_context(self, files_content: Dict[str, str], project_name: str) -> str:
        """Monta contexto completo do projeto para análise por LLM"""
        context_parts = []
        
        # Cabeçalho do contexto
        context_parts.append(f"===== PROJETO DELPHI: {project_name} =====")
        context_parts.append(f"Total de arquivos: {len(files_content)}")
        context_parts.append(f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        context_parts.append("")
        
        # Adiciona conteúdo de cada arquivo
        for file_path, content in files_content.items():
            context_parts.append(f"===== ARQUIVO: {file_path} =====")
            context_parts.append(f"Tamanho: {len(content)} caracteres")
            context_parts.append(f"Linhas: {len(content.splitlines())}")
            context_parts.append("")
            context_parts.append("CONTEÚDO:")
            context_parts.append(content)
            context_parts.append("")
            context_parts.append("===== FIM DO ARQUIVO =====")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _analyze_project_with_llm(self, project_context: str, project_name: str) -> str:
        """Usa LLM para análise completa do projeto"""
        if not self.llm_service:
            raise RuntimeError("LLM Service não disponível para análise")
        
        # Carrega prompt de análise
        analysis_prompt = self._load_analysis_prompt()
        
        # Monta prompt final
        full_prompt = f"""
{analysis_prompt}

===== DADOS DO PROJETO PARA ANÁLISE =====
{project_context}

INSTRUÇÃO FINAL: Analise COMPLETAMENTE o projeto acima e gere uma análise técnica detalhada seguindo exatamente o formato especificado no prompt. Use APENAS os dados reais encontrados nos arquivos fornecidos.
"""
        
        logger.info(f"🤖 Enviando {len(full_prompt)} caracteres para análise LLM...")
        
        try:
            # Chama LLM para análise - usando apenas o prompt completo
            analysis_result = self.llm_service.generate_content(full_prompt)
            
            if not analysis_result or len(analysis_result.strip()) < 100:
                raise RuntimeError("LLM retornou análise insuficiente")
            
            logger.info(f"✅ LLM retornou análise de {len(analysis_result)} caracteres")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise LLM: {str(e)}")
            raise
    
    def _load_analysis_prompt(self) -> str:
        """Carrega prompt de análise dos arquivos"""
        prompt_file = Path(__file__).parent.parent / "prompts" / "backend_analysis_prompt.txt"
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            # Fallback para prompt básico
            return """
# ANÁLISE DE PROJETO DELPHI

Analise o projeto Delphi fornecido e gere uma análise técnica detalhada incluindo:

1. **Visão Geral**: Nome do projeto, tipo de aplicação, arquivos analisados
2. **Estrutura**: Classes, métodos, propriedades identificadas
3. **Funcionalidades**: Principais funcionalidades baseadas no código
4. **Arquitetura**: Padrões utilizados, organização dos componentes
5. **Complexidade**: Métricas de qualidade e complexidade
6. **Modernização**: Recomendações específicas para Java Spring Boot

Use APENAS os dados reais encontrados nos arquivos fornecidos.
"""
    
    def _convert_llm_analysis_to_structured_format(self, llm_analysis: str, 
                                                  files_content: Dict[str, str],
                                                  project_name: str, 
                                                  project_path: str) -> Dict[str, Any]:
        """Converte análise do LLM para formato estruturado esperado"""
        
        # Extrai informações básicas dos arquivos
        total_lines = sum(len(content.splitlines()) for content in files_content.values())
        
        # Conta tipos de arquivo
        file_types = {}
        for file_path in files_content.keys():
            ext = Path(file_path).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        # Monta resultado estruturado
        structured_result = {
            'metadata': {
                'project_name': project_name,
                'project_path': str(project_path),
                'analysis_date': datetime.now().isoformat(),
                'analyzer_version': self.version,
                'analysis_type': 'llm_based_analysis',
                'llm_analysis_length': len(llm_analysis)
            },
            'files_analyzed': {
                'total_files': len(files_content),
                'file_types': file_types,
                'files': [{'filename': Path(fp).name, 'filepath': fp, 'size': len(content)} 
                         for fp, content in files_content.items()]
            },
            'code_structure': {
                'functions': self._extract_functions_from_llm_analysis(llm_analysis),
                'classes': self._extract_classes_from_llm_analysis(llm_analysis),
                'forms': self._extract_forms_from_llm_analysis(llm_analysis),
                'data_modules': []
            },
            'business_logic': {
                'rules': self._extract_business_rules_from_llm_analysis(llm_analysis),
                'patterns': [],
                'workflows': []
            },
            'database_elements': {
                'connections': [],
                'queries': [],
                'tables_referenced': []
            },
            'ui_components': {
                'forms': self._extract_forms_from_llm_analysis(llm_analysis),
                'controls': [],
                'menus': []
            },
            'dependencies': {
                'internal_units': [],
                'external_libraries': [],
                'system_units': []
            },
            'complexity_metrics': {
                'total_lines': total_lines,
                'function_count': 0,
                'class_count': 0,
                'estimated_complexity': 'média'
            },
            'llm_analysis': {
                'full_analysis': llm_analysis,
                'summary': llm_analysis[:500] + "..." if len(llm_analysis) > 500 else llm_analysis
            },
            'documentation_hints': self._generate_documentation_hints_from_llm(llm_analysis),
            'modernization_suggestions': self._generate_modernization_suggestions_from_llm(llm_analysis)
        }
        
        return structured_result
    
    def _extract_functions_from_llm_analysis(self, llm_analysis: str) -> List[Dict[str, Any]]:
        """Extrai funções mencionadas na análise LLM"""
        functions = []
        # Procura por padrões comuns de menção de funções na análise
        import re
        
        # Padrões para identificar funções mencionadas
        patterns = [
            r'função\s+(\w+)',
            r'procedure\s+(\w+)',
            r'function\s+(\w+)',
            r'método\s+(\w+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, llm_analysis, re.IGNORECASE)
            for match in matches:
                func_name = match.group(1)
                functions.append({
                    'name': func_name,
                    'type': 'function',
                    'source': 'llm_analysis',
                    'line_number': 0
                })
        
        return functions[:10]  # Limita a 10 para não sobrecarregar
    
    def _extract_classes_from_llm_analysis(self, llm_analysis: str) -> List[Dict[str, Any]]:
        """Extrai classes mencionadas na análise LLM"""
        classes = []
        import re
        
        # Padrões para identificar classes mencionadas
        patterns = [
            r'classe\s+(\w+)',
            r'class\s+(\w+)',
            r'TForm\w*',
            r'T\w+Form',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, llm_analysis, re.IGNORECASE)
            for match in matches:
                class_name = match.group(0) if 'TForm' in pattern or r'T\w+' in pattern else match.group(1)
                classes.append({
                    'name': class_name,
                    'type': 'class',
                    'source': 'llm_analysis',
                    'methods': [],
                    'properties': []
                })
        
        return classes[:10]  # Limita a 10
    
    def _extract_forms_from_llm_analysis(self, llm_analysis: str) -> List[Dict[str, Any]]:
        """Extrai forms mencionadas na análise LLM"""
        forms = []
        import re
        
        # Procura por menções de forms
        form_patterns = [
            r'formulário\s+(\w+)',
            r'form\s+(\w+)',
            r'tela\s+(\w+)',
        ]
        
        for pattern in form_patterns:
            matches = re.finditer(pattern, llm_analysis, re.IGNORECASE)
            for match in matches:
                form_name = match.group(1)
                forms.append({
                    'name': form_name,
                    'type': 'form',
                    'source': 'llm_analysis'
                })
        
        return forms[:5]  # Limita a 5
    
    def _extract_business_rules_from_llm_analysis(self, llm_analysis: str) -> List[str]:
        """Extrai regras de negócio mencionadas na análise LLM"""
        rules = []
        
        # Procura por seções que mencionam regras de negócio
        lines = llm_analysis.split('\n')
        in_business_section = False
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['negócio', 'business', 'regra', 'validação']):
                in_business_section = True
            elif in_business_section and line.strip().startswith('-'):
                rules.append(line.strip())
            elif in_business_section and not line.strip():
                in_business_section = False
        
        return rules[:5]  # Limita a 5
    
    def _generate_documentation_hints_from_llm(self, llm_analysis: str) -> Dict[str, Any]:
        """Gera dicas de documentação baseadas na análise LLM"""
        return {
            'key_components': [],
            'main_flows': [],
            'critical_functions': [],
            'business_highlights': [],
            'llm_analysis_available': True
        }
    
    def _generate_modernization_suggestions_from_llm(self, llm_analysis: str) -> Dict[str, Any]:
        """Gera sugestões de modernização baseadas na análise LLM"""
        return {
            'priority_components': [],
            'architecture_recommendations': [
                "Análise completa por LLM disponível",
                "Consulte seção llm_analysis para recomendações detalhadas"
            ],
            'technology_mappings': [],
            'migration_phases': []
        }
    
    def _create_empty_analysis_result(self, project_name: str, project_path: str) -> Dict[str, Any]:
        """Cria resultado vazio quando nenhum arquivo é encontrado"""
        return {
            'metadata': {
                'project_name': project_name,
                'project_path': str(project_path),
                'analysis_date': datetime.now().isoformat(),
                'analyzer_version': self.version,
                'analysis_type': 'empty_project'
            },
            'files_analyzed': {'total_files': 0, 'files': []},
            'code_structure': {'functions': [], 'classes': [], 'forms': [], 'data_modules': []},
            'business_logic': {'rules': [], 'patterns': [], 'workflows': []},
            'database_elements': {'connections': [], 'queries': [], 'tables_referenced': []},
            'ui_components': {'forms': [], 'controls': [], 'menus': []},
            'dependencies': {'internal_units': [], 'external_libraries': [], 'system_units': []},
            'complexity_metrics': {'total_lines': 0, 'function_count': 0, 'class_count': 0, 'estimated_complexity': 'baixa'},
            'llm_analysis': {'full_analysis': 'Nenhum arquivo Delphi encontrado para análise', 'summary': 'Projeto vazio'},
            'documentation_hints': {'key_components': [], 'main_flows': [], 'critical_functions': [], 'business_highlights': []},
            'modernization_suggestions': {'priority_components': [], 'architecture_recommendations': [], 'technology_mappings': [], 'migration_phases': []}
        }
    
    def _fallback_to_structured_analysis(self, project_path: str, project_name: str) -> Dict[str, Any]:
        """Fallback para análise estruturada quando LLM falha"""
        logger.info("🔄 Executando análise estruturada como fallback...")
        return self.analyze_project_structured_fallback(project_path, project_name)
    
    def analyze_project_structured_fallback(self, project_path: str, project_name: str = None) -> Dict[str, Any]:
        """
        Análise estruturada original como fallback
        """
        start_time = time.time()
        logger.info(f"🚀 Iniciando análise ESTRUTURADA (fallback) do projeto: {project_path}")
        
        # Se project_name não foi fornecido, extrai do caminho
        if project_name is None:
            project_name = Path(project_path).stem
        
        try:
            # Lista arquivos Delphi relevantes
            delphi_extensions = {'.pas', '.dfm', '.dpr', '.dpk', '.dproj'}
            delphi_files = []
            
            project_path_obj = Path(project_path)
            if project_path_obj.is_file():
                # Se é um arquivo único, analisa apenas ele
                if project_path_obj.suffix.lower() in delphi_extensions:
                    delphi_files.append(project_path_obj)
            else:
                # Se é um diretório, busca arquivos recursivamente
                for file_path in project_path_obj.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in delphi_extensions:
                        delphi_files.append(file_path)
            
            logger.info(f"📁 Encontrados {len(delphi_files)} arquivos Delphi")
            
            # Estrutura de análise compatível com DocumentationGenerator
            analysis_results = {
                'metadata': {
                    'project_name': project_name,
                    'project_path': str(project_path),
                    'analysis_date': datetime.now().isoformat(),
                    'analyzer_version': self.version,
                    'analysis_type': 'structured_legacy_analysis_fallback'
                },
                'files_analyzed': {
                    'total_files': len(delphi_files),
                    'files': []
                },
                'code_structure': {
                    'functions': [],
                    'classes': [],
                    'forms': [],
                    'data_modules': [],
                    'units': []
                },
                'business_logic': {
                    'rules': [],
                    'patterns': [],
                    'workflows': []
                },
                'database_elements': {
                    'connections': [],
                    'queries': [],
                    'tables_referenced': []
                },
                'ui_components': {
                    'forms': [],
                    'controls': [],
                    'menus': []
                },
                'dependencies': {
                    'internal_units': [],
                    'external_libraries': [],
                    'system_units': []
                },
                'complexity_metrics': {
                    'total_lines': 0,
                    'function_count': 0,
                    'class_count': 0,
                    'estimated_complexity': 'baixa'
                }
            }
            
            # Analisa cada arquivo de forma estruturada
            total_lines = 0
            for file_path in delphi_files:
                try:
                    file_analysis = self._analyze_file_structured(file_path, project_name)
                    if file_analysis:
                        self._merge_structured_analysis(analysis_results, file_analysis)
                        total_lines += file_analysis.get('lines_count', 0)
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao analisar {file_path}: {str(e)}")
                    continue
            
            # Atualiza métricas de complexidade
            analysis_results['complexity_metrics']['total_lines'] = total_lines
            analysis_results['complexity_metrics']['function_count'] = len(analysis_results['code_structure']['functions'])
            analysis_results['complexity_metrics']['class_count'] = len(analysis_results['code_structure']['classes'])
            analysis_results['complexity_metrics']['estimated_complexity'] = self._estimate_project_complexity(analysis_results)
            
            # Adiciona informações específicas para documentação
            analysis_results['documentation_hints'] = self._generate_documentation_hints(analysis_results)
            
            # Gera correlações para modernização
            analysis_results['modernization_suggestions'] = self._generate_modernization_suggestions(analysis_results)
            
            elapsed_time = time.time() - start_time
            logger.info(f"✅ Análise estruturada (fallback) concluída em {elapsed_time:.2f}s")
            logger.info(f"📊 Resultados: {len(analysis_results['files_analyzed']['files'])} arquivos, "
                       f"{len(analysis_results['code_structure']['functions'])} funções, "
                       f"{len(analysis_results['code_structure']['classes'])} classes")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Erro na análise estruturada (fallback): {str(e)}")
            return self._create_empty_analysis_result(project_name, project_path)
    
    def _analyze_file_structured(self, file_path: Path, project_name: str) -> Dict[str, Any]:
        """Análise estruturada de um arquivo individual"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            file_result = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_type': file_path.suffix,
                'lines_count': len(content.splitlines()),
                'functions': [],
                'classes': [],
                'forms': [],
                'units_referenced': [],
                'database_elements': []
            }
            
            # Análise de funções e procedimentos
            function_patterns = [
                r'function\s+(\w+)\s*\([^)]*\)\s*:\s*(\w+);',
                r'procedure\s+(\w+)\s*\([^)]*\);'
            ]
            
            for pattern in function_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    func_name = match.group(1)
                    func_type = 'function' if 'function' in match.group(0).lower() else 'procedure'
                    file_result['functions'].append({
                        'name': func_name,
                        'type': func_type,
                        'file': file_path.name
                    })
            
            # Análise de classes
            class_pattern = r'type\s+(\w+)\s*=\s*class\s*\(([^)]*)\)'
            class_matches = re.finditer(class_pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in class_matches:
                class_name = match.group(1)
                parent_class = match.group(2) if match.group(2) else 'TObject'
                file_result['classes'].append({
                    'name': class_name,
                    'parent': parent_class,
                    'file': file_path.name
                })
            
            # Análise de forms (se for .dfm)
            if file_path.suffix.lower() == '.dfm':
                form_pattern = r'object\s+(\w+):\s*(\w+)'
                form_matches = re.finditer(form_pattern, content, re.IGNORECASE)
                for match in form_matches:
                    form_name = match.group(1)
                    form_type = match.group(2)
                    file_result['forms'].append({
                        'name': form_name,
                        'type': form_type,
                        'file': file_path.name
                    })
            
            # Análise de units referenciadas
            uses_pattern = r'uses\s+(.*?);'
            uses_matches = re.finditer(uses_pattern, content, re.IGNORECASE | re.DOTALL)
            for match in uses_matches:
                units_text = match.group(1)
                units = [unit.strip() for unit in units_text.replace('\n', '').replace('\r', '').split(',')]
                file_result['units_referenced'].extend(units)
            
            # Análise básica de elementos de banco de dados
            db_keywords = ['TDataSet', 'TQuery', 'TTable', 'TStoredProc', 'TDataSource', 'SQL', 'SELECT', 'INSERT', 'UPDATE', 'DELETE']
            for keyword in db_keywords:
                if keyword.lower() in content.lower():
                    file_result['database_elements'].append({
                        'type': keyword,
                        'file': file_path.name,
                        'context': 'detected'
                    })
            
            return file_result
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar arquivo {file_path}: {str(e)}")
            return None
    
    def _merge_structured_analysis(self, main_analysis: Dict[str, Any], file_analysis: Dict[str, Any]):
        """Mescla resultado de análise de arquivo com análise principal"""
        if not file_analysis:
            return
        
        # Adiciona arquivo à lista
        main_analysis['files_analyzed']['files'].append({
            'path': file_analysis['file_path'],
            'name': file_analysis['file_name'],
            'type': file_analysis['file_type'],
            'lines': file_analysis['lines_count']
        })
        
        # Mescla funções
        main_analysis['code_structure']['functions'].extend(file_analysis['functions'])
        
        # Mescla classes
        main_analysis['code_structure']['classes'].extend(file_analysis['classes'])
        
        # Mescla forms
        main_analysis['code_structure']['forms'].extend(file_analysis['forms'])
        
        # Mescla units
        for unit in file_analysis['units_referenced']:
            if unit and unit not in main_analysis['dependencies']['internal_units']:
                if any(sys_unit in unit.lower() for sys_unit in ['system', 'sysutils', 'classes', 'controls', 'forms', 'windows']):
                    main_analysis['dependencies']['system_units'].append(unit)
                else:
                    main_analysis['dependencies']['internal_units'].append(unit)
        
        # Mescla elementos de banco
        main_analysis['database_elements']['queries'].extend(file_analysis['database_elements'])
    
    def _estimate_project_complexity(self, analysis: Dict[str, Any]) -> str:
        """Estima complexidade do projeto baseada em métricas"""
        total_lines = analysis['complexity_metrics']['total_lines']
        function_count = analysis['complexity_metrics']['function_count']
        class_count = analysis['complexity_metrics']['class_count']
        
        if total_lines > 50000 or function_count > 500 or class_count > 100:
            return 'alta'
        elif total_lines > 10000 or function_count > 100 or class_count > 20:
            return 'média'
        else:
            return 'baixa'
    
    def _generate_documentation_hints(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera dicas para documentação baseada na análise"""
        return {
            'suggested_sections': [
                'Arquitetura Geral',
                'Módulos Principais',
                'Fluxo de Dados',
                'Interface do Usuário',
                'Integração com Banco de Dados'
            ],
            'key_components': [f['name'] for f in analysis['code_structure']['forms'][:5]],
            'main_functions': [f['name'] for f in analysis['code_structure']['functions'][:10]],
            'complexity_level': analysis['complexity_metrics']['estimated_complexity']
        }
    
    def _generate_modernization_suggestions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera sugestões de modernização baseada na análise"""
        suggestions = {
            'priority_areas': [],
            'technology_migration': [],
            'architecture_improvements': []
        }
        
        # Baseado na complexidade
        complexity = analysis['complexity_metrics']['estimated_complexity']
        if complexity == 'alta':
            suggestions['priority_areas'].append('Refatoração em módulos menores')
            suggestions['architecture_improvements'].append('Implementar padrão MVC')
        
        # Baseado em elementos de banco
        if analysis['database_elements']['queries']:
            suggestions['technology_migration'].append('Migrar para ORM moderno')
            suggestions['priority_areas'].append('Revisar queries SQL')
        
        # Baseado em forms
        if len(analysis['code_structure']['forms']) > 10:
            suggestions['priority_areas'].append('Modernizar interface do usuário')
            suggestions['technology_migration'].append('Considerar framework web')
        
        return suggestions
    
    def _analyze_file_structured(self, file_path: Path, project_name: str) -> Optional[Dict[str, Any]]:
        """Analisa um arquivo de forma estruturada para compatibilidade com DocumentationGenerator"""
        try:
            if not file_path.exists() or not file_path.is_file():
                return None
            
            # Lê o conteúdo do arquivo
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler arquivo {file_path}: {str(e)}")
                try:
                    # Tenta com encoding latin-1 como fallback
                    with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                        content = f.read()
                except:
                    return None
            
            if not content.strip():
                return None
            
            lines = content.splitlines()
            file_info = {
                'filename': file_path.name,
                'filepath': str(file_path),
                'file_type': file_path.suffix.lower(),
                'size': len(content),
                'lines_count': len(lines),
                'functions': [],
                'classes': [],
                'units_referenced': [],
                'database_operations': [],
                'ui_elements': [],
                'business_rules': []
            }
            
            # Análise específica por tipo de arquivo
            if file_path.suffix.lower() == '.pas':
                self._analyze_pascal_unit_structured(content, file_info, project_name)
            elif file_path.suffix.lower() == '.dfm':
                self._analyze_form_file_structured(content, file_info)
            elif file_path.suffix.lower() == '.dpr':
                self._analyze_project_file_structured(content, file_info)
            
            return file_info
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar arquivo estruturado {file_path}: {str(e)}")
            return None
    
    def _analyze_pascal_unit_structured(self, content: str, file_info: Dict[str, Any], project_name: str):
        """Analisa unit Pascal de forma estruturada"""
        try:
            # Extrai funções e procedimentos
            functions = self._extract_functions_structured(content, file_info['filename'])
            file_info['functions'] = functions
            
            # Extrai classes
            classes = self._extract_classes_structured(content, file_info['filename'])
            file_info['classes'] = classes
            
            # Extrai uses (dependências)
            uses = self._extract_uses_section(content)
            file_info['units_referenced'] = uses
            
            # Identifica operações de banco de dados
            db_ops = self._extract_database_operations_structured(content)
            file_info['database_operations'] = db_ops
            
            # Identifica regras de negócio
            business_rules = self._extract_business_rules_structured(content, project_name)
            file_info['business_rules'] = business_rules
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na análise estruturada do Pascal: {str(e)}")
    
    def _extract_functions_structured(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Extrai funções e procedimentos de forma estruturada MELHORADA"""
        functions = []
        
        # Padrões melhorados para funções e procedimentos
        function_pattern = r'^\s*(function|procedure)\s+(\w+(?:\.\w+)?)\s*(?:\((.*?)\))?\s*(?::\s*(\w+(?:\.\w+)?))?\s*;'
        
        # Padrão para métodos de classe
        method_pattern = r'^\s*(function|procedure)\s+T\w+\.(\w+)\s*(?:\((.*?)\))?\s*(?::\s*(\w+(?:\.\w+)?))?\s*;'
        
        # Padrão para eventos
        event_pattern = r'^\s*procedure\s+(\w+(?:Click|Change|Enter|Exit|Show|Close|Create|Destroy|Paint|Resize|KeyPress|KeyDown|KeyUp))\s*\('
        
        lines = content.splitlines()
        for i, line in enumerate(lines):
            # Verifica método de classe primeiro
            method_match = re.match(method_pattern, line, re.IGNORECASE)
            if method_match:
                func_type = method_match.group(1).lower()
                func_name = method_match.group(2)
                parameters_str = method_match.group(3) or ''
                return_type = method_match.group(4) or ''
                
                # Identifica se é evento
                is_event = bool(re.search(r'(Click|Change|Enter|Exit|Show|Close|Create|Destroy|Paint|Resize|KeyPress|KeyDown|KeyUp)', func_name, re.IGNORECASE))
                
                functions.append({
                    'name': func_name,
                    'type': func_type,
                    'category': 'event' if is_event else 'method',
                    'parameters': self._parse_parameters(parameters_str),
                    'return_type': return_type,
                    'line_number': i + 1,
                    'is_class_method': True,
                    'is_event_handler': is_event
                })
                continue
            
            # Verifica função/procedimento normal
            func_match = re.match(function_pattern, line, re.IGNORECASE)
            if func_match:
                func_type = func_match.group(1).lower()
                func_name = func_match.group(2)
                parameters_str = func_match.group(3) or ''
                return_type = func_match.group(4) or ''
                
                # Identifica categoria da função
                category = 'function'
                if func_type == 'procedure':
                    category = 'procedure'
                if 'Create' in func_name or 'Initialize' in func_name:
                    category = 'constructor'
                elif 'Destroy' in func_name or 'Free' in func_name:
                    category = 'destructor'
                elif func_name.startswith('Get') or func_name.startswith('Set'):
                    category = 'property_accessor'
                
                functions.append({
                    'name': func_name,
                    'type': func_type,
                    'category': category,
                    'parameters': self._parse_parameters(parameters_str),
                    'return_type': return_type,
                    'line_number': i + 1,
                    'is_class_method': False,
                    'is_event_handler': False
                })
        
        return functions
    
    def _parse_parameters(self, parameters_str: str) -> List[Dict[str, Any]]:
        """Parse melhorado de parâmetros"""
        parameters = []
        if not parameters_str:
            return parameters
            
        param_parts = parameters_str.split(';')
        for param_part in param_parts:
            param_part = param_part.strip()
            if ':' in param_part:
                # Identifica modificadores (var, const, out)
                modifier = ''
                if param_part.lower().startswith(('var ', 'const ', 'out ')):
                    modifier, param_part = param_part.split(' ', 1)
                    modifier = modifier.lower()
                
                names_part, type_part = param_part.rsplit(':', 1)
                param_names = [name.strip() for name in names_part.split(',')]
                param_type = type_part.strip()
                
                for param_name in param_names:
                    parameters.append({
                        'name': param_name,
                        'type': param_type,
                        'modifier': modifier
                    })
        
        return parameters
    
    def _extract_classes_structured(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Extrai classes de forma estruturada MELHORADA"""
        classes = []
        
        # Padrões melhorados para classes
        class_pattern = r'^\s*(\w+)\s*=\s*class\s*(?:\(([^)]+)\))?\s*'
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            match = re.match(class_pattern, line, re.IGNORECASE)
            if match:
                class_name = match.group(1)
                parent_class = match.group(2) or 'TObject'
                
                # Identifica tipo de classe
                class_type = 'class'
                if 'TForm' in parent_class:
                    class_type = 'form'
                elif 'TDataModule' in parent_class:
                    class_type = 'datamodule'
                elif 'TFrame' in parent_class:
                    class_type = 'frame'
                elif 'Exception' in class_name or 'Error' in class_name:
                    class_type = 'exception'
                
                class_info = {
                    'name': class_name,
                    'parent_class': parent_class,
                    'class_type': class_type,
                    'methods': [],
                    'properties': [],
                    'fields': [],
                    'events': [],
                    'line_number': i + 1,
                    'source_file': filename,
                    'is_abstract': False,
                    'interfaces': []
                }
                
                # Extrai membros da classe
                self._extract_class_members_enhanced(content, i, class_info)
                classes.append(class_info)
        
        return classes
    
    def _extract_class_members_enhanced(self, content: str, class_start_line: int, class_info: Dict[str, Any]):
        """Extrai membros de uma classe de forma melhorada"""
        lines = content.splitlines()
        in_private = False
        in_protected = False
        in_public = False
        in_published = False
        current_visibility = 'private'
        
        for i in range(class_start_line + 1, len(lines)):
            line = lines[i].strip()
            line_lower = line.lower()
            
            # Identifica mudanças de visibilidade
            if line_lower.startswith('private'):
                current_visibility = 'private'
                in_private = True
                continue
            elif line_lower.startswith('protected'):
                current_visibility = 'protected'
                in_protected = True
                continue
            elif line_lower.startswith('public'):
                current_visibility = 'public'
                in_public = True
                continue
            elif line_lower.startswith('published'):
                current_visibility = 'published'
                in_published = True
                continue
            
            # Para quando encontra "end;" da classe
            if line_lower == 'end;' and not line.startswith(' '):
                break
            
            # Extrai propriedades
            prop_match = re.match(r'property\s+(\w+)\s*(?::\s*(\w+))?\s*(?:read\s+(\w+))?\s*(?:write\s+(\w+))?', line, re.IGNORECASE)
            if prop_match:
                prop_name = prop_match.group(1)
                prop_type = prop_match.group(2) or 'Variant'
                read_method = prop_match.group(3)
                write_method = prop_match.group(4)
                
                class_info['properties'].append({
                    'name': prop_name,
                    'type': prop_type,
                    'read_method': read_method,
                    'write_method': write_method,
                    'visibility': current_visibility,
                    'line_number': i + 1
                })
                continue
            
            # Extrai campos (fields)
            field_match = re.match(r'(\w+)\s*:\s*(\w+(?:\[\w+\])?)\s*;', line, re.IGNORECASE)
            if field_match and not line_lower.startswith(('function', 'procedure', 'property')):
                field_name = field_match.group(1)
                field_type = field_match.group(2)
                
                class_info['fields'].append({
                    'name': field_name,
                    'type': field_type,
                    'visibility': current_visibility,
                    'line_number': i + 1
                })
                continue
            
            # Extrai declarações de métodos
            method_match = re.match(r'(function|procedure)\s+(\w+)', line, re.IGNORECASE)
            if method_match:
                method_type = method_match.group(1).lower()
                method_name = method_match.group(2)
                
                # Identifica se é evento
                is_event = bool(re.search(r'(Click|Change|Enter|Exit|Show|Close|Create|Destroy|Paint|Resize|KeyPress|KeyDown|KeyUp)', method_name, re.IGNORECASE))
                
                method_info = {
                    'name': method_name,
                    'type': method_type,
                    'visibility': current_visibility,
                    'is_event_handler': is_event,
                    'line_number': i + 1
                }
                
                if is_event:
                    class_info['events'].append(method_info)
                else:
                    class_info['methods'].append(method_info)
    
    def _analyze_project_hierarchy(self, project_path: str) -> Dict[str, Any]:
        """Analisa a hierarquia e estrutura do projeto MELHORADA"""
        hierarchy = {
            'root_files': [],
            'subdirectories': {},
            'main_units': [],
            'form_units': [],
            'datamodule_units': [],
            'utility_units': [],
            'total_files': 0,
            'file_types': {}
        }
        
        try:
            for root, dirs, files in os.walk(project_path):
                rel_path = os.path.relpath(root, project_path)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file).suffix.lower()
                    
                    # Conta tipos de arquivo
                    if file_ext not in hierarchy['file_types']:
                        hierarchy['file_types'][file_ext] = 0
                    hierarchy['file_types'][file_ext] += 1
                    hierarchy['total_files'] += 1
                    
                    if file.endswith('.pas'):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # Classifica o tipo de unit baseado no conteúdo
                            if 'TForm' in content or ': TForm' in content:
                                hierarchy['form_units'].append({
                                    'name': file,
                                    'path': rel_path,
                                    'type': 'form'
                                })
                            elif 'TDataModule' in content or ': TDataModule' in content:
                                hierarchy['datamodule_units'].append({
                                    'name': file,
                                    'path': rel_path,
                                    'type': 'datamodule'
                                })
                            elif file.lower().endswith('main.pas') or 'program ' in content.lower():
                                hierarchy['main_units'].append({
                                    'name': file,
                                    'path': rel_path,
                                    'type': 'main'
                                })
                            else:
                                hierarchy['utility_units'].append({
                                    'name': file,
                                    'path': rel_path,
                                    'type': 'utility'
                                })
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Erro ao analisar {file}: {e}")
                    
                    if rel_path == '.':  # Arquivo na raiz
                        hierarchy['root_files'].append(file)
                    else:
                        if rel_path not in hierarchy['subdirectories']:
                            hierarchy['subdirectories'][rel_path] = []
                        hierarchy['subdirectories'][rel_path].append(file)
        
        except Exception as e:
            logger.error(f"❌ Erro na análise de hierarquia: {e}")
        
        return hierarchy
    
    def _extract_uses_section(self, content: str) -> List[str]:
        """Extrai seção uses"""
        uses_units = []
        
        # Procura pela seção uses
        uses_pattern = r'uses\s+(.*?);'
        matches = re.findall(uses_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            # Remove quebras de linha e espacos extras
            units_text = re.sub(r'\s+', ' ', match.strip())
            # Divide por vírgulas
            units = [unit.strip() for unit in units_text.split(',')]
            uses_units.extend(units)
        
        return list(set(uses_units))  # Remove duplicatas
    
    def _extract_database_operations_structured(self, content: str) -> List[Dict[str, Any]]:
        """Extrai operações de banco de dados"""
        db_operations = []
        
        # Padrões para identificar operações de BD
        sql_patterns = [
            r'(SELECT\s+.*?FROM\s+(\w+))',
            r'(INSERT\s+INTO\s+(\w+))',
            r'(UPDATE\s+(\w+)\s+SET)',
            r'(DELETE\s+FROM\s+(\w+))'
        ]
        
        for pattern in sql_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                operation = {
                    'type': match.group(1).split()[0].upper(),
                    'sql_snippet': match.group(1)[:100] + '...' if len(match.group(1)) > 100 else match.group(1),
                    'table': match.group(2) if len(match.groups()) > 1 else 'unknown'
                }
                db_operations.append(operation)
        
        return db_operations
    
    def _extract_business_rules_structured(self, content: str, project_name: str) -> List[str]:
        """Extrai regras de negócio identificáveis no código"""
        business_rules = []
        
        # Procura por comentários que indicam regras de negócio
        comment_patterns = [
            r'//\s*(regra|rule|business|negócio|validação|validation).*',
            r'\(\*\s*(regra|rule|business|negócio|validação|validation).*?\*\)',
            r'{\s*(regra|rule|business|negócio|validação|validation).*?}'
        ]
        
        for pattern in comment_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                rule_text = match.group(0).strip()
                if len(rule_text) > 10:  # Ignora comentários muito pequenos
                    business_rules.append(rule_text)
        
        # Procura por validações em código
        validation_patterns = [
            r'if\s+.*\s+then\s+raise\s+.*',
            r'if\s+.*\s+then\s+ShowMessage\s*\(',
            r'if\s+.*\s+then\s+MessageDlg\s*\('
        ]
        
        for pattern in validation_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                validation = match.group(0).strip()
                if len(validation) > 20:
                    business_rules.append(f"Validação: {validation}")
        
        return business_rules[:10]  # Limita a 10 regras por arquivo
    
    def _merge_structured_analysis(self, analysis_results: Dict[str, Any], file_analysis: Dict[str, Any]):
        """Combina análise de arquivo com resultado geral"""
        # Adiciona arquivo à lista
        analysis_results['files_analyzed']['files'].append({
            'filename': file_analysis['filename'],
            'filepath': file_analysis['filepath'],
            'file_type': file_analysis['file_type'],
            'size': file_analysis['size'],
            'lines_count': file_analysis['lines_count'],
            'functions': len(file_analysis['functions']),
            'classes': len(file_analysis['classes'])
        })
        
        # Adiciona funções ao resultado global
        for func in file_analysis['functions']:
            analysis_results['code_structure']['functions'].append(func)
        
        # Adiciona classes ao resultado global
        for cls in file_analysis['classes']:
            analysis_results['code_structure']['classes'].append(cls)
        
        # Adiciona regras de negócio
        for rule in file_analysis['business_rules']:
            analysis_results['business_logic']['rules'].append(rule)
        
        # Adiciona operações de banco
        for db_op in file_analysis['database_operations']:
            analysis_results['database_elements']['queries'].append(db_op)
        
        # Adiciona dependências
        for unit in file_analysis['units_referenced']:
            if unit not in analysis_results['dependencies']['internal_units']:
                analysis_results['dependencies']['internal_units'].append(unit)
    
    def _estimate_project_complexity(self, analysis_results: Dict[str, Any]) -> str:
        """Estima complexidade do projeto baseado nas métricas"""
        total_lines = analysis_results['complexity_metrics']['total_lines']
        function_count = analysis_results['complexity_metrics']['function_count']
        class_count = analysis_results['complexity_metrics']['class_count']
        
        complexity_score = 0
        
        # Pontuação baseada em linhas de código
        if total_lines > 10000:
            complexity_score += 3
        elif total_lines > 5000:
            complexity_score += 2
        elif total_lines > 1000:
            complexity_score += 1
        
        # Pontuação baseada em número de funções
        if function_count > 100:
            complexity_score += 3
        elif function_count > 50:
            complexity_score += 2
        elif function_count > 20:
            complexity_score += 1
        
        # Pontuação baseada em número de classes
        if class_count > 20:
            complexity_score += 2
        elif class_count > 10:
            complexity_score += 1
        
        if complexity_score >= 6:
            return 'alta'
        elif complexity_score >= 3:
            return 'média'
        else:
            return 'baixa'
    
    def _generate_documentation_hints(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Gera dicas específicas para documentação baseada na análise"""
        hints = {
            'key_components': [],
            'main_flows': [],
            'critical_functions': [],
            'business_highlights': []
        }
        
        # Identifica componentes-chave
        functions = analysis_results['code_structure']['functions']
        if functions:
            # Funções principais (com nomes sugestivos)
            key_functions = [f for f in functions if any(keyword in f['name'].lower() 
                           for keyword in ['main', 'principal', 'execute', 'process', 'calculate'])]
            hints['key_components'] = [f['name'] for f in key_functions[:5]]
        
        # Identifica fluxos principais
        forms = analysis_results['code_structure']['forms']
        if forms:
            hints['main_flows'] = [f"Formulário: {form['name']}" for form in forms[:3]]
        
        # Funções críticas
        critical_functions = [f for f in functions if 'validate' in f['name'].lower() or 'check' in f['name'].lower()]
        hints['critical_functions'] = [f['name'] for f in critical_functions[:5]]
        
        # Destaques de negócio
        business_rules = analysis_results['business_logic']['rules']
        hints['business_highlights'] = business_rules[:3]
        
        return hints
    
    def _generate_modernization_suggestions(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Gera sugestões específicas para modernização"""
        suggestions = {
            'priority_components': [],
            'architecture_recommendations': [],
            'technology_mappings': [],
            'migration_phases': []
        }
        
        # Componentes prioritários baseados na análise
        functions = analysis_results['code_structure']['functions']
        classes = analysis_results['code_structure']['classes']
        
        if classes:
            suggestions['priority_components'].append(f"Migrar {len(classes)} classes para Spring @Component")
        
        if functions:
            db_functions = [f for f in functions if any(keyword in f['name'].lower() 
                          for keyword in ['query', 'insert', 'update', 'delete', 'select'])]
            if db_functions:
                suggestions['priority_components'].append(f"Converter {len(db_functions)} operações DB para Spring Data JPA")
        
        # Recomendações de arquitetura
        suggestions['architecture_recommendations'] = [
            "Implementar padrão MVC com Spring Boot",
            "Usar Spring Security para autenticação",
            "Aplicar injeção de dependência"
        ]
        
        return suggestions
    
    def _analyze_form_file_structured(self, content: str, file_info: Dict[str, Any]):
        """Analisa arquivo de formulário (.dfm) de forma estruturada"""
        try:
            # Extrai informações do formulário
            form_info = self._extract_form_info(content)
            file_info['form_name'] = form_info.get('name', 'UnknownForm')
            file_info['form_class'] = form_info.get('class', 'TForm')
            
            # Extrai controles do formulário
            controls = self._extract_form_controls(content)
            file_info['ui_elements'] = controls
            
            # Identifica eventos
            events = self._extract_form_events(content)
            file_info['events'] = events
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na análise do formulário: {str(e)}")
    
    def _analyze_project_file_structured(self, content: str, file_info: Dict[str, Any]):
        """Analisa arquivo de projeto (.dpr) de forma estruturada"""
        try:
            # Extrai informações do projeto
            project_info = self._extract_project_info(content)
            file_info['project_type'] = project_info.get('type', 'application')
            file_info['project_title'] = project_info.get('title', 'Unknown Project')
            
            # Extrai units usadas no projeto
            project_uses = self._extract_uses_section(content)
            file_info['units_referenced'] = project_uses
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na análise do arquivo de projeto: {str(e)}")
    
    def _extract_form_info(self, content: str) -> Dict[str, str]:
        """Extrai informações básicas do formulário"""
        form_info = {}
        
        # Procura pela declaração do objeto
        object_match = re.search(r'object\s+(\w+):\s*(\w+)', content, re.IGNORECASE)
        if object_match:
            form_info['name'] = object_match.group(1)
            form_info['class'] = object_match.group(2)
        
        return form_info
    
    def _extract_form_controls(self, content: str) -> List[Dict[str, Any]]:
        """Extrai controles do formulário"""
        controls = []
        
        # Padrão para controles (objetos aninhados)
        control_pattern = r'object\s+(\w+):\s*(\w+)'
        
        matches = re.finditer(control_pattern, content, re.IGNORECASE)
        for match in matches:
            control_name = match.group(1)
            control_class = match.group(2)
            
            # Evita duplicar o próprio formulário
            if not control_class.startswith('TForm'):
                controls.append({
                    'name': control_name,
                    'class': control_class,
                    'type': self._classify_control_type(control_class)
                })
        
        return controls
    
    def _classify_control_type(self, control_class: str) -> str:
        """Classifica o tipo de controle baseado na classe"""
        if control_class.startswith('TButton'):
            return 'button'
        elif control_class.startswith('TEdit'):
            return 'input'
        elif control_class.startswith('TLabel'):
            return 'label'
        elif control_class.startswith('TGrid') or control_class.startswith('TDBGrid'):
            return 'grid'
        elif control_class.startswith('TPanel'):
            return 'container'
        elif control_class.startswith('TMenu'):
            return 'menu'
        elif control_class.startswith('TComboBox'):
            return 'dropdown'
        elif control_class.startswith('TMemo'):
            return 'textarea'
        else:
            return 'component'
    
    def _extract_form_events(self, content: str) -> List[str]:
        """Extrai eventos do formulário"""
        events = []
        
        # Procura por propriedades que terminam com event handlers
        event_pattern = r'(\w+)\s*=\s*(\w+)'
        
        matches = re.finditer(event_pattern, content)
        for match in matches:
            property_name = match.group(1)
            handler_name = match.group(2)
            
            # Identifica eventos comuns
            if any(event_type in property_name.lower() for event_type in 
                   ['onclick', 'onchange', 'onenter', 'onexit', 'onshow', 'onclose']):
                events.append(f"{property_name}: {handler_name}")
        
        return events[:10]  # Limita a 10 eventos
    
    def _extract_project_info(self, content: str) -> Dict[str, str]:
        """Extrai informações do arquivo de projeto"""
        project_info = {}
        
        # Procura por declaração de programa
        program_match = re.search(r'program\s+(\w+)', content, re.IGNORECASE)
        if program_match:
            project_info['name'] = program_match.group(1)
            project_info['type'] = 'application'
        
        # Procura por library
        library_match = re.search(r'library\s+(\w+)', content, re.IGNORECASE)
        if library_match:
            project_info['name'] = library_match.group(1)
            project_info['type'] = 'library'
        
        return project_info
    
    def _analyze_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analisa um único arquivo Delphi"""
        try:
            if not file_path.exists() or not file_path.is_file():
                return None
            
            # Lê o conteúdo do arquivo
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler arquivo {file_path}: {str(e)}")
                return None
            
            if not content.strip():
                return None
            
            # Analisa o conteúdo baseado na extensão do arquivo
            analysis = self._analyze_file_content(content, file_path)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar arquivo {file_path}: {str(e)}")
            return None
    
    def _analyze_file_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analisa conteúdo do arquivo baseado no tipo"""
        file_extension = file_path.suffix.lower()
        
        analysis = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_type': file_extension,
            'size': len(content),
            'lines': len(content.splitlines())
        }
        
        # Análise específica por tipo de arquivo
        if file_extension == '.pas':
            analysis.update(self._analyze_pascal_unit(content))
        elif file_extension == '.dfm':
            analysis.update(self._analyze_form_file(content))
        elif file_extension == '.dpr':
            analysis.update(self._analyze_project_file(content))
        elif file_extension == '.dpk':
            analysis.update(self._analyze_package_file(content))
        
        return analysis
    
    def _merge_file_analysis(self, results: Dict[str, Any], file_analysis: Dict[str, Any]):
        """Combina análise de arquivo com resultados gerais"""
        try:
            file_type = file_analysis.get('file_type', '')
            file_name = file_analysis.get('file_name', '')
            
            if file_type == '.pas':
                # Adiciona unit
                results['units'][file_name] = file_analysis
                
                # Se contém form, adiciona aos forms
                if file_analysis.get('has_form', False):
                    results['forms'][file_name] = file_analysis
                
                # Se é datamodule, adiciona aos data_modules
                if file_analysis.get('is_datamodule', False):
                    results['data_modules'][file_name] = file_analysis
                    
            elif file_type == '.dfm':
                # Arquivos de form
                results['forms'][file_name] = file_analysis
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao combinar análise: {str(e)}")
    
    def _generate_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo da análise"""
        try:
            return {
                'total_units': len(analysis_results.get('units', {})),
                'total_forms': len(analysis_results.get('forms', {})),
                'total_datamodules': len(analysis_results.get('data_modules', {})),
                'total_files': analysis_results.get('metadata', {}).get('total_files', 0),
                'main_technologies': ['Delphi', 'Pascal', 'VCL'],
                'analysis_complete': True
            }
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo: {str(e)}")
            return {'analysis_complete': False, 'error': str(e)}
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
    
    def _analyze_pascal_unit(self, content: str) -> Dict[str, Any]:
        """Analisa uma unit Pascal/Delphi"""
        try:
            analysis = {
                'type': 'pascal_unit',
                'has_interface': 'interface' in content.lower(),
                'has_implementation': 'implementation' in content.lower(),
                'classes': [],
                'procedures': [],
                'functions': [],
                'uses_units': [],
                'constants': [],
                'variables': [],
                'complexity': {},
                'is_form': False,
                'is_datamodule': False
            }
            
            # Detecta se é form ou datamodule
            content_lower = content.lower()
            if 'tform' in content_lower or ': tform' in content_lower:
                analysis['is_form'] = True
                analysis['has_form'] = True
            if 'tdatamodule' in content_lower or ': tdatamodule' in content_lower:
                analysis['is_datamodule'] = True
            
            # Extrai uses
            analysis['uses_units'] = self._extract_uses_clause(content)
            
            # Extrai classes
            analysis['classes'] = self._extract_classes(content)
            
            # Extrai procedures e functions
            analysis['procedures'] = self._extract_procedures(content)
            analysis['functions'] = self._extract_functions(content)
            
            # Calcula complexidade
            analysis['complexity'] = self._calculate_complexity(content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar unit Pascal: {str(e)}")
            return {'type': 'pascal_unit', 'error': str(e)}
    
    def _analyze_form_file(self, content: str) -> Dict[str, Any]:
        """Analisa arquivo .dfm (form)"""
        try:
            analysis = {
                'type': 'form_file',
                'form_class': '',
                'components': [],
                'properties': {},
                'events': []
            }
            
            # Extrai nome da classe do form
            class_match = re.search(r'object\s+(\w+):\s*(\w+)', content, re.IGNORECASE)
            if class_match:
                analysis['form_name'] = class_match.group(1)
                analysis['form_class'] = class_match.group(2)
            
            # Extrai componentes
            component_pattern = r'object\s+(\w+):\s*(\w+)'
            components = re.findall(component_pattern, content, re.IGNORECASE)
            analysis['components'] = [{'name': comp[0], 'type': comp[1]} for comp in components]
            
            # Extrai eventos (OnClick, OnShow, etc.)
            event_pattern = r'(\w+)\s*=\s*(\w+)'
            events = re.findall(event_pattern, content)
            analysis['events'] = [{'property': evt[0], 'handler': evt[1]} for evt in events if evt[0].startswith('On')]
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar form file: {str(e)}")
            return {'type': 'form_file', 'error': str(e)}
    
    def _analyze_project_file(self, content: str) -> Dict[str, Any]:
        """Analisa arquivo .dpr (projeto)"""
        try:
            analysis = {
                'type': 'project_file',
                'program_name': '',
                'uses_units': [],
                'forms': [],
                'main_form': ''
            }
            
            # Extrai nome do programa
            program_match = re.search(r'program\s+(\w+)', content, re.IGNORECASE)
            if program_match:
                analysis['program_name'] = program_match.group(1)
            
            # Extrai uses
            analysis['uses_units'] = self._extract_uses_clause(content)
            
            # Extrai forms criados
            form_pattern = r'Application\.CreateForm\((\w+),\s*(\w+)\)'
            forms = re.findall(form_pattern, content, re.IGNORECASE)
            analysis['forms'] = [{'class': form[0], 'variable': form[1]} for form in forms]
            
            # Detecta main form
            if analysis['forms']:
                analysis['main_form'] = analysis['forms'][0]['variable']
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar project file: {str(e)}")
            return {'type': 'project_file', 'error': str(e)}
    
    def _analyze_package_file(self, content: str) -> Dict[str, Any]:
        """Analisa arquivo .dpk (package)"""
        try:
            analysis = {
                'type': 'package_file',
                'package_name': '',
                'requires': [],
                'contains': []
            }
            
            # Extrai nome do package
            package_match = re.search(r'package\s+(\w+)', content, re.IGNORECASE)
            if package_match:
                analysis['package_name'] = package_match.group(1)
            
            # Extrai requires
            requires_match = re.search(r'requires\s+(.*?);', content, re.IGNORECASE | re.DOTALL)
            if requires_match:
                requires_text = requires_match.group(1)
                analysis['requires'] = [req.strip() for req in requires_text.split(',')]
            
            # Extrai contains
            contains_match = re.search(r'contains\s+(.*?);', content, re.IGNORECASE | re.DOTALL)
            if contains_match:
                contains_text = contains_match.group(1)
                analysis['contains'] = [cont.strip() for cont in contains_text.split(',')]
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar package file: {str(e)}")
            return {'type': 'package_file', 'error': str(e)}
    
    def _extract_uses_clause(self, content: str) -> List[str]:
        """Extrai unidades da cláusula uses"""
        try:
            uses_units = []
            
            # Padrão para capturar uses clause
            uses_pattern = r'uses\s+(.*?);'
            matches = re.finditer(uses_pattern, content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                units_text = match.group(1)
                # Remove comentários e espaços
                units_text = re.sub(r'\{[^}]*\}', '', units_text)
                units_text = re.sub(r'//.*$', '', units_text, flags=re.MULTILINE)
                units_text = re.sub(r'\(\*.*?\*\)', '', units_text, re.DOTALL)
                
                # Separa por vírgula e limpa
                units = [unit.strip() for unit in units_text.split(',') if unit.strip()]
                uses_units.extend(units)
            
            return list(set(uses_units))  # Remove duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao extrair uses clause: {str(e)}")
            return []
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extrai classes do código Pascal"""
        try:
            classes = []
            
            # Padrão para capturar declarações de classe
            class_pattern = r'(\w+)\s*=\s*class\s*(?:\(([^)]+)\))?\s*(.*?)end;'
            matches = re.finditer(class_pattern, content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                class_name = match.group(1)
                parent_class = match.group(2) if match.group(2) else ''
                class_body = match.group(3) if match.group(3) else ''
                
                class_info = {
                    'name': class_name,
                    'parent': parent_class.strip() if parent_class else '',
                    'methods': self._extract_methods_from_class(class_body),
                    'properties': self._extract_properties_from_class(class_body),
                    'is_form': 'tform' in parent_class.lower() if parent_class else False,
                    'is_datamodule': 'tdatamodule' in parent_class.lower() if parent_class else False
                }
                
                classes.append(class_info)
            
            return classes
            
        except Exception as e:
            logger.error(f"Erro ao extrair classes: {str(e)}")
            return []
    
    def _extract_procedures(self, content: str) -> List[Dict[str, Any]]:
        """Extrai procedures do código Pascal"""
        try:
            procedures = []
            
            # Padrão para capturar procedures
            proc_pattern = r'procedure\s+(\w+(?:\.\w+)?)\s*(?:\((.*?)\))?\s*;'
            matches = re.finditer(proc_pattern, content, re.IGNORECASE)
            
            for match in matches:
                proc_name = match.group(1)
                params = match.group(2) if match.group(2) else ''
                
                proc_info = {
                    'name': proc_name,
                    'parameters': self._parse_parameters(params),
                    'type': 'procedure',
                    'visibility': self._determine_visibility(content, match.start())
                }
                
                procedures.append(proc_info)
            
            return procedures
            
        except Exception as e:
            logger.error(f"Erro ao extrair procedures: {str(e)}")
            return []
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extrai functions do código Pascal"""
        try:
            functions = []
            
            # Padrão para capturar functions
            func_pattern = r'function\s+(\w+(?:\.\w+)?)\s*(?:\((.*?)\))?\s*:\s*(\w+)\s*;'
            matches = re.finditer(func_pattern, content, re.IGNORECASE)
            
            for match in matches:
                func_name = match.group(1)
                params = match.group(2) if match.group(2) else ''
                return_type = match.group(3)
                
                func_info = {
                    'name': func_name,
                    'parameters': self._parse_parameters(params),
                    'return_type': return_type,
                    'type': 'function',
                    'visibility': self._determine_visibility(content, match.start())
                }
                
                functions.append(func_info)
            
            return functions
            
        except Exception as e:
            logger.error(f"Erro ao extrair functions: {str(e)}")
            return []
    
    def _extract_methods_from_class(self, class_body: str) -> List[Dict[str, Any]]:
        """Extrai métodos de uma classe"""
        try:
            methods = []
            
            # Extrai procedures da classe
            proc_pattern = r'procedure\s+(\w+)\s*(?:\((.*?)\))?\s*;'
            proc_matches = re.finditer(proc_pattern, class_body, re.IGNORECASE)
            
            for match in proc_matches:
                method_info = {
                    'name': match.group(1),
                    'parameters': self._parse_parameters(match.group(2) if match.group(2) else ''),
                    'type': 'procedure',
                    'is_event_handler': match.group(1).lower().startswith('on')
                }
                methods.append(method_info)
            
            # Extrai functions da classe
            func_pattern = r'function\s+(\w+)\s*(?:\((.*?)\))?\s*:\s*(\w+)\s*;'
            func_matches = re.finditer(func_pattern, class_body, re.IGNORECASE)
            
            for match in func_matches:
                method_info = {
                    'name': match.group(1),
                    'parameters': self._parse_parameters(match.group(2) if match.group(2) else ''),
                    'return_type': match.group(3),
                    'type': 'function',
                    'is_event_handler': match.group(1).lower().startswith('on')
                }
                methods.append(method_info)
            
            return methods
            
        except Exception as e:
            logger.error(f"Erro ao extrair métodos da classe: {str(e)}")
            return []
    
    def _extract_properties_from_class(self, class_body: str) -> List[Dict[str, Any]]:
        """Extrai propriedades de uma classe"""
        try:
            properties = []
            
            # Padrão para capturar propriedades
            prop_pattern = r'property\s+(\w+)\s*:\s*(\w+)(?:\s+read\s+(\w+))?(?:\s+write\s+(\w+))?'
            matches = re.finditer(prop_pattern, class_body, re.IGNORECASE)
            
            for match in matches:
                prop_info = {
                    'name': match.group(1),
                    'type': match.group(2),
                    'read_accessor': match.group(3) if match.group(3) else '',
                    'write_accessor': match.group(4) if match.group(4) else ''
                }
                properties.append(prop_info)
            
            return properties
            
        except Exception as e:
            logger.error(f"Erro ao extrair propriedades da classe: {str(e)}")
            return []
    
    def _parse_parameters(self, params_str: str) -> List[Dict[str, Any]]:
        """Analisa string de parâmetros"""
        try:
            if not params_str or not params_str.strip():
                return []
            
            parameters = []
            
            # Remove espaços e separa por ponto e vírgula
            param_groups = params_str.split(';')
            
            for group in param_groups:
                group = group.strip()
                if not group:
                    continue
                
                # Analisa cada grupo de parâmetros
                if ':' in group:
                    names_part, type_part = group.split(':', 1)
                    param_type = type_part.strip()
                    
                    # Separa nomes de parâmetros
                    param_names = [name.strip() for name in names_part.split(',')]
                    
                    for name in param_names:
                        if name:
                            param_info = {
                                'name': name,
                                'type': param_type,
                                'is_var': name.lower().startswith('var '),
                                'is_const': name.lower().startswith('const ')
                            }
                            parameters.append(param_info)
            
            return parameters
            
        except Exception as e:
            logger.error(f"Erro ao analisar parâmetros: {str(e)}")
            return []
    
    def _determine_visibility(self, content: str, position: int) -> str:
        """Determina a visibilidade de um método baseado na seção"""
        try:
            # Encontra a seção anterior à posição
            content_before = content[:position]
            
            # Procura por palavras-chave de visibilidade
            if 'private' in content_before.lower().split()[-10:]:
                return 'private'
            elif 'protected' in content_before.lower().split()[-10:]:
                return 'protected'
            elif 'public' in content_before.lower().split()[-10:]:
                return 'public'
            elif 'published' in content_before.lower().split()[-10:]:
                return 'published'
            else:
                return 'public'  # Default
                
        except Exception as e:
            logger.error(f"Erro ao determinar visibilidade: {str(e)}")
            return 'public'
    
    def _create_empty_analysis_result(self, project_name: str, project_path: str) -> Dict[str, Any]:
        """Cria resultado vazio em caso de erro"""
        return {
            'metadata': {
                'project_name': project_name,
                'project_path': project_path,
                'analysis_date': datetime.now().isoformat(),
                'analyzer_version': self.version,
                'analysis_type': 'empty_result',
                'error': 'Falha na análise do projeto'
            },
            'files_analyzed': {
                'total_files': 0,
                'files': []
            },
            'code_structure': {
                'functions': [],
                'classes': [],
                'forms': [],
                'data_modules': [],
                'units': []
            },
            'business_logic': {
                'rules': [],
                'patterns': [],
                'workflows': []
            },
            'database_elements': {
                'connections': [],
                'queries': [],
                'tables_referenced': []
            },
            'ui_components': {
                'forms': [],
                'controls': [],
                'menus': []
            },
            'dependencies': {
                'internal_units': [],
                'external_libraries': [],
                'system_units': []
            },
            'complexity_metrics': {
                'total_lines': 0,
                'function_count': 0,
                'class_count': 0,
                'estimated_complexity': 'indefinida'
            },
            'documentation_hints': {
                'suggested_sections': [],
                'key_components': [],
                'main_functions': [],
                'complexity_level': 'indefinida'
            },
            'modernization_suggestions': {
                'priority_areas': [],
                'technology_migration': [],
                'architecture_improvements': []
            }
        }