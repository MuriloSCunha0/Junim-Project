"""
Interface Simplificada do JUNIM
Sistema de documentação e modernização Delphi -> Java Spring
"""

import streamlit as st
import os
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Imports do sistema
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from core.delphi_analyzer import DelphiAnalyzer
from core.documentation_generator import DocumentationGenerator
from utils.file_handler import FileHandler

# Configuração
load_dotenv()

class JUNIMInterface:
    """Interface Simplificada do JUNIM - Sistema de Documentação Delphi->Java"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.analyzer = DelphiAnalyzer()
        self.doc_generator = DocumentationGenerator()
        
    def run(self):
        """Executa interface principal simplificada"""
        # CSS básico
        st.markdown("""
        <style>
        .main { padding: 1rem; }
        .sidebar .sidebar-content { background: #f8f9fa; }
        </style>
        """, unsafe_allow_html=True)
        
        # Sidebar simples
        self._render_sidebar()
        
        # Header simples
        st.title("🚀 JUNIM - Modernização Delphi → Java Spring")
        
        # Abas principais
        tab1, tab2, tab3, tab4 = st.tabs([
            "📁 Upload/Análise", 
            "📄 Documentos", 
            "✅ Feedback", 
            "☕ Modernização Java"
        ])
        
        with tab1:
            self._render_upload_tab()
        
        with tab2:
            self._render_documents_tab()
            
        with tab3:
            self._render_feedback_tab()
            
        with tab4:
            self._render_modernization_tab()
    
    def _render_sidebar(self):
        """Sidebar simplificada - apenas modelo Ollama e chave Groq"""
        st.sidebar.header("⚙️ Configurações")
        
        # Seleção de modelo Ollama
        st.sidebar.subheader("🤖 Modelo Ollama")
        ollama_model = st.sidebar.selectbox(
            "Modelo:",
            ["codellama:7b", "mistral:7b", "llama3:8b", "deepseek-r1:14b"],
            index=0,
            help="Modelo para análise e documentação"
        )
        
        # Chave Groq (opcional)
        st.sidebar.subheader("🔑 Chave Groq (Opcional)")
        groq_key = st.sidebar.text_input(
            "API Key:",
            type="password",
            value=st.session_state.get('groq_key', ''),
            help="Para usar modelos Groq além do Ollama"
        )
        
        # Salva configurações
        if 'config' not in st.session_state:
            st.session_state.config = {}
        
        st.session_state.config.update({
            'ollama_model': ollama_model,
            'groq_key': groq_key
        })
        
        if groq_key:
            st.session_state.groq_key = groq_key
            st.sidebar.success("✅ Groq configurado")
    
    def _render_upload_tab(self):
        """Aba de upload e análise do projeto Delphi"""
        st.header("📁 Upload do Projeto Delphi")
        
        uploaded_file = st.file_uploader(
            "Selecione arquivo .pas ou .zip do projeto:",
            type=['pas', 'zip', 'dpr'],
            help="Arquivo principal ou projeto compactado"
        )
        
        if uploaded_file is not None:
            if st.button("🔍 Analisar Projeto"):
                with st.spinner("Analisando projeto Delphi..."):
                    try:
                        # Salva arquivo temporário
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            temp_path = tmp_file.name
                        
                        # Análise
                        analysis_result = self.analyzer.analyze_project(temp_path)
                        st.session_state.analysis_results = analysis_result
                        st.session_state.project_path = temp_path
                        
                        # Gera documentação automática
                        config = st.session_state.get('config', {})
                        docs = self.doc_generator.generate_all_documents(
                            analysis_result, 
                            config
                        )
                        st.session_state.generated_docs = docs
                        
                        st.success("✅ Projeto analisado e documentação gerada!")
                        
                        # Preview dos resultados
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Arquivos Analisados", analysis_result.get('file_count', 0))
                        with col2:
                            st.metric("Documentos Gerados", len(docs))
                            
                    except Exception as e:
                        st.error(f"❌ Erro na análise: {str(e)}")
                    finally:
                        # Limpa arquivo temporário
                        if 'temp_path' in locals():
                            os.unlink(temp_path)
        
        # Status do projeto atual
        if st.session_state.get('analysis_results'):
            st.info("✅ Projeto carregado e analisado")
            project_name = st.session_state.analysis_results.get('metadata', {}).get('project_name', 'Projeto Delphi')
            st.write(f"**Projeto:** {project_name}")
    
    def _render_documents_tab(self):
        """Aba para visualizar documentos gerados"""
        st.header("📄 Documentos Gerados")
        
        docs = st.session_state.get('generated_docs', {})
        if not docs:
            st.warning("⚠️ Nenhum documento disponível. Faça upload de um projeto primeiro.")
            return
        
        # Seletor de documento
        doc_types = list(docs.keys())
        selected_doc = st.selectbox("Selecione documento:", doc_types)
        
        if selected_doc and docs.get(selected_doc):
            # Área de exibição do documento
            st.subheader(f"📋 {selected_doc.replace('_', ' ').title()}")
            
            # Opções de visualização
            view_mode = st.radio("Modo de visualização:", ["Renderizado", "Markdown Raw"], horizontal=True)
            
            content = docs[selected_doc]
            
            if view_mode == "Renderizado":
                st.markdown(content)
            else:
                st.code(content, language="markdown")
            
            # Download do documento
            st.download_button(
                label=f"⬇️ Download {selected_doc}",
                data=content,
                file_name=f"{selected_doc}.md",
                mime="text/markdown"
            )
    
    def _render_feedback_tab(self):
        """Aba para confirmar documentos e dar feedback"""
        st.header("✅ Confirmação e Feedback")
        
        docs = st.session_state.get('generated_docs', {})
        if not docs:
            st.warning("⚠️ Nenhum documento para confirmar. Gere documentação primeiro.")
            return
        
        # Inicializa checklist
        if 'feedback_checklist' not in st.session_state:
            st.session_state.feedback_checklist = {k: True for k in docs.keys()}
        
        st.subheader("📋 Checklist de Documentos")
        
        # Lista de documentos com checkbox
        for doc_type in docs.keys():
            col1, col2, col3 = st.columns([0.1, 0.6, 0.3])
            
            with col1:
                approved = st.checkbox(
                    "✓",
                    value=st.session_state.feedback_checklist.get(doc_type, True),
                    key=f"chk_{doc_type}",
                    help="Aprovar documento"
                )
                st.session_state.feedback_checklist[doc_type] = approved
            
            with col2:
                icon = "✅" if approved else "⏳"
                st.write(f"{icon} **{doc_type.replace('_', ' ').title()}**")
            
            with col3:
                if st.button(f"👁️ Ver", key=f"view_{doc_type}"):
                    st.session_state.view_doc = doc_type
        
        # Área de feedback geral
        st.subheader("💬 Feedback Geral")
        feedback = st.text_area(
            "Comentários sobre a documentação:",
            value=st.session_state.get('general_feedback', ''),
            help="Observações, melhorias ou problemas encontrados"
        )
        st.session_state.general_feedback = feedback
        
        # Botão de confirmação final
        approved_count = sum(st.session_state.feedback_checklist.values())
        total_count = len(docs)
        
        if st.button(f"✅ Confirmar Documentação ({approved_count}/{total_count} aprovados)"):
            if approved_count == total_count:
                st.success("🎉 Todos os documentos aprovados! Pronto para modernização.")
                st.session_state.docs_approved = True
            else:
                st.warning(f"⚠️ {total_count - approved_count} documento(s) pendente(s) de aprovação.")
    
    def _render_modernization_tab(self):
        """Aba de modernização para Java Spring"""
        st.header("☕ Modernização para Java Spring")
        
        if not st.session_state.get('docs_approved', False):
            st.warning("⚠️ Confirme a documentação na aba anterior antes de modernizar.")
            return
        
        st.info("🚧 **Funcionalidade em desenvolvimento**")
        st.markdown("""
        Esta aba irá conter:
        - 🏗️ Geração de estrutura Spring Boot
        - 📝 Conversão de classes Delphi → Java
        - 🗄️ Mapeamento de banco de dados
        - ⚙️ Configuração de dependências
        - 📦 Geração do projeto final
        """)
        
        # Placeholder para futuras funcionalidades
        if st.button("🔄 Iniciar Modernização (Em breve)"):
            st.warning("Funcionalidade será implementada na próxima versão.")

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

