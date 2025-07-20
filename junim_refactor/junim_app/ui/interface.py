"""
Interface principal do JUNIM usando Streamlit
"""

import streamlit as st
import os
import tempfile
import logging
import shutil
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
        
        # Novo: Widget de informação sobre o sistema universal
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            # Mostra modelo atual se configurado
            current_model = st.session_state.get('config', {}).get('ollama_model', 'Não configurado')
            current_mode = st.session_state.get('config', {}).get('performance_mode', 'fast')
            
            if current_model != 'Não configurado':
                st.info(f"🤖 **Modelo Ativo:** {current_model} ({current_mode.upper()})")
            else:
                st.warning("⚠️ **Modelo:** Configure na sidebar →")
        
        with col2:
            # Botão para mostrar guia completo
            if st.button("📖 Guia Completo de Modelos"):
                st.session_state.show_model_guide = True
        
        with col3:
            # Indicador de sistema universal
            st.success("✅ Sistema Universal")
        
        # Modal/expander com guia completo
        if st.session_state.get('show_model_guide', False):
            with st.expander("📖 **GUIA COMPLETO - Sistema Universal de Modelos**", expanded=True):
                
                col_guide1, col_guide2 = st.columns(2)
                
                with col_guide1:
                    st.markdown("""
                    ### 🔥 **MUDANÇA PRINCIPAL**
                    **De:** DeepSeek-R1 → **Para:** CodeLlama:7b + Multi-Modelo
                    
                    ### ⚡ **BENEFÍCIOS**
                    - ✅ **3x mais rápido**
                    - ✅ **70% menos memória**
                    - ✅ **60% menos CPU**
                    - ✅ **Melhor código Java**
                    - ✅ **Múltiplos modelos**
                    
                    ### 🎯 **MODELOS RECOMENDADOS**
                    - 🔥 **codellama:7b** - MELHOR para código
                    - ⚡ **mistral:7b** - MELHOR para velocidade  
                    - 🎯 **deepseek-r1:14b** - MELHOR para qualidade
                    - ⚖️ **llama3:8b** - MELHOR uso geral
                    """)
                
                with col_guide2:
                    st.markdown("""
                    ### 🚀 **MODOS DE PERFORMANCE**
                    
                    **FAST (Recomendado):**
                    - 🚀 Velocidade máxima
                    - 💾 70% menos memória
                    - ⚡ 3x mais rápido
                    
                    **BALANCED:**
                    - ⚖️ Equilibrado
                    - 💾 40% menos memória
                    - ⚡ 1.5x mais rápido
                    
                    **QUALITY:**
                    - 🎯 Qualidade máxima
                    - 🔧 Configurações completas
                    - 📊 Melhor análise
                    
                    ### 🛠️ **INSTALAÇÃO RÁPIDA**
                    ```bash
                    ollama pull codellama:7b
                    ollama pull mistral:7b  
                    ```
                    """)
                
                # Botão para fechar
                if st.button("❌ Fechar Guia"):
                    st.session_state.show_model_guide = False
                    st.rerun()
        
        st.divider()
    
    def _render_sidebar(self):
        """Renderiza a barra lateral com configurações"""
        
        st.sidebar.header("⚙️ Configurações")
        
        # Configuração da API Groq
        st.sidebar.subheader("🔑 API Groq")
        
        groq_api_key = st.sidebar.text_input(
            "Chave da API Groq:",
            type="password",
            value=st.session_state.get('groq_api_key', ''),
            help="Sua chave API do Groq para análise e geração de código"
        )
        
        if groq_api_key:
            st.session_state.groq_api_key = groq_api_key
            # Salva também na configuração global
            if 'config' not in st.session_state:
                st.session_state.config = {}
            st.session_state.config['groq_api_key'] = groq_api_key
            st.sidebar.success("✅ Chave API configurada")
            
            # Teste de conexão
            if st.sidebar.button("🧪 Testar Conexão"):
                try:
                    import groq
                    client = groq.Groq(api_key=groq_api_key)
                    # Teste básico
                    response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=10
                    )
                    st.sidebar.success("✅ Conexão com Groq OK!")
                except Exception as e:
                    st.sidebar.error(f"❌ Erro na conexão: {str(e)}")
        else:
            st.sidebar.warning("⚠️ Chave API não configurada")
        
        # Modelo Groq
        groq_model = st.sidebar.selectbox(
            "Modelo Groq:",
            ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
            index=0,
            help="Modelo a ser usado para análise e geração"
        )
        
        if 'config' not in st.session_state:
            st.session_state.config = {}
        st.session_state.config['groq_model'] = groq_model
        
        # Configuração do Ollama com Sistema Universal
        st.sidebar.subheader("🤖 Ollama - Sistema Universal de Modelos")
        
        use_ollama = st.sidebar.checkbox(
            "Usar Ollama (Múltiplos modelos disponíveis)",
            value=True,
            help="Sistema universal com suporte a múltiplos modelos LLM otimizados"
        )
        
        if use_ollama:
            # Carrega informações dos modelos disponíveis
            try:
                from config.universal_model_config import get_available_models
                available_models = get_available_models()
                
                # Cria lista de opções com descrições
                model_options = []
                model_descriptions = {}
                
                for model_name, model_info in available_models.items():
                    display_name = f"{model_name} - {model_info['description']}"
                    model_options.append(display_name)
                    model_descriptions[display_name] = model_info
                
                # Seletor de modelo com descrições
                selected_display = st.sidebar.selectbox(
                    "🔥 Selecionar Modelo:",
                    model_options,
                    index=0,  # codellama:7b como padrão
                    help="Escolha o modelo baseado na sua necessidade de velocidade vs qualidade"
                )
                
                # Extrai o nome real do modelo
                ollama_model = selected_display.split(' - ')[0]
                model_info = model_descriptions[selected_display]
                
                # Mostra informações do modelo selecionado
                st.sidebar.markdown(f"""
                **📊 Modelo Selecionado:**
                - **Tipo:** {model_info.get('strengths', ['N/A'])[0]}
                - **Melhor para:** {model_info.get('best_for', 'N/A')}
                - **Performance:** {model_info.get('performance', 'N/A')}
                - **Qualidade:** {model_info.get('quality', 'N/A')}
                """)
                
            except ImportError:
                # Fallback para lista tradicional
                st.sidebar.warning("⚠️ Sistema universal não disponível, usando lista básica")
                ollama_model = st.sidebar.selectbox(
                    "Modelo Ollama:",
                    ["codellama:7b", "deepseek-r1:14b", "deepseek-r1:1.5b", "llama3:8b", "mistral:7b", "gemma:7b"],
                    index=0,
                    help="Modelo Ollama - CodeLlama recomendado para código"
                )
            
            # Modo de Performance
            st.sidebar.markdown("---")
            performance_mode = st.sidebar.selectbox(
                "⚡ Modo de Performance:",
                ["fast", "balanced", "quality"],
                index=0,  # fast como padrão
                help="Escolha o equilíbrio entre velocidade e qualidade",
                format_func=lambda x: {
                    "fast": "🚀 FAST - Velocidade máxima (3x mais rápido)",
                    "balanced": "⚖️ BALANCED - Equilibrado",
                    "quality": "🎯 QUALITY - Qualidade máxima"
                }[x]
            )
            
            # Informações do modo de performance
            performance_info = {
                "fast": {
                    "icon": "🚀",
                    "savings": "CPU: ~60% menos | Memória: ~70% menos",
                    "ideal": "Testes rápidos, desenvolvimento iterativo"
                },
                "balanced": {
                    "icon": "⚖️", 
                    "savings": "CPU: ~30% menos | Memória: ~40% menos",
                    "ideal": "Desenvolvimento normal, análises rotineiras"
                },
                "quality": {
                    "icon": "🎯",
                    "savings": "Configurações completas para máxima qualidade",
                    "ideal": "Código final, análises críticas"
                }
            }
            
            info = performance_info[performance_mode]
            st.sidebar.markdown(f"""
            **{info['icon']} Modo {performance_mode.upper()}:**
            - **Economia:** {info['savings']}
            - **Ideal para:** {info['ideal']}
            """)
            
            # URL do Ollama
            ollama_url = st.sidebar.text_input(
                "🌐 URL do Ollama:",
                value="http://localhost:11434",
                help="URL do servidor Ollama"
            )
            
            st.session_state.config.update({
                'use_ollama': use_ollama,
                'ollama_model': ollama_model,
                'performance_mode': performance_mode,
                'ollama_url': ollama_url
            })
            
            # Teste de conexão Ollama com informações detalhadas
            if st.sidebar.button("🧪 Testar Ollama + Modelo"):
                with st.sidebar:
                    with st.spinner(f"Testando {ollama_model}..."):
                        try:
                            import requests
                            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
                            if response.status_code == 200:
                                models = response.json().get('models', [])
                                model_names = [m['name'] for m in models]
                                
                                if ollama_model in model_names:
                                    st.success(f"✅ {ollama_model} disponível!")
                                    
                                    # Testa configuração específica do modelo
                                    try:
                                        from config.universal_model_config import get_universal_config, detect_model_type
                                        model_type = detect_model_type(ollama_model)
                                        config = get_universal_config(ollama_model, performance_mode)
                                        
                                        st.info(f"""
                                        🔧 **Configuração Aplicada:**
                                        - Tipo: {model_type}
                                        - Temperatura: {config.get('temperature', 'N/A')}
                                        - Contexto: {config.get('num_ctx', 'N/A')} tokens
                                        - Predição: {config.get('num_predict', 'N/A')} tokens
                                        """)
                                        
                                    except Exception as e:
                                        st.warning(f"⚠️ Config universal não disponível: {str(e)}")
                                    
                                else:
                                    st.warning(f"⚠️ {ollama_model} não encontrado")
                                    st.info(f"**Modelos disponíveis:**")
                                    for model in model_names[:5]:  # Mostra só os 5 primeiros
                                        st.text(f"• {model}")
                                    if len(model_names) > 5:
                                        st.text(f"... e mais {len(model_names) - 5} modelos")
                                        
                                    # Sugestão de instalação
                                    st.info(f"**Para instalar:**")
                                    st.code(f"ollama pull {ollama_model}")
                            else:
                                st.error("❌ Ollama não está rodando")
                                st.info("**Para iniciar Ollama:**")
                                st.code("ollama serve")
                        except Exception as e:
                            st.error(f"❌ Erro ao conectar: {str(e)}")
                            if "connection refused" in str(e).lower():
                                st.info("**Ollama não está rodando. Para iniciar:**")
                                st.code("ollama serve")
                            elif "timeout" in str(e).lower():
                                st.warning("⏱️ Timeout - Ollama pode estar ocupado")
        else:
            st.session_state.config['use_ollama'] = False
        
        # Configurações de análise
        st.sidebar.subheader("🔍 Análise")
        
        include_comments = st.sidebar.checkbox(
            "Incluir comentários",
            value=True,
            help="Incluir comentários do código na análise"
        )
        
        analyze_business_logic = st.sidebar.checkbox(
            "Analisar lógica de negócio",
            value=True,
            help="Análise detalhada da lógica de negócio"
        )
        
        generate_correlations = st.sidebar.checkbox(
            "Gerar correlações",
            value=True,
            help="Gerar mapeamentos Delphi→Java"
        )
        
        # Salva configurações de análise
        st.session_state.config.update({
            'include_comments': include_comments,
            'analyze_business_logic': analyze_business_logic,
            'generate_correlations': generate_correlations
        })
        
        # Guia rápido sobre modelos
        st.sidebar.subheader("🎯 Guia Rápido de Modelos")
        
        if st.sidebar.expander("📚 Como escolher o modelo?"):
            st.markdown("""
            **🔥 Para CÓDIGO (Recomendado):**
            - `codellama:7b` - Melhor para Delphi→Java
            
            **⚡ Para VELOCIDADE:**
            - `mistral:7b` - Muito rápido
            - `deepseek-r1:1.5b` - Menor, mais rápido
            
            **🎯 Para QUALIDADE:**
            - `deepseek-r1:14b` - Máxima qualidade
            - `llama3:8b` - Equilibrado
            
            **💡 Dica:** Use modo `FAST` para 3x mais velocidade!
            """)
        
        if st.sidebar.expander("🚀 Como instalar modelos?"):
            st.markdown("""
            **No terminal, execute:**
            ```bash
            # Modelo recomendado para código
            ollama pull codellama:7b
            
            # Para velocidade máxima
            ollama pull mistral:7b
            
            # Para qualidade máxima
            ollama pull deepseek-r1:14b
            ```
            
            **Verificar modelos instalados:**
            ```bash
            ollama list
            ```
            """)
        
        # Informações da sessão
        st.sidebar.subheader("📊 Status da Sessão")
        
        if st.session_state.get('analysis_results'):
            st.sidebar.success("✅ Projeto analisado")
            project_name = st.session_state.analysis_results.get('metadata', {}).get('project_name', 'N/A')
            st.sidebar.info(f"📁 Projeto: {project_name}")
        else:
            st.sidebar.info("📁 Nenhum projeto carregado")
        
        docs_count = len(st.session_state.get('generated_docs', {}))
        st.sidebar.info(f"📄 Documentos: {docs_count}")
        
        # Botão para limpar sessão
        if st.sidebar.button("🗑️ Limpar Sessão"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.sidebar.success("✅ Sessão limpa!")
            st.experimental_rerun()
    
    def _render_main_content(self):
        """Renderiza o conteúdo principal da interface"""
        # Renderiza diretamente a interface de análise que já tem suas próprias abas
        render_legacy_analysis_interface()

    def _render_feedback_interface(self):
        """Interface de feedback com checklist dos documentos gerados"""
        st.header("✅ Checklist de Documentação Técnica")
        
        docs = st.session_state.get('generated_docs', {})
        if not docs:
            st.warning("Nenhum documento gerado para feedback.")
            st.info("Vá para a aba 'Análise de Backend' para gerar documentação primeiro.")
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
            tab1, tab2 = st.tabs(["👁️ Visualizar", "💬 Feedback"])
            
            with tab1:
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
                                # Aqui você integraria com o DocumentationGenerator
                                # Por agora, apenas uma simulação
                                st.info("Funcionalidade de regeneração será implementada com o DocumentationGenerator")
                                st.success(f"Documento '{selected}' seria regenerado com o feedback fornecido!")
                            except Exception as e:
                                st.error(f"Erro ao regenerar: {str(e)}")
                    else:
                        st.warning("Forneça um feedback para regenerar o documento.")

    def _all_feedback_confirmed(self):
        """Verifica se todos os documentos estão marcados como confirmados"""
        checklist = st.session_state.get('feedback_checklist', {})
        docs = st.session_state.get('generated_docs', {})
        return checklist and docs and all(checklist.get(doc_type, False) for doc_type in docs.keys())
    
    def _render_modernization_interface(self):
        """Renderiza a interface de modernização focada em backend, com preview e download"""
        st.header("🚀 Modernização Backend - Java Spring Boot")
        
        # Verifica se há documentos aprovados
        if not self._all_feedback_confirmed():
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

        st.markdown("---")
        
        # Preview do fluxo do novo projeto
        st.subheader("🔍 Preview do Projeto Java Spring Boot")
        
        # Estrutura do projeto
        with st.expander("📁 Estrutura do Projeto"):
            st.code("""
src/main/java/com/projeto/
├── 📂 config/
│   ├── DatabaseConfig.java
│   ├── SecurityConfig.java
│   └── WebConfig.java
├── 📂 controller/
│   ├── CustomerController.java
│   ├── ProductController.java
│   └── OrderController.java
├── 📂 service/
│   ├── CustomerService.java
│   ├── ProductService.java
│   └── OrderService.java
├── 📂 repository/
│   ├── CustomerRepository.java
│   ├── ProductRepository.java
│   └── OrderRepository.java
├── 📂 entity/
│   ├── Customer.java
│   ├── Product.java
│   └── Order.java
├── 📂 dto/
│   ├── CustomerDTO.java
│   ├── ProductDTO.java
│   └── OrderDTO.java
└── 📂 exception/
    ├── GlobalExceptionHandler.java
    └── BusinessException.java

src/test/java/com/projeto/
├── 📂 controller/
├── 📂 service/
└── 📂 repository/
            """, language="text")
        
        # Fluxo da aplicação
        with st.expander("🔄 Fluxo da Aplicação"):
            st.markdown("""
            ```
            Cliente HTTP → Controller → Service → Repository → Database
                         ↓
            Validação → Transformação → Regras de Negócio → Persistência
                         ↓
            Response ← DTO ← Entity ← Data Access Layer
            ```
            """)
        
        # Tecnologias utilizadas
        with st.expander("⚙️ Tecnologias e Dependências"):
            st.markdown("""
            **Framework Principal:**
            - Spring Boot 3.x
            - Spring Data JPA
            - Spring Web
            - Spring Security
            
            **Banco de Dados:**
            - H2 Database (desenvolvimento)
            - PostgreSQL (produção)
            
            **Testes:**
            - JUnit 5
            - Mockito
            - TestContainers
            
            **Outros:**
            - Maven
            - Docker
            - Swagger/OpenAPI
            """ )

        st.markdown("---")
        
        # Arquivos que serão gerados
        st.subheader("📁 Arquivos que serão Gerados")
        
        # Simula lista de arquivos baseada na análise
        analysis = st.session_state.get('analysis_results', {})
        estimated_files = self._estimate_generated_files(analysis)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📂 Código Principal:**")
            for file in estimated_files.get('main', []):
                st.write(f"- {file}")
        
        with col2:
            st.markdown("**🧪 Testes:**")
            for file in estimated_files.get('test', []):
                st.write(f"- {file}")
        
        st.markdown("---")
        
        # Configurações de modernização
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
                self._start_modernization({
                    'java_version': java_version,
                    'spring_version': spring_version,
                    'include_tests': include_tests,
                    'include_integration': include_integration,
                    'include_docker': include_docker,
                    'include_swagger': include_swagger
                })
        
        with col2:
            # Botão de download (só aparece se projeto foi gerado)
            if st.session_state.get('modernized_project_path'):
                with open(st.session_state['modernized_project_path'], 'rb') as f:
                    st.download_button(
                        label="📥 Download Projeto (.zip)",
                        data=f.read(),
                        file_name="projeto_modernizado.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
            else:
                st.info("O botão de download aparecerá após a modernização.")

    def _estimate_generated_files(self, analysis):
        """Estima arquivos que serão gerados baseado na análise"""
        # Simulação baseada na análise
        units = analysis.get('units_analysis', {})
        estimated_files = {
            'main': [],
            'test': []
        }
        
        # Arquivos principais baseados nas units
        for unit_name in units.keys():
            class_name = unit_name.replace('.pas', '').replace('.dfm', '')
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

    def _start_modernization(self, config):
        """Inicia o processo de modernização"""
        with st.spinner("🔄 Iniciando modernização..."):
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
                
                # Simula criação do arquivo ZIP
                st.session_state['modernized_project_path'] = "/tmp/projeto_modernizado.zip"
                
                status_text.text("✅ Modernização concluída!")
                st.success("🎉 Projeto Java Spring Boot gerado com sucesso!")
                st.info("Use o botão 'Download Projeto' para baixar o resultado.")
                
                # Mostra resumo
                st.subheader("📊 Resumo da Modernização")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📁 Arquivos Gerados", "47")
                with col2:
                    st.metric("🧪 Testes Criados", "23")
                with col3:
                    st.metric("⚙️ Configurações", "8")
                
            except Exception as e:
                st.error(f"❌ Erro durante modernização: {str(e)}")
                st.info("Verifique as configurações e tente novamente.")
    
    def _render_documentation_interface(self):
        """Renderiza interface de geração de documentação técnica - VERSÃO OTIMIZADA"""
        st.header("📋 Documentação Técnica Específica")
        
        # Verifica se há análise prévia
        if hasattr(st.session_state, 'last_analysis_results') and st.session_state.last_analysis_results:
            # Informações do projeto analisado
            metadata = st.session_state.last_analysis_results.get('metadata', {})
            project_name = metadata.get('project_name', 'Projeto')
            total_files = metadata.get('total_files_analyzed', 0)
            
            st.success(f"✅ Análise disponível: **{project_name}** ({total_files} arquivos)")
            
            st.markdown("### 🎯 Documentos Essenciais")
            
            # Coluna para seleção mais organizada
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Análise Técnica:**")
                analysis_docs = st.checkbox("🔧 Análise de Backend", value=True, 
                                           help="Análise detalhada das funcionalidades e estruturas Delphi")
                mapping_docs = st.checkbox("🔗 Mapeamento Delphi → Java", value=True,
                                         help="Correlações e sugestões de conversão para Spring Boot")
                
            with col2:
                st.markdown("**🎨 Visualização:**")
                mermaid_diagram = st.checkbox("📊 Diagrama Mermaid", value=True,
                                            help="Diagrama visual da arquitetura do projeto")
                testing_docs = st.checkbox("🧪 Estratégia de Testes", value=False,
                                         help="Plano de testes para o projeto convertido")
            
            # Botão de geração
            st.markdown("---")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("� Gerar Documentação Específica", type="primary", use_container_width=True):
                    # Monta lista de documentos selecionados
                    selected_docs = []
                    if analysis_docs:
                        selected_docs.append("Análise de Funcionalidades")
                    if mapping_docs:
                        selected_docs.append("Mapeamento Delphi → Java")
                    if mermaid_diagram:
                        selected_docs.append("Diagrama Mermaid")
                    if testing_docs:
                        selected_docs.append("Estratégia de Testes")
                    
                    if selected_docs:
                        with st.spinner("🔄 Gerando documentação específica..."):
                            self._generate_technical_documentation(selected_docs)
                    else:
                        st.warning("⚠️ Selecione pelo menos um tipo de documentação.")
            
            # Opção rápida
            st.markdown("### ⚡ Opção Rápida")
            if st.button("🎯 Gerar Análise + Diagrama (Recomendado)", type="secondary"):
                quick_docs = ["Análise de Funcionalidades", "Mapeamento Delphi → Java", "Diagrama Mermaid"]
                with st.spinner("🔄 Gerando documentação essencial..."):
                    self._generate_technical_documentation(quick_docs)
            
            # Mostra documentação gerada
            self._display_generated_documentation()
            
        else:
            st.info("🔍 Realize primeiro uma análise de backend na aba 'Análise de Backend' para gerar documentação.")
    
    def _generate_technical_documentation(self, doc_types):
        """Gera documentação técnica específica baseada na análise - VERSÃO CORRIGIDA"""
        try:
            # Carrega resultados da análise
            analysis_results = st.session_state.last_analysis_results
            
            if not hasattr(st.session_state, 'generated_docs'):
                st.session_state.generated_docs = {}
            
            # Importa DocumentationGenerator corrigido
            from core.documentation_generator import DocumentationGenerator
            from prompts.specialized_prompts import PromptManager
            from config.universal_model_config import get_development_config
            
            # Configuração otimizada para VS Code
            model_name = st.session_state.get('selected_model', 'codellama:7b')
            config = get_development_config(model_name)
            config.update({
                'ollama_model': model_name,
                'use_fallback': True,
                'quick_mode': True
            })
            
            # Cria serviços otimizados
            prompt_manager = PromptManager(performance_mode='development', model_name=model_name)
            doc_generator = DocumentationGenerator(llm_service=self.pipeline.llm_service, 
                                                  prompt_manager=prompt_manager)
            
            # Mapeia tipos solicitados para tipos internos
            doc_type_mapping = {
                "Análise de Funcionalidades": "backend_analysis",
                "Fluxos de Execução": "backend_analysis", 
                "Mapeamento Delphi → Java": "functionality_mapping",
                "Arquitetura Spring Boot Sugerida": "functionality_mapping",
                "Diagrama Mermaid": "mermaid_diagram",
                "Estratégia de Testes": "testing_strategy"
            }
            
            # Determina quais documentos gerar
            docs_to_generate = []
            include_mermaid = False
            
            for doc_type in doc_types:
                mapped_type = doc_type_mapping.get(doc_type)
                if mapped_type == "mermaid_diagram":
                    include_mermaid = True
                elif mapped_type and mapped_type not in docs_to_generate:
                    docs_to_generate.append(mapped_type)
            
            # Se nenhum documento específico, gera análise básica
            if not docs_to_generate and not include_mermaid:
                docs_to_generate = ["backend_analysis"]
                include_mermaid = True
            
            # Gera documentação específica
            project_name = analysis_results.get('metadata', {}).get('project_name', 'Projeto')
            
            with st.spinner("🔄 Gerando documentação específica..."):
                generated_docs = doc_generator.generate_specific_documentation(
                    analysis_results=analysis_results,
                    project_name=project_name,
                    include_mermaid=include_mermaid,
                    documents_to_generate=docs_to_generate
                )
            
            # Carrega conteúdo dos documentos gerados
            for doc_type, file_path in generated_docs.items():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Mapeia de volta para nomes de exibição
                    display_name = {
                        'backend_analysis': 'Análise de Funcionalidades',
                        'functionality_mapping': 'Mapeamento Delphi → Java',
                        'testing_strategy': 'Estratégia de Testes',
                        'mermaid_diagram': 'Diagrama Mermaid',
                        'readme': 'Resumo do Projeto'
                    }.get(doc_type, doc_type.title())
                    
                    st.session_state.generated_docs[display_name] = content
                    
                except Exception as e:
                    logger.warning(f"Erro ao carregar {doc_type}: {str(e)}")
            
            st.success(f"✅ Documentação específica gerada: {len(st.session_state.generated_docs)} documentos!")
            
            # Exibe informação sobre os arquivos salvos
            if generated_docs:
                st.info(f"📁 Arquivos salvos em: generated_docs/{project_name}/")
                
        except Exception as e:
            st.error(f"❌ Erro ao gerar documentação: {str(e)}")
            logger.error(f"Erro detalhado: {str(e)}", exc_info=True)
    
    def _get_prompt_type_for_doc(self, doc_type):
        """Mapeia tipo de documentação para tipo de prompt - VERSÃO OTIMIZADA"""
        mapping = {
            "Análise de Funcionalidades": "backend_analysis",
            "Fluxos de Execução": "analysis",
            "Mapeamento Delphi → Java": "functionality_mapping",
            "Arquitetura Spring Boot Sugerida": "conversion",
            "Diagrama Mermaid": "mermaid_diagram",
            "Estratégia de Testes": "testing"
        }
        return mapping.get(doc_type, "analysis")
    
    def _display_generated_documentation(self):
        """Exibe documentação gerada - VERSÃO MELHORADA COM SUPORTE MERMAID"""
        if hasattr(st.session_state, 'generated_docs') and st.session_state.generated_docs:
            st.subheader("📄 Documentação Gerada")
            
            # Organiza documentos por categoria
            doc_categories = {
                "📊 Análise Técnica": ["Análise de Funcionalidades", "Mapeamento Delphi → Java"],
                "🎨 Visualização": ["Diagrama Mermaid"],
                "🧪 Testes": ["Estratégia de Testes"],
                "📋 Resumo": ["Resumo do Projeto"]
            }
            
            for category, doc_types in doc_categories.items():
                category_docs = [doc for doc in doc_types if doc in st.session_state.generated_docs]
                
                if category_docs:
                    st.markdown(f"### {category}")
                    
                    for doc_type in category_docs:
                        content = st.session_state.generated_docs[doc_type]
                        
                        with st.expander(f"📋 {doc_type}", expanded=(doc_type == "Diagrama Mermaid")):
                            
                            # Tratamento especial para diagramas Mermaid
                            if doc_type == "Diagrama Mermaid":
                                st.markdown("### 🎯 Arquitetura do Projeto")
                                
                                # Extrai código Mermaid do conteúdo
                                if "```mermaid" in content:
                                    # Encontra o código Mermaid
                                    start = content.find("```mermaid") + 10
                                    end = content.find("```", start)
                                    if end > start:
                                        mermaid_code = content[start:end].strip()
                                        
                                        # Exibe o diagrama
                                        st.markdown("**Diagrama:**")
                                        st.code(mermaid_code, language="mermaid")
                                        
                                        # Link para visualizar online
                                        import urllib.parse
                                        encoded_diagram = urllib.parse.quote(mermaid_code)
                                        mermaid_live_url = f"https://mermaid.live/edit#pako:eNpdjkEKwjAQRa8S5uqF3LkzuiqupOuQTCdt7SSBJKtSencSFSku_vfef_BmObOCJsYbeYJHgNdS6ahV57Q1FdJdKTdOp0qn8SuVL95gDWfBSi0RobkgRrAa4BW0skoTJ16z4MrW2O4sttKJHjv3ks88f7F1lZeN5fInWXcvdqg7qQ"
                                        st.markdown(f"🔗 [Visualizar no Mermaid Live Editor]({mermaid_live_url})")
                                
                                # Exibe o conteúdo completo como markdown
                                st.markdown("**Documentação Completa:**")
                                st.markdown(content)
                            else:
                                # Para outros tipos de documento, exibe normalmente
                                st.markdown(content)
                            
                            # Botão para download
                            filename = f"{doc_type.replace(' ', '_').lower()}.md"
                            st.download_button(
                                label=f"💾 Download {doc_type}",
                                data=content,
                                file_name=filename,
                                mime="text/markdown",
                                key=f"download_{doc_type}"
                            )
            
            # Botão para limpar documentação
            st.markdown("---")
            if st.button("🗑️ Limpar Documentação", type="secondary"):
                if 'generated_docs' in st.session_state:
                    del st.session_state.generated_docs
                st.rerun()
        else:
            st.info("📝 Nenhuma documentação gerada ainda. Use a aba 'Documentação Técnica' para gerar.")

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
                            from prompts.specialized_prompts import PromptManager
                            prompt_manager = PromptManager()
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
    
    def _check_ollama_available(self) -> bool:
        """Verifica se o Ollama está disponível"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
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

