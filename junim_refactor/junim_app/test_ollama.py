#!/usr/bin/env python3
"""
Script para testar a conexão com o Ollama
"""

import sys
import os
import requests
import json

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ollama_connection():
    """Testa a conexão com o Ollama"""
    print("🔍 Testando conexão com Ollama...")
    
    try:
        # Testa se o servidor está rodando
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Servidor Ollama está rodando!")
            
            # Lista modelos disponíveis
            data = response.json()
            models = data.get('models', [])
            
            print(f"\n📋 Modelos disponíveis ({len(models)}):")
            for model in models:
                name = model.get('name', 'Unknown')
                size = model.get('size', 0)
                size_mb = size / (1024*1024) if size > 0 else 0
                print(f"  • {name} ({size_mb:.1f} MB)")
            
            # Verifica se o deepseek-r1:1.5b está disponível
            model_names = [m['name'] for m in models]
            if 'deepseek-r1:1.5b' in model_names:
                print("\n✅ deepseek-r1:1.5b está disponível!")
                return True
            else:
                print("\n⚠️  deepseek-r1:1.5b não encontrado!")
                print("💡 Para instalar: ollama pull deepseek-r1:1.5b")
                return False
                
        else:
            print(f"❌ Erro ao conectar com Ollama: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama não está rodando ou não está acessível")
        print("💡 Verifique se o Ollama está instalado e rodando: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

def test_ollama_generation():
    """Testa a geração de código com Ollama"""
    print("\n🧪 Testando geração de código...")
    
    try:
        import ollama
        
        # Prompt simples de teste
        test_prompt = """
        Converta este código Delphi simples para Java Spring Boot:
        
        procedure TForm1.Button1Click(Sender: TObject);
        begin
          ShowMessage('Hello World');
        end;
        
        Retorne JSON no formato: {"files": [{"name": "arquivo.java", "content": "código"}]}
        """
        
        response = ollama.chat(
            model='deepseek-r1:1.5b',
            messages=[
                {
                    'role': 'system',
                    'content': 'Você é um especialista em migração de sistemas Delphi para Java Spring Boot. Retorne código Java funcional no formato JSON.'
                },
                {
                    'role': 'user',
                    'content': test_prompt
                }
            ],
            options={
                'temperature': 0.1,
                'num_predict': 200
            }
        )
        
        print("✅ Resposta gerada com sucesso!")
        print(f"📄 Conteúdo: {response['message']['content'][:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar código: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 JUNIM - Teste de Integração com Ollama")
    print("=" * 50)
    
    # Testa conexão
    connection_ok = test_ollama_connection()
    
    # Testa geração se a conexão estiver OK
    if connection_ok:
        test_ollama_generation()
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")
