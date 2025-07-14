#!/bin/bash

# Script para executar o JUNIM
echo "🚀 Iniciando JUNIM - Java Unified Interoperability Migration"
echo

# Verifica se Python está instalado
if ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado. Por favor, instale Python 3.8+ primeiro."
    exit 1
fi

# Verifica se pip está instalado
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado. Por favor, instale pip primeiro."
    exit 1
fi

# Instala dependências se necessário
echo "📦 Verificando dependências..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências verificadas com sucesso!"
    echo
    
    # Executa aplicação Streamlit
    echo "🌐 Iniciando interface web..."
    echo "Acesse: http://localhost:8501"
    echo
    
    streamlit run main.py
else
    echo "❌ Erro ao instalar dependências. Verifique o arquivo requirements.txt"
    exit 1
fi
