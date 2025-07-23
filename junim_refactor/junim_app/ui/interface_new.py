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

from core.legacy_project_analyzer import LegacyProjectAnalyzer
from core.documentation_generator import DocumentationGenerator
from utils.file_handler import FileHandler

# Configuração
load_dotenv()


class JUNIMInterface:
    """Interface Simplificada do JUNIM - Sistema de Documentação Delphi->Java"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        try:
            self.analyzer = LegacyProjectAnalyzer()
            self.doc_generator = DocumentationGenerator()
        except Exception as e:
            st.error(f"Erro ao inicializar componentes: {e}")
            self.analyzer = None
            self.doc_generator = None
        
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
                if not self.analyzer or not self.doc_generator:
                    st.error("❌ Componentes não inicializados. Verifique as dependências.")
                    return
                
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
                        project_name = analysis_result.get('metadata', {}).get('project_name', 'Projeto Delphi')
                        doc_paths = self.doc_generator.generate_complete_documentation(
                            analysis_result, 
                            project_name
                        )
                        
                        # Carrega conteúdo dos documentos
                        docs = {}
                        for doc_type, file_path in doc_paths.items():
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    docs[doc_type] = f.read()
                            except Exception as e:
                                st.warning(f"Erro ao carregar {doc_type}: {e}")
                                docs[doc_type] = f"Erro ao carregar documento: {e}"
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
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
        
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


# Função para executar a aplicação
def main():
    """Função principal para executar a aplicação"""
    if 'interface' not in st.session_state:
        st.session_state.interface = JUNIMInterface()
    
    st.session_state.interface.run()


if __name__ == "__main__":
    main()
