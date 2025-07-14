"""
Script simples para testar se a aplicação está funcionando
"""

import sys
import os

# Adiciona o path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Testa importações básicas"""
    try:
        print("🔍 Testando importações básicas...")
        
        # Testa importação de módulos sem Streamlit
        from core.delphi_parser import DelphiParser
        print("✅ DelphiParser importado")
        
        from core.rag_builder import RAGBuilder
        print("✅ RAGBuilder importado")
        
        from utils.file_handler import FileHandler
        print("✅ FileHandler importado")
        
        from core.llm_service import LLMService
        print("✅ LLMService importado")
        
        from core.java_builder import JavaBuilder
        print("✅ JavaBuilder importado")
        
        print("\n✅ Todas as importações básicas funcionaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_knowledge_base():
    """Testa se a base de conhecimento está acessível"""
    try:
        print("\n📚 Testando base de conhecimento...")
        
        from core.rag_builder import RAGBuilder
        rag = RAGBuilder()
        summary = rag.get_knowledge_base_summary()
        
        print(f"Status: {summary['status']}")
        print(f"Seções: {summary['total_sections']}")
        
        if summary['status'] == 'loaded' and summary['total_sections'] > 0:
            print("✅ Base de conhecimento carregada com sucesso!")
            return True
        else:
            print("⚠️ Base de conhecimento vazia ou não carregada")
            return False
            
    except Exception as e:
        print(f"❌ Erro na base de conhecimento: {e}")
        return False

if __name__ == "__main__":
    print("🚀 JUNIM - Teste Rápido de Componentes\n")
    
    success = test_basic_imports()
    success = test_knowledge_base() and success
    
    if success:
        print("\n🎉 Testes básicos passaram! A aplicação deve funcionar.")
        print("\nPara executar:")
        print("  streamlit run main.py")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique as dependências.")
