"""
Interface principal do JUNIM usando Streamlit
"""

import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from core.pipeline import ModernizationPipeline
from utils.file_handler import FileHandler
from ui.legacy_analysis_interface import render_legacy_analysis_interface

# Carrega variáveis de ambiente
load_dotenv()

class JUNIMInterface:
    """Classe responsável pela interface do usuário do JUNIM"""
    
    def __init__(self):
        """Inicializa a interface"""
        self.file_handler = FileHandler()
        self.pipeline = None
        
    def run(self):
        """Executa a interface principal"""
        # Aplica CSS customizado
        add_custom_css()
        
        self._render_header()
        self._render_sidebar()
        self._render_main_content()
    
    def _render_header(self):
        """Renderiza o cabeçalho da aplicação"""
        st.title("🚀 JUNIM - Java Unified Interoperability Migration")
        st.markdown("""
        **Modernizador automático de sistemas Delphi para Java Spring Boot**
        
        Esta aplicação utiliza IA generativa para converter projetos Delphi legados em aplicações 
        Java Spring modernas, mantendo a lógica de negócio e estrutura dos dados.
        """)
        
        st.divider()
    
    def _render_sidebar(self):
        """Renderiza a barra lateral com configurações"""
        with st.sidebar:
            st.header("⚙️ Configurações")
            
            # Configuração da API Groq
            st.subheader("API Groq")
            groq_api_key = st.text_input(
                "Chave da API Groq",
                type="password",
                value=os.getenv("GROQ_API_KEY", ""),
                help="Sua chave de API da Groq para acesso aos modelos LLM"
            )
            
            groq_model = st.selectbox(
                "Modelo Groq",
                ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
                index=0,
                help="Modelo da Groq a ser utilizado"
            )
            
            # Configuração do Ollama (fallback)
            st.subheader("Ollama (Fallback)")
            ollama_url = st.text_input(
                "URL do Ollama",
                value=os.getenv("OLLAMA_URL", "http://localhost:11434"),
                help="URL da instância local do Ollama"
            )
            
            ollama_model = st.text_input(
                "Modelo Ollama",
                value=os.getenv("OLLAMA_DEFAULT_MODEL", "codellama:34b"),
                help="Modelo local do Ollama para fallback"
            )
            
            # Armazena configurações na sessão
            st.session_state.config = {
                "groq_api_key": groq_api_key,
                "groq_model": groq_model,
                "ollama_url": ollama_url,
                "ollama_model": ollama_model
            }
            
            st.divider()
            
            # Informações do sistema
            st.subheader("ℹ️ Informações")
            st.info("""
            **Como usar:**
            1. Configure suas credenciais
            2. Faça upload do projeto Delphi (.zip)
            3. Clique em 'Modernizar'
            4. Baixe o projeto Java Spring
            """)
    
    def _render_main_content(self):
        """Renderiza o conteúdo principal da interface"""
        
        # Navegação por abas
        tab1, tab2, tab3 = st.tabs([
            "🔍 Análise de Projeto Legado", 
            "🔄 Modernização Completa", 
            "📊 Dashboard"
        ])
        
        with tab1:
            # Nova funcionalidade de análise detalhada
            render_legacy_analysis_interface()
        
        with tab2:
            # Funcionalidade original de modernização
            self._render_modernization_interface()
        
        with tab3:
            # Dashboard de estatísticas
            self._render_dashboard()
    
    def _render_modernization_interface(self):
        """Renderiza a interface de modernização completa"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("📁 Upload do Projeto Delphi")
            
            uploaded_file = st.file_uploader(
                "Selecione o arquivo .zip do projeto Delphi",
                type=["zip"],
                help="Faça upload de um arquivo .zip contendo todo o projeto Delphi (.pas, .dfm, etc.)"
            )
            
            if uploaded_file is not None:
                st.success(f"✅ Arquivo carregado: {uploaded_file.name} ({uploaded_file.size} bytes)")
                
                # Botão para iniciar modernização
                if st.button("🔄 Modernizar Projeto", type="primary", use_container_width=True):
                    self._run_modernization(uploaded_file)
        
        with col2:
            st.header("📊 Status")
            
            # Container para status em tempo real
            status_container = st.container()
            
            # Histórico de projetos (placeholder)
            with st.expander("📈 Estatísticas"):
                st.metric("Projetos Modernizados", "0", "0")
                st.metric("Taxa de Sucesso", "0%", "0%")
                st.metric("Tempo Médio", "0 min", "0")
    
    def _render_dashboard(self):
        """Renderiza dashboard de estatísticas e informações"""
        st.header("📊 Dashboard do JUNIM")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🔍 Análises Realizadas",
                value=len(getattr(st.session_state, 'analysis_history', [])),
                delta=None
            )
        
        with col2:
            st.metric(
                label="🔄 Modernizações",
                value=len(getattr(st.session_state, 'modernization_history', [])),
                delta=None
            )
        
        with col3:
            st.metric(
                label="📄 Documentos Gerados",
                value=len(getattr(st.session_state, 'generated_docs', {})),
                delta=None
            )
        
        with col4:
            st.metric(
                label="⚙️ Configurações",
                value="OK" if hasattr(st.session_state, 'config') else "Pendente",
                delta=None
            )
        
        # Informações sobre o sistema
        st.subheader("ℹ️ Sobre o JUNIM")
        st.markdown("""
        ### Java Unified Interoperability Migration
        
        **JUNIM** é uma ferramenta avançada para modernização de sistemas legados Delphi, 
        oferecendo análise detalhada e migração automática para Java Spring Boot.
        
        #### 🎯 Principais Funcionalidades:
        
        1. **📋 Análise Detalhada**: Extração de requisitos, funcionalidades e fluxos
        2. **📝 Documentação Automática**: Geração de documentação técnica completa
        3. **🔗 Mapeamento de Correlações**: Delphi → Java Spring equivalentes
        4. **🔄 Modernização Completa**: Conversão automática do código
        5. **📊 Métricas de Qualidade**: Análise de complexidade e manutenibilidade
        
        #### 🛠️ Tecnologias Utilizadas:
        - **Python** com Streamlit para interface
        - **Groq API** para processamento IA de alto desempenho
        - **Ollama** para modelos locais como fallback
        - **Regex avançado** para parsing de código Delphi
        - **Templates Spring Boot** para geração de código
        
        #### 📈 Benefícios:
        - ⚡ **Rapidez**: Análise em minutos vs. semanas manuais
        - 🎯 **Precisão**: Preservação da lógica de negócio
        - 📚 **Documentação**: Criação automática de documentação técnica
        - 🔄 **Iterativo**: Análise antes da modernização
        - 🛡️ **Confiável**: Múltiplas validações e verificações
        """)
        
        # Configurações atuais
        if hasattr(st.session_state, 'config'):
            with st.expander("⚙️ Configurações Atuais"):
                config = st.session_state.config
                st.json({
                    "groq_model": config.get("groq_model", "N/A"),
                    "ollama_model": config.get("ollama_model", "N/A"),
                    "ollama_url": config.get("ollama_url", "N/A"),
                    "groq_configured": bool(config.get("groq_api_key", "")),
                })
        
        # Links úteis
        st.subheader("🔗 Links Úteis")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📚 Documentação**
            - [Spring Boot Guide](https://spring.io/guides)
            - [Java Migration Best Practices](https://docs.oracle.com/javase/8/docs/)
            """)
        
        with col2:
            st.markdown("""
            **🛠️ Ferramentas**
            - [Groq Console](https://console.groq.com/)
            - [Ollama Documentation](https://ollama.ai/docs)
            """)
        
        with col3:
            st.markdown("""
            **🎓 Recursos**
            - [Delphi to Java Migration](https://example.com)
            - [Legacy System Modernization](https://example.com)
            """)
    
    
    def _run_modernization(self, uploaded_file):
        """Executa o pipeline de modernização"""
        try:
            # Inicializa o pipeline com as configurações
            self.pipeline = ModernizationPipeline(st.session_state.config)
            
            # Container para progresso
            progress_container = st.container()
            
            with progress_container:
                st.header("🔄 Modernização em Andamento")
                
                # Barra de progresso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Callback para atualizar progresso
                def update_progress(step, total_steps, message):
                    progress = step / total_steps
                    progress_bar.progress(progress)
                    status_text.text(f"Passo {step}/{total_steps}: {message}")
                
                # Cria arquivo temporário para o upload
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_path = tmp_file.name
                
                try:
                    # Executa o pipeline
                    result_path = self.pipeline.run(
                        delphi_project_path=temp_path,
                        progress_callback=update_progress
                    )
                    
                    # Sucesso - oferece download
                    progress_bar.progress(1.0)
                    status_text.text("✅ Modernização concluída com sucesso!")
                    
                    st.success("🎉 Projeto modernizado com sucesso!")
                    
                    # Botão de download
                    with open(result_path, 'rb') as file:
                        st.download_button(
                            label="📥 Baixar Projeto Java Spring",
                            data=file.read(),
                            file_name="modernized_project.zip",
                            mime="application/zip",
                            type="primary",
                            use_container_width=True
                        )
                    
                    # Limpa arquivo temporário
                    os.unlink(temp_path)
                    os.unlink(result_path)
                    
                except Exception as e:
                    st.error(f"❌ Erro durante a modernização: {str(e)}")
                    status_text.text(f"❌ Erro: {str(e)}")
                    
                    # Limpa arquivo temporário
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    
        except Exception as e:
            st.error(f"❌ Erro ao inicializar pipeline: {str(e)}")
    
    def _render_footer(self):
        """Renderiza o rodapé da aplicação"""
        st.divider()
        st.markdown("""
        ---
        **JUNIM v1.0** - Desenvolvido como parte do TCC de Sistemas de Informação  
        *Powered by IA Generativa (Groq/Ollama) + RAG*
        """)

# Adiciona CSS customizado
def add_custom_css():
    """Adiciona estilos CSS customizados"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2d5aa0);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    
    .status-box {
        background: #f0f2f6;
        border-left: 5px solid #1f4e79;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Não aplica CSS na inicialização - será aplicado na execução da interface
