"""
Interface de análise de projetos legados - Upload e documentação
"""

import streamlit as st
import os
import tempfile
import zipfile
import shutil
from typing import Dict, Any, List
import logging
from datetime import datetime

from core.legacy_project_analyzer import LegacyProjectAnalyzer
from core.documentation_generator import DocumentationGenerator

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_legacy_analysis_interface():
    """Renderiza a interface de análise de projetos legados"""
    
    st.header("🔍 Análise de Projeto Legado")
    st.markdown("**Faça upload do seu projeto Delphi para gerar documentação completa**")
    
    # Inicializa objetos na sessão
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = LegacyProjectAnalyzer()
    
    if 'doc_generator' not in st.session_state:
        st.session_state.doc_generator = DocumentationGenerator()
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'generated_docs' not in st.session_state:
        st.session_state.generated_docs = {}
    
    # Tabs para organizar funcionalidades
    tab1, tab2, tab3 = st.tabs(["📁 Upload & Análise", "📄 Documentos Gerados", "📊 Visualização"])
    
    with tab1:
        render_upload_analysis_tab()
    
    with tab2:
        render_documents_tab()
    
    with tab3:
        render_visualization_tab()

def render_upload_analysis_tab():
    """Tab de upload e análise"""
    
    st.subheader("Upload do Projeto")
    
    # Opções de upload
    upload_method = st.radio(
        "Método de Upload:",
        ["Arquivo ZIP", "Pasta Local"],
        horizontal=True
    )
    
    project_path = None
    
    if upload_method == "Arquivo ZIP":
        uploaded_file = st.file_uploader(
            "Selecione um arquivo ZIP contendo o projeto Delphi",
            type=['zip'],
            help="O arquivo deve conter todos os arquivos .pas, .dfm, .dpr do projeto"
        )
        
        if uploaded_file is not None:
            # Salva arquivo temporário
            temp_dir = tempfile.mkdtemp(prefix="junim_project_")
            zip_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(zip_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Extrai ZIP
            extract_dir = os.path.join(temp_dir, "extracted")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                project_path = extract_dir
                st.success(f"✅ Arquivo extraído com sucesso: {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ Erro ao extrair arquivo: {str(e)}")
                return
    
    else:  # Pasta Local
        folder_path = st.text_input(
            "Caminho da pasta do projeto:",
            placeholder=r"C:\MeuProjeto\DelphiApp",
            help="Digite o caminho completo para a pasta contendo o projeto Delphi"
        )
        
        if folder_path and os.path.exists(folder_path):
            project_path = folder_path
            st.success(f"✅ Pasta encontrada: {folder_path}")
        elif folder_path:
            st.error("❌ Pasta não encontrada")
    
    # Configurações de análise
    st.subheader("Configurações da Análise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input(
            "Nome do Projeto:",
            value="MeuProjeto",
            help="Nome que aparecerá nos documentos gerados"
        )
        
        include_comments = st.checkbox(
            "Incluir análise de comentários",
            value=True,
            help="Analisa comentários no código para extrair mais contexto"
        )
    
    with col2:
        analyze_business_logic = st.checkbox(
            "Análise de lógica de negócio",
            value=True,
            help="Identifica regras de negócio e validações"
        )
        
        generate_correlations = st.checkbox(
            "Gerar correlações Delphi→Java",
            value=True,
            help="Cria mapeamento para modernização"
        )
    
    # Botão de análise
    if project_path and st.button("🚀 Iniciar Análise", type="primary"):
        start_analysis(
            project_path, 
            project_name, 
            include_comments, 
            analyze_business_logic, 
            generate_correlations
        )

def start_analysis(project_path: str, project_name: str, include_comments: bool, 
                  analyze_business_logic: bool, generate_correlations: bool):
    """Inicia a análise do projeto"""
    
    with st.spinner("🔄 Analisando projeto... Isso pode levar alguns minutos."):
        try:
            # Configura parâmetros da análise
            analysis_config = {
                'project_name': project_name,
                'include_comments': include_comments,
                'analyze_business_logic': analyze_business_logic,
                'generate_correlations': generate_correlations,
                'output_detailed_logs': True
            }
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Etapa 1: Análise básica
            status_text.text("📋 Analisando estrutura do projeto...")
            progress_bar.progress(20)
            
            analysis_results = st.session_state.analyzer.analyze_project(
                project_path, 
                **analysis_config
            )
            
            # Etapa 2: Análise avançada
            status_text.text("🧠 Extraindo lógica de negócio...")
            progress_bar.progress(40)
            
            if analyze_business_logic:
                business_analysis = st.session_state.analyzer.extract_business_logic(
                    analysis_results.get('units_analysis', {})
                )
                analysis_results['business_logic'] = business_analysis
            
            # Etapa 3: Geração de correlações
            status_text.text("🔗 Gerando correlações...")
            progress_bar.progress(60)
            
            if generate_correlations:
                correlations = st.session_state.analyzer.generate_delphi_java_correlations(
                    analysis_results
                )
                analysis_results['correlations'] = correlations
            
            # Etapa 4: Geração de documentação
            status_text.text("📝 Gerando documentação...")
            progress_bar.progress(80)
            
            generated_docs = st.session_state.doc_generator.generate_complete_documentation(
                analysis_results
            )
            
            # Finalização
            progress_bar.progress(100)
            status_text.text("✅ Análise concluída!")
            
            # Salva resultados na sessão
            st.session_state.analysis_results = analysis_results
            st.session_state.generated_docs = generated_docs
            
            # Mostra resumo
            show_analysis_summary(analysis_results, generated_docs)
            
        except Exception as e:
            st.error(f"❌ Erro durante análise: {str(e)}")
            logger.error(f"Erro na análise: {str(e)}")

def show_analysis_summary(analysis_results: Dict[str, Any], generated_docs: Dict[str, str]):
    """Mostra resumo da análise realizada"""
    
    st.success("🎉 **Análise Concluída com Sucesso!**")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_files = analysis_results.get('metadata', {}).get('total_files_analyzed', 0)
        st.metric("Arquivos Analisados", total_files)
    
    with col2:
        units_count = len(analysis_results.get('units_analysis', {}))
        st.metric("Units Encontradas", units_count)
    
    with col3:
        docs_count = len(generated_docs)
        st.metric("Documentos Gerados", docs_count)
    
    with col4:
        complexity = analysis_results.get('characteristics', {}).get('complexity_level', 'Média')
        st.metric("Complexidade", complexity)
    
    # Lista de documentos gerados
    st.subheader("📄 Documentos Gerados")
    
    doc_names = {
        'executive_summary': '📋 Resumo Executivo',
        'requirements': '📝 Requisitos do Sistema',
        'functionality': '⚙️ Funcionalidades',
        'characteristics': '🔧 Características Técnicas',
        'execution_flows': '🔄 Fluxos de Execução',
        'data_flows': '💾 Fluxos de Dados',
        'correlations': '🔗 Correlações Delphi→Java',
        'technical_analysis': '🔬 Análise Técnica Detalhada',
        'structured_data': '📊 Dados Estruturados (JSON)'
    }
    
    for doc_key, doc_path in generated_docs.items():
        doc_name = doc_names.get(doc_key, doc_key.title())
        file_size = os.path.getsize(doc_path) if os.path.exists(doc_path) else 0
        st.write(f"✅ {doc_name} - {file_size:,} bytes")

def render_documents_tab():
    """Tab de visualização de documentos"""
    
    st.subheader("📄 Documentos Gerados")
    
    if not st.session_state.generated_docs:
        st.info("🔍 Nenhum documento gerado ainda. Faça uma análise primeiro.")
        return
    
    # Seleção de documento
    doc_names = {
        'executive_summary': '📋 Resumo Executivo',
        'requirements': '📝 Requisitos do Sistema',
        'functionality': '⚙️ Funcionalidades',
        'characteristics': '🔧 Características Técnicas',
        'execution_flows': '🔄 Fluxos de Execução',
        'data_flows': '💾 Fluxos de Dados',
        'correlations': '🔗 Correlações Delphi→Java',
        'technical_analysis': '🔬 Análise Técnica Detalhada',
        'structured_data': '📊 Dados Estruturados (JSON)'
    }
    
    selected_doc = st.selectbox(
        "Selecione um documento para visualizar:",
        options=list(st.session_state.generated_docs.keys()),
        format_func=lambda x: doc_names.get(x, x.title())
    )
    
    if selected_doc:
        doc_path = st.session_state.generated_docs[selected_doc]
        
        # Botões de ação
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📥 Download"):
                download_document(doc_path)
        
        with col2:
            if st.button("📋 Copiar Conteúdo"):
                copy_document_content(doc_path)
        
        # Visualização do conteúdo
        st.subheader(f"Conteúdo: {doc_names.get(selected_doc, selected_doc.title())}")
        
        if doc_path.endswith('.json'):
            # Para arquivos JSON, mostra formatado
            try:
                import json
                with open(doc_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                st.json(data)
            except Exception as e:
                st.error(f"Erro ao carregar JSON: {str(e)}")
        else:
            # Para arquivos Markdown, mostra conteúdo
            try:
                content = st.session_state.doc_generator.get_document_content(doc_path)
                st.markdown(content)
            except Exception as e:
                st.error(f"Erro ao carregar documento: {str(e)}")

def render_visualization_tab():
    """Tab de visualização e estatísticas"""
    
    st.subheader("📊 Visualização da Análise")
    
    if not st.session_state.analysis_results:
        st.info("🔍 Nenhuma análise disponível. Execute uma análise primeiro.")
        return
    
    analysis = st.session_state.analysis_results
    
    # Gráfico de distribuição de tipos de arquivo
    st.subheader("📁 Distribuição de Arquivos")
    
    file_counts = analysis.get('project_info', {}).get('file_counts', {})
    if file_counts:
        import plotly.express as px
        import pandas as pd
        
        df = pd.DataFrame(list(file_counts.items()), columns=['Tipo', 'Quantidade'])
        fig = px.pie(df, values='Quantidade', names='Tipo', title='Distribuição por Tipo de Arquivo')
        st.plotly_chart(fig, use_container_width=True)
    
    # Métricas de complexidade
    st.subheader("🔧 Métricas de Complexidade")
    
    units_analysis = analysis.get('units_analysis', {})
    if units_analysis:
        complexities = []
        unit_names = []
        
        for unit_name, unit_data in units_analysis.items():
            complexity = unit_data.get('complexity_metrics', {}).get('cyclomatic_complexity', 0)
            if complexity > 0:
                complexities.append(complexity)
                unit_names.append(unit_name)
        
        if complexities:
            import plotly.graph_objects as go
            
            fig = go.Figure(data=go.Bar(x=unit_names[:10], y=complexities[:10]))
            fig.update_layout(
                title='Top 10 Units por Complexidade Ciclomática',
                xaxis_title='Unit',
                yaxis_title='Complexidade'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas gerais
    st.subheader("📈 Estatísticas Gerais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Total de Linhas de Código",
            sum(unit.get('lines_count', 0) for unit in units_analysis.values())
        )
        
        st.metric(
            "Média de Complexidade",
            f"{sum(unit.get('complexity_metrics', {}).get('cyclomatic_complexity', 0) for unit in units_analysis.values()) / max(len(units_analysis), 1):.1f}"
        )
    
    with col2:
        st.metric(
            "Units com Alta Complexidade",
            sum(1 for unit in units_analysis.values() 
                if unit.get('complexity_metrics', {}).get('cyclomatic_complexity', 0) > 10)
        )
        
        readiness = analysis.get('characteristics', {}).get('modernization_readiness', 'Não avaliado')
        st.metric("Prontidão para Modernização", readiness)

def download_document(doc_path: str):
    """Prepara download do documento"""
    try:
        with open(doc_path, 'rb') as file:
            st.download_button(
                label="📥 Baixar Documento",
                data=file.read(),
                file_name=os.path.basename(doc_path),
                mime='text/markdown' if doc_path.endswith('.md') else 'application/json'
            )
    except Exception as e:
        st.error(f"Erro ao preparar download: {str(e)}")

def copy_document_content(doc_path: str):
    """Copia conteúdo do documento para clipboard"""
    try:
        content = st.session_state.doc_generator.get_document_content(doc_path)
        # Streamlit não tem função nativa de clipboard, então mostra o conteúdo em text_area
        st.text_area(
            "Conteúdo para copiar:",
            value=content,
            height=200,
            help="Selecione todo o texto e copie (Ctrl+A, Ctrl+C)"
        )
    except Exception as e:
        st.error(f"Erro ao copiar conteúdo: {str(e)}")

def get_project_summary_stats(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai estatísticas resumidas do projeto"""
    
    if not analysis_results:
        return {}
    
    units_analysis = analysis_results.get('units_analysis', {})
    
    return {
        'total_units': len(units_analysis),
        'total_lines': sum(unit.get('lines_count', 0) for unit in units_analysis.values()),
        'avg_complexity': sum(unit.get('complexity_metrics', {}).get('cyclomatic_complexity', 0) 
                             for unit in units_analysis.values()) / max(len(units_analysis), 1),
        'high_complexity_units': sum(1 for unit in units_analysis.values() 
                                   if unit.get('complexity_metrics', {}).get('cyclomatic_complexity', 0) > 10),
        'forms_count': sum(1 for unit in units_analysis.values() 
                          if unit.get('unit_type') == 'form'),
        'datamodules_count': sum(1 for unit in units_analysis.values() 
                               if unit.get('unit_type') == 'datamodule')
    }
