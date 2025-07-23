"""
Interface Web para Análise Comparativa de Projetos
Permite analisar projetos Delphi, Java e comparar ambos
"""

import streamlit as st
import requests
import json
import os
import tempfile
from datetime import datetime
import zipfile

# Configuração da página
st.set_page_config(
    page_title="Análise Comparativa de Projetos",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Análise Comparativa de Projetos")
st.subheader("Delphi Legacy → Java Spring Boot")

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # URL da API (caso esteja rodando em servidor diferente)
    api_url = st.text_input(
        "URL da API", 
        value="http://localhost:5000/api",
        help="URL base da API Flask"
    )
    
    # Status da API
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ API Online")
        else:
            st.error("❌ API com problemas")
    except:
        st.error("❌ API Offline")

# Tabs para diferentes tipos de análise
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Análise Delphi", 
    "☕ Análise Java", 
    "🔄 Comparação", 
    "🚀 Modernização Completa"
])

with tab1:
    st.header("🏛️ Análise de Projeto Delphi")
    st.write("Analise um projeto Delphi legado e gere documentação completa.")
    
    delphi_file = st.file_uploader(
        "Selecione o arquivo ZIP do projeto Delphi",
        type=['zip'],
        key="delphi_only"
    )
    
    if st.button("🔍 Analisar Projeto Delphi", key="analyze_delphi"):
        if delphi_file is not None:
            with st.spinner("Analisando projeto Delphi..."):
                try:
                    # Prepara arquivo para upload
                    files = {'file': delphi_file}
                    
                    # Chama API
                    response = requests.post(f"{api_url}/analyze/delphi", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Análise concluída!")
                        
                        # Exibe resultados
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("📊 Estatísticas do Projeto")
                            analysis = result['analysis']
                            metadata = analysis['metadata']
                            files_info = analysis['files_analyzed']
                            
                            st.metric("Nome do Projeto", metadata['project_name'])
                            st.metric("Total de Arquivos", files_info['total_files'])
                            st.metric("Arquivos Pascal", files_info['pascal_files'])
                            st.metric("Funções", len(analysis['code_structure']['functions']))
                            st.metric("Classes", len(analysis['code_structure']['classes']))
                        
                        with col2:
                            st.subheader("📄 Documentação Gerada")
                            docs = result['documentation']
                            
                            for doc_type, content in docs.items():
                                if content:
                                    with st.expander(f"📋 {doc_type.replace('_', ' ').title()}"):
                                        st.markdown(content[:1000] + "..." if len(content) > 1000 else content)
                                        
                                        # Botão para download
                                        st.download_button(
                                            label=f"📥 Download {doc_type}",
                                            data=content,
                                            file_name=f"{doc_type}_{metadata['project_name']}.md",
                                            mime="text/markdown"
                                        )
                    else:
                        st.error(f"❌ Erro na análise: {response.json().get('error', 'Erro desconhecido')}")
                        
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        else:
            st.warning("⚠️ Selecione um arquivo ZIP")

with tab2:
    st.header("☕ Análise de Projeto Java")
    st.write("Analise um projeto Java Spring Boot modernizado.")
    
    java_file = st.file_uploader(
        "Selecione o arquivo ZIP do projeto Java",
        type=['zip'],
        key="java_only"
    )
    
    if st.button("🔍 Analisar Projeto Java", key="analyze_java"):
        if java_file is not None:
            with st.spinner("Analisando projeto Java..."):
                try:
                    files = {'file': java_file}
                    response = requests.post(f"{api_url}/analyze/java", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Análise Java concluída!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("📊 Componentes Spring")
                            analysis = result['java_analysis']
                            components = analysis['spring_components']['component_summary']
                            
                            st.metric("Controllers", components['total_controllers'])
                            st.metric("Services", components['total_services']) 
                            st.metric("Repositories", components['total_repositories'])
                            st.metric("Entities", components['total_entities'])
                        
                        with col2:
                            st.subheader("🏗️ Arquitetura")
                            project_structure = analysis['project_structure']
                            
                            st.metric("Pacotes", project_structure['package_count'])
                            st.metric("Arquivos Java", analysis['files_analyzed']['java_files'])
                            
                            # Padrões arquiteturais
                            patterns = analysis.get('architecture_analysis', {})
                            if patterns:
                                st.write("**Padrões Identificados:**")
                                for pattern, enabled in patterns.items():
                                    if isinstance(enabled, bool) and enabled:
                                        st.write(f"✅ {pattern.replace('_', ' ').title()}")
                        
                        # Documentação Java
                        st.subheader("📄 Documentação Java")
                        docs = result['java_documentation']
                        
                        for doc_type, content in docs.items():
                            if content:
                                with st.expander(f"📋 {doc_type.replace('_', ' ').title()}"):
                                    st.markdown(content[:1000] + "..." if len(content) > 1000 else content)
                                    
                                    st.download_button(
                                        label=f"📥 Download {doc_type}",
                                        data=content,
                                        file_name=f"{doc_type}_{analysis['metadata']['project_name']}.md",
                                        mime="text/markdown"
                                    )
                    else:
                        st.error(f"❌ Erro: {response.json().get('error', 'Erro desconhecido')}")
                        
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        else:
            st.warning("⚠️ Selecione um arquivo ZIP")

with tab3:
    st.header("🔄 Comparação Delphi ↔ Java")
    st.write("Compare um projeto Delphi original com sua versão Java modernizada.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏛️ Projeto Delphi Original")
        delphi_compare_file = st.file_uploader(
            "Arquivo ZIP do projeto Delphi",
            type=['zip'],
            key="delphi_compare"
        )
    
    with col2:
        st.subheader("☕ Projeto Java Modernizado")
        java_compare_file = st.file_uploader(
            "Arquivo ZIP do projeto Java",
            type=['zip'],
            key="java_compare"
        )
    
    if st.button("🔄 Comparar Projetos", key="compare_projects"):
        if delphi_compare_file is not None and java_compare_file is not None:
            with st.spinner("Comparando projetos..."):
                try:
                    files = {
                        'delphi_file': delphi_compare_file,
                        'java_file': java_compare_file
                    }
                    
                    response = requests.post(f"{api_url}/compare/projects", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Comparação concluída!")
                        
                        # Exibe comparação
                        comparison = result['comparison']
                        
                        # Métricas de cobertura
                        st.subheader("📊 Cobertura da Migração")
                        coverage = comparison['migration_coverage']
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "Cobertura Geral",
                                f"{coverage['overall_coverage_percent']:.1f}%",
                                delta=coverage['coverage_status']
                            )
                        
                        with col2:
                            st.metric(
                                "Funções",
                                f"{coverage['function_coverage_percent']:.1f}%"
                            )
                        
                        with col3:
                            st.metric(
                                "Classes", 
                                f"{coverage['class_coverage_percent']:.1f}%"
                            )
                        
                        # Validação da migração
                        st.subheader("✅ Validação da Migração")
                        validation = comparison['validation_results']
                        
                        status_color = {
                            'PASS': '🟢',
                            'WARNING': '🟡', 
                            'FAIL': '🔴'
                        }
                        
                        st.write(f"**Status Geral:** {status_color.get(validation['overall_status'], '⚪')} {validation['overall_status']}")
                        
                        for val in validation['validations']:
                            status_icon = status_color.get(val['status'], '⚪')
                            st.write(f"{status_icon} **{val['aspect']}:** {val['message']}")
                        
                        # Mapeamento de funcionalidades
                        st.subheader("🗺️ Mapeamento de Funcionalidades")
                        mapping = comparison['functionality_mapping']
                        
                        if mapping.get('mapping_summary'):
                            summary = mapping['mapping_summary']
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Projeto Delphi:**")
                                st.write(f"• Funções: {summary['total_delphi_functions']}")
                            
                            with col2:
                                st.write("**Projeto Java:**")
                                st.write(f"• Métodos: {summary['total_java_methods']}")
                            
                            st.write("**Mapeamento:**")
                            st.write(f"• ✅ Mapeadas: {summary['mapped_functions']}")
                            st.write(f"• ❌ Não mapeadas: {summary['unmapped_functions']}")
                        
                        # Recomendações
                        if comparison.get('recommendations'):
                            st.subheader("💡 Recomendações")
                            
                            for rec in comparison['recommendations']:
                                priority_color = {
                                    'CRITICAL': '🚨',
                                    'HIGH': '🔴',
                                    'MEDIUM': '🟡',
                                    'LOW': '🟢'
                                }
                                
                                with st.expander(f"{priority_color.get(rec['priority'], '⚪')} {rec['category']} ({rec['priority']})"):
                                    st.write(f"**Recomendação:** {rec['recommendation']}")
                                    if rec.get('rationale'):
                                        st.write(f"**Justificativa:** {rec['rationale']}")
                        
                        # Downloads de documentação
                        st.subheader("📥 Downloads")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Documentação Delphi:**")
                            delphi_docs = result['delphi_documentation']
                            for doc_type, content in delphi_docs.items():
                                if content:
                                    st.download_button(
                                        label=f"📄 {doc_type}",
                                        data=content,
                                        file_name=f"delphi_{doc_type}.md",
                                        mime="text/markdown",
                                        key=f"delphi_{doc_type}"
                                    )
                        
                        with col2:
                            st.write("**Documentação Java:**")
                            java_docs = result['java_documentation']
                            for doc_type, content in java_docs.items():
                                if content:
                                    st.download_button(
                                        label=f"📄 {doc_type}",
                                        data=content,
                                        file_name=f"java_{doc_type}.md",
                                        mime="text/markdown",
                                        key=f"java_{doc_type}"
                                    )
                        
                        # Download da comparação completa
                        comparison_json = json.dumps(comparison, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="📊 Download Comparação Completa (JSON)",
                            data=comparison_json,
                            file_name="comparacao_projetos.json",
                            mime="application/json"
                        )
                    
                    else:
                        st.error(f"❌ Erro: {response.json().get('error', 'Erro desconhecido')}")
                        
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        else:
            st.warning("⚠️ Selecione ambos os arquivos (Delphi e Java)")

with tab4:
    st.header("🚀 Análise Completa de Modernização")
    st.write("Análise completa: estratégia + comparação (se projeto Java fornecido).")
    
    modernization_delphi = st.file_uploader(
        "Arquivo ZIP do projeto Delphi (obrigatório)",
        type=['zip'],
        key="modernization_delphi"
    )
    
    modernization_java = st.file_uploader(
        "Arquivo ZIP do projeto Java (opcional - para comparação)",
        type=['zip'],
        key="modernization_java"
    )
    
    if st.button("🚀 Analisar Modernização", key="analyze_modernization"):
        if modernization_delphi is not None:
            with st.spinner("Executando análise completa de modernização..."):
                try:
                    files = {'delphi_file': modernization_delphi}
                    
                    if modernization_java is not None:
                        files['java_file'] = modernization_java
                    
                    response = requests.post(f"{api_url}/modernization/analyze", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Análise de modernização concluída!")
                        
                        analysis_type = result['analysis_type']
                        
                        if analysis_type == 'complete_with_comparison':
                            st.info("🔄 Análise completa com comparação realizada")
                            
                            modernization_analysis = result['modernization_analysis']
                            
                            # Validação da modernização
                            st.subheader("🎯 Validação da Modernização")
                            validation = modernization_analysis['modernization_validation']
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Status", validation['overall_status'])
                            
                            with col2:
                                st.metric("Sucesso", f"{validation['success_percentage']:.1f}%")
                            
                            with col3:
                                st.metric("Score", validation['success_score'])
                            
                            st.write(f"**Resultado:** {validation['status_message']}")
                            
                            # Detalhes da validação
                            with st.expander("📋 Detalhes da Validação"):
                                for detail in validation['validation_details']:
                                    status_icon = {'PASS': '✅', 'FAIL': '❌', 'WARNING': '⚠️'}.get(detail['status'], '❓')
                                    st.write(f"{status_icon} **{detail['criterion']}:** {detail['value']} (req: {detail['requirement']})")
                            
                            # Próximos passos
                            if modernization_analysis.get('recommended_next_steps'):
                                st.subheader("🎯 Próximos Passos")
                                
                                for step in modernization_analysis['recommended_next_steps']:
                                    priority_color = {'CRITICAL': '🚨', 'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(step['priority'], '⚪')
                                    
                                    with st.expander(f"{priority_color} {step['category']} ({step['priority']}) - {step['timeline']}"):
                                        st.write(f"**Ação:** {step['action']}")
                                        st.write(f"**Detalhes:** {step['details']}")
                            
                            # Análise comparativa (resumida)
                            comparison = modernization_analysis['comparison_with_original']
                            coverage = comparison['migration_coverage']
                            
                            st.subheader("📊 Resumo da Migração")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Cobertura", f"{coverage['overall_coverage_percent']:.1f}%")
                            with col2:
                                st.metric("Status", coverage['coverage_status'])
                            with col3:
                                gaps = len(coverage.get('missing_components', []))
                                st.metric("Gaps", gaps)
                        
                        else:  # strategy_only
                            st.info("📋 Estratégia de modernização gerada")
                            
                            strategy = result['modernization_strategy']
                            
                            # Resumo da estratégia
                            st.subheader("📊 Resumo da Estratégia")
                            summary = strategy['summary']
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Complexidade", summary['complexity_level'].upper())
                            
                            with col2:
                                st.metric("Esforço Estimado", f"{summary['estimated_effort_weeks']} semanas")
                            
                            with col3:
                                st.metric("Componentes", strategy['metadata']['total_components'])
                            
                            # Componentes prioritários
                            if summary.get('priority_components'):
                                st.subheader("🎯 Componentes Prioritários")
                                for i, component in enumerate(summary['priority_components'], 1):
                                    st.write(f"{i}. {component}")
                            
                            # Fatores de risco
                            if summary.get('risk_factors'):
                                st.subheader("⚠️ Fatores de Risco")
                                for risk in summary['risk_factors']:
                                    st.warning(f"• {risk}")
                            
                            # Fases de migração
                            st.subheader("📅 Fases de Migração")
                            phases = strategy['migration_phases']
                            
                            for phase in phases:
                                with st.expander(f"Fase {phase['phase']}: {phase['name']} ({phase['duration_weeks']} semanas)"):
                                    st.write(f"**Descrição:** {phase['description']}")
                                    
                                    if phase.get('deliverables'):
                                        st.write("**Entregáveis:**")
                                        for deliverable in phase['deliverables']:
                                            st.write(f"• {deliverable}")
                                    
                                    if phase.get('components'):
                                        st.write(f"**Componentes:** {len(phase['components'])} itens")
                            
                            # Stack tecnológico
                            tech_stack = strategy['technology_stack']
                            
                            st.subheader("💻 Stack Tecnológico Recomendado")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Backend:**")
                                backend = tech_stack['backend']
                                for key, value in backend.items():
                                    if value:
                                        st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
                            
                            with col2:
                                st.write("**Frontend:**")
                                frontend = tech_stack['frontend']
                                for key, value in frontend.items():
                                    st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
                        
                        # Downloads disponíveis
                        st.subheader("📥 Downloads")
                        
                        # Documentação Delphi sempre disponível
                        if result.get('delphi_documentation'):
                            st.write("**Documentação do Projeto Original:**")
                            delphi_docs = result['delphi_documentation']
                            
                            cols = st.columns(min(len(delphi_docs), 4))
                            for idx, (doc_type, content) in enumerate(delphi_docs.items()):
                                if content:
                                    with cols[idx % 4]:
                                        st.download_button(
                                            label=f"📄 {doc_type}",
                                            data=content,
                                            file_name=f"delphi_{doc_type}.md",
                                            mime="text/markdown",
                                            key=f"mod_delphi_{doc_type}"
                                        )
                        
                        # Documentação Java se disponível
                        if analysis_type == 'complete_with_comparison':
                            java_docs = modernization_analysis['java_documentation']
                            if java_docs:
                                st.write("**Documentação do Projeto Modernizado:**")
                                
                                cols = st.columns(min(len(java_docs), 4))
                                for idx, (doc_type, content) in enumerate(java_docs.items()):
                                    if content:
                                        with cols[idx % 4]:
                                            st.download_button(
                                                label=f"📄 {doc_type}",
                                                data=content,
                                                file_name=f"java_{doc_type}.md",
                                                mime="text/markdown",
                                                key=f"mod_java_{doc_type}"
                                            )
                        
                        # Download dos dados completos
                        complete_data = json.dumps(result, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="📊 Download Análise Completa (JSON)",
                            data=complete_data,
                            file_name="analise_modernizacao_completa.json",
                            mime="application/json"
                        )
                    
                    else:
                        st.error(f"❌ Erro: {response.json().get('error', 'Erro desconhecido')}")
                        
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        else:
            st.warning("⚠️ Selecione pelo menos o arquivo Delphi")

# Footer
st.markdown("---")
st.markdown("""
**Sistema de Análise Comparativa de Projetos v2.0**  
🏛️ Analisa projetos Delphi legados  
☕ Analisa projetos Java Spring Boot  
🔄 Compara projetos e valida migrações  
🚀 Gera estratégias completas de modernização  
""")

# Debug info na sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("🐛 Debug")
    st.write(f"**API URL:** {api_url}")
    st.write(f"**Timestamp:** {datetime.now().strftime('%H:%M:%S')}")
    
    if st.button("🔄 Testar Conexão API"):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ API OK - v{data.get('version', 'unknown')}")
            else:
                st.error(f"❌ API retornou status {response.status_code}")
        except Exception as e:
            st.error(f"❌ Erro de conexão: {str(e)}")
