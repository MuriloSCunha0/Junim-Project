"""
Gerador de documentação estruturada para projetos Delphi analisados
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationGenerator:
    """Gerador de documentação estruturada para análise de projetos legados"""
    
    def __init__(self, output_directory: str = None):
        """
        Inicializa o gerador de documentação
        
        Args:
            output_directory: Diretório onde salvar os documentos gerados
        """
        if output_directory is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            output_directory = os.path.join(project_root, 'generated_docs')
        
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)
        
        self.generated_documents = {}
    
    def generate_complete_documentation(self, analysis_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Gera documentação completa baseada na análise
        
        Args:
            analysis_data: Dados da análise completa do projeto
            
        Returns:
            Dicionário com caminhos dos documentos gerados
        """
        try:
            logger.info("Iniciando geração de documentação completa")
            
            project_name = analysis_data.get('metadata', {}).get('project_name', 'Unknown')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Cria diretório específico para este projeto
            project_dir = os.path.join(self.output_directory, f"{project_name}_{timestamp}")
            os.makedirs(project_dir, exist_ok=True)
            
            documents = {}
            
            # 1. Documento de Requisitos
            requirements_doc = self._generate_requirements_document(analysis_data)
            req_path = os.path.join(project_dir, "01_Requisitos_Sistema.md")
            self._save_document(req_path, requirements_doc)
            documents['requirements'] = req_path
            
            # 2. Documento de Funcionalidades
            functionality_doc = self._generate_functionality_document(analysis_data)
            func_path = os.path.join(project_dir, "02_Funcionalidades_Sistema.md")
            self._save_document(func_path, functionality_doc)
            documents['functionality'] = func_path
            
            # 3. Documento de Características Técnicas
            characteristics_doc = self._generate_characteristics_document(analysis_data)
            char_path = os.path.join(project_dir, "03_Caracteristicas_Tecnicas.md")
            self._save_document(char_path, characteristics_doc)
            documents['characteristics'] = char_path
            
            # 4. Documento de Fluxos de Execução
            execution_flows_doc = self._generate_execution_flows_document(analysis_data)
            exec_path = os.path.join(project_dir, "04_Fluxos_Execucao.md")
            self._save_document(exec_path, execution_flows_doc)
            documents['execution_flows'] = exec_path
            
            # 5. Documento de Fluxos de Dados
            data_flows_doc = self._generate_data_flows_document(analysis_data)
            data_path = os.path.join(project_dir, "05_Fluxos_Dados.md")
            self._save_document(data_path, data_flows_doc)
            documents['data_flows'] = data_path
            
            # 6. Documento de Correlações Delphi → Java
            correlations_doc = self._generate_correlations_document(analysis_data)
            corr_path = os.path.join(project_dir, "06_Correlacoes_Delphi_Java.md")
            self._save_document(corr_path, correlations_doc)
            documents['correlations'] = corr_path
            
            # 7. Documento de Análise Técnica Detalhada
            technical_analysis_doc = self._generate_technical_analysis_document(analysis_data)
            tech_path = os.path.join(project_dir, "07_Analise_Tecnica_Detalhada.md")
            self._save_document(tech_path, technical_analysis_doc)
            documents['technical_analysis'] = tech_path
            
            # 8. Documento JSON com dados estruturados
            json_path = os.path.join(project_dir, "08_Dados_Estruturados.json")
            self._save_json_document(json_path, analysis_data)
            documents['structured_data'] = json_path
            
            # 9. Resumo Executivo
            executive_summary_doc = self._generate_executive_summary(analysis_data)
            summary_path = os.path.join(project_dir, "00_Resumo_Executivo.md")
            self._save_document(summary_path, executive_summary_doc)
            documents['executive_summary'] = summary_path
            
            # Atualiza lista de documentos gerados
            self.generated_documents[project_name] = {
                'project_directory': project_dir,
                'documents': documents,
                'generation_date': datetime.now().isoformat(),
                'metadata': analysis_data.get('metadata', {})
            }
            
            logger.info(f"Documentação completa gerada em: {project_dir}")
            return documents
            
        except Exception as e:
            logger.error(f"Erro na geração de documentação: {str(e)}")
            raise Exception(f"Falha na geração de documentação: {str(e)}")
    
    def _generate_requirements_document(self, analysis_data: Dict[str, Any]) -> str:
        """Gera documento de requisitos do sistema"""
        project_name = analysis_data.get('metadata', {}).get('project_name', 'Sistema')
        requirements = analysis_data.get('requirements', {})
        
        doc = f"""# Requisitos do Sistema - {project_name}

## Informações Gerais
- **Data da Análise**: {analysis_data.get('metadata', {}).get('analysis_date', 'N/A')}
- **Versão do Analisador**: {analysis_data.get('metadata', {}).get('analyzer_version', 'N/A')}

## 1. Requisitos Funcionais

Os requisitos funcionais identificados através da análise do código fonte:

"""
        
        functional_reqs = requirements.get('functional_requirements', [])
        if functional_reqs:
            for i, req in enumerate(functional_reqs, 1):
                doc += f"### RF{i:03d} - {req.get('title', 'Requisito Funcional')}\n"
                doc += f"- **Módulo**: {req.get('module', 'N/A')}\n"
                doc += f"- **Descrição**: {req.get('description', 'N/A')}\n"
                doc += f"- **Prioridade**: {req.get('priority', 'Média')}\n\n"
        else:
            doc += "Nenhum requisito funcional específico foi identificado automaticamente.\n\n"
        
        doc += """## 2. Requisitos Não Funcionais

"""
        
        non_functional_reqs = requirements.get('non_functional_requirements', [])
        if non_functional_reqs:
            for i, req in enumerate(non_functional_reqs, 1):
                doc += f"### RNF{i:03d} - {req.get('title', 'Requisito Não Funcional')}\n"
                doc += f"- **Categoria**: {req.get('category', 'N/A')}\n"
                doc += f"- **Descrição**: {req.get('description', 'N/A')}\n"
                doc += f"- **Critério de Aceitação**: {req.get('acceptance_criteria', 'N/A')}\n\n"
        else:
            doc += "Requisitos não funcionais serão definidos durante a modernização.\n\n"
        
        doc += """## 3. Requisitos de Negócio

"""
        
        business_reqs = requirements.get('business_requirements', [])
        if business_reqs:
            for i, req in enumerate(business_reqs, 1):
                doc += f"### RN{i:03d} - {req.get('title', 'Requisito de Negócio')}\n"
                doc += f"- **Área de Negócio**: {req.get('business_area', 'N/A')}\n"
                doc += f"- **Descrição**: {req.get('description', 'N/A')}\n"
                doc += f"- **Justificativa**: {req.get('justification', 'N/A')}\n\n"
        else:
            doc += "Requisitos de negócio serão levantados com stakeholders.\n\n"
        
        doc += """## 4. Requisitos Técnicos

"""
        
        technical_reqs = requirements.get('technical_requirements', [])
        if technical_reqs:
            for i, req in enumerate(technical_reqs, 1):
                doc += f"### RT{i:03d} - {req.get('title', 'Requisito Técnico')}\n"
                doc += f"- **Tecnologia**: {req.get('technology', 'N/A')}\n"
                doc += f"- **Descrição**: {req.get('description', 'N/A')}\n"
                doc += f"- **Impacto**: {req.get('impact', 'N/A')}\n\n"
        else:
            doc += "Requisitos técnicos serão definidos durante a arquitetura da solução.\n\n"
        
        return doc
    
    def _generate_functionality_document(self, analysis_data: Dict[str, Any]) -> str:
        """Gera documento de funcionalidades do sistema"""
        project_name = analysis_data.get('metadata', {}).get('project_name', 'Sistema')
        units_analysis = analysis_data.get('units_analysis', {})
        business_logic = analysis_data.get('business_logic', {})
        
        doc = f"""# Funcionalidades do Sistema - {project_name}

## Visão Geral das Funcionalidades

Este documento detalha as funcionalidades identificadas no sistema legado através da análise do código fonte.

## 1. Módulos Principais

"""
        
        # Agrupa funcionalidades por módulo/unit
        for unit_name, unit_data in units_analysis.items():
            unit_type = unit_data.get('unit_type', 'unknown')
            
            doc += f"### {unit_name} ({unit_type.title()})\n\n"
            
            if unit_type == 'form':
                doc += "**Tipo**: Interface de Usuário\n"
                doc += "**Funcionalidades**:\n"
                
                # Extrai funcionalidades de formulários
                procedures = unit_data.get('procedures_functions', [])
                for proc in procedures:
                    if 'click' in proc.get('name', '').lower() or 'event' in proc.get('purpose', ''):
                        doc += f"- {proc.get('name', 'N/A')}: {proc.get('purpose', 'Ação do usuário')}\n"
            
            elif unit_type == 'datamodule':
                doc += "**Tipo**: Acesso a Dados\n"
                doc += "**Funcionalidades**:\n"
                
                # Extrai operações de banco de dados
                db_operations = unit_data.get('database_operations', [])
                for db_op in db_operations:
                    doc += f"- {db_op.get('name', 'N/A')}: {db_op.get('description', 'Operação de dados')}\n"
            
            else:
                doc += "**Tipo**: Lógica de Negócio\n"
                doc += "**Funcionalidades**:\n"
                
                procedures = unit_data.get('procedures_functions', [])
                for proc in procedures[:5]:  # Limita a 5 principais
                    doc += f"- {proc.get('name', 'N/A')}: {proc.get('purpose', 'Processamento')}\n"
            
            doc += "\n"
        
        doc += """## 2. Regras de Negócio Identificadas

"""
        
        business_rules = business_logic.get('business_rules', [])
        if business_rules:
            for i, rule in enumerate(business_rules, 1):
                doc += f"### RN{i:03d} - {rule.get('unit', 'N/A')}\n"
                doc += f"**Regra**: {rule.get('rule', 'N/A')}\n\n"
        else:
            doc += "Regras de negócio serão identificadas durante análise detalhada.\n\n"
        
        doc += """## 3. Validações do Sistema

"""
        
        validations = business_logic.get('validations', [])
        if validations:
            for validation in validations:
                doc += f"- **{validation.get('function', 'N/A')}** (em {validation.get('unit', 'N/A')})\n"
                doc += f"  - Descrição: {validation.get('description', 'Validação de dados')}\n"
        else:
            doc += "Validações serão mapeadas durante análise detalhada.\n\n"
        
        doc += """## 4. Cálculos e Processamentos

"""
        
        calculations = business_logic.get('calculations', [])
        if calculations:
            for calc in calculations:
                doc += f"- **{calc.get('name', 'N/A')}** (em {calc.get('unit', 'N/A')})\n"
                doc += f"  - Tipo: {calc.get('type', 'Cálculo')}\n"
        else:
            doc += "Cálculos serão identificados durante análise detalhada.\n\n"
        
        return doc
    
    def _generate_characteristics_document(self, analysis_data: Dict[str, Any]) -> str:
        """Gera documento de características técnicas"""
        project_name = analysis_data.get('metadata', {}).get('project_name', 'Sistema')
        characteristics = analysis_data.get('characteristics', {})
        project_info = analysis_data.get('project_info', {})
        
        doc = f"""# Características Técnicas - {project_name}

## 1. Arquitetura do Sistema

- **Padrão Arquitetural**: {characteristics.get('architecture_pattern', 'Não identificado')}
- **Tipo de Aplicação**: {project_info.get('architecture_type', 'Desktop')}
- **Versão do Delphi**: {project_info.get('delphi_version', 'Não identificada')}

## 2. Stack Tecnológico

"""
        
        tech_stack = characteristics.get('technology_stack', [])
        if tech_stack:
            for tech in tech_stack:
                doc += f"- {tech}\n"
        else:
            doc += "- Delphi/Object Pascal\n- Componentes VCL\n- Banco de dados (a identificar)\n"
        
        doc += f"""

## 3. Métricas de Complexidade

- **Nível de Complexidade**: {characteristics.get('complexity_level', 'Médio')}
- **Score de Manutenibilidade**: {characteristics.get('maintainability_score', 0.0):.2f}
- **Prontidão para Modernização**: {characteristics.get('modernization_readiness', 'Avaliar')}

## 4. Estrutura do Projeto

- **Total de Arquivos**: {project_info.get('total_files', 0)}
- **Units Pascal**: {project_info.get('file_counts', {}).get('pascal_units', 0)}
- **Formulários**: {project_info.get('file_counts', {}).get('forms', 0)}
- **Projetos**: {project_info.get('file_counts', {}).get('projects', 0)}

## 5. Pontos Fortes do Sistema

"""
        
        strengths = characteristics.get('strengths', [])
        if strengths:
            for strength in strengths:
                doc += f"- {strength}\n"
        else:
            doc += "- Funcionalidade consolidada\n- Base de código existente\n- Conhecimento do domínio\n"
        
        doc += f"""

## 6. Pontos de Melhoria

"""
        
        weaknesses = characteristics.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                doc += f"- {weakness}\n"
        else:
            doc += "- Tecnologia legada\n- Possível acoplamento alto\n- Documentação limitada\n"
        
        doc += f"""

## 7. Fatores de Risco

"""
        
        risk_factors = characteristics.get('risk_factors', [])
        if risk_factors:
            for risk in risk_factors:
                doc += f"- {risk}\n"
        else:
            doc += "- Dependências de bibliotecas legadas\n- Complexidade de migração\n- Perda de conhecimento\n"
        
        return doc
    
    def _generate_execution_flows_document(self, analysis_data: Dict[str, Any]) -> str:
        """Gera documento de fluxos de execução"""
        project_name = analysis_data.get('metadata', {}).get('project_name', 'Sistema')
        execution_flows = analysis_data.get('execution_flows', {})
        
        doc = f"""# Fluxos de Execução - {project_name}

## 1. Sequência de Inicialização

"""
        
        startup_sequence = execution_flows.get('startup_sequence', [])
        if startup_sequence:
            for i, step in enumerate(startup_sequence, 1):
                doc += f"{i}. {step.get('description', 'Passo de inicialização')}\n"
        else:
            doc += "1. Carregamento da aplicação principal\n2. Inicialização de módulos\n3. Conexão com banco de dados\n4. Apresentação da interface principal\n"
        
        doc += """

## 2. Fluxos de Trabalho do Usuário

"""
        
        user_workflows = execution_flows.get('user_workflows', [])
        if user_workflows:
            for workflow in user_workflows:
                doc += f"### {workflow.get('name', 'Fluxo de Trabalho')}\n"
                doc += f"**Módulo**: {workflow.get('module', 'N/A')}\n"
                doc += f"**Descrição**: {workflow.get('description', 'N/A')}\n"
                
                steps = workflow.get('steps', [])
                if steps:
                    doc += "**Passos**:\n"
                    for i, step in enumerate(steps, 1):
                        doc += f"{i}. {step}\n"
                doc += "\n"
        else:
            doc += "Fluxos de trabalho serão mapeados durante análise detalhada.\n\n"
        
        doc += """## 3. Tratamento de Erros

"""
        
        error_handling = execution_flows.get('error_handling_flows', [])
        if error_handling:
            for error_flow in error_handling:
                doc += f"- **{error_flow.get('type', 'Erro')}**: {error_flow.get('handling', 'Tratamento padrão')}\n"
        else:
            doc += "- Tratamento de exceções genérico\n- Logs de erro do sistema\n- Mensagens de erro para usuário\n"
        
        doc += """

## 4. Sequência de Finalização

"""
        
        shutdown_sequence = execution_flows.get('shutdown_sequence', [])
        if shutdown_sequence:
            for i, step in enumerate(shutdown_sequence, 1):
                doc += f"{i}. {step.get('description', 'Passo de finalização')}\n"
        else:
            doc += "1. Salvamento de dados pendentes\n2. Fechamento de conexões\n3. Liberação de recursos\n4. Finalização da aplicação\n"
        
        return doc
    
    def _generate_data_flows_document(self, analysis_data: Dict[str, Any]) -> str:
        """Gera documento de fluxos de dados"""
        project_name = analysis_data.get('metadata', {}).get('project_name', 'Sistema')
        data_flows = analysis_data.get('data_flows', {})
        
        doc = f"""# Fluxos de Dados - {project_name}

## 1. Fluxos de Banco de Dados

"""
        
        database_flows = data_flows.get('database_flows', [])
        if database_flows:
            for flow in database_flows:
                doc += f"### {flow.get('source_unit', 'N/A')}\n"
                doc += f"- **Tipo de Operação**: {flow.get('operation_type', 'N/A')}\n"
                doc += f"- **Tabelas Envolvidas**: {', '.join(flow.get('tables_involved', []))}\n"
                doc += f"- **Direção dos Dados**: {flow.get('data_direction', 'N/A')}\n"
                doc += f"- **Descrição**: {flow.get('description', 'N/A')}\n\n"
        else:
            doc += "Fluxos de banco de dados serão mapeados durante análise detalhada.\n\n"
        
        doc += """## 2. Fluxos entre Formulários

"""
        
        form_flows = data_flows.get('form_data_flows', [])
        if form_flows:
            for flow in form_flows:
                doc += f"- **De**: {flow.get('source', 'N/A')} **Para**: {flow.get('target', 'N/A')}\n"
                doc += f"  - Dados: {flow.get('data_type', 'N/A')}\n"
                doc += f"  - Método: {flow.get('method', 'N/A')}\n"
        else:
            doc += "Fluxos entre formulários serão identificados durante análise.\n\n"
        
        doc += """## 3. Fluxos entre Módulos

"""
        
        inter_unit_flows = data_flows.get('inter_unit_flows', [])
        if inter_unit_flows:
            for flow in inter_unit_flows:
                doc += f"- **{flow.get('source_unit', 'N/A')}** → **{flow.get('target_unit', 'N/A')}**\n"
                doc += f"  - Interface: {flow.get('interface', 'N/A')}\n"
                doc += f"  - Dados: {flow.get('data_description', 'N/A')}\n"
        else:
            doc += "Fluxos entre módulos serão mapeados durante análise.\n\n"
        
        doc += """## 4. Fluxos Externos

"""
        
        external_flows = data_flows.get('external_flows', [])
        if external_flows:
            for flow in external_flows:
                doc += f"- **Sistema Externo**: {flow.get('external_system', 'N/A')}\n"
                doc += f"  - Tipo de Integração: {flow.get('integration_type', 'N/A')}\n"
                doc += f"  - Dados Trocados: {flow.get('data_exchanged', 'N/A')}\n"
        else:
            doc += "Integrações externas serão identificadas durante análise.\n\n"
        
        return doc
    
    def _generate_correlations_document(self, analysis_data: Dict[str, Any]) -> str:
        """Gera documento de correlações Delphi → Java"""
        project_name = analysis_data.get('metadata', {}).get('project_name', 'Sistema')
        correlations = analysis_data.get('correlations', {})
        
        doc = f"""# Correlações Delphi → Java Spring - {project_name}

## Introdução

Este documento mapeia como cada componente/funcionalidade do sistema Delphi deve ser implementado no Java Spring Boot.

## 1. Mapeamento de Componentes

"""
        
        component_mappings = correlations.get('component_mappings', [])
        if component_mappings:
            for mapping in component_mappings:
                doc += f"### {mapping.get('delphi_component', 'N/A')}\n"
                doc += f"**Delphi**: {mapping.get('delphi_description', 'N/A')}\n"
                doc += f"**Java Spring**: {mapping.get('java_equivalent', 'N/A')}\n"
                doc += f"**Justificativa**: {mapping.get('rationale', 'N/A')}\n"
                doc += f"**Exemplo de Implementação**:\n"
                doc += f"```java\n{mapping.get('java_example', '// Exemplo a ser implementado')}\n```\n\n"
        else:
            doc += """### TDataModule → Service + Repository

**Delphi**: Módulo de dados com queries e lógica de acesso
**Java Spring**: Separação em Service (lógica) e Repository (acesso)

```java
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
    
    public List<User> findActiveUsers() {
        return userRepository.findByActiveTrue();
    }
}
```

### TForm → RestController

**Delphi**: Formulário com eventos de botão
**Java Spring**: Controller REST com endpoints

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private UserService userService;
    
    @GetMapping
    public ResponseEntity<List<User>> getUsers() {
        return ResponseEntity.ok(userService.findActiveUsers());
    }
}
```

"""
        
        doc += """## 2. Mapeamento de Padrões

"""
        
        pattern_mappings = correlations.get('pattern_mappings', [])
        if pattern_mappings:
            for pattern in pattern_mappings:
                doc += f"### {pattern.get('delphi_pattern', 'N/A')}\n"
                doc += f"**Padrão Delphi**: {pattern.get('delphi_description', 'N/A')}\n"
                doc += f"**Padrão Java**: {pattern.get('java_pattern', 'N/A')}\n"
                doc += f"**Vantagens**: {pattern.get('advantages', 'N/A')}\n\n"
        else:
            doc += "Padrões de migração serão definidos durante implementação.\n\n"
        
        doc += """## 3. Mapeamento de Tecnologias

"""
        
        tech_mappings = correlations.get('technology_mappings', [])
        if tech_mappings:
            for tech in tech_mappings:
                doc += f"- **{tech.get('delphi_tech', 'N/A')}** → **{tech.get('java_tech', 'N/A')}**\n"
                doc += f"  - Motivo: {tech.get('reason', 'N/A')}\n"
        else:
            doc += """- **Delphi VCL** → **Spring Boot REST API + Frontend**
- **ADO/DBExpress** → **Spring Data JPA**
- **TQuery** → **JpaRepository methods**
- **TDataSource** → **Service layer**
- **Exception handling** → **@ExceptionHandler**

"""
        
        return doc
    
    def _generate_technical_analysis_document(self, analysis_data: Dict[str, Any]) -> str:
        """Gera documento de análise técnica detalhada"""
        project_name = analysis_data.get('metadata', {}).get('project_name', 'Sistema')
        units_analysis = analysis_data.get('units_analysis', {})
        
        doc = f"""# Análise Técnica Detalhada - {project_name}

## Resumo da Análise

Este documento contém a análise técnica detalhada de cada componente do sistema.

"""
        
        for unit_name, unit_data in units_analysis.items():
            doc += f"## {unit_name}\n\n"
            doc += f"**Tipo**: {unit_data.get('unit_type', 'N/A').title()}\n"
            doc += f"**Arquivo**: {os.path.basename(unit_data.get('file_path', 'N/A'))}\n"
            doc += f"**Tamanho**: {unit_data.get('lines_count', 0)} linhas\n\n"
            
            # Complexidade
            complexity = unit_data.get('complexity_metrics', {})
            doc += "### Métricas de Complexidade\n"
            doc += f"- **Complexidade Ciclomática**: {complexity.get('cyclomatic_complexity', 0)}\n"
            doc += f"- **Número de Funções**: {complexity.get('function_count', 0)}\n"
            doc += f"- **Número de Classes**: {complexity.get('class_count', 0)}\n"
            doc += f"- **Profundidade de Aninhamento**: {complexity.get('nesting_depth', 0)}\n\n"
            
            # Classes
            classes = unit_data.get('classes', [])
            if classes:
                doc += "### Classes Identificadas\n"
                for cls in classes:
                    doc += f"- **{cls.get('name', 'N/A')}** (herda de {cls.get('parent_class', 'N/A')})\n"
                    doc += f"  - Propósito: {cls.get('purpose', 'N/A')}\n"
                doc += "\n"
            
            # Procedures/Functions
            procedures = unit_data.get('procedures_functions', [])
            if procedures:
                doc += "### Principais Funções\n"
                for proc in procedures[:5]:  # Top 5
                    doc += f"- **{proc.get('name', 'N/A')}** ({proc.get('type', 'N/A')})\n"
                    doc += f"  - Complexidade: {proc.get('complexity', 0)}\n"
                    doc += f"  - Propósito: {proc.get('purpose', 'N/A')}\n"
                doc += "\n"
            
            # Operações de banco
            db_ops = unit_data.get('database_operations', [])
            if db_ops:
                doc += "### Operações de Banco de Dados\n"
                for db_op in db_ops:
                    doc += f"- {db_op.get('name', 'N/A')}: {db_op.get('description', 'N/A')}\n"
                doc += "\n"
            
            doc += "---\n\n"
        
        return doc
    
    def _generate_executive_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Gera resumo executivo da análise"""
        project_name = analysis_data.get('metadata', {}).get('project_name', 'Sistema')
        project_info = analysis_data.get('project_info', {})
        characteristics = analysis_data.get('characteristics', {})
        
        doc = f"""# Resumo Executivo - Análise do Sistema {project_name}

## Visão Geral

Este documento apresenta um resumo executivo da análise realizada no sistema legado {project_name}, incluindo suas características principais, complexidade e recomendações para modernização.

## Características do Sistema

- **Arquivos Analisados**: {analysis_data.get('metadata', {}).get('total_files_analyzed', 0)}
- **Tipo de Aplicação**: {project_info.get('architecture_type', 'Desktop')}
- **Complexidade**: {characteristics.get('complexity_level', 'Média')}
- **Prontidão para Modernização**: {characteristics.get('modernization_readiness', 'Avaliar')}

## Resumo Técnico

### Estrutura do Projeto
- Units Pascal: {project_info.get('file_counts', {}).get('pascal_units', 0)}
- Formulários: {project_info.get('file_counts', {}).get('forms', 0)}
- Módulos de Dados: Identificados durante análise

### Tecnologias Identificadas
- Linguagem: Delphi/Object Pascal
- Interface: VCL (Visual Component Library)
- Banco de Dados: A identificar durante análise detalhada

## Recomendações

### Estratégia de Modernização
1. **Análise Detalhada**: Aprofundar análise de regras de negócio
2. **Migração por Etapas**: Priorizar módulos de menor complexidade
3. **Validação Contínua**: Testes de funcionalidade durante migração

### Tecnologias Alvo
- **Backend**: Java Spring Boot
- **Frontend**: React/Angular (a definir)
- **Banco de Dados**: Manter compatibilidade existente
- **API**: REST para integração

## Próximos Passos

1. Revisão da documentação gerada
2. Validação com stakeholders
3. Definição de cronograma de modernização
4. Início da implementação por módulos priorizados

---

**Data da Análise**: {analysis_data.get('metadata', {}).get('analysis_date', 'N/A')}
**Ferramenta**: JUNIM - Java Unified Interoperability Migration v{analysis_data.get('metadata', {}).get('analyzer_version', '1.0')}
"""
        
        return doc
    
    def _save_document(self, file_path: str, content: str):
        """Salva documento em arquivo"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info(f"Documento salvo: {file_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar documento {file_path}: {str(e)}")
    
    def _save_json_document(self, file_path: str, data: Dict[str, Any]):
        """Salva dados estruturados em JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Dados JSON salvos: {file_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar JSON {file_path}: {str(e)}")
    
    def get_generated_documents(self) -> Dict[str, Any]:
        """Retorna lista de documentos gerados"""
        return self.generated_documents
    
    def get_document_content(self, document_path: str) -> str:
        """Lê conteúdo de um documento gerado"""
        try:
            with open(document_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Erro ao ler documento {document_path}: {str(e)}")
            return f"Erro ao carregar documento: {str(e)}"
