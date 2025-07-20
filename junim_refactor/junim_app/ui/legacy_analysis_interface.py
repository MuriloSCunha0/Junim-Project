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
import json
import re
import time

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
    from core.pipeline import ModernizationPipeline
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _check_ollama_available() -> bool:
    """Verifica se o Ollama está disponível"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def render_legacy_analysis_interface():
    """Interface principal para análise de projetos legados"""
    
    st.header("🔍 Análise de Projeto Legado")
    st.markdown("**Faça upload do seu projeto Delphi para gerar documentação completa**")
    
    # Inicializa objetos na sessão
    if 'analyzer' not in st.session_state:
        # Configura a chave da API se disponível
        config = st.session_state.get('config', {})
        
        # Garantir que está usando prompts especializados
        try:
            from prompts.specialized_prompts import PromptManager
            prompt_manager = PromptManager()
            logger.info("✅ PromptManager especializado configurado para análise")
            
            # Testa se os métodos estão disponíveis
            if hasattr(prompt_manager, 'get_analysis_prompt'):
                test_prompt = prompt_manager.get_analysis_prompt()
                logger.info(f"✅ Prompt de análise carregado: {len(test_prompt)} caracteres")
            else:
                logger.warning("⚠️ Método get_analysis_prompt não encontrado")
                
        except ImportError as e:
            logger.warning(f"⚠️ Falha ao importar PromptManager especializado: {str(e)}")
            st.warning("⚠️ Usando prompts padrão para análise")
            prompt_manager = None
        
        # Inicializa o analyzer com o prompt_manager
        st.session_state.analyzer = LegacyProjectAnalyzer(prompt_manager=prompt_manager)
        
        # Configura a API se disponível
        if config.get('groq_api_key'):
            st.session_state.analyzer.update_api_config(
                groq_api_key=config['groq_api_key'],
                groq_model=config.get('groq_model', 'llama3-70b-8192')
            )
            logger.info("✅ API configurada no analyzer")
    
    # Atualiza a configuração da API se mudou
    config = st.session_state.get('config', {})
    if config.get('groq_api_key'):
        # Usa o novo método para atualizar a configuração
        st.session_state.analyzer.update_api_config(
            groq_api_key=config['groq_api_key'],
            groq_model=config.get('groq_model', 'llama3-70b-8192')
        )
    
    if 'doc_generator' not in st.session_state:
        # Usa o mesmo prompt_manager do analyzer se disponível
        prompt_manager = getattr(st.session_state.analyzer, 'prompt_manager', None)
        st.session_state.doc_generator = DocumentationGenerator(prompt_manager=prompt_manager)
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'generated_docs' not in st.session_state:
        st.session_state.generated_docs = {}
    
    # Exibe informações sobre configuração
    with st.expander("🤖 Status da Configuração"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Status da API
            groq_configured = bool(config.get('groq_api_key', ''))
            ollama_available = _check_ollama_available()
            
            if groq_configured:
                st.success("✅ **API Groq Configurada**")
                st.info(f"Modelo: {config.get('groq_model', 'llama3-70b-8192')}")
            elif ollama_available:
                st.success("✅ **Ollama Disponível**")
                ollama_model = config.get('ollama_model', 'deepseek-r1:14b')
                if 'deepseek-r1:14b' in ollama_model:
                    st.info("🚀 **DeepSeek-R1:14b** - Modelo de alta performance")
                    st.success("🎯 **Recomendado para análises complexas**")
                elif 'deepseek-r1' in ollama_model:
                    st.info(f"🤖 **{ollama_model}** - Modelo DeepSeek-R1")
                else:
                    st.info(f"Modelo: {ollama_model}")
            else:
                st.error("❌ **Nenhuma API Configurada**")
                st.warning("Configure Groq API key ou inicie o Ollama")
                st.info("Configure a chave na barra lateral")
            
            # Status dos prompts
            if hasattr(st.session_state.analyzer, 'prompt_manager') and st.session_state.analyzer.prompt_manager:
                st.success("✅ **Prompts Especializados Ativos**")
                
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
        
        with col2:
            # Configurações de análise
            st.write("**Configurações de Análise:**")
            st.write(f"• Incluir comentários: {config.get('include_comments', True)}")
            st.write(f"• Analisar lógica de negócio: {config.get('analyze_business_logic', True)}")
            st.write(f"• Gerar correlações: {config.get('generate_correlations', True)}")
            
            # Destaque para DeepSeek-R1
            if config.get('ollama_model') == 'deepseek-r1:14b':
                st.markdown("---")
                st.write("🚀 **DeepSeek-R1:14b Ativo**")
                st.success("✨ **Benefícios:**")
                st.write("• Análise mais profunda de código")
                st.write("• Melhor compreensão de lógica de negócio")
                st.write("• Geração de código mais precisa")
                st.write("• Suporte a projetos mais complexos")
            
            if st.button("🔄 Recarregar Configurações"):
                try:
                    # Recarrega prompt manager
                    from prompts.specialized_prompts import PromptManager
                    st.session_state.analyzer.prompt_manager = PromptManager()
                    
                    # Recarrega configuração da API
                    config = st.session_state.get('config', {})
                    if config.get('groq_api_key'):
                        st.session_state.analyzer.groq_api_key = config['groq_api_key']
                    
                    st.success("✅ Configurações recarregadas!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao recarregar: {str(e)}")

    # Tabs para organizar funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload & Análise", "📄 Documentos Gerados", "� Feedback & Regeneração", "🚀 Modernização"])
    
    with tab1:
        render_upload_analysis_tab()
    
    with tab2:
        render_documents_tab()
    
    with tab3:
        render_feedback_tab()
    
    with tab4:
        render_modernization_tab()

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

def start_analysis(project_path: str, project_name: str = None, include_comments: bool = True, 
                  analyze_business_logic: bool = True, generate_correlations: bool = True):
    """Inicia a análise do projeto e gera documentação completa"""
    try:
        with st.spinner("🔍 Analisando projeto Delphi..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Verifica se o analyzer está configurado
            if not hasattr(st.session_state, 'analyzer') or not st.session_state.analyzer:
                st.error("❌ Analisador não configurado!")
                return
            
            # Atualiza configuração se necessário
            config = st.session_state.get('config', {})
            if config.get('groq_api_key') and hasattr(st.session_state.analyzer, 'groq_api_key'):
                st.session_state.analyzer.groq_api_key = config['groq_api_key']
            
            # Configura opções de análise
            analysis_options = {
                'include_comments': include_comments,
                'analyze_business_logic': analyze_business_logic,
                'generate_correlations': generate_correlations
            }
            
            # Passa as opções para o analyzer se ele suportar
            if hasattr(st.session_state.analyzer, 'set_analysis_options'):
                st.session_state.analyzer.set_analysis_options(analysis_options)
            
            # Executa análise do projeto
            status_text.text("🔍 Executando análise do projeto...")
            progress_bar.progress(20)
            
            try:
                # Usa o método correto com parâmetros corretos
                if hasattr(st.session_state.analyzer, 'analyze_project_with_prompts'):
                    analysis_results = st.session_state.analyzer.analyze_project_with_prompts(
                        project_path, 
                        project_name
                    )
                else:
                    # Fallback para método básico
                    analysis_results = st.session_state.analyzer.analyze_project(
                        project_path, 
                        project_name
                    )
                
                progress_bar.progress(50)
                status_text.text("✅ Análise estrutural concluída!")
                
            except Exception as e:
                logger.error(f"Erro geral na análise: {str(e)}")
                st.error(f"❌ Erro na análise: {str(e)}")
                return
            
            # Enriquece os resultados com as opções de análise
            analysis_results['analysis_options'] = analysis_options
            
            # Armazena resultados
            st.session_state.analysis_results = analysis_results
            
            # Gera documentação completa automaticamente
            status_text.text("📄 Gerando documentação completa...")
            progress_bar.progress(60)
            
            try:
                # Configura o gerador de documentação COM LLM SERVICE
                doc_generator = st.session_state.get('doc_generator')
                if not doc_generator:
                    from core.documentation_generator import DocumentationGenerator
                    # Usa o mesmo prompt_manager e LLM service do analyzer
                    prompt_manager = getattr(st.session_state.analyzer, 'prompt_manager', None)
                    llm_service = getattr(st.session_state.analyzer, 'llm_service', None)
                    
                    doc_generator = DocumentationGenerator(
                        llm_service=llm_service,  # IMPORTANTE: passa o LLM service
                        prompt_manager=prompt_manager
                    )
                    st.session_state.doc_generator = doc_generator
                    logger.info(f"✅ DocumentationGenerator configurado com LLM: {llm_service is not None}")
                
                # Verifica se o LLM service está disponível
                if not doc_generator.llm_service:
                    logger.warning("⚠️ LLM service não disponível, usando fallback")
                    # Tenta pegar do analyzer novamente
                    if hasattr(st.session_state.analyzer, 'llm_service'):
                        doc_generator.llm_service = st.session_state.analyzer.llm_service
                        logger.info("✅ LLM service recuperado do analyzer")
                
                # Atualiza prompt manager se necessário
                if hasattr(st.session_state.analyzer, 'prompt_manager'):
                    doc_generator.prompt_manager = st.session_state.analyzer.prompt_manager
                
                # Gera documentação específica - agora retorna conteúdo diretamente
                generated_docs_content = doc_generator.generate_specific_documentation(
                    analysis_results=analysis_results, 
                    project_name=project_name or "Projeto",
                    include_mermaid=True,
                    documents_to_generate=['backend_analysis', 'functionality_mapping']
                )
                
                # Mapeia para nomes de exibição amigáveis
                generated_docs = {}
                for doc_type, content in generated_docs_content.items():
                    display_name = {
                        'backend_analysis': '🔧 Análise de Backend',
                        'functionality_mapping': '🔗 Mapeamento de Funcionalidades',
                        'mermaid_diagram': '📊 Diagrama Mermaid',
                        'readme': '📄 Resumo do Projeto'
                    }.get(doc_type, doc_type.title())
                    
                    generated_docs[display_name] = content
                
                st.session_state.generated_docs = generated_docs
                
                progress_bar.progress(90)
                status_text.text("📚 Documentação completa gerada!")
                
            except Exception as doc_error:
                logger.warning(f"Erro ao gerar documentação: {str(doc_error)}")
                st.warning(f"⚠️ Erro ao gerar documentação: {str(doc_error)}")
                st.session_state.generated_docs = {}
            
            # Finaliza
            progress_bar.progress(100)
            status_text.text("🎉 Análise e documentação concluídas!")
            
            # Mostra resumo dos resultados
            show_analysis_summary(analysis_results, st.session_state.generated_docs)
            
    except Exception as e:
        logger.error(f"Erro na análise: {str(e)}")
        st.error(f"❌ Erro na análise: {str(e)}")

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
        'backend_analysis': '🎯 Análise de Backend',
        'functionality_mapping': '🗺️ Mapeamento de Funcionalidades',
        'testing_strategy': '🧪 Estratégia de Testes',
        'mermaid_diagram': '� Diagrama Mermaid'
    }
    
    for doc_key, doc_path in generated_docs.items():
        doc_name = doc_names.get(doc_key, doc_key.title())
        file_size = os.path.getsize(doc_path) if os.path.exists(doc_path) else 0
        st.write(f"✅ {doc_name} ({file_size} bytes)")
    
    st.info("📝 **Próximo Passo**: Revise os documentos gerados na aba 'Documentos Gerados' e forneça feedback se necessário.")

def render_documents_tab():
    """Renderiza a aba de documentos gerados"""
    
    if not st.session_state.get('generated_docs'):
        st.info("📋 Nenhum documento gerado ainda. Execute a análise primeiro.")
        return
    
    # Mapeamento de nomes amigáveis para os documentos
    doc_names = {
        'backend_analysis': '🎯 Análise de Backend',
        'functionality_mapping': '🗺️ Mapeamento de Funcionalidades',
        'testing_strategy': '🧪 Estratégia de Testes',
        'mermaid_diagram': '� Diagrama Mermaid',
        # Compatibilidade com nomes antigos
        'executive_summary': '📋 Resumo Executivo',
        'requirements': '📝 Requisitos do Sistema',
        'functionality': '⚙️ Funcionalidades',
        'characteristics': '🔧 Características Técnicas',
        'technical_analysis': '🧪 Análise Técnica',
        'structured_data': '📋 Dados Estruturados'
    }
    
    # Filtra apenas documentos válidos (strings com caminhos)
    valid_docs = {}
    for key, value in st.session_state.generated_docs.items():
        if isinstance(value, str) and value.strip():  # Verifica se é string não vazia
            valid_docs[key] = value
    
    if not valid_docs:
        st.warning("⚠️ Nenhum documento válido encontrado.")
        return
    
    st.subheader("📄 Documentos Gerados")
    
    selected_doc = st.selectbox(
        "Selecione um documento para visualizar:",
        options=list(valid_docs.keys()),
        format_func=lambda x: doc_names.get(x, x.title())
    )
    
    if selected_doc:
        doc_content = valid_docs[selected_doc]
        
        # Botões de ação
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # Prepara nome do arquivo para download
            safe_doc_name = selected_doc.lower().replace(' ', '_').replace('🔧', '').replace('🔗', '').replace('📊', '').replace('📄', '').strip()
            filename = f"{safe_doc_name}.md"
            if selected_doc == '📊 Diagrama Mermaid':
                filename = "diagrama_arquitetura.md"
            
            st.download_button(
                label="📥 Download",
                data=doc_content,
                file_name=filename,
                mime="text/markdown",
                help=f"Baixar {selected_doc}"
            )
        
        with col2:
            if st.button("📋 Copiar Conteúdo"):
                # Usa o clipboard do navegador
                st.write("📋 Conteúdo copiado! Use Ctrl+V para colar.")
                # Mostra o conteúdo em um text_area para facilitar a cópia manual
                st.text_area("Conteúdo para copiar:", doc_content, height=100, key=f"copy_{selected_doc}")
        
        # Visualização do conteúdo
        st.subheader(f"Conteúdo: {doc_names.get(selected_doc, selected_doc.title())}")
        
        try:
            # Para diagrama Mermaid
            if selected_doc == '📊 Diagrama Mermaid' or 'mermaid' in selected_doc.lower():
                st.subheader("📊 Diagrama de Arquitetura")
                
                # Extrai código Mermaid
                mermaid_code = doc_content
                if "```mermaid" in mermaid_code:
                    import re
                    mermaid_match = re.search(r'```mermaid\n(.*?)\n```', mermaid_code, re.DOTALL)
                    if mermaid_match:
                        pure_mermaid = mermaid_match.group(1).strip()
                    else:
                        pure_mermaid = mermaid_code
                else:
                    pure_mermaid = mermaid_code
                
                # Primeiro mostra o código
                st.code(pure_mermaid, language="mermaid")
                
                # Tenta renderizar o diagrama
                try:
                    import streamlit.components.v1 as components
                    
                    mermaid_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    </head>
                    <body>
                        <div class="mermaid">
                            {pure_mermaid}
                        </div>
                        <script>
                            mermaid.initialize({{
                                startOnLoad: true,
                                theme: 'default',
                                securityLevel: 'loose'
                            }});
                        </script>
                    </body>
                    </html>
                    """
                    
                    components.html(mermaid_html, height=500)
                    
                except Exception as render_error:
                    st.warning(f"⚠️ Não foi possível renderizar o diagrama: {render_error}")
                    st.info("💡 O código Mermaid está exibido acima e pode ser copiado para visualização externa.")
            
            # Para conteúdo JSON
            elif doc_content.strip().startswith('{') and doc_content.strip().endswith('}'):
                try:
                    import json
                    json_content = json.loads(doc_content)
                    st.json(json_content)
                except json.JSONDecodeError:
                    st.error("❌ Erro ao decodificar JSON")
                    st.text_area("Conteúdo bruto:", doc_content, height=400)
            
            # Para outros tipos de conteúdo (markdown, texto simples)
            else:
                # Verifica se é Markdown
                if '# ' in doc_content or '## ' in doc_content or '### ' in doc_content:
                    st.markdown(doc_content)
                else:
                    # Texto simples
                    st.text_area("Conteúdo:", doc_content, height=400)
                    
        except Exception as e:
            st.error(f"❌ Erro ao processar documento: {str(e)}")
            st.text_area("Conteúdo bruto:", doc_content, height=200)

def render_feedback_tab():
    """Renderiza a aba de feedback com checklist dos documentos gerados"""
    
    st.header("✅ Checklist de Documentação Técnica")
    
    # Verifica se há documentos gerados
    docs = st.session_state.get('generated_docs', {})
    if not docs:
        st.warning("Nenhum documento gerado para feedback.")
        st.info("Vá para a aba 'Upload & Análise' para gerar documentação primeiro.")
        return

    # Inicializa checklist - por padrão todos marcados
    if 'feedback_checklist' not in st.session_state:
        st.session_state.feedback_checklist = {k: True for k in docs.keys()}
    
    # Botão para marcar/desmarcar todos
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("✅ Marcar Todos"):
            st.session_state.feedback_checklist = {k: True for k in docs.keys()}
            st.rerun()
    with col2:
        if st.button("❌ Desmarcar Todos"):
            st.session_state.feedback_checklist = {k: False for k in docs.keys()}
            st.rerun()

    st.markdown("---")
    
    # Lista de documentos com checkboxes
    st.subheader("📋 Documentos Gerados")
    
    for doc_type, content in docs.items():
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
        
        with col1:
            # Checkbox para aprovação
            checked = st.checkbox(
                "Aprovar", 
                value=st.session_state.feedback_checklist.get(doc_type, True),
                key=f"chk_{doc_type}",
                help="Marque para aprovar este documento",
                label_visibility="collapsed"
            )
            st.session_state.feedback_checklist[doc_type] = checked
            
        with col2:
            # Nome do documento
            status = "✅ Aprovado" if checked else "⏳ Pendente"
            st.write(f"**{doc_type}** - {status}")
            
        with col3:
            # Botão para ver/editar
            if st.button("📖 Ver", key=f"btn_{doc_type}"):
                st.session_state.selected_doc = doc_type

    # Progresso
    approved_count = sum(1 for v in st.session_state.feedback_checklist.values() if v)
    total_count = len(docs)
    progress = approved_count / total_count if total_count > 0 else 0
    
    st.markdown("---")
    st.subheader("📊 Progresso da Aprovação")
    st.progress(progress)
    st.write(f"**{approved_count}/{total_count} documentos aprovados**")
    
    if approved_count == total_count:
        st.success("🎉 Todos os documentos aprovados! Você pode prosseguir para a modernização.")
    else:
        st.info(f"⏳ {total_count - approved_count} documento(s) pendente(s) de aprovação.")

    # Exibe documento selecionado para feedback detalhado
    selected = st.session_state.get('selected_doc')
    if selected and selected in docs:
        st.markdown("---")
        st.subheader(f"📄 {selected}")
        
        # Tabs para visualização e feedback
        tab1, tab2 = st.tabs(["�️ Visualizar", "💬 Feedback"])
        
        with tab1:
            # Verifica se é um diagrama Mermaid
            if "mermaid" in selected.lower() or "```mermaid" in docs[selected]:
                st.subheader("📊 Diagrama de Arquitetura")
                
                # Exibe o diagrama Mermaid renderizado
                mermaid_code = docs[selected]
                
                # Extrai apenas o código Mermaid se estiver em markdown
                if "```mermaid" in mermaid_code:
                    import re
                    mermaid_match = re.search(r'```mermaid\n(.*?)\n```', mermaid_code, re.DOTALL)
                    if mermaid_match:
                        pure_mermaid = mermaid_match.group(1)
                        
                        # Exibe o diagrama usando componente nativo do Streamlit
                        try:
                            import streamlit.components.v1 as components
                            
                            # HTML para renderizar Mermaid
                            mermaid_html = f"""
                            <div id="mermaid-diagram">
                                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                                <script>
                                    mermaid.initialize({{startOnLoad: true}});
                                </script>
                                <div class="mermaid">
                                    {pure_mermaid}
                                </div>
                            </div>
                            """
                            
                            components.html(mermaid_html, height=600)
                            
                        except ImportError:
                            st.info("💡 Para melhor visualização do diagrama, instale: pip install streamlit-mermaid")
                            st.code(pure_mermaid, language="mermaid")
                
                # Mostra também o código fonte completo
                with st.expander("📝 Código Fonte do Diagrama"):
                    st.markdown(mermaid_code)
            else:
                # Exibição normal para outros documentos
                st.markdown(docs[selected])
            
            # Botão para download individual
            st.download_button(
                label=f"💾 Download {selected}",
                data=docs[selected],
                file_name=f"{selected.replace(' ', '_').lower()}.md",
                mime="text/markdown"
            )
            
        with tab2:
            feedback = st.text_area(
                "Forneça feedback sobre este documento (opcional):",
                placeholder="Ex: Falta mais detalhes sobre..., Corrija a seção..., Inclua exemplos de...",
                height=150
            )
            
            if st.button("🔄 Regenerar com Feedback", key=f"regen_{selected}"):
                if feedback.strip():
                    # Regenerar documento com feedback
                    with st.spinner("Regenerando documento..."):
                        try:
                            # Integração com DocumentationGenerator
                            if 'doc_generator' in st.session_state:
                                doc_generator = st.session_state.doc_generator
                                analysis_results = st.session_state.get('analysis_results', {})
                                project_name = analysis_results.get('metadata', {}).get('project_name', 'Projeto')
                                
                                new_content = doc_generator.regenerate_document_with_feedback(
                                    selected, 
                                    docs[selected], 
                                    feedback, 
                                    analysis_results, 
                                    project_name
                                )
                                
                                if new_content and new_content != docs[selected]:
                                    st.session_state.generated_docs[selected] = new_content
                                    st.success(f"Documento '{selected}' regenerado com sucesso!")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ O documento não foi alterado significativamente.")
                            else:
                                st.info("Funcionalidade de regeneração será implementada com o DocumentationGenerator")
                        except Exception as e:
                            st.error(f"Erro ao regenerar: {str(e)}")
                else:
                    st.warning("Forneça um feedback para regenerar o documento.")

def _all_feedback_confirmed():
    """Verifica se todos os documentos estão marcados como confirmados"""
    checklist = st.session_state.get('feedback_checklist', {})
    docs = st.session_state.get('generated_docs', {})
    return checklist and docs and all(checklist.get(doc_type, False) for doc_type in docs.keys())

def render_modernization_tab():
    """Renderiza a aba de modernização focada em backend, com preview e download"""
    
    st.header("🚀 Modernização Backend - Java Spring Boot")
    
    # Verifica se há documentos aprovados
    if not _all_feedback_confirmed():
        st.warning("⚠️ Aprove todos os documentos na aba 'Feedback' antes de prosseguir com a modernização.")
        return
    
    # Informações da documentação aprovada
    docs = st.session_state.get('generated_docs', {})
    if docs:
        st.subheader("📄 Documentação Técnica Aprovada")
        approved_docs = [doc for doc, approved in st.session_state.get('feedback_checklist', {}).items() if approved]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📋 Documentos Aprovados", len(approved_docs))
        with col2:
            st.metric("📊 Total de Documentos", len(docs))
        with col3:
            approval_rate = len(approved_docs) / len(docs) * 100 if docs else 0
            st.metric("✅ Taxa de Aprovação", f"{approval_rate:.0f}%")
        
        # Lista dos documentos aprovados
        with st.expander("📋 Ver Documentos Aprovados"):
            for doc_type in approved_docs:
                st.write(f"✅ **{doc_type}**")

        st.markdown("---")    # Configurações de modernização
    st.subheader("⚙️ Configurações de Modernização")
    
    col1, col2 = st.columns(2)
    with col1:
        java_version = st.selectbox(
            "Versão Java:",
            ["Java 17", "Java 11", "Java 8"],
            index=0
        )
        
        spring_version = st.selectbox(
            "Versão Spring Boot:",
            ["3.2.x", "3.1.x", "2.7.x"],
            index=0
        )
    
    with col2:
        include_tests = st.checkbox("Gerar Testes Unitários", value=True)
        include_integration = st.checkbox("Gerar Testes de Integração", value=True)
        include_docker = st.checkbox("Incluir Dockerfile", value=True)
        include_swagger = st.checkbox("Incluir Swagger/OpenAPI", value=True)

    st.markdown("---")
    
    # Botões de ação
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Iniciar Modernização", type="primary", use_container_width=True):
            _start_modernization({
                'java_version': java_version,
                'spring_version': spring_version,
                'include_tests': include_tests,
                'include_integration': include_integration,
                'include_docker': include_docker,
                'include_swagger': include_swagger
            })
    
    with col2:
        # Botão de download (só aparece se projeto foi gerado)
        modernized_path = st.session_state.get('modernized_project_path')
        if modernized_path and os.path.exists(modernized_path):
            with open(modernized_path, 'rb') as f:
                st.download_button(
                    label="📥 Download Projeto (.zip)",
                    data=f.read(),
                    file_name="projeto_modernizado.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        else:
            st.info("O botão de download aparecerá após a modernização.")

def _estimate_generated_files(analysis):
    """Estima arquivos que serão gerados baseado na análise"""
    # Simulação baseada na análise
    units = analysis.get('units_analysis', {})
    estimated_files = {
        'main': [],
        'test': []
    }
    
    # Arquivos principais baseados nas units
    for unit_name in units.keys():
        class_name = _sanitize_class_name(unit_name)
        estimated_files['main'].extend([
            f"{class_name}Controller.java",
            f"{class_name}Service.java",
            f"{class_name}Repository.java",
            f"{class_name}Entity.java",
            f"{class_name}DTO.java"
        ])
        
        # Arquivos de teste
        estimated_files['test'].extend([
            f"{class_name}ControllerTest.java",
            f"{class_name}ServiceTest.java",
            f"{class_name}RepositoryTest.java"
        ])
    
    # Arquivos de configuração sempre presentes
    estimated_files['main'].extend([
        "Application.java",
        "DatabaseConfig.java",
        "WebConfig.java",
        "SecurityConfig.java",
        "GlobalExceptionHandler.java"
    ])
    
    return estimated_files

def _start_modernization(config):
    """Inicia o processo de modernização"""
    with st.spinner("� Iniciando modernização..."):
        try:
            # Simula processo de modernização
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Passos da modernização
            steps = [
                "Preparando documentação...",
                "Gerando estrutura do projeto...",
                "Criando entities e DTOs...",
                "Implementando controllers...",
                "Criando services...",
                "Configurando repositories...",
                "Gerando testes...",
                "Criando arquivos de configuração...",
                "Empacotando projeto..."
            ]
            
            for i, step in enumerate(steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(steps))
                # Simula tempo de processamento
                import time
                time.sleep(0.5)
            
            # Cria estrutura do projeto modernizado
            temp_dir = tempfile.mkdtemp()
            project_files = _create_modernized_project_structure(temp_dir, config)
            
            # Cria o arquivo ZIP
            zip_path = os.path.join(temp_dir, "projeto_modernizado.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != "projeto_modernizado.zip":
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
            
            # Armazena informações do projeto modernizado
            st.session_state['modernized_project_path'] = zip_path
            st.session_state['project_files'] = project_files
            st.session_state['modernization_completed'] = True
            
            status_text.text("✅ Modernização concluída!")
            st.success("🎉 Projeto Java Spring Boot gerado com sucesso!")
            
            # Agora mostra o preview do projeto gerado
            _show_modernized_project_preview(project_files)
            
            # Mostra resumo
            st.subheader("📊 Resumo da Modernização")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📁 Arquivos Gerados", len(project_files))
            with col2:
                test_files = len([f for f in project_files if 'test' in f.lower() or 'Test' in f])
                st.metric("🧪 Testes Criados", test_files)
            with col3:
                config_files = len([f for f in project_files if 'config' in f.lower() or 'Config' in f])
                st.metric("⚙️ Configurações", config_files)
            
        except Exception as e:
            st.error(f"❌ Erro durante modernização: {str(e)}")
            st.info("Verifique as configurações e tente novamente.")

def start_modernization(config: Dict[str, Any]):
    """Inicia o processo de modernização"""
    try:
        with st.spinner("🔄 Modernizando projeto para Java Spring Boot..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Configura o pipeline
            pipeline_config = st.session_state.get('config', {})
            pipeline = ModernizationPipeline(pipeline_config)
            
            # Carrega dados de análise
            analysis_results = st.session_state.get('analysis_results')
            generated_docs = st.session_state.get('generated_docs')
            
            if analysis_results and generated_docs:
                # Configura dados da análise prévia
                pipeline.set_analysis_data(analysis_results, generated_docs)
                
                # Configura prompt manager se disponível
                if 'analyzer' in st.session_state and hasattr(st.session_state.analyzer, 'prompt_manager'):
                    pipeline.set_prompt_manager(st.session_state.analyzer.prompt_manager)
                
                status_text.text("🔄 Gerando código Java Spring Boot...")
                progress_bar.progress(20)
                
                # Executa modernização sem arquivo ZIP (usa análise prévia)
                def update_progress(step, total, message=""):
                    progress = int((step / total) * 80) + 20
                    progress_bar.progress(progress)
                    status_text.text(f"🔄 Modernizando... ({step}/{total})")
                
                # Executa pipeline
                zip_path = pipeline.run(
                    delphi_project_path=None,  # Usa análise prévia
                    progress_callback=update_progress
                )
                
                if zip_path:
                    progress_bar.progress(100)
                    status_text.text("✅ Modernização concluída!")
                    
                    st.success("🎉 **Modernização Concluída com Sucesso!**")
                    
                    # Oferece download do projeto Java
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download Projeto Java",
                            data=f.read(),
                            file_name=f"projeto_java_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip"
                        )
                    
                    # Mostra estatísticas
                    pipeline_status = pipeline.get_pipeline_status()
                    detailed_report = pipeline.get_detailed_report()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Etapas Concluídas", pipeline_status['current_step'])
                    
                    with col2:
                        st.metric("Código Gerado", "✅" if pipeline_status['code_generated'] else "❌")
                    
                    with col3:
                        st.metric("Projeto Construído", "✅" if pipeline_status['project_built'] else "❌")
                    
                    # Mostra relatório detalhado
                    if detailed_report:
                        with st.expander("📊 Relatório Detalhado"):
                            st.json(detailed_report)
                else:
                    st.error("❌ Falha na modernização. Verifique os logs para mais detalhes.")
            else:
                st.error("❌ Dados de análise não disponíveis.")
                
    except Exception as e:
        logger.error(f"Erro na modernização: {str(e)}")
        st.error(f"❌ Erro na modernização: {str(e)}")


def _show_modernized_project_preview(project_files):
    """Mostra preview do projeto modernizado"""
    st.markdown("---")
    st.subheader("🔍 Preview do Projeto Java Spring Boot Gerado")
    
    # Estrutura do projeto baseada nos arquivos reais
    st.markdown("#### 📁 Estrutura do Projeto")
    
    # Organiza arquivos por categoria
    java_files = [f for f in project_files if f.endswith('.java')]
    config_files = [f for f in project_files if f.endswith('.properties') or f.endswith('.xml')]
    test_files = [f for f in project_files if 'test' in f.lower()]
    doc_files = [f for f in project_files if f.endswith('.md')]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**☕ Código Java:**")
        for file in java_files:
            if 'test' not in file.lower():
                st.write(f"- {file}")
    
    with col2:
        st.markdown("**🧪 Testes:**")
        for file in test_files:
            st.write(f"- {file}")
    
    # Arquivos de configuração
    with st.expander("⚙️ Arquivos de Configuração"):
        for file in config_files:
            st.write(f"- {file}")
    
    # Documentação
    with st.expander("📚 Documentação"):
        for file in doc_files:
            st.write(f"- {file}")
    
    # Fluxo da aplicação
    with st.expander("🔄 Fluxo da Aplicação Gerada"):
        st.markdown("""
        ```
        Cliente HTTP → Controller → Service → Repository → Entity → Database
                     ↓                ↓            ↓           ↓
        JSON Response ← DTO ← Business Logic ← JPA Query ← H2/Database
        ```
        """)
    
    # Tecnologias utilizadas
    with st.expander("🛠️ Tecnologias Implementadas"):
        st.markdown("""
        **Framework:**
        - Spring Boot (Web, Data JPA)
        - Spring MVC (Controllers REST)
        - Hibernate (ORM)
        
        **Banco de Dados:**
        - H2 Database (desenvolvimento)
        - JPA/Hibernate (mapeamento)
        
        **Ferramentas:**
        - Maven (build)
        - Lombok (redução de código)
        - JUnit 5 (testes)
        
        **Padrões Implementados:**
        - Repository Pattern
        - Service Layer
        - DTO Pattern
        - REST API
        """)
    
    # Endpoints disponíveis
    with st.expander("🌐 Endpoints REST Gerados"):
        analysis = st.session_state.get('analysis_results', {})
        units = analysis.get('units_analysis', {})
        
        if units:
            st.markdown("**APIs REST disponíveis:**")
            for unit_name in units.keys():
                class_name = _sanitize_class_name(unit_name)
                base_url = f"/api/{class_name.lower()}"
                st.markdown(f"""
                **{class_name}:**
                - `GET {base_url}` - Lista todos
                - `GET {base_url}/{{id}}` - Busca por ID
                - `POST {base_url}` - Cria nova
                - `PUT {base_url}/{{id}}` - Atualiza
                - `DELETE {base_url}/{{id}}` - Remove
                """)
        else:
            st.info("Endpoints serão baseados na análise do projeto Delphi")
