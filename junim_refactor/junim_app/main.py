"""
JUNIM - Java Unified Interoperability Migration
Aplicação Streamlit para modernização de sistemas Delphi para Java Spring
"""

import streamlit as st

# Configura página ANTES de qualquer outro comando Streamlit
st.set_page_config(
    page_title="JUNIM - Modernizador Delphi → Java Spring",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
import os

# Adiciona o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.interface import JUNIMInterface

def main():
    """Função principal da aplicação Streamlit"""
    # Inicializa e executa a interface
    app = JUNIMInterface()
    app.run()

if __name__ == "__main__":
    main()
