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

# Imports absolutos para evitar problemas
import sys
from pathlib import Path

# Adiciona diretório pai ao path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

try:
    from core.legacy_project_analyzer import LegacyProjectAnalyzer
    from core.documentation_generator import DocumentationGenerator
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_legacy_analysis_interface():
    """Interface principal para análise de projetos legados"""
    
    st.header("🔍 Análise de Projeto Legado")
    st.markdown("**Faça upload do seu projeto Delphi para gerar documentação completa**")
    
    # Inicializa objetos na sessão
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = LegacyProjectAnalyzer()
        # Garantir que está usando prompts especializados
        try:
            from prompts.specialized_prompts import PromptManager
            st.session_state.analyzer.prompt_manager = PromptManager()
            logger.info("✅ PromptManager especializado configurado para análise")
            
            # Testa se os métodos estão disponíveis
            if hasattr(st.session_state.analyzer.prompt_manager, 'get_analysis_prompt'):
                test_prompt = st.session_state.analyzer.prompt_manager.get_analysis_prompt()
                logger.info(f"✅ Prompt de análise carregado: {len(test_prompt)} caracteres")
            else:
                logger.warning("⚠️ Método get_analysis_prompt não encontrado")
                
        except ImportError as e:
            logger.warning(f"⚠️ Falha ao importar PromptManager especializado: {str(e)}")
            st.warning("⚠️ Usando prompts padrão para análise")
    
    if 'doc_generator' not in st.session_state:
        st.session_state.doc_generator = DocumentationGenerator()
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'generated_docs' not in st.session_state:
        st.session_state.generated_docs = {}
    
    # Exibe informações sobre prompts
    with st.expander("🤖 Configuração de Prompts"):
        col1, col2 = st.columns(2)
        
        with col1:
            if hasattr(st.session_state.analyzer, 'prompt_manager') and st.session_state.analyzer.prompt_manager:
                st.success("✅ **Prompts Especializados Ativos**")
                st.info("Seus prompts personalizados estão sendo usados para análise")
                
                # Verifica quais métodos estão disponíveis
                available_methods = []
                for method_name in ['get_analysis_prompt', 'get_documentation_generation_prompt', 'get_specialized_prompt']:
                    if hasattr(st.session_state.analyzer.prompt_manager, method_name):
                        available_methods.append(method_name)
                
                if available_methods:
                    st.write("**Métodos disponíveis:**")
                    for method in available_methods:
                        st.write(f"• {method}")
                
            else:
                st.warning("⚠️ **Usando Prompts Padrão**")
                st.info("Prompts especializados não estão disponíveis")
        
        with col2:
            if st.button("🔄 Recarregar Prompts"):
                try:
                    from prompts.specialized_prompts import PromptManager
                    st.session_state.analyzer.prompt_manager = PromptManager()
                    st.success("✅ Prompts recarregados com sucesso!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao recarregar prompts: {str(e)}")

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
            try:
                # Validação adicional para garantir que o arquivo é válido
                if not hasattr(uploaded_file, 'seek') or not hasattr(uploaded_file, 'getbuffer'):
                    st.error("❌ Arquivo inválido. Por favor, faça o upload novamente.")
                    return
                
                # Salva arquivo temporário
                temp_dir = tempfile.mkdtemp(prefix="junim_project_")
                zip_path = os.path.join(temp_dir, uploaded_file.name)
                
                # Garante que o arquivo está no início para leitura
                try:
                    uploaded_file.seek(0)
                except Exception as seek_error:
                    st.error(f"❌ Erro ao acessar arquivo: {seek_error}")
                    return
                
                # Lê o conteúdo do arquivo
                try:
                    file_content = uploaded_file.getbuffer()
                    if len(file_content) == 0:
                        st.error("❌ Arquivo está vazio. Por favor, selecione um arquivo válido.")
                        return
                except Exception as read_error:
                    st.error(f"❌ Erro ao ler arquivo: {read_error}")
                    return
                
                with open(zip_path, "wb") as f:
                    f.write(file_content)
                
                # Extrai ZIP
                extract_dir = os.path.join(temp_dir, "extracted")
                os.makedirs(extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Verifica se a extração foi bem-sucedida
                if os.path.exists(extract_dir) and os.listdir(extract_dir):
                    project_path = extract_dir
                    st.success(f"✅ Arquivo extraído com sucesso: {uploaded_file.name}")
                else:
                    st.error("❌ Erro: Arquivo ZIP vazio ou corrompido")
                    return
                    
            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo ZIP: {str(e)}")
                logger.error(f"Erro ao processar ZIP: {str(e)}")
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
        # Valida se o projeto contém arquivos Delphi
        delphi_files = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.lower().endswith(('.pas', '.dfm', '.dpr')):
                    delphi_files.append(file)
        
        if not delphi_files:
            st.error("❌ Nenhum arquivo Delphi (.pas, .dfm, .dpr) encontrado no projeto!")
            return
        
        st.info(f"📁 Encontrados {len(delphi_files)} arquivos Delphi para análise")
        
        start_analysis(
            project_path, 
            project_name, 
            include_comments, 
            analyze_business_logic, 
            generate_correlations
        )

def start_analysis(project_path: str, project_name: str, include_comments: bool, 
                  analyze_business_logic: bool, generate_correlations: bool):
    """Inicia a análise do projeto usando prompts especializados para mapeamento de funcionalidades"""
    
    with st.spinner("🔄 Analisando projeto... Isso pode levar alguns minutos."):
        try:
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Etapa 1: Preparação e análise estrutural
            status_text.text("📋 Preparando análise com mapeamento de funcionalidades...")
            progress_bar.progress(10)
            
            # Encontra e prepara arquivos para análise
            uploaded_files = []
            total_files = 0
            
            # Conta arquivos primeiro
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.lower().endswith(('.pas', '.dfm', '.dpr')):
                        total_files += 1
            
            if total_files == 0:
                st.error("❌ Nenhum arquivo Delphi encontrado no diretório!")
                return
            
            # Processa arquivos
            processed_files = 0
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.lower().endswith(('.pas', '.dfm', '.dpr')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            if content.strip():  # Só adiciona se o arquivo não está vazio
                                uploaded_files.append({
                                    'name': file,
                                    'path': file_path,
                                    'content': content,
                                    'type': file.split('.')[-1].lower()
                                })
                                processed_files += 1
                        except Exception as e:
                            st.warning(f"⚠️ Erro ao ler arquivo {file}: {e}")
                            continue
            
            if not uploaded_files:
                st.error("❌ Nenhum arquivo válido foi processado!")
                return
            
            st.info(f"📁 Processados {processed_files} de {total_files} arquivos Delphi")
            
            # Etapa 2: Análise com prompts especializados
            status_text.text("🧠 Executando análise com foco em funcionalidades...")
            progress_bar.progress(30)
            
            # Usa novo método com prompts especializados
            analysis_results = st.session_state.analyzer.analyze_project_with_prompts(
                project_path, 
                uploaded_files
            )
            
            # Etapa 3: Análise estrutural complementar
            status_text.text("🏗️ Executando análise estrutural...")
            progress_bar.progress(50)
            
            # Combina com análise estrutural padrão para completar dados
            structural_analysis = st.session_state.analyzer.analyze_project(
                project_path,
                project_name=project_name,
                include_comments=include_comments,
                analyze_business_logic=analyze_business_logic,
                generate_correlations=generate_correlations,
                output_detailed_logs=True
            )
            
            # Mescla resultados para ter dados completos
            analysis_results.update(structural_analysis)
            analysis_results['functional_mapping_enhanced'] = True
            
            # Etapa 4: Geração de documentação com mapeamento
            status_text.text("📝 Gerando documentação com mapeamento de funcionalidades...")
            progress_bar.progress(75)
            
            generated_docs = st.session_state.analyzer.generate_documentation_with_mapping(
                analysis_results
            )
            
            # Se não conseguiu gerar com prompt especializado, usa método padrão
            if 'error' in generated_docs or not generated_docs.get('documentation'):
                st.warning("⚠️ Usando método de documentação padrão como fallback...")
                generated_docs = st.session_state.doc_generator.generate_complete_documentation(
                    analysis_results
                )
            
            # Finalização
            progress_bar.progress(100)
            status_text.text("✅ Análise com mapeamento de funcionalidades concluída!")
            
            # Salva resultados na sessão
            st.session_state.analysis_results = analysis_results
            st.session_state.generated_docs = generated_docs
            
            # Mostra resumo
            st.success("🎉 Análise completada com mapeamento detalhado de funcionalidades!")
            show_analysis_summary(analysis_results, generated_docs)
            
        except FileNotFoundError as e:
            st.error(f"❌ Arquivo ou diretório não encontrado: {str(e)}")
            logger.error(f"FileNotFoundError na análise: {str(e)}")
        except PermissionError as e:
            st.error(f"❌ Erro de permissão ao acessar arquivos: {str(e)}")
            logger.error(f"PermissionError na análise: {str(e)}")
        except zipfile.BadZipFile as e:
            st.error(f"❌ Arquivo ZIP corrompido ou inválido: {str(e)}")
            logger.error(f"BadZipFile na análise: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erro durante análise: {str(e)}")
            logger.error(f"Erro geral na análise: {str(e)}", exc_info=True)
            # Fallback para método padrão em caso de erro
            st.info("🔄 Tentando análise com método padrão...")
            try:
                # Análise básica como fallback
                basic_analysis = st.session_state.analyzer.analyze_project(
                    project_path,
                    project_name=project_name or "Projeto_Delphi",
                    include_comments=include_comments,
                    analyze_business_logic=analyze_business_logic,
                    generate_correlations=generate_correlations
                )
                
                st.session_state.analysis_results = basic_analysis
                st.success("✅ Análise básica completada como fallback!")
                show_analysis_summary(basic_analysis, {})
                
            except Exception as fallback_error:
                st.error(f"❌ Falha também na análise básica: {str(fallback_error)}")
                logger.error(f"Erro no fallback: {str(fallback_error)}")

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
