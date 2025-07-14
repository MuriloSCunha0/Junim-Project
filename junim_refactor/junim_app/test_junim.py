"""
Script de teste para verificar componentes do JUNIM
"""

import sys
import os

# Adiciona path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🔍 Testando imports dos módulos...")
    
    try:
        from ui.interface import JUNIMInterface
        print("✅ Interface UI importada com sucesso")
        
        from core.pipeline import ModernizationPipeline
        print("✅ Pipeline importado com sucesso")
        
        from core.delphi_parser import DelphiParser
        print("✅ Parser Delphi importado com sucesso")
        
        from core.rag_builder import RAGBuilder
        print("✅ RAG Builder importado com sucesso")
        
        from core.llm_service import LLMService
        print("✅ LLM Service importado com sucesso")
        
        from core.java_builder import JavaBuilder
        print("✅ Java Builder importado com sucesso")
        
        from utils.file_handler import FileHandler
        print("✅ File Handler importado com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar: {e}")
        return False

def test_dependencies():
    """Testa dependências externas"""
    print("\n📦 Testando dependências externas...")
    
    try:
        import streamlit
        print("✅ Streamlit disponível")
    except ImportError:
        print("❌ Streamlit não encontrado")
    
    try:
        import groq
        print("✅ Groq disponível")
    except ImportError:
        print("⚠️ Groq não encontrado (opcional)")
    
    try:
        import ollama
        print("✅ Ollama disponível")
    except ImportError:
        print("⚠️ Ollama não encontrado (opcional)")
    
    try:
        import requests
        print("✅ Requests disponível")
    except ImportError:
        print("❌ Requests não encontrado")

def test_knowledge_base():
    """Testa se a base de conhecimento está acessível"""
    print("\n📚 Testando base de conhecimento...")
    
    try:
        from core.rag_builder import RAGBuilder
        rag = RAGBuilder()
        summary = rag.get_knowledge_base_summary()
        
        if summary['status'] == 'loaded':
            print(f"✅ Base de conhecimento carregada: {summary['total_sections']} seções")
            return True
        else:
            print("⚠️ Base de conhecimento vazia")
            return False
            
    except Exception as e:
        print(f"❌ Erro na base de conhecimento: {e}")
        return False

def test_file_structure():
    """Testa estrutura de arquivos"""
    print("\n📁 Testando estrutura de arquivos...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'ui/interface.py',
        'core/pipeline.py',
        'core/delphi_parser.py',
        'core/rag_builder.py',
        'core/llm_service.py',
        'core/java_builder.py',
        'utils/file_handler.py',
        'knowledge_base/delphi_to_spring_mappings.md'
    ]
    
    all_found = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} não encontrado")
            all_found = False
    
    return all_found

def test_basic_functionality():
    """Testa funcionalidade básica"""
    print("\n⚙️ Testando funcionalidade básica...")
    
    try:
        # Testa FileHandler
        from utils.file_handler import FileHandler
        fh = FileHandler()
        print("✅ FileHandler inicializado")
        
        # Testa DelphiParser
        from core.delphi_parser import DelphiParser
        dp = DelphiParser()
        print("✅ DelphiParser inicializado")
        
        # Testa RAGBuilder
        from core.rag_builder import RAGBuilder
        rb = RAGBuilder()
        print("✅ RAGBuilder inicializado")
        
        # Testa JavaBuilder
        from core.java_builder import JavaBuilder
        jb = JavaBuilder()
        print("✅ JavaBuilder inicializado")
        
        # Testa configuração do LLMService
        from core.llm_service import LLMService
        config = {
            'groq_api_key': '',
            'groq_model': 'llama3-70b-8192',
            'ollama_url': 'http://localhost:11434',
            'ollama_model': 'codellama:34b'
        }
        llm = LLMService(config)
        print("✅ LLMService inicializado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na funcionalidade básica: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 JUNIM - Teste de Componentes\n")
    
    tests = [
        ("Imports", test_imports),
        ("Dependências", test_dependencies),
        ("Base de Conhecimento", test_knowledge_base),
        ("Estrutura de Arquivos", test_file_structure),
        ("Funcionalidade Básica", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Executando: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro durante teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print(f"\n{'='*50}")
    print("RESUMO DOS TESTES")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! JUNIM está pronto para uso.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam. Verifique as dependências.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    print("\n" + "="*50)
    print("Para executar o JUNIM:")
    print("  Windows: run_junim.bat")
    print("  Linux/Mac: ./run_junim.sh")
    print("  Manual: streamlit run main.py")
    print("="*50)
    
    sys.exit(exit_code)
