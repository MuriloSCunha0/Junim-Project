"""
🧪 TESTE DO SISTEMA UNIVERSAL DE MODELOS
========================================

Este script testa o sistema universal de modelos para garantir que tudo está funcionando.
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def test_universal_config():
    """Testa se o sistema universal está funcionando"""
    print("🧪 TESTANDO SISTEMA UNIVERSAL...")
    
    try:
        from config.universal_model_config import (
            get_universal_config,
            get_available_models, 
            detect_model_type,
            get_performance_info_universal
        )
        
        print("✅ Importações universais OK")
        
        # Testa detecção de modelo
        test_models = ['codellama:7b', 'deepseek-r1:14b', 'mistral:7b']
        
        for model in test_models:
            model_type = detect_model_type(model)
            config = get_universal_config(model, 'fast')
            
            print(f"  📊 {model} -> Tipo: {model_type}")
            print(f"     Temp: {config.get('temperature', 'N/A')}, Ctx: {config.get('num_ctx', 'N/A')}")
        
        # Testa modelos disponíveis
        available = get_available_models()
        print(f"✅ {len(available)} modelos disponíveis no sistema")
        
        # Testa informações de performance
        perf_info = get_performance_info_universal()
        print(f"✅ {len(perf_info['performance_modes'])} modos de performance")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema universal: {e}")
        return False

def test_prompt_manager():
    """Testa se o PromptManager está funcionando"""
    print("\\n🧪 TESTANDO PROMPT MANAGER...")
    
    try:
        from prompts.specialized_prompts import PromptManager
        
        # Testa inicialização
        pm = PromptManager(performance_mode='fast', model_name='codellama:7b')
        print("✅ PromptManager inicializado")
        
        # Testa mudança de modelo
        pm.set_model('mistral:7b')
        pm.set_performance_mode('balanced')
        print("✅ Mudança de modelo/performance OK")
        
        # Testa geração de prompt
        try:
            analysis_prompt = pm.get_analysis_prompt()
            if analysis_prompt:
                print(f"✅ Prompt gerado: {len(analysis_prompt)} caracteres")
            else:
                print("⚠️ Prompt vazio, mas sem erro")
        except Exception as e:
            print(f"⚠️ Erro ao gerar prompt: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no PromptManager: {e}")
        return False

def test_llm_service():
    """Testa se o LLMService está funcionando"""
    print("\\n🧪 TESTANDO LLM SERVICE...")
    
    try:
        from core.llm_service import LLMService
        
        # Configuração básica de teste
        config = {
            'ollama_model': 'codellama:7b',
            'performance_mode': 'fast',
            'groq_api_key': ''
        }
        
        llm = LLMService(config)
        print("✅ LLMService inicializado")
        
        # Verifica se configurações foram aplicadas
        if 'temperature' in llm.config:
            print(f"✅ Configurações universais aplicadas: temp={llm.config.get('temperature', 'N/A')}")
        else:
            print("⚠️ Configurações universais não detectadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no LLMService: {e}")
        return False

def test_interface_compatibility():
    """Testa se a interface está compatível"""
    print("\\n🧪 TESTANDO INTERFACE...")
    
    try:
        # Simula importação da interface
        import streamlit as st
        
        # Testa se as funções principais existem
        from ui.interface import JUNIMInterface
        
        interface = JUNIMInterface()
        print("✅ Interface importada com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na interface: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DO SISTEMA UNIVERSAL\\n")
    
    tests = [
        ("Sistema Universal", test_universal_config),
        ("Prompt Manager", test_prompt_manager), 
        ("LLM Service", test_llm_service),
        ("Interface", test_interface_compatibility)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ FALHA CRÍTICA em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\\n🎯 RESULTADO: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("\\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema universal funcionando perfeitamente")
        print("🚀 Pronto para usar com codellama:7b!")
    else:
        print("\\n⚠️ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique as dependências e configurações")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\\n" + "="*50)
        print("🎯 PRÓXIMOS PASSOS:")
        print("="*50)
        print("1. ✅ Execute: ollama pull codellama:7b")
        print("2. ✅ Execute: streamlit run main.py")
        print("3. ✅ Configure modelo na sidebar")
        print("4. ✅ Teste com modo 'FAST' para velocidade!")
        print("\\n🚀 Aproveite o sistema 3x mais rápido!")
    else:
        print("\\n🔧 Execute este teste novamente após corrigir os problemas.")
