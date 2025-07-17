"""
Interface principal do JUNIM usando Streamlit
"""

import streamlit as st
import os
import tempfile
import logging
from datetime import datetime
from dotenv import load_dotenv

# Imports absolutos para evitar problemas de importação
import sys
from pathlib import Path

# Adiciona diretório pai ao path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from core.pipeline import ModernizationPipeline
from utils.file_handler import FileHandler

# Import direto da interface de análise
try:
    from ui.legacy_analysis_interface import render_legacy_analysis_interface
except ImportError:
    # Se falhar, criamos uma função placeholder
    def render_legacy_analysis_interface():
        st.error("Módulo de análise não disponível. Verifique as dependências.")

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        st.header("🔄 Modernização para Java Spring Boot")
        
        # Verifica se há projeto pré-carregado da análise
        if self._has_analyzed_project():
            self._render_pre_loaded_project()
        else:
            self._render_upload_interface()
    
    def _has_analyzed_project(self):
        """Verifica se há um projeto analisado disponível"""
        return (hasattr(st.session_state, 'analysis_results') and 
                st.session_state.analysis_results is not None and
                hasattr(st.session_state, 'generated_docs') and 
                st.session_state.generated_docs)
    
    def _render_pre_loaded_project(self):
        """Renderiza interface para projeto pré-carregado da análise"""
        st.success("🎯 **Projeto pré-carregado da análise!**")
        
        analysis = st.session_state.analysis_results
        docs = st.session_state.generated_docs
        
        # Informações do projeto analisado
        col1, col2, col3 = st.columns(3)
        
        with col1:
            project_name = analysis.get('metadata', {}).get('project_name', 'Projeto')
            st.metric("Projeto", project_name)
            st.info("Análise de projeto carregada e pronta para modernização")
        
        with col2:
            units_count = len(analysis.get('units_analysis', {}))
            st.metric("Units Analisadas", units_count)
        
        with col3:
            docs_count = len(docs)
            st.metric("Documentos Gerados", docs_count)
        
        st.markdown("---")
        
        # Configurações de modernização
        self._render_modernization_settings()
        
        # Botão de modernização com documentação
        if st.button("🚀 Modernizar com Documentação", type="primary", use_container_width=True):
            self._run_documentation_enhanced_modernization()
        
        st.markdown("---")
        
        # Opção para carregar outro projeto
        with st.expander("🔄 Carregar Projeto Diferente"):
            self._render_upload_interface(show_expander=False)
    
    def _render_upload_interface(self, show_expander=True):
        """Renderiza interface de upload de projeto"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📁 Upload do Projeto Delphi")
            
            uploaded_file = st.file_uploader(
                "Selecione o arquivo .zip do projeto Delphi",
                type=["zip"],
                help="Faça upload de um arquivo .zip contendo todo o projeto Delphi (.pas, .dfm, etc.)"
            )
            
            if uploaded_file is not None:
                st.success(f"✅ Arquivo carregado: {uploaded_file.name} ({uploaded_file.size} bytes)")
                
                # Configurações de modernização
                self._render_modernization_settings()
                
                # Botão para iniciar modernização
                if st.button("🔄 Modernizar Projeto", type="primary", use_container_width=True):
                    self._run_modernization(uploaded_file)
        
        with col2:
            st.subheader("📊 Status")
            
            # Container para status em tempo real
            status_container = st.container()
            
            # Histórico de projetos (placeholder)
            if show_expander:
                with st.expander("📈 Estatísticas"):
                    st.metric("Projetos Modernizados", "0", "0")
            else:
                st.metric("Projetos Modernizados", "0", "0")
    
    def _render_modernization_settings(self):
        """Renderiza configurações da modernização"""
        st.subheader("⚙️ Configurações da Modernização")
        
        # Verificação de prompts
        with st.expander("🤖 Status dos Prompts Personalizados"):
            try:
                from prompts.specialized_prompts import PromptManager, prompt_manager
                st.success("✅ **Seus prompts personalizados estão ativos!**")
                st.info("""
                **Prompts sendo utilizados:**
                - 🧠 Análise de funcionalidades
                - 🔄 Modernização de código
                - 📝 Geração de documentação
                - 🧪 Criação de testes
                """)
                
                # Mostra alguns detalhes dos prompts
                st.markdown("**Exemplo de prompt personalizado carregado:**")
                analysis_prompt = prompt_manager.get_analysis_prompt()
                st.code(analysis_prompt[:200] + "..." if len(analysis_prompt) > 200 else analysis_prompt, language="text")
                
            except ImportError as e:
                st.warning("⚠️ **Prompts padrão em uso**")
                st.error(f"Erro ao carregar prompts personalizados: {str(e)}")
                st.info("Para usar seus prompts personalizados, verifique se o arquivo `prompts/specialized_prompts.py` está configurado corretamente.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            modernization_type = st.selectbox(
                "Tipo de Modernização:",
                ["Conversão Completa", "Apenas Entidades", "Apenas APIs", "Apenas Serviços"],
                help="Escolha o escopo da modernização"
            )
            
            include_tests = st.checkbox(
                "Gerar Testes Unitários",
                value=True,
                help="Inclui testes JUnit para o código gerado"
            )
        
        with col2:
            use_specialized_prompts = st.checkbox(
                "Usar Prompts Especializados",
                value=True,
                help="Utiliza prompts otimizados para cada tipo de conversão"
            )
            
            generate_documentation = st.checkbox(
                "Gerar Documentação",
                value=True,
                help="Inclui documentação técnica do código Java"
            )
        
        # Armazena configurações na sessão
        st.session_state.modernization_config = {
            'type': modernization_type,
            'include_tests': include_tests,
            'use_specialized_prompts': use_specialized_prompts,
            'generate_documentation': generate_documentation
        }
    
    def _run_documentation_enhanced_modernization(self):
        """Executa modernização, gera e salva projeto Java completo (código, docs, testes) em 'generated_project', com preview detalhado."""
        import shutil
        with st.spinner("🔄 Gerando e salvando projeto Java modernizado..."):
            try:
                config = getattr(st.session_state, 'modernization_config', {})
                pipeline_config = st.session_state.config.copy()
                pipeline_config.update(config)
                
                # Debug da configuração
                logger.info(f"Configuração do pipeline: {pipeline_config}")
                logger.info(f"API Groq: {'Configurada' if pipeline_config.get('groq_api_key') else 'Não configurada'}")
                
                self.pipeline = ModernizationPipeline(pipeline_config)
                
                # FORÇA o uso dos prompts especializados
                prompt_manager_loaded = False
                try:
                    from prompts.specialized_prompts import prompt_manager
                    self.pipeline.set_prompt_manager(prompt_manager)
                    prompt_manager_loaded = True
                    logger.info("✅ Prompts especializados FORÇADOS no pipeline")
                    st.info("🤖 **Usando seus prompts personalizados para modernização!**")
                except ImportError as e:
                    logger.error(f"❌ Falha ao carregar prompts especializados: {str(e)}")
                    try:
                        from prompts.simple_loader import simple_prompt_loader as prompt_manager
                        self.pipeline.set_prompt_manager(prompt_manager)
                        st.warning("⚠️ **Usando prompts padrão como fallback**")
                    except ImportError:
                        st.error("❌ **Nenhum sistema de prompts disponível!**")
                        return
                
                # Validação adicional
                if not hasattr(self.pipeline, 'prompt_manager') or self.pipeline.prompt_manager is None:
                    st.error("❌ **Erro crítico: Pipeline sem prompts configurados!**")
                    return
                self.pipeline.set_analysis_data(
                    st.session_state.analysis_results,
                    st.session_state.generated_docs
                )
                progress_bar = st.progress(0)
                status_text = st.empty()
                def update_progress(step, total_steps, message):
                    progress = step / total_steps
                    progress_bar.progress(progress)
                    status_text.text(f"Passo {step}/{total_steps}: {message}")
                # Executa pipeline real e salva projeto em 'generated_project'
                # Executa modernização usando dados de análise prévia
                status_text.text("📋 Preparando modernização...")
                progress_bar.progress(10)
                java_project_path = self.pipeline.run(
                    progress_callback=lambda s, t, m: update_progress(s, t, m)
                )
                # Copia tudo para 'generated_project'
                target_dir = os.path.abspath(os.path.join(os.getcwd(), 'generated_project'))
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                shutil.copytree(java_project_path, target_dir)
                # Copia documentação gerada
                docs_dir = os.path.abspath(os.path.join(os.getcwd(), 'generated_docs'))
                if os.path.exists(docs_dir):
                    shutil.copytree(docs_dir, os.path.join(target_dir, 'documentacao'))
                status_text.text("✅ Projeto Java modernizado salvo em 'generated_project'!")
                progress_bar.progress(100)
                st.success(f"🎉 Projeto Java modernizado salvo em: {target_dir}")
                # Preview detalhado
                enhanced_prompt = prompt_manager.get_documentation_enhanced_prompt(
                    analysis_results=st.session_state.analysis_results,
                    generated_docs=st.session_state.generated_docs
                )
                self._show_modernization_preview(enhanced_prompt)
                # Salva no histórico
                if 'modernization_history' not in st.session_state:
                    st.session_state.modernization_history = []
                st.session_state.modernization_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'documentation_enhanced',
                    'config': config,
                    'project_name': st.session_state.analysis_results.get('metadata', {}).get('project_name', 'Unknown')
                })
            except Exception as e:
                st.error(f"❌ Erro durante modernização: {str(e)}")
                logger.error(f"Erro na modernização com documentação: {str(e)}")
    
    def _show_modernization_preview(self, enhanced_prompt: str):
        """Mostra preview do que seria gerado na modernização, incluindo testes automatizados."""
        st.subheader("👀 Preview da Modernização")

        # Tabs para diferentes aspectos
        preview_tab1, preview_tab2, preview_tab3, preview_tab4 = st.tabs([
            "📝 Prompt Gerado",
            "🏗️ Estrutura Planejada",
            "🧪 Testes Automatizados",
            "📊 Métricas"
        ])

        with preview_tab1:
            st.markdown("**Prompt enriquecido com documentação:**")
            st.text_area(
                "Prompt que seria usado para gerar o código Java:",
                value=enhanced_prompt[:2000] + "..." if len(enhanced_prompt) > 2000 else enhanced_prompt,
                height=300,
                disabled=True
            )

        with preview_tab2:
            st.markdown("**Estrutura Java Spring que seria gerada:**")
            st.code("""
src/main/java/com/projeto/
├── config/
│   ├── DatabaseConfig.java
│   └── WebConfig.java
├── controller/
│   ├── CustomerController.java
│   └── ProductController.java
├── service/
│   ├── CustomerService.java
│   └── ProductService.java
├── repository/
│   ├── CustomerRepository.java
│   └── ProductRepository.java
├── entity/
│   ├── Customer.java
│   └── Product.java
├── dto/
│   ├── CustomerDTO.java
│   └── ProductDTO.java
└── exception/
    ├── GlobalExceptionHandler.java
    └── BusinessException.java
            """, language="text")

        with preview_tab3:
            st.markdown("**Exemplo de Testes Automatizados Gerados:**")
            # Exemplo didático baseado no novo prompt de testes
            st.code(
                """
@WebMvcTest(CustomerController.class)
class CustomerControllerTest {
    // Teste: Usuário cadastra cliente com dados válidos
    @Test
    void deveCadastrarClienteComSucesso() throws Exception {
        // ... implementação do teste
    }

    // Teste: Busca cliente inexistente retorna 404
    @Test
    void deveRetornar404ParaClienteInexistente() throws Exception {
        // ... implementação do teste
    }
}

@ExtendWith(MockitoExtension.class)
class CustomerServiceTest {
    // Teste: Regra de negócio - nome obrigatório
    @Test
    void deveLancarExcecaoSeNomeVazio() {
        // ... implementação do teste
    }
}

@DataJpaTest
class CustomerRepositoryTest {
    // Teste: Consulta clientes ativos
    @Test
    void deveBuscarClientesAtivos() {
        // ... implementação do teste
    }
}
                """,
                language="java"
            )

        with preview_tab4:
            analysis = st.session_state.analysis_results
            col1, col2, col3 = st.columns(3)
            with col1:
                units_count = len(analysis.get('units_analysis', {}))
                estimated_classes = units_count * 2  # Estimativa
                st.metric("Classes Java Estimadas", estimated_classes)
            with col2:
                total_lines = sum(unit.get('lines_count', 0) for unit in analysis.get('units_analysis', {}).values())
                estimated_java_lines = int(total_lines * 1.3)  # Estimativa
                st.metric("Linhas Java Estimadas", f"{estimated_java_lines:,}")
            with col3:
                config = getattr(st.session_state, 'modernization_config', {})
                features = sum([
                    config.get('include_tests', False),
                    config.get('generate_documentation', False),
                    config.get('use_specialized_prompts', False)
                ])
                st.metric("Recursos Habilitados", features)
    
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
            # Validação do arquivo
            if uploaded_file is None:
                st.error("❌ Arquivo não encontrado. Por favor, faça o upload novamente.")
                return
            
            # Verifica se o arquivo tem os métodos necessários
            if not hasattr(uploaded_file, 'getvalue') and not hasattr(uploaded_file, 'getbuffer'):
                st.error("❌ Arquivo inválido. Por favor, faça o upload de um arquivo ZIP válido.")
                return
            
            # Carrega configurações da modernização
            config = getattr(st.session_state, 'modernization_config', {})
            
            # Inicializa o pipeline com as configurações
            pipeline_config = st.session_state.config.copy()
            pipeline_config.update(config)
            self.pipeline = ModernizationPipeline(pipeline_config)
            
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
                    try:
                        # Tenta usar getvalue() primeiro, depois getbuffer()
                        if hasattr(uploaded_file, 'getvalue'):
                            file_content = uploaded_file.getvalue()
                        elif hasattr(uploaded_file, 'getbuffer'):
                            uploaded_file.seek(0)  # Garante que está no início
                            file_content = uploaded_file.getbuffer()
                        else:
                            raise Exception("Método de leitura do arquivo não suportado")
                        
                        if len(file_content) == 0:
                            st.error("❌ Arquivo está vazio. Por favor, selecione um arquivo válido.")
                            return
                        
                        tmp_file.write(file_content)
                        temp_path = tmp_file.name
                        
                        # Valida se o arquivo foi criado corretamente
                        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                            st.error("❌ Erro ao criar arquivo temporário.")
                            return
                        
                    except Exception as file_error:
                        st.error(f"❌ Erro ao processar arquivo: {str(file_error)}")
                        logger.error(f"Erro ao processar arquivo no pipeline: {str(file_error)}")
                        return
                
                try:
                    # FORÇA o uso de prompts especializados
                    if config.get('use_specialized_prompts', True):
                        try:
                            from prompts.specialized_prompts import prompt_manager
                            update_progress(1, 8, "✅ Carregando SEUS prompts especializados...")
                            self.pipeline.set_prompt_manager(prompt_manager)
                            logger.info("✅ Prompts especializados configurados com sucesso")
                        except ImportError as e:
                            logger.warning(f"⚠️ Falha ao importar prompts especializados: {str(e)}")
                            try:
                                from prompts.simple_loader import simple_prompt_loader
                                update_progress(1, 8, "⚠️ Carregando prompts padrão...")
                                self.pipeline.set_prompt_manager(simple_prompt_loader)
                            except ImportError:
                                st.error("❌ Nenhum sistema de prompts disponível!")
                                return
                    else:
                        st.info("ℹ️ Prompts especializados desabilitados pelo usuário")
                    
                    # Validação crítica
                    if not hasattr(self.pipeline, 'prompt_manager') or self.pipeline.prompt_manager is None:
                        st.error("❌ **ERRO: Pipeline sem prompts! Interrompendo processo.**")
                        return
                    
                    # Se há análise prévia, carrega os dados e não passa caminho do projeto
                    if self._has_analyzed_project():
                        update_progress(2, 8, "Carregando dados de análise prévia...")
                        self.pipeline.set_analysis_data(
                            st.session_state.analysis_results,
                            st.session_state.generated_docs
                        )
                        
                        # Executa o pipeline sem passar o caminho do projeto
                        logger.info("Executando pipeline com dados de análise prévia")
                        result_path = self.pipeline.run(
                            delphi_project_path=None,  # Não passa caminho para usar análise prévia
                            progress_callback=lambda s, t, m: update_progress(s + 3, 8, m)
                        )
                    else:
                        # Valida o arquivo antes de passar para o pipeline
                        if not temp_path or not os.path.exists(temp_path):
                            st.error("❌ Arquivo temporário não encontrado.")
                            return
                        
                        logger.info(f"Executando pipeline com arquivo: {temp_path}")
                        
                        # Executa o pipeline com o arquivo
                        result_path = self.pipeline.run(
                            delphi_project_path=temp_path,
                            progress_callback=lambda s, t, m: update_progress(s + 3, 8, m)
                        )
                    
                    # Sucesso - oferece download
                    progress_bar.progress(1.0)
                    status_text.text("✅ Modernização concluída com sucesso!")
                    
                    st.success("🎉 Projeto modernizado com sucesso!")
                    
                    # Mostra estatísticas da modernização
                    self._show_modernization_stats()
                    
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

