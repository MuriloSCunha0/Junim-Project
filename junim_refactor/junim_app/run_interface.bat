@echo off
echo 🚀 JUNIM - Interface Simplificada
echo ================================

echo 📋 Verificando dependencias...
python check_setup.py

echo.
echo 🌐 Iniciando interface Streamlit...
echo ✅ Acesse: http://localhost:8501
echo ❌ Para parar: Ctrl+C

streamlit run ui/interface.py --server.port 8501
