"""
Motor de Modernização - Responsável pela lógica de modernização Delphi → Java Spring
Focado em análise estruturada e geração de estratégias de modernização
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class ModernizationComponent:
    """Representa um componente para modernização"""
    delphi_name: str
    delphi_type: str  # 'unit', 'form', 'class', 'function'
    java_equivalent: str
    java_type: str  # 'controller', 'service', 'entity', 'repository'
    complexity_score: int  # 1-5 (1=simples, 5=complexo)
    dependencies: List[str]
    migration_notes: List[str]

class ModernizationEngine:
    """
    Motor principal de modernização que analisa código Delphi e gera estratégias
    estruturadas para conversão para Java Spring Boot
    """
    
    def __init__(self):
        self.version = "2.0.0"
        self.delphi_java_mappings = self._load_default_mappings()
        self.modernization_components = []
    
    def analyze_for_modernization(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa dados estruturados do projeto Delphi e gera estratégia de modernização
        
        Args:
            analysis_data: Dados estruturados do LegacyProjectAnalyzer
            
        Returns:
            Estratégia detalhada de modernização
        """
        logger.info("🚀 Iniciando análise para modernização")
        
        try:
            # Valida se recebeu dados estruturados adequados
            if not self._validate_analysis_data(analysis_data):
                raise ValueError("Dados de análise inválidos ou incompletos")
            
            # Extrai componentes principais para modernização
            components = self._extract_modernization_components(analysis_data)
            
            # Gera mapeamento Delphi → Java
            java_mapping = self._generate_java_mapping(components, analysis_data)
            
            # Calcula métricas de complexidade
            complexity_analysis = self._analyze_migration_complexity(components)
            
            # Gera fases de migração
            migration_phases = self._generate_migration_phases(components, complexity_analysis)
            
            # Gera recomendações arquiteturais
            architecture_recommendations = self._generate_architecture_recommendations(analysis_data)
            
            # Compila estratégia final
            modernization_strategy = {
                'metadata': {
                    'project_name': analysis_data['metadata']['project_name'],
                    'modernization_engine_version': self.version,
                    'analysis_date': analysis_data['metadata']['analysis_date'],
                    'total_components': len(components)
                },
                'summary': {
                    'complexity_level': complexity_analysis['overall_complexity'],
                    'estimated_effort_weeks': complexity_analysis['estimated_weeks'],
                    'priority_components': complexity_analysis['priority_list'][:5],
                    'risk_factors': complexity_analysis['risk_factors']
                },
                'component_mapping': java_mapping,
                'migration_phases': migration_phases,
                'architecture_strategy': architecture_recommendations,
                'detailed_components': [component.__dict__ for component in components],
                'technology_stack': self._recommend_technology_stack(analysis_data),
                'implementation_guidelines': self._generate_implementation_guidelines(),
                'validation_checklist': self._generate_validation_checklist()
            }
            
            logger.info(f"✅ Estratégia de modernização gerada: {len(components)} componentes analisados")
            return modernization_strategy
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de modernização: {str(e)}")
            raise Exception(f"Falha na geração da estratégia de modernização: {str(e)}")
    
    def analyze_modernized_project(self, java_project_path: str, 
                                 original_delphi_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa projeto Java modernizado e compara com o Delphi original
        
        Args:
            java_project_path: Caminho para o projeto Java
            original_delphi_analysis: Análise do projeto Delphi original
            
        Returns:
            Análise completa do projeto modernizado com comparações
        """
        logger.info(f"🔄 Analisando projeto modernizado: {java_project_path}")
        
        try:
            # Importa analisadores (lazy import para evitar dependências circulares)
            from .java_project_analyzer import JavaProjectAnalyzer
            from .project_comparator import ProjectComparator
            from .java_documentation_generator import JavaDocumentationGenerator
            
            # Analisa projeto Java
            java_analyzer = JavaProjectAnalyzer()
            java_analysis = java_analyzer.analyze_java_project(java_project_path)
            
            # Compara com projeto Delphi original
            comparator = ProjectComparator()
            comparison_data = comparator.compare_projects(original_delphi_analysis, java_analysis)
            
            # Gera documentação do projeto modernizado
            java_doc_generator = JavaDocumentationGenerator()
            
            # Determina diretório de saída
            project_name = java_analysis['metadata']['project_name']
            output_dir = f"output/java_documentation_{project_name}"
            
            java_documentation = java_doc_generator.generate_java_documentation(
                java_analysis, comparison_data, output_dir
            )
            
            # Compila resultado final
            modernized_project_analysis = {
                'metadata': {
                    'analysis_date': java_analysis['metadata']['analysis_date'],
                    'modernization_engine_version': self.version,
                    'java_project_name': java_analysis['metadata']['project_name'],
                    'original_delphi_project': original_delphi_analysis['metadata']['project_name']
                },
                'java_project_analysis': java_analysis,
                'comparison_with_original': comparison_data,
                'java_documentation': java_documentation,
                'modernization_validation': self._validate_modernization_success(comparison_data),
                'recommended_next_steps': self._generate_next_steps(comparison_data)
            }
            
            logger.info("✅ Análise do projeto modernizado concluída")
            return modernized_project_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise do projeto modernizado: {str(e)}")
            raise Exception(f"Falha na análise do projeto modernizado: {str(e)}")
    
    def _validate_modernization_success(self, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida se a modernização foi bem-sucedida"""
        validation_results = comparison_data.get('validation_results', {})
        coverage = comparison_data.get('migration_coverage', {})
        
        # Critérios de sucesso
        success_criteria = {
            'minimum_coverage': 75.0,  # 75% de cobertura mínima
            'critical_validations': 0,  # Zero validações críticas falharam
            'architecture_compliance': True  # Arquitetura Spring adequada
        }
        
        # Avalia critérios
        coverage_percent = coverage.get('overall_coverage_percent', 0)
        failed_validations = validation_results.get('summary', {}).get('failed', 0)
        overall_validation_status = validation_results.get('overall_status', 'FAIL')
        
        success_score = 0
        max_score = len(success_criteria)
        
        validation_details = []
        
        # Cobertura de migração
        if coverage_percent >= success_criteria['minimum_coverage']:
            success_score += 1
            validation_details.append({
                'criterion': 'Cobertura de Migração',
                'status': 'PASS',
                'value': f"{coverage_percent:.1f}%",
                'requirement': f">= {success_criteria['minimum_coverage']}%"
            })
        else:
            validation_details.append({
                'criterion': 'Cobertura de Migração',
                'status': 'FAIL',
                'value': f"{coverage_percent:.1f}%",
                'requirement': f">= {success_criteria['minimum_coverage']}%"
            })
        
        # Validações críticas
        if failed_validations <= success_criteria['critical_validations']:
            success_score += 1
            validation_details.append({
                'criterion': 'Validações Críticas',
                'status': 'PASS',
                'value': f"{failed_validations} falhas",
                'requirement': f"<= {success_criteria['critical_validations']} falhas"
            })
        else:
            validation_details.append({
                'criterion': 'Validações Críticas',
                'status': 'FAIL',
                'value': f"{failed_validations} falhas",
                'requirement': f"<= {success_criteria['critical_validations']} falhas"
            })
        
        # Conformidade arquitetural
        if overall_validation_status == 'PASS':
            success_score += 1
            validation_details.append({
                'criterion': 'Conformidade Arquitetural',
                'status': 'PASS',
                'value': overall_validation_status,
                'requirement': 'PASS'
            })
        else:
            validation_details.append({
                'criterion': 'Conformidade Arquitetural',
                'status': 'FAIL' if overall_validation_status == 'FAIL' else 'WARNING',
                'value': overall_validation_status,
                'requirement': 'PASS'
            })
        
        # Determina status geral
        success_percentage = (success_score / max_score) * 100
        
        if success_percentage >= 100:
            overall_status = 'SUCCESS'
            status_message = 'Modernização bem-sucedida'
        elif success_percentage >= 66:
            overall_status = 'PARTIAL_SUCCESS'
            status_message = 'Modernização parcialmente bem-sucedida'
        else:
            overall_status = 'NEEDS_IMPROVEMENT'
            status_message = 'Modernização precisa de melhorias'
        
        return {
            'overall_status': overall_status,
            'status_message': status_message,
            'success_percentage': success_percentage,
            'success_score': f"{success_score}/{max_score}",
            'validation_details': validation_details,
            'summary': {
                'coverage_achieved': coverage_percent,
                'validations_passed': validation_results.get('summary', {}).get('passed', 0),
                'critical_issues': failed_validations
            }
        }
    
    def _generate_next_steps(self, comparison_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Gera próximos passos baseados na análise comparativa"""
        next_steps = []
        
        # Baseado na cobertura
        coverage = comparison_data.get('migration_coverage', {})
        coverage_percent = coverage.get('overall_coverage_percent', 0)
        
        if coverage_percent < 90:
            missing_components = coverage.get('missing_components', [])
            if missing_components:
                next_steps.append({
                    'priority': 'HIGH',
                    'category': 'Completar Migração',
                    'action': 'Implementar componentes não migrados',
                    'details': f"Identificados {len(missing_components)} componentes pendentes",
                    'timeline': '1-2 semanas'
                })
        
        # Baseado na validação
        validation = comparison_data.get('validation_results', {})
        if validation.get('summary', {}).get('failed', 0) > 0:
            next_steps.append({
                'priority': 'CRITICAL',
                'category': 'Corrigir Falhas',
                'action': 'Resolver problemas de validação',
                'details': 'Corrigir validações que falharam',
                'timeline': 'Imediato'
            })
        
        # Baseado nas recomendações
        recommendations = comparison_data.get('recommendations', [])
        high_priority_recs = [r for r in recommendations if r.get('priority') in ['HIGH', 'CRITICAL']]
        
        for rec in high_priority_recs[:3]:  # Top 3 recomendações
            next_steps.append({
                'priority': rec.get('priority', 'MEDIUM'),
                'category': rec.get('category', 'Melhoria'),
                'action': rec.get('recommendation', 'N/A'),
                'details': rec.get('rationale', ''),
                'timeline': '1-3 semanas'
            })
        
        # Próximos passos padrão se não houver problemas críticos
        if not next_steps or all(step['priority'] not in ['CRITICAL', 'HIGH'] for step in next_steps):
            next_steps.extend([
                {
                    'priority': 'MEDIUM',
                    'category': 'Testes',
                    'action': 'Implementar suite completa de testes',
                    'details': 'Testes unitários, integração e end-to-end',
                    'timeline': '2-3 semanas'
                },
                {
                    'priority': 'MEDIUM',
                    'category': 'Documentação',
                    'action': 'Finalizar documentação técnica',
                    'details': 'APIs, deployment e manutenção',
                    'timeline': '1 semana'
                },
                {
                    'priority': 'LOW',
                    'category': 'Otimização',
                    'action': 'Otimizar performance e configurações',
                    'details': 'Cache, conexões de banco, monitoramento',
                    'timeline': '1-2 semanas'
                }
            ])
        
        return next_steps
    
    def analyze_for_modernization(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa dados estruturados do projeto Delphi e gera estratégia de modernização
        
        Args:
            analysis_data: Dados estruturados do LegacyProjectAnalyzer
            
        Returns:
            Estratégia detalhada de modernização
        """
        logger.info("🚀 Iniciando análise para modernização")
        
        try:
            # Valida se recebeu dados estruturados adequados
            if not self._validate_analysis_data(analysis_data):
                raise ValueError("Dados de análise inválidos ou incompletos")
            
            # Extrai componentes principais para modernização
            components = self._extract_modernization_components(analysis_data)
            
            # Gera mapeamento Delphi → Java
            java_mapping = self._generate_java_mapping(components, analysis_data)
            
            # Calcula métricas de complexidade
            complexity_analysis = self._analyze_migration_complexity(components)
            
            # Gera fases de migração
            migration_phases = self._generate_migration_phases(components, complexity_analysis)
            
            # Gera recomendações arquiteturais
            architecture_recommendations = self._generate_architecture_recommendations(analysis_data)
            
            # Compila estratégia final
            modernization_strategy = {
                'metadata': {
                    'project_name': analysis_data['metadata']['project_name'],
                    'modernization_engine_version': self.version,
                    'analysis_date': analysis_data['metadata']['analysis_date'],
                    'total_components': len(components)
                },
                'summary': {
                    'complexity_level': complexity_analysis['overall_complexity'],
                    'estimated_effort_weeks': complexity_analysis['estimated_weeks'],
                    'priority_components': complexity_analysis['priority_list'][:5],
                    'risk_factors': complexity_analysis['risk_factors']
                },
                'component_mapping': java_mapping,
                'migration_phases': migration_phases,
                'architecture_strategy': architecture_recommendations,
                'detailed_components': [component.__dict__ for component in components],
                'technology_stack': self._recommend_technology_stack(analysis_data),
                'implementation_guidelines': self._generate_implementation_guidelines(),
                'validation_checklist': self._generate_validation_checklist()
            }
            
            logger.info(f"✅ Estratégia de modernização gerada: {len(components)} componentes analisados")
            return modernization_strategy
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de modernização: {str(e)}")
            raise Exception(f"Falha na geração da estratégia de modernização: {str(e)}")
    
    def _validate_analysis_data(self, analysis_data: Dict[str, Any]) -> bool:
        """Valida se os dados de análise são adequados para modernização"""
        required_keys = ['metadata', 'code_structure', 'files_analyzed']
        
        for key in required_keys:
            if key not in analysis_data:
                logger.warning(f"⚠️ Chave obrigatória '{key}' não encontrada nos dados de análise")
                return False
        
        if analysis_data['files_analyzed']['total_files'] == 0:
            logger.warning("⚠️ Nenhum arquivo foi analisado")
            return False
        
        return True
    
    def _extract_modernization_components(self, analysis_data: Dict[str, Any]) -> List[ModernizationComponent]:
        """Extrai componentes identificados na análise para criar estratégia de modernização"""
        components = []
        
        # Processa funções
        for func in analysis_data['code_structure']['functions']:
            component = ModernizationComponent(
                delphi_name=func['name'],
                delphi_type='function',
                java_equivalent=self._map_function_to_java(func),
                java_type=self._determine_java_type_for_function(func),
                complexity_score=self._calculate_function_complexity(func),
                dependencies=self._extract_function_dependencies(func),
                migration_notes=self._generate_function_migration_notes(func)
            )
            components.append(component)
        
        # Processa classes
        for cls in analysis_data['code_structure']['classes']:
            component = ModernizationComponent(
                delphi_name=cls['name'],
                delphi_type='class',
                java_equivalent=self._map_class_to_java(cls),
                java_type=self._determine_java_type_for_class(cls),
                complexity_score=self._calculate_class_complexity(cls),
                dependencies=self._extract_class_dependencies(cls),
                migration_notes=self._generate_class_migration_notes(cls)
            )
            components.append(component)
        
        # Processa formulários (Forms)
        for form in analysis_data['code_structure'].get('forms', []):
            component = ModernizationComponent(
                delphi_name=form['name'],
                delphi_type='form',
                java_equivalent=self._map_form_to_java(form),
                java_type='controller',
                complexity_score=self._calculate_form_complexity(form),
                dependencies=self._extract_form_dependencies(form),
                migration_notes=self._generate_form_migration_notes(form)
            )
            components.append(component)
        
        # Processa Data Modules
        for dm in analysis_data['code_structure'].get('data_modules', []):
            component = ModernizationComponent(
                delphi_name=dm['name'],
                delphi_type='data_module',
                java_equivalent=self._map_datamodule_to_java(dm),
                java_type='service',
                complexity_score=self._calculate_datamodule_complexity(dm),
                dependencies=self._extract_datamodule_dependencies(dm),
                migration_notes=self._generate_datamodule_migration_notes(dm)
            )
            components.append(component)
        
        return components
    
    def _map_function_to_java(self, func: Dict[str, Any]) -> str:
        """Mapeia função Delphi para equivalente Java"""
        func_name = func['name']
        
        # Aplica convenções de nomenclatura Java
        java_name = self._convert_to_camel_case(func_name)
        
        # Verifica padrões comuns
        if func_name.lower().startswith('btn') or 'click' in func_name.lower():
            return f"{java_name}Handler"
        elif func_name.lower().startswith('validate'):
            return f"{java_name}Validator"
        elif func_name.lower().startswith('calculate'):
            return f"{java_name}Calculator"
        else:
            return java_name
    
    def _map_class_to_java(self, cls: Dict[str, Any]) -> str:
        """Mapeia classe Delphi para equivalente Java"""
        class_name = cls['name']
        
        # Remove prefixo T comum em Delphi
        if class_name.startswith('T') and len(class_name) > 1:
            class_name = class_name[1:]
        
        return class_name
    
    def _map_form_to_java(self, form: Dict[str, Any]) -> str:
        """Mapeia formulário Delphi para controller Java"""
        form_name = form['name']
        
        # Remove prefixos comuns
        if form_name.lower().startswith('form'):
            form_name = form_name[4:]
        elif form_name.lower().startswith('frm'):
            form_name = form_name[3:]
        
        return f"{form_name}Controller"
    
    def _map_datamodule_to_java(self, dm: Dict[str, Any]) -> str:
        """Mapeia Data Module para service Java"""
        dm_name = dm['name']
        
        # Remove prefixos comuns
        if dm_name.lower().startswith('datamodule'):
            dm_name = dm_name[10:]
        elif dm_name.lower().startswith('dm'):
            dm_name = dm_name[2:]
        
        return f"{dm_name}Service"
    
    def _determine_java_type_for_function(self, func: Dict[str, Any]) -> str:
        """Determina o tipo de componente Java para uma função"""
        func_name = func['name'].lower()
        
        if any(keyword in func_name for keyword in ['validate', 'check', 'verify']):
            return 'validator'
        elif any(keyword in func_name for keyword in ['calculate', 'compute', 'process']):
            return 'service'
        elif any(keyword in func_name for keyword in ['click', 'button', 'event']):
            return 'controller'
        else:
            return 'utility'
    
    def _determine_java_type_for_class(self, cls: Dict[str, Any]) -> str:
        """Determina o tipo de componente Java para uma classe"""
        class_name = cls['name'].lower()
        parent_class = cls.get('parent_class', '').lower()
        
        if 'form' in class_name or 'tform' in parent_class:
            return 'controller'
        elif 'data' in class_name or 'entity' in class_name:
            return 'entity'
        elif 'service' in class_name or 'manager' in class_name:
            return 'service'
        else:
            return 'component'
    
    def _calculate_function_complexity(self, func: Dict[str, Any]) -> int:
        """Calcula complexidade de migração de uma função (1-5)"""
        complexity = 1
        
        # Baseado no número de parâmetros
        param_count = len(func.get('parameters', []))
        if param_count > 5:
            complexity += 2
        elif param_count > 2:
            complexity += 1
        
        # Tipo de retorno complexo
        return_type = func.get('return_type', '').lower()
        if return_type in ['variant', 'olevariant', 'pointer']:
            complexity += 1
        
        return min(complexity, 5)
    
    def _calculate_class_complexity(self, cls: Dict[str, Any]) -> int:
        """Calcula complexidade de migração de uma classe (1-5)"""
        complexity = 2  # Base para classes
        
        # Baseado no número de métodos
        method_count = len(cls.get('methods', []))
        if method_count > 10:
            complexity += 2
        elif method_count > 5:
            complexity += 1
        
        # Baseado no número de propriedades
        property_count = len(cls.get('properties', []))
        if property_count > 10:
            complexity += 1
        
        return min(complexity, 5)
    
    def _calculate_form_complexity(self, form: Dict[str, Any]) -> int:
        """Calcula complexidade de migração de um formulário (1-5)"""
        return 3  # Formulários são moderadamente complexos por natureza
    
    def _calculate_datamodule_complexity(self, dm: Dict[str, Any]) -> int:
        """Calcula complexidade de migração de um data module (1-5)"""
        return 4  # Data modules tendem a ser mais complexos
    
    def _extract_function_dependencies(self, func: Dict[str, Any]) -> List[str]:
        """Extrai dependências de uma função"""
        return []  # Implementação específica baseada na análise
    
    def _extract_class_dependencies(self, cls: Dict[str, Any]) -> List[str]:
        """Extrai dependências de uma classe"""
        dependencies = []
        if cls.get('parent_class'):
            dependencies.append(cls['parent_class'])
        return dependencies
    
    def _extract_form_dependencies(self, form: Dict[str, Any]) -> List[str]:
        """Extrai dependências de um formulário"""
        return []
    
    def _extract_datamodule_dependencies(self, dm: Dict[str, Any]) -> List[str]:
        """Extrai dependências de um data module"""
        return []
    
    def _generate_function_migration_notes(self, func: Dict[str, Any]) -> List[str]:
        """Gera notas específicas para migração de função"""
        notes = []
        
        func_name = func['name'].lower()
        if 'event' in func_name or 'click' in func_name:
            notes.append("Converter para método handler em Spring Controller")
        
        if func.get('return_type'):
            notes.append(f"Converter tipo de retorno: {func['return_type']} → Java equivalent")
        
        return notes
    
    def _generate_class_migration_notes(self, cls: Dict[str, Any]) -> List[str]:
        """Gera notas específicas para migração de classe"""
        notes = []
        
        if cls.get('parent_class', '').lower().startswith('tform'):
            notes.append("Converter para Spring Controller com endpoints REST")
        
        if cls.get('methods'):
            notes.append(f"Migrar {len(cls['methods'])} métodos para Java")
        
        return notes
    
    def _generate_form_migration_notes(self, form: Dict[str, Any]) -> List[str]:
        """Gera notas específicas para migração de formulário"""
        return [
            "Converter para Spring MVC Controller",
            "Implementar endpoints REST para ações do formulário",
            "Criar DTOs para transferência de dados",
            "Implementar validação com Bean Validation"
        ]
    
    def _generate_datamodule_migration_notes(self, dm: Dict[str, Any]) -> List[str]:
        """Gera notas específicas para migração de data module"""
        return [
            "Converter para Spring Service",
            "Implementar repositórios com Spring Data JPA",
            "Configurar transações declarativas",
            "Migrar queries para JPQL ou Criteria API"
        ]
    
    def _generate_java_mapping(self, components: List[ModernizationComponent], 
                             analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera mapeamento detalhado Delphi → Java"""
        mapping = {
            'controllers': [],
            'services': [],
            'entities': [],
            'repositories': [],
            'utilities': []
        }
        
        for component in components:
            java_type = component.java_type
            if java_type in mapping:
                mapping[java_type].append({
                    'delphi_original': component.delphi_name,
                    'java_equivalent': component.java_equivalent,
                    'complexity': component.complexity_score,
                    'migration_notes': component.migration_notes
                })
        
        return mapping
    
    def _analyze_migration_complexity(self, components: List[ModernizationComponent]) -> Dict[str, Any]:
        """Analisa complexidade geral da migração"""
        total_complexity = sum(comp.complexity_score for comp in components)
        avg_complexity = total_complexity / len(components) if components else 0
        
        # Determina nível de complexidade geral
        if avg_complexity <= 2:
            overall_complexity = 'baixa'
            estimated_weeks = len(components) * 0.5
        elif avg_complexity <= 3.5:
            overall_complexity = 'média'
            estimated_weeks = len(components) * 1
        else:
            overall_complexity = 'alta'
            estimated_weeks = len(components) * 2
        
        # Identifica componentes prioritários (mais complexos primeiro)
        priority_list = sorted(components, key=lambda x: x.complexity_score, reverse=True)
        
        # Identifica fatores de risco
        risk_factors = []
        high_complexity_count = len([c for c in components if c.complexity_score >= 4])
        if high_complexity_count > 0:
            risk_factors.append(f"{high_complexity_count} componentes de alta complexidade")
        
        return {
            'overall_complexity': overall_complexity,
            'estimated_weeks': int(estimated_weeks),
            'priority_list': [comp.delphi_name for comp in priority_list],
            'risk_factors': risk_factors,
            'total_components': len(components),
            'complexity_distribution': {
                'baixa': len([c for c in components if c.complexity_score <= 2]),
                'média': len([c for c in components if 2 < c.complexity_score <= 3]),
                'alta': len([c for c in components if c.complexity_score > 3])
            }
        }
    
    def _generate_migration_phases(self, components: List[ModernizationComponent], 
                                 complexity_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera fases estruturadas de migração"""
        phases = [
            {
                'phase': 1,
                'name': 'Preparação e Infraestrutura',
                'description': 'Setup do projeto Spring Boot e infraestrutura básica',
                'duration_weeks': 2,
                'deliverables': [
                    'Projeto Spring Boot configurado',
                    'Estrutura de pacotes definida',
                    'Configuração de banco de dados',
                    'Setup de testes unitários'
                ],
                'components': []
            },
            {
                'phase': 2,
                'name': 'Migração de Entidades e Serviços Base',
                'description': 'Migração dos componentes de dados e lógica de negócio',
                'duration_weeks': 3,
                'deliverables': [
                    'Entidades JPA criadas',
                    'Repositórios Spring Data implementados',
                    'Serviços base migrados'
                ],
                'components': [c.delphi_name for c in components 
                             if c.java_type in ['entity', 'service'] and c.complexity_score <= 3]
            },
            {
                'phase': 3,
                'name': 'Migração de Controllers e APIs',
                'description': 'Implementação das APIs REST e controllers',
                'duration_weeks': 4,
                'deliverables': [
                    'Controllers REST implementados',
                    'DTOs criados',
                    'Validações implementadas'
                ],
                'components': [c.delphi_name for c in components 
                             if c.java_type == 'controller']
            },
            {
                'phase': 4,
                'name': 'Componentes Complexos e Integração',
                'description': 'Migração de componentes complexos e testes de integração',
                'duration_weeks': 3,
                'deliverables': [
                    'Componentes complexos migrados',
                    'Testes de integração',
                    'Documentação da API'
                ],
                'components': [c.delphi_name for c in components 
                             if c.complexity_score >= 4]
            }
        ]
        
        return phases
    
    def _generate_architecture_recommendations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera recomendações arquiteturais específicas"""
        return {
            'core_frameworks': [
                'Spring Boot 3.x',
                'Spring Data JPA',
                'Spring Security',
                'Spring Validation'
            ],
            'database_migration': {
                'recommended_approach': 'Spring Data JPA com Hibernate',
                'migration_tool': 'Flyway ou Liquibase',
                'connection_pooling': 'HikariCP'
            },
            'api_design': {
                'style': 'REST com Spring MVC',
                'documentation': 'OpenAPI 3 com SpringDoc',
                'validation': 'Bean Validation (JSR-303)'
            },
            'testing_strategy': {
                'unit_tests': 'JUnit 5 + Mockito',
                'integration_tests': 'Spring Boot Test',
                'api_tests': 'RestAssured ou TestContainers'
            },
            'deployment': {
                'containerization': 'Docker',
                'build_tool': 'Maven ou Gradle',
                'monitoring': 'Spring Actuator + Micrometer'
            }
        }
    
    def _recommend_technology_stack(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recomenda stack tecnológico baseado na análise"""
        # Analisa características do projeto para recomendar tecnologias
        has_database = len(analysis_data.get('database_elements', {}).get('queries', [])) > 0
        has_complex_ui = len(analysis_data.get('ui_components', {}).get('forms', [])) > 5
        
        stack = {
            'backend': {
                'framework': 'Spring Boot 3.2+',
                'java_version': 'Java 17 LTS',
                'build_tool': 'Maven',
                'database': 'PostgreSQL' if has_database else 'H2 (desenvolvimento)',
                'orm': 'Spring Data JPA + Hibernate' if has_database else None
            },
            'frontend': {
                'recommended': 'React + TypeScript' if has_complex_ui else 'Thymeleaf',
                'alternative': 'Angular ou Vue.js',
                'ui_library': 'Material-UI ou Bootstrap'
            },
            'development_tools': [
                'IntelliJ IDEA ou Eclipse',
                'Docker para containerização',
                'Git para versionamento',
                'SonarQube para qualidade'
            ]
        }
        
        return stack
    
    def _generate_implementation_guidelines(self) -> List[str]:
        """Gera diretrizes de implementação"""
        return [
            "Seguir convenções de nomenclatura Java (camelCase)",
            "Implementar padrão Repository para acesso a dados",
            "Usar injeção de dependência do Spring",
            "Aplicar princípios SOLID no design das classes",
            "Implementar tratamento de exceções centralizado",
            "Criar DTOs para transferência de dados entre camadas",
            "Usar anotações Spring para configuração",
            "Implementar logging estruturado com SLF4J",
            "Aplicar validações com Bean Validation",
            "Documentar APIs com OpenAPI/Swagger"
        ]
    
    def _generate_validation_checklist(self) -> List[str]:
        """Gera checklist de validação pós-migração"""
        return [
            "✅ Todas as funcionalidades principais migradas",
            "✅ Testes unitários implementados (cobertura > 80%)",
            "✅ Testes de integração executando",
            "✅ APIs documentadas e testadas",
            "✅ Configuração de segurança implementada",
            "✅ Logs estruturados funcionando",
            "✅ Monitoramento básico configurado",
            "✅ Documentação técnica atualizada",
            "✅ Performance aceitável em testes",
            "✅ Deploy automatizado funcionando"
        ]
    
    def _convert_to_camel_case(self, snake_str: str) -> str:
        """Converte string para camelCase"""
        components = snake_str.split('_')
        return components[0].lower() + ''.join(x.capitalize() for x in components[1:])
    
    def _load_default_mappings(self) -> Dict[str, str]:
        """Carrega mapeamentos padrão Delphi → Java"""
        return {
            'String': 'String',
            'Integer': 'Integer',
            'Boolean': 'Boolean',
            'Double': 'Double',
            'TDateTime': 'LocalDateTime',
            'TStringList': 'List<String>',
            'TList': 'List<Object>',
            'TForm': '@Controller',
            'TDataModule': '@Service'
        }
