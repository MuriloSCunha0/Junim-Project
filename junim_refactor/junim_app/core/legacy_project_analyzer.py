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

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegacyProjectAnalyzer:
    """Analisador avançado de projetos Delphi legados"""
    
    def __init__(self):
        """Inicializa o analisador"""
        self.version = "1.0.0"
        self.project_info = {}
        self.units_analysis = {}
        self.business_logic = {}
        self.data_flows = {}
        self.execution_flows = {}
        self.correlations = {}
        self.requirements = {}
        self.characteristics = {}
        
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
                    'user_interface': self._extract_ui_elements(content),
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
    
    def analyze_project(self, project_path: str, **kwargs) -> Dict[str, Any]:
        """
        Analisa projeto Delphi completo e retorna dados estruturados
        
        Args:
            project_path: Caminho para o projeto
            **kwargs: Configurações adicionais
            
        Returns:
            Dicionário com análise completa do projeto
        """
        try:
            logger.info(f"Iniciando análise do projeto: {project_path}")
            
            # Configurações da análise
            config = {
                'project_name': kwargs.get('project_name', 'Unknown Project'),
                'include_comments': kwargs.get('include_comments', True),
                'analyze_business_logic': kwargs.get('analyze_business_logic', True),
                'generate_correlations': kwargs.get('generate_correlations', True)
            }
            
            # Coleta informações básicas do projeto
            project_info = self.extract_project_info(project_path)
            
            # Análise de cada unit
            units_analysis = self.analyze_units(project_path)
            
            # Extrai características do sistema
            characteristics = self.extract_system_characteristics(units_analysis)
            
            # Identifica fluxos de execução
            execution_flows = self.identify_execution_flows(units_analysis)
            
            # Mapeia fluxos de dados
            data_flows = self.map_data_flows(units_analysis)
            
            # Extrai requisitos do sistema
            requirements = self.extract_requirements(units_analysis, project_info)
            
            # Monta resultado final
            analysis_result = {
                'metadata': {
                    'project_name': config['project_name'],
                    'analysis_date': datetime.now().isoformat(),
                    'analyzer_version': self.version,
                    'total_files_analyzed': project_info.get('total_files', 0),
                    'analysis_config': config
                },
                'project_info': project_info,
                'units_analysis': units_analysis,
                'characteristics': characteristics,
                'execution_flows': execution_flows,
                'data_flows': data_flows,
                'requirements': requirements
            }
            
            logger.info(f"Análise concluída: {len(units_analysis)} units analisadas")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Erro na análise do projeto: {str(e)}")
            raise Exception(f"Falha na análise: {str(e)}")

    def extract_project_info(self, project_path: str) -> Dict[str, Any]:
        """Extrai informações básicas do projeto"""
        try:
            project_info = {
                'project_path': project_path,
                'total_files': 0,
                'file_counts': {'pascal_units': 0, 'forms': 0, 'projects': 0, 'others': 0},
                'delphi_version': 'Unknown',
                'architecture_type': 'Desktop'
            }
            
            # Conta arquivos por tipo
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    project_info['total_files'] += 1
                    
                    if file.endswith('.pas'):
                        project_info['file_counts']['pascal_units'] += 1
                    elif file.endswith('.dfm'):
                        project_info['file_counts']['forms'] += 1
                    elif file.endswith(('.dpr', '.dpk')):
                        project_info['file_counts']['projects'] += 1
                    else:
                        project_info['file_counts']['others'] += 1
            
            # Tenta identificar versão do Delphi através de arquivos de projeto
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.dpr'):
                        dpr_path = os.path.join(root, file)
                        try:
                            with open(dpr_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if 'program' in content.lower():
                                    project_info['architecture_type'] = 'Desktop Application'
                                elif 'library' in content.lower():
                                    project_info['architecture_type'] = 'Library/DLL'
                        except:
                            pass
            
            return project_info
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações do projeto: {str(e)}")
            return {'error': str(e)}

    def analyze_units(self, project_path: str) -> Dict[str, Any]:
        """Analisa todas as units do projeto"""
        units_analysis = {}
        
        try:
            # Encontra todos os arquivos Pascal
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.pas'):
                        file_path = os.path.join(root, file)
                        unit_name = os.path.splitext(file)[0]
                        
                        try:
                            unit_data = self.analyze_single_unit(file_path)
                            units_analysis[unit_name] = unit_data
                        except Exception as e:
                            logger.warning(f"Erro ao analisar unit {unit_name}: {str(e)}")
                            units_analysis[unit_name] = {'error': str(e), 'file_path': file_path}
            
            return units_analysis
            
        except Exception as e:
            logger.error(f"Erro na análise de units: {str(e)}")
            return {'error': str(e)}

    def analyze_single_unit(self, file_path: str) -> Dict[str, Any]:
        """Analisa uma única unit Pascal"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            unit_data = {
                'file_path': file_path,
                'lines_count': len(content.splitlines()),
                'unit_type': self._detect_unit_type(content),
                'classes': self._extract_classes(content),
                'procedures_functions': self._extract_procedures_functions(content),
                'uses_units': self._extract_uses_units(content),
                'database_operations': self._extract_database_operations(content),
                'complexity_metrics': self._calculate_complexity(content),
                'comments': self._extract_comments(content)
            }
            
            return unit_data
            
        except Exception as e:
            logger.error(f"Erro ao analisar unit {file_path}: {str(e)}")
            return {'error': str(e), 'file_path': file_path}

    def _detect_unit_type(self, content: str) -> str:
        """Detecta o tipo da unit baseado no conteúdo"""
        content_lower = content.lower()
        
        if 'tform' in content_lower or 'inherited' in content_lower:
            return 'form'
        elif 'tdatamodule' in content_lower or 'datamodule' in content_lower:
            return 'datamodule'
        elif 'class(' in content_lower or 'class ' in content_lower:
            return 'class'
        elif 'interface' in content_lower and 'implementation' in content_lower:
            return 'unit'
        else:
            return 'unknown'

    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extrai classes do código"""
        classes = []
        
        # Pattern para classes Delphi
        class_pattern = re.compile(r'(\w+)\s*=\s*class\s*\(([^)]*)\)', re.IGNORECASE)
        
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            parent_class = match.group(2).strip() if match.group(2) else None
            
            classes.append({
                'name': class_name,
                'parent_class': parent_class,
                'purpose': self._infer_class_purpose(class_name, parent_class)
            })
        
        return classes

    def _extract_procedures_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extrai procedures e functions"""
        procedures = []
        
        # Patterns para procedures e functions
        proc_pattern = re.compile(r'(procedure|function)\s+(\w+)', re.IGNORECASE)
        
        for match in proc_pattern.finditer(content):
            proc_type = match.group(1).lower()
            proc_name = match.group(2)
            
            procedures.append({
                'name': proc_name,
                'type': proc_type,
                'purpose': self._infer_procedure_purpose(proc_name),
                'complexity': self._calculate_procedure_complexity(content, proc_name)
            })
        
        return procedures

    def _extract_uses_units(self, content: str) -> List[str]:
        """Extrai units referenciadas na cláusula uses"""
        uses_units = []
        
        uses_pattern = re.compile(r'uses\s+(.*?);', re.DOTALL | re.IGNORECASE)
        match = uses_pattern.search(content)
        
        if match:
            uses_content = match.group(1)
            # Remove comentários e quebras de linha
            uses_content = re.sub(r'\{.*?\}', '', uses_content)
            uses_content = re.sub(r'//.*', '', uses_content)
            
            units = [unit.strip() for unit in uses_content.split(',')]
            uses_units = [unit for unit in units if unit]
        
        return uses_units

    def _extract_database_operations(self, content: str) -> List[Dict[str, Any]]:
        """Extrai operações de banco de dados"""
        db_operations = []
        
        # Patterns para operações de BD
        db_patterns = [
            (r'(Query\w*|Table\w*)\s*\.\s*(Open|Close|ExecSQL)', 'query_operation'),
            (r'(SQL\w*)\s*\.\s*(Add|Clear)', 'sql_manipulation'),
            (r'(Transaction\w*)\s*\.\s*(StartTransaction|Commit|Rollback)', 'transaction'),
            (r'(Connection\w*)\s*\.\s*(Connect|Disconnect)', 'connection')
        ]
        
        for pattern, operation_type in db_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                db_operations.append({
                    'name': match.group(0),
                    'type': operation_type,
                    'description': f"{operation_type.replace('_', ' ').title()} operation"
                })
        
        return db_operations

    def _calculate_complexity(self, content: str) -> Dict[str, int]:
        """Calcula métricas de complexidade"""
        lines = content.splitlines()
        
        metrics = {
            'lines_of_code': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity(content),
            'function_count': len(re.findall(r'(procedure|function)\s+\w+', content, re.IGNORECASE)),
            'class_count': len(re.findall(r'\w+\s*=\s*class\s*\(', content, re.IGNORECASE)),
            'nesting_depth': self._calculate_nesting_depth(content)
        }
        
        return metrics

    def _calculate_cyclomatic_complexity(self, content: str) -> int:
        """Calcula complexidade ciclomática básica"""
        # Conta estruturas de controle que aumentam complexidade
        complexity_keywords = [
            r'\bif\b', r'\bwhile\b', r'\bfor\b', r'\brepeat\b',
            r'\bcase\b', r'\btry\b', r'\band\b', r'\bor\b'
        ]
        
        total_complexity = 1  # Complexidade base
        
        for keyword in complexity_keywords:
            matches = re.findall(keyword, content, re.IGNORECASE)
            total_complexity += len(matches)
        
        return total_complexity

    def _calculate_nesting_depth(self, content: str) -> int:
        """Calcula profundidade máxima de aninhamento"""
        max_depth = 0
        current_depth = 0
        
        begin_keywords = ['begin', 'try', 'case']
        end_keywords = ['end', 'except', 'finally']
        
        lines = content.splitlines()
        
        for line in lines:
            line_clean = line.strip().lower()
            
            for keyword in begin_keywords:
                if keyword in line_clean:
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)
            
            for keyword in end_keywords:
                if keyword in line_clean:
                    current_depth = max(0, current_depth - 1)
        
        return max_depth

    def _extract_comments(self, content: str) -> List[str]:
        """Extrai comentários do código"""
        comments = []
        
        # Comentários de linha única
        single_line_comments = re.findall(r'//\s*(.+)', content)
        comments.extend(single_line_comments)
        
        # Comentários de bloco
        block_comments = re.findall(r'\{\s*(.*?)\s*\}', content, re.DOTALL)
        comments.extend(block_comments)
        
        # Limpa e filtra comentários
        comments = [comment.strip() for comment in comments if comment.strip()]
        
        return comments

    def _infer_class_purpose(self, class_name: str, parent_class: str) -> str:
        """Infere o propósito de uma classe baseado no nome e herança"""
        name_lower = class_name.lower()
        parent_lower = parent_class.lower() if parent_class else ""
        
        if 'form' in name_lower or 'tform' in parent_lower:
            return 'User Interface Form'
        elif 'datamodule' in name_lower or 'tdatamodule' in parent_lower:
            return 'Data Access Module'
        elif 'service' in name_lower or 'manager' in name_lower:
            return 'Business Logic Service'
        elif 'helper' in name_lower or 'util' in name_lower:
            return 'Utility Class'
        else:
            return 'General Purpose Class'

    def _infer_procedure_purpose(self, proc_name: str) -> str:
        """Infere o propósito de uma procedure/function"""
        name_lower = proc_name.lower()
        
        if 'click' in name_lower or 'btn' in name_lower:
            return 'User Interface Event'
        elif 'create' in name_lower or 'insert' in name_lower:
            return 'Data Creation'
        elif 'update' in name_lower or 'modify' in name_lower:
            return 'Data Update'
        elif 'delete' in name_lower or 'remove' in name_lower:
            return 'Data Deletion'
        elif 'get' in name_lower or 'find' in name_lower or 'select' in name_lower:
            return 'Data Retrieval'
        elif 'validate' in name_lower or 'check' in name_lower:
            return 'Data Validation'
        elif 'calculate' in name_lower or 'compute' in name_lower:
            return 'Calculation/Processing'
        else:
            return 'General Processing'

    def _calculate_procedure_complexity(self, content: str, proc_name: str) -> int:
        """Calcula complexidade de uma procedure específica"""
        # Encontra o corpo da procedure
        proc_pattern = re.compile(f'procedure\\s+{proc_name}.*?begin(.*?)end;', re.DOTALL | re.IGNORECASE)
        match = proc_pattern.search(content)
        
        if match:
            proc_body = match.group(1)
            return self._calculate_cyclomatic_complexity(proc_body)
        
        return 1

    def _extract_classes_detailed(self, content: str) -> List[Dict[str, Any]]:
        """Extrai classes com análise detalhada"""
        classes = []
        
        # Pattern para classes Delphi
        class_pattern = re.compile(r'(\w+)\s*=\s*class\s*\(([^)]*)\)', re.IGNORECASE)
        
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            parent_class = match.group(2).strip() if match.group(2) else None
            
            class_info = {
                'name': class_name,
                'parent_class': parent_class,
                'purpose': self._infer_class_purpose(class_name, parent_class),
                'visibility_sections': self._extract_visibility_sections(content, class_name),
                'methods': self._extract_class_methods_detailed(content, class_name),
                'properties': self._extract_class_properties(content, class_name),
                'fields': self._extract_class_fields(content, class_name),
                'events': self._extract_class_events(content, class_name)
            }
            
            classes.append(class_info)
        
        return classes
    
    def _extract_procedures_functions_detailed(self, content: str) -> List[Dict[str, Any]]:
        """Extrai procedures e functions com análise detalhada"""
        procedures = []
        
        # Patterns para procedures e functions
        proc_pattern = re.compile(
            r'(procedure|function)\s+(\w+)\s*(\([^)]*\))?\s*(?::\s*(\w+))?\s*;',
            re.IGNORECASE
        )
        
        for match in proc_pattern.finditer(content):
            proc_type = match.group(1).lower()
            proc_name = match.group(2)
            parameters = match.group(3) if match.group(3) else ""
            return_type = match.group(4) if match.group(4) else None
            
            # Extrai corpo da procedure/function
            proc_body = self._extract_procedure_body(content, proc_name)
            
            proc_info = {
                'name': proc_name,
                'type': proc_type,
                'parameters': self._parse_parameters(parameters),
                'return_type': return_type,
                'body': proc_body,
                'complexity_metrics': {
                    'cyclomatic_complexity': self._calculate_function_complexity(proc_body)
                },
                'function_calls': self._extract_function_calls(proc_body),
                'purpose': self._infer_function_purpose(proc_name, proc_body),
                'description': f"{proc_type.title()} {proc_name}"
            }
            
            procedures.append(proc_info)
        
        return procedures
    
    def _calculate_complexity_metrics(self, content: str) -> Dict[str, Any]:
        """Calcula métricas de complexidade detalhadas"""
        lines = content.splitlines()
        
        metrics = {
            'lines_of_code': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity(content),
            'function_count': len(re.findall(r'(procedure|function)\s+\w+', content, re.IGNORECASE)),
            'class_count': len(re.findall(r'\w+\s*=\s*class\s*\(', content, re.IGNORECASE)),
            'nesting_depth': self._calculate_max_nesting_depth(content),
            'comment_ratio': self._calculate_comment_ratio(content),
            'maintainability_index': self._calculate_maintainability_index(content)
        }
        
        return metrics
    
    def _calculate_maintainability_index(self, content: str) -> float:
        """Calcula índice de manutenibilidade simplificado"""
        try:
            loc = len([line for line in content.splitlines() if line.strip()])
            complexity = self._calculate_cyclomatic_complexity(content)
            comment_ratio = self._calculate_comment_ratio(content)
            
            # Fórmula simplificada do índice de manutenibilidade
            if loc == 0:
                return 0.0
            
            volume = loc * 4.32  # Estimativa de volume de Halstead simplificada
            maintainability = max(0, (171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(loc) + 50 * math.sin(math.sqrt(2.4 * comment_ratio))) / 171)
            
            return round(maintainability, 2)
            
        except:
            return 0.5  # Valor padrão
    
    # Placeholder para métodos adicionais que serão implementados conforme necessário
    def _extract_dependencies(self, content: str) -> List[str]: return []
    def _extract_variables(self, content: str) -> List[Dict]: return []
    def _extract_constants(self, content: str) -> List[Dict]: return []
    def _extract_database_operations(self, content: str) -> List[Dict]: return []
    def _extract_ui_elements(self, content: str) -> List[Dict]: return []
    def _extract_business_rules(self, content: str) -> List[str]: return []
    def _analyze_form_file(self, content: str) -> Dict: return {}
    def _is_validation_function(self, proc: Dict) -> bool: return False
    def _extract_calculations(self, unit_data: Dict) -> List[Dict]: return []
    def _determine_data_direction(self, db_op: Dict) -> str: return 'bidirectional'
    def _analyze_form_data_flows(self, unit_data: Dict) -> List[Dict]: return []
    def _analyze_inter_unit_flows(self, unit_name: str, unit_data: Dict) -> List[Dict]: return []
    def _find_main_project_unit(self) -> Optional[Dict]: return None
    def _analyze_startup_sequence(self, main_project: Dict) -> List[Dict]: return []
    def _extract_user_workflows(self, unit_name: str, unit_data: Dict) -> List[Dict]: return []
    def _analyze_error_handling(self) -> List[Dict]: return []
    def _extract_functional_requirements(self, unit_name: str, unit_data: Dict) -> List[Dict]: return []
    def _identify_non_functional_requirements(self) -> List[Dict]: return []
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
    def _generate_unit_correlations(self, unit_name: str, unit_data: Dict) -> List[Dict]: return []
    def _generate_pattern_mappings(self) -> List[Dict]: return []
    def _generate_architecture_mappings(self) -> List[Dict]: return []
    def _generate_technology_mappings(self) -> List[Dict]: return []
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
        """Método público para extrair lógica de negócio"""
        try:
            # Atualiza análise interna
            self.units_analysis = units_analysis
            # Chama método privado
            return self._extract_business_logic()
        except Exception as e:
            logger.error(f"Erro ao extrair lógica de negócio: {str(e)}")
            return {'error': str(e)}

    def generate_delphi_java_correlations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Método público para gerar correlações Delphi→Java"""
        try:
            # Atualiza análise interna
            self.units_analysis = analysis_results.get('units_analysis', {})
            self.project_info = analysis_results.get('project_info', {})
            # Chama método privado
            return self._generate_correlations()
        except Exception as e:
            logger.error(f"Erro ao gerar correlações: {str(e)}")
            return {'error': str(e)}

    # ...existing code...
