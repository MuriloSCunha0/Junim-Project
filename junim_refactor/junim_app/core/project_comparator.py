"""
Comparador de Projetos - Compara projetos Delphi e Java para validar modernização
Gera análises comparativas, mapeia funcionalidades e identifica gaps
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ProjectComparator:
    """
    Compara projeto Delphi original com projeto Java modernizado
    Identifica funcionalidades migradas, gaps e diferenças arquiteturais
    """
    
    def __init__(self):
        self.comparison_version = "1.0.0"
        
    def compare_projects(self, delphi_analysis: Dict[str, Any], 
                        java_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara análises de projetos Delphi e Java
        
        Args:
            delphi_analysis: Resultado do LegacyProjectAnalyzer
            java_analysis: Resultado do JavaProjectAnalyzer
            
        Returns:
            Análise comparativa detalhada
        """
        logger.info("🔍 Iniciando comparação entre projetos Delphi e Java")
        
        try:
            comparison_result = {
                'metadata': self._generate_comparison_metadata(delphi_analysis, java_analysis),
                'functionality_mapping': self._map_functionalities(delphi_analysis, java_analysis),
                'architecture_comparison': self._compare_architectures(delphi_analysis, java_analysis),
                'migration_coverage': self._calculate_migration_coverage(delphi_analysis, java_analysis),
                'quality_metrics': self._compare_quality_metrics(delphi_analysis, java_analysis),
                'technology_evolution': self._analyze_technology_evolution(delphi_analysis, java_analysis),
                'validation_results': self._validate_migration(delphi_analysis, java_analysis),
                'recommendations': self._generate_recommendations(delphi_analysis, java_analysis)
            }
            
            logger.info("✅ Comparação de projetos concluída")
            return comparison_result
            
        except Exception as e:
            logger.error(f"❌ Erro na comparação de projetos: {str(e)}")
            raise Exception(f"Falha na comparação de projetos: {str(e)}")
    
    def _generate_comparison_metadata(self, delphi_analysis: Dict[str, Any], 
                                    java_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera metadados da comparação"""
        return {
            'comparison_date': datetime.now().isoformat(),
            'comparator_version': self.comparison_version,
            'original_project': {
                'name': delphi_analysis['metadata']['project_name'],
                'type': 'Delphi Legacy',
                'analysis_date': delphi_analysis['metadata']['analysis_date'],
                'total_files': delphi_analysis['files_analyzed']['total_files']
            },
            'modernized_project': {
                'name': java_analysis['metadata']['project_name'],
                'type': 'Java Spring Boot',
                'analysis_date': java_analysis['metadata']['analysis_date'],
                'total_files': java_analysis['files_analyzed']['total_files']
            }
        }
    
    def _map_functionalities(self, delphi_analysis: Dict[str, Any], 
                           java_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia funcionalidades entre projetos Delphi e Java"""
        logger.info("🗺️ Mapeando funcionalidades entre projetos")
        
        # Extrai funcionalidades do Delphi
        delphi_functions = delphi_analysis['code_structure']['functions']
        delphi_classes = delphi_analysis['code_structure']['classes']
        delphi_forms = delphi_analysis['code_structure'].get('forms', [])
        
        # Extrai funcionalidades do Java
        java_classes = java_analysis['code_structure']['classes']
        java_controllers = java_analysis['spring_components']['controllers']
        java_services = java_analysis['spring_components']['services']
        java_entities = java_analysis['spring_components']['entities']
        
        # Mapeia funcionalidades
        function_mapping = self._map_functions_to_methods(delphi_functions, java_classes)
        class_mapping = self._map_classes_to_components(delphi_classes, java_classes)
        form_mapping = self._map_forms_to_controllers(delphi_forms, java_controllers)
        data_mapping = self._map_data_modules_to_services(delphi_analysis, java_services)
        
        return {
            'function_mapping': function_mapping,
            'class_mapping': class_mapping,
            'form_mapping': form_mapping,
            'data_mapping': data_mapping,
            'mapping_summary': {
                'total_delphi_functions': len(delphi_functions),
                'total_java_methods': sum(len(cls['methods']) for cls in java_classes),
                'mapped_functions': len([m for m in function_mapping if m['mapped']]),
                'unmapped_functions': len([m for m in function_mapping if not m['mapped']])
            }
        }
    
    def _map_functions_to_methods(self, delphi_functions: List[Dict[str, Any]], 
                                java_classes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mapeia funções Delphi para métodos Java"""
        mapping = []
        
        # Coleta todos os métodos Java
        java_methods = []
        for cls in java_classes:
            for method in cls['methods']:
                java_methods.append({
                    'name': method['name'],
                    'class': cls['name'],
                    'return_type': method['return_type'],
                    'parameters': method.get('parameters', [])
                })
        
        for delphi_func in delphi_functions:
            mapped_method = self._find_equivalent_method(delphi_func, java_methods)
            
            mapping.append({
                'delphi_function': delphi_func['name'],
                'delphi_file': delphi_func.get('file', ''),
                'java_method': mapped_method['name'] if mapped_method else None,
                'java_class': mapped_method['class'] if mapped_method else None,
                'mapped': mapped_method is not None,
                'confidence_score': self._calculate_mapping_confidence(delphi_func, mapped_method),
                'mapping_notes': self._generate_mapping_notes(delphi_func, mapped_method)
            })
        
        return mapping
    
    def _find_equivalent_method(self, delphi_function: Dict[str, Any], 
                              java_methods: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Encontra método Java equivalente à função Delphi"""
        delphi_name = delphi_function['name'].lower()
        
        # Busca por nome exato (ignorando case)
        for method in java_methods:
            if method['name'].lower() == delphi_name:
                return method
        
        # Busca por nome similar (remove prefixos/sufixos comuns)
        normalized_delphi = self._normalize_function_name(delphi_name)
        for method in java_methods:
            normalized_java = self._normalize_function_name(method['name'].lower())
            if normalized_delphi == normalized_java:
                return method
        
        # Busca por similaridade semântica
        for method in java_methods:
            if self._calculate_name_similarity(delphi_name, method['name'].lower()) > 0.7:
                return method
        
        return None
    
    def _normalize_function_name(self, name: str) -> str:
        """Normaliza nome de função removendo prefixos/sufixos comuns"""
        # Remove prefixos comuns
        prefixes = ['btn', 'frm', 'get', 'set', 'create', 'delete', 'update']
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        
        # Remove sufixos comuns
        suffixes = ['click', 'handler', 'action', 'event', 'method']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        
        return name.strip('_')
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calcula similaridade entre nomes (algoritmo simples)"""
        if not name1 or not name2:
            return 0.0
        
        # Similaridade baseada em caracteres comuns
        common_chars = sum(1 for a, b in zip(name1, name2) if a == b)
        max_length = max(len(name1), len(name2))
        
        return common_chars / max_length if max_length > 0 else 0.0
    
    def _calculate_mapping_confidence(self, delphi_function: Dict[str, Any], 
                                    java_method: Optional[Dict[str, Any]]) -> float:
        """Calcula confiança do mapeamento (0.0 a 1.0)"""
        if not java_method:
            return 0.0
        
        score = 0.0
        
        # Nome exato ou similar
        if delphi_function['name'].lower() == java_method['name'].lower():
            score += 0.5
        elif self._calculate_name_similarity(delphi_function['name'].lower(), 
                                           java_method['name'].lower()) > 0.7:
            score += 0.3
        
        # Número de parâmetros similar
        delphi_params = len(delphi_function.get('parameters', []))
        java_params = len(java_method.get('parameters', []))
        if delphi_params == java_params:
            score += 0.3
        elif abs(delphi_params - java_params) <= 1:
            score += 0.1
        
        # Tipo de retorno (se disponível)
        if delphi_function.get('return_type') and java_method.get('return_type'):
            if self._are_types_equivalent(delphi_function['return_type'], 
                                        java_method['return_type']):
                score += 0.2
        
        return min(score, 1.0)
    
    def _are_types_equivalent(self, delphi_type: str, java_type: str) -> bool:
        """Verifica se tipos Delphi e Java são equivalentes"""
        type_mappings = {
            'string': 'string',
            'integer': 'integer',
            'boolean': 'boolean',
            'double': 'double',
            'tdatetime': 'localdatetime',
            'void': 'void'
        }
        
        delphi_normalized = delphi_type.lower().strip()
        java_normalized = java_type.lower().strip()
        
        return type_mappings.get(delphi_normalized) == java_normalized
    
    def _generate_mapping_notes(self, delphi_function: Dict[str, Any], 
                              java_method: Optional[Dict[str, Any]]) -> List[str]:
        """Gera notas sobre o mapeamento"""
        notes = []
        
        if not java_method:
            notes.append("Função não encontrada no projeto Java")
            notes.append("Verificar se foi migrada com nome diferente")
        else:
            if delphi_function['name'] != java_method['name']:
                notes.append(f"Nome alterado: {delphi_function['name']} → {java_method['name']}")
            
            delphi_params = len(delphi_function.get('parameters', []))
            java_params = len(java_method.get('parameters', []))
            if delphi_params != java_params:
                notes.append(f"Parâmetros alterados: {delphi_params} → {java_params}")
        
        return notes
    
    def _map_classes_to_components(self, delphi_classes: List[Dict[str, Any]], 
                                 java_classes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mapeia classes Delphi para componentes Java"""
        mapping = []
        
        for delphi_class in delphi_classes:
            java_equivalent = self._find_equivalent_class(delphi_class, java_classes)
            
            mapping.append({
                'delphi_class': delphi_class['name'],
                'delphi_type': delphi_class.get('type', 'class'),
                'java_class': java_equivalent['name'] if java_equivalent else None,
                'java_type': self._determine_java_component_type(java_equivalent) if java_equivalent else None,
                'mapped': java_equivalent is not None,
                'confidence_score': self._calculate_class_mapping_confidence(delphi_class, java_equivalent)
            })
        
        return mapping
    
    def _find_equivalent_class(self, delphi_class: Dict[str, Any], 
                             java_classes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Encontra classe Java equivalente à classe Delphi"""
        delphi_name = delphi_class['name'].lower()
        
        # Remove prefixo T comum em Delphi
        if delphi_name.startswith('t') and len(delphi_name) > 1:
            delphi_name = delphi_name[1:]
        
        # Busca por nome similar
        for java_class in java_classes:
            java_name = java_class['name'].lower()
            
            if java_name == delphi_name or delphi_name in java_name or java_name in delphi_name:
                return java_class
        
        return None
    
    def _determine_java_component_type(self, java_class: Dict[str, Any]) -> str:
        """Determina o tipo de componente Java baseado nas anotações"""
        annotations = java_class.get('annotations', [])
        
        if 'Controller' in annotations or 'RestController' in annotations:
            return 'Controller'
        elif 'Service' in annotations:
            return 'Service'
        elif 'Repository' in annotations:
            return 'Repository'
        elif 'Entity' in annotations:
            return 'Entity'
        elif 'Configuration' in annotations:
            return 'Configuration'
        else:
            return 'Component'
    
    def _calculate_class_mapping_confidence(self, delphi_class: Dict[str, Any], 
                                          java_class: Optional[Dict[str, Any]]) -> float:
        """Calcula confiança do mapeamento de classe"""
        if not java_class:
            return 0.0
        
        # Implementação similar ao mapeamento de funções
        return 0.8  # Placeholder - implementar lógica específica
    
    def _map_forms_to_controllers(self, delphi_forms: List[Dict[str, Any]], 
                                java_controllers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mapeia formulários Delphi para controllers Java"""
        mapping = []
        
        for form in delphi_forms:
            controller = self._find_equivalent_controller(form, java_controllers)
            
            mapping.append({
                'delphi_form': form['name'],
                'java_controller': controller['name'] if controller else None,
                'endpoints': controller['endpoints'] if controller else [],
                'mapped': controller is not None
            })
        
        return mapping
    
    def _find_equivalent_controller(self, delphi_form: Dict[str, Any], 
                                  java_controllers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Encontra controller Java equivalente ao formulário Delphi"""
        form_name = delphi_form['name'].lower()
        
        # Remove prefixos comuns de formulários
        if form_name.startswith('frm'):
            form_name = form_name[3:]
        elif form_name.startswith('form'):
            form_name = form_name[4:]
        
        for controller in java_controllers:
            controller_name = controller['name'].lower()
            if form_name in controller_name or controller_name.replace('controller', '') in form_name:
                return controller
        
        return None
    
    def _map_data_modules_to_services(self, delphi_analysis: Dict[str, Any], 
                                    java_services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mapeia data modules Delphi para services Java"""
        mapping = []
        
        data_modules = delphi_analysis['code_structure'].get('data_modules', [])
        
        for dm in data_modules:
            service = self._find_equivalent_service(dm, java_services)
            
            mapping.append({
                'delphi_data_module': dm['name'],
                'java_service': service['name'] if service else None,
                'mapped': service is not None
            })
        
        return mapping
    
    def _find_equivalent_service(self, data_module: Dict[str, Any], 
                               java_services: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Encontra service Java equivalente ao data module Delphi"""
        dm_name = data_module['name'].lower()
        
        # Remove prefixos comuns
        if dm_name.startswith('dm'):
            dm_name = dm_name[2:]
        elif dm_name.startswith('datamodule'):
            dm_name = dm_name[10:]
        
        for service in java_services:
            service_name = service['name'].lower()
            if dm_name in service_name or service_name.replace('service', '') in dm_name:
                return service
        
        return None
    
    def _compare_architectures(self, delphi_analysis: Dict[str, Any], 
                             java_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compara arquiteturas entre projetos"""
        return {
            'delphi_architecture': {
                'pattern': 'Monolithic Desktop Application',
                'ui_technology': 'VCL Forms',
                'data_access': 'Direct Database Access',
                'components': {
                    'forms': len(delphi_analysis['code_structure'].get('forms', [])),
                    'data_modules': len(delphi_analysis['code_structure'].get('data_modules', [])),
                    'classes': len(delphi_analysis['code_structure']['classes']),
                    'functions': len(delphi_analysis['code_structure']['functions'])
                }
            },
            'java_architecture': {
                'pattern': 'Layered Web Application (Spring MVC)',
                'ui_technology': 'REST API',
                'data_access': 'JPA/Hibernate ORM',
                'components': java_analysis['spring_components']['component_summary']
            },
            'architectural_improvements': [
                'Separação de responsabilidades (Controllers, Services, Repositories)',
                'API REST para integração com diferentes frontends',
                'ORM para abstração de banco de dados',
                'Injeção de dependência automática',
                'Configuração baseada em anotações',
                'Melhor testabilidade com Spring Test'
            ]
        }
    
    def _calculate_migration_coverage(self, delphi_analysis: Dict[str, Any], 
                                    java_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula cobertura da migração"""
        delphi_functions = len(delphi_analysis['code_structure']['functions'])
        delphi_classes = len(delphi_analysis['code_structure']['classes'])
        
        java_methods = sum(len(cls['methods']) for cls in java_analysis['code_structure']['classes'])
        java_classes = len(java_analysis['code_structure']['classes'])
        
        # Calcula percentuais de cobertura (estimativa)
        function_coverage = min((java_methods / delphi_functions) * 100, 100) if delphi_functions > 0 else 100
        class_coverage = min((java_classes / delphi_classes) * 100, 100) if delphi_classes > 0 else 100
        
        overall_coverage = (function_coverage + class_coverage) / 2
        
        return {
            'function_coverage_percent': round(function_coverage, 2),
            'class_coverage_percent': round(class_coverage, 2),
            'overall_coverage_percent': round(overall_coverage, 2),
            'coverage_status': self._determine_coverage_status(overall_coverage),
            'missing_components': self._identify_missing_components(delphi_analysis, java_analysis)
        }
    
    def _determine_coverage_status(self, coverage_percent: float) -> str:
        """Determina status da cobertura"""
        if coverage_percent >= 90:
            return "Excelente"
        elif coverage_percent >= 75:
            return "Boa"
        elif coverage_percent >= 50:
            return "Parcial"
        else:
            return "Insuficiente"
    
    def _identify_missing_components(self, delphi_analysis: Dict[str, Any], 
                                   java_analysis: Dict[str, Any]) -> List[str]:
        """Identifica componentes não migrados"""
        missing = []
        
        # Identifica funções não migradas (implementação simplificada)
        delphi_function_names = [f['name'] for f in delphi_analysis['code_structure']['functions']]
        java_method_names = []
        for cls in java_analysis['code_structure']['classes']:
            java_method_names.extend([m['name'] for m in cls['methods']])
        
        for func_name in delphi_function_names:
            if not any(self._calculate_name_similarity(func_name.lower(), java_name.lower()) > 0.7 
                      for java_name in java_method_names):
                missing.append(f"Função: {func_name}")
        
        return missing[:10]  # Limita a 10 para não sobrecarregar
    
    def _compare_quality_metrics(self, delphi_analysis: Dict[str, Any], 
                               java_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compara métricas de qualidade"""
        return {
            'code_organization': {
                'delphi': 'Procedural/OOP misto',
                'java': 'OOP puro com padrões Spring',
                'improvement': 'Melhor organização e separação de responsabilidades'
            },
            'maintainability': {
                'delphi': 'Dependente de IDE específica',
                'java': 'Multiplataforma com ferramentas diversas',
                'improvement': 'Maior flexibilidade de ferramentas e ambiente'
            },
            'testability': {
                'delphi': 'Testes limitados',
                'java': 'Framework completo de testes',
                'improvement': 'Melhor cobertura e facilidade de testes'
            },
            'scalability': {
                'delphi': 'Desktop monousuário',
                'java': 'Web multiusuário escalável',
                'improvement': 'Suporte a múltiplos usuários simultâneos'
            }
        }
    
    def _analyze_technology_evolution(self, delphi_analysis: Dict[str, Any], 
                                    java_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa evolução tecnológica"""
        return {
            'platform_evolution': {
                'from': 'Windows Desktop (Delphi/Pascal)',
                'to': 'Multiplataforma Web (Java Spring Boot)',
                'benefits': [
                    'Execução em diferentes sistemas operacionais',
                    'Acesso via navegador web',
                    'Facilidade de deployment em nuvem',
                    'Integração com outros sistemas via API'
                ]
            },
            'data_access_evolution': {
                'from': 'Acesso direto ao banco via componentes VCL',
                'to': 'ORM (JPA/Hibernate) com abstração de banco',
                'benefits': [
                    'Independência de banco de dados específico',
                    'Melhor performance com cache de entidades',
                    'Consultas type-safe com Criteria API',
                    'Controle automático de transações'
                ]
            },
            'integration_evolution': {
                'from': 'Integração limitada via COM/DLL',
                'to': 'API REST com JSON e documentação automática',
                'benefits': [
                    'Integração fácil com qualquer tecnologia',
                    'Documentação automática com OpenAPI',
                    'Versionamento de API',
                    'Testes automatizados de integração'
                ]
            }
        }
    
    def _validate_migration(self, delphi_analysis: Dict[str, Any], 
                          java_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Valida se a migração foi bem-sucedida"""
        validations = []
        
        # Validação de funcionalidades principais
        delphi_functions = len(delphi_analysis['code_structure']['functions'])
        java_methods = sum(len(cls['methods']) for cls in java_analysis['code_structure']['classes'])
        
        if java_methods >= delphi_functions * 0.8:
            validations.append({
                'aspect': 'Cobertura de Funcionalidades',
                'status': 'PASS',
                'message': f'Migração de funcionalidades adequada ({java_methods} métodos Java para {delphi_functions} funções Delphi)'
            })
        else:
            validations.append({
                'aspect': 'Cobertura de Funcionalidades',
                'status': 'WARNING',
                'message': f'Possível funcionalidade não migrada ({java_methods} métodos Java para {delphi_functions} funções Delphi)'
            })
        
        # Validação de arquitetura Spring
        spring_components = java_analysis['spring_components']['component_summary']
        if spring_components['total_controllers'] > 0:
            validations.append({
                'aspect': 'Arquitetura Spring MVC',
                'status': 'PASS',
                'message': f'{spring_components["total_controllers"]} controllers implementados'
            })
        else:
            validations.append({
                'aspect': 'Arquitetura Spring MVC',
                'status': 'FAIL',
                'message': 'Nenhum controller encontrado'
            })
        
        # Validação de persistência
        if spring_components['total_entities'] > 0 and spring_components['total_repositories'] > 0:
            validations.append({
                'aspect': 'Camada de Persistência',
                'status': 'PASS',
                'message': f'{spring_components["total_entities"]} entidades e {spring_components["total_repositories"]} repositórios'
            })
        else:
            validations.append({
                'aspect': 'Camada de Persistência',
                'status': 'WARNING',
                'message': 'Camada de persistência pode estar incompleta'
            })
        
        # Validação de lógica de negócio
        if spring_components['total_services'] > 0:
            validations.append({
                'aspect': 'Lógica de Negócio',
                'status': 'PASS',
                'message': f'{spring_components["total_services"]} services implementados'
            })
        else:
            validations.append({
                'aspect': 'Lógica de Negócio',
                'status': 'WARNING',
                'message': 'Poucos services encontrados - verificar lógica de negócio'
            })
        
        # Calcula resultado geral
        passed = len([v for v in validations if v['status'] == 'PASS'])
        warnings = len([v for v in validations if v['status'] == 'WARNING'])
        failed = len([v for v in validations if v['status'] == 'FAIL'])
        
        if failed > 0:
            overall_status = 'FAIL'
        elif warnings > passed:
            overall_status = 'WARNING'
        else:
            overall_status = 'PASS'
        
        return {
            'overall_status': overall_status,
            'validations': validations,
            'summary': {
                'passed': passed,
                'warnings': warnings,
                'failed': failed,
                'total': len(validations)
            }
        }
    
    def _generate_recommendations(self, delphi_analysis: Dict[str, Any], 
                                java_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Gera recomendações baseadas na comparação"""
        recommendations = []
        
        # Baseado na cobertura de migração
        coverage = self._calculate_migration_coverage(delphi_analysis, java_analysis)
        if coverage['overall_coverage_percent'] < 80:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Completude da Migração',
                'recommendation': 'Revisar componentes não migrados e implementar funcionalidades ausentes',
                'rationale': f'Cobertura de migração de {coverage["overall_coverage_percent"]:.1f}% pode indicar funcionalidades perdidas'
            })
        
        # Baseado na validação
        validation = self._validate_migration(delphi_analysis, java_analysis)
        if validation['summary']['failed'] > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Correção de Falhas',
                'recommendation': 'Corrigir problemas críticos identificados na validação',
                'rationale': f'{validation["summary"]["failed"]} validações falharam'
            })
        
        # Recomendações gerais
        recommendations.extend([
            {
                'priority': 'MEDIUM',
                'category': 'Testes',
                'recommendation': 'Implementar suite completa de testes unitários e de integração',
                'rationale': 'Garantir qualidade e facilitar manutenção futura'
            },
            {
                'priority': 'LOW',
                'category': 'Documentação',
                'recommendation': 'Documentar APIs com OpenAPI/Swagger',
                'rationale': 'Facilitar integração e uso por outros sistemas'
            },
            {
                'priority': 'MEDIUM',
                'category': 'Monitoramento',
                'recommendation': 'Configurar monitoramento e logging estruturado',
                'rationale': 'Facilitar operação e troubleshooting em produção'
            }
        ])
        
        return recommendations
