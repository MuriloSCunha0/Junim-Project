"""
Script de inicialização para verificar dependências do JUNIM
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Verifica se todas as dependências estão disponíveis"""
    print("🔍 Verificando dependências do JUNIM...")
    
    # Adiciona o diretório ao path
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir))
    
    missing_deps = []
    available_deps = []
    
    # Testa imports básicos
    try:
        from core.legacy_project_analyzer import LegacyProjectAnalyzer
        available_deps.append("✅ LegacyProjectAnalyzer")
    except Exception as e:
        missing_deps.append(f"❌ LegacyProjectAnalyzer: {e}")
    
    try:
        from core.documentation_generator import DocumentationGenerator
        available_deps.append("✅ DocumentationGenerator")
    except Exception as e:
        missing_deps.append(f"❌ DocumentationGenerator: {e}")
    
    try:
        from utils.file_handler import FileHandler
        available_deps.append("✅ FileHandler")
    except Exception as e:
        missing_deps.append(f"❌ FileHandler: {e}")
    
    try:
        from prompts.specialized_prompts import PromptManager
        available_deps.append("✅ PromptManager")
    except Exception as e:
        missing_deps.append(f"❌ PromptManager: {e}")
    
    # Exibe resultados
    print("\n📦 Dependências Disponíveis:")
    for dep in available_deps:
        print(f"  {dep}")
    
    if missing_deps:
        print("\n⚠️ Dependências com Problemas:")
        for dep in missing_deps:
            print(f"  {dep}")
    
    # Testa inicialização dos componentes principais
    print("\n🚀 Testando inicialização dos componentes...")
    
    try:
        from core.legacy_project_analyzer import LegacyProjectAnalyzer
        analyzer = LegacyProjectAnalyzer()
        print("✅ LegacyProjectAnalyzer inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar LegacyProjectAnalyzer: {e}")
    
    try:
        from core.documentation_generator import DocumentationGenerator
        doc_gen = DocumentationGenerator()
        print("✅ DocumentationGenerator inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar DocumentationGenerator: {e}")
    
    print("\n🎯 Interface Simplificada - Status:")
    print("  📁 Upload/Análise: Pronto")
    print("  📄 Documentos: Pronto") 
    print("  ✅ Feedback: Pronto")
    print("  ☕ Modernização Java: Em desenvolvimento")
    
    print("\n🚀 Para executar a interface:")
    print("  streamlit run ui/interface.py")
    
    return len(missing_deps) == 0

if __name__ == "__main__":
    success = check_dependencies()
    if success:
        print("\n🎉 Todas as dependências estão funcionando!")
    else:
        print("\n⚠️ Alguns componentes precisam de atenção.")
