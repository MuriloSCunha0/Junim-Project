@echo off
rem Script para executar o JUNIM no Windows

echo 🚀 Iniciando JUNIM - Java Unified Interoperability Migration
echo.

rem Verifica se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

rem Verifica se pip está instalado
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado. Por favor, instale pip primeiro.
    pause
    exit /b 1
)

rem Teste básico antes de instalar dependências
echo 🔍 Testando componentes básicos...
python test_basic.py

rem Instala dependências se necessário
echo.
echo 📦 Instalando/atualizando dependências...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ✅ Dependências instaladas com sucesso!
    echo.
    
    rem Executa aplicação Streamlit
    echo 🌐 Iniciando interface web...
    echo.
    echo ==========================================
    echo   Acesse: http://localhost:8501
    echo   Para parar: Ctrl+C no terminal
    echo ==========================================
    echo.
    
    streamlit run main.py
) else (
    echo ❌ Erro ao instalar dependências. Verifique o arquivo requirements.txt
    echo.
    echo Tentando executar mesmo assim...
    streamlit run main.py
)
