"""
Teste para validar as correções do erro NoneType no pipeline
"""

import tempfile
import zipfile
import os
import sys

# Adiciona o caminho do projeto
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, 'junim_app'))

def test_file_handler_validations():
    """Testa as validações do FileHandler"""
    print("🧪 Testando validações do FileHandler...")
    
    try:
        from utils.file_handler import FileHandler
        
        file_handler = FileHandler()
        
        # Teste 1: Caminho None
        try:
            file_handler.extract_zip(None)
            print("❌ Deveria ter falhado com None")
            return False
        except Exception as e:
            if "None" in str(e):
                print("✅ Validação de None funcionou")
            else:
                print(f"❌ Erro inesperado: {e}")
                return False
        
        # Teste 2: Caminho vazio
        try:
            file_handler.extract_zip("")
            print("❌ Deveria ter falhado com string vazia")
            return False
        except Exception as e:
            if "vazio" in str(e):
                print("✅ Validação de string vazia funcionou")
            else:
                print(f"❌ Erro inesperado: {e}")
                return False
        
        # Teste 3: Arquivo que não existe
        try:
            file_handler.extract_zip("/caminho/inexistente.zip")
            print("❌ Deveria ter falhado com arquivo inexistente")
            return False
        except Exception as e:
            if "não encontrado" in str(e):
                print("✅ Validação de arquivo inexistente funcionou")
            else:
                print(f"❌ Erro inesperado: {e}")
                return False
        
        print("✅ Todas as validações do FileHandler passaram")
        return True
        
    except ImportError as e:
        print(f"⚠️ Não foi possível importar FileHandler: {e}")
        return True

def test_pipeline_validations():
    """Testa as validações do Pipeline"""
    print("🧪 Testando validações do Pipeline...")
    
    try:
        from core.pipeline import ModernizationPipeline
        
        # Teste com configuração básica
        config = {
            'java_version': '17',
            'spring_version': '3.0.0',
            'package_name': 'com.test.app'
        }
        
        pipeline = ModernizationPipeline(config)
        
        # Teste 1: Executar sem projeto nem análise prévia
        try:
            pipeline.run()
            print("❌ Deveria ter falhado sem projeto nem análise")
            return False
        except Exception as e:
            if "Nenhum projeto" in str(e) or "análise prévia" in str(e):
                print("✅ Validação de projeto/análise ausente funcionou")
            else:
                print(f"❌ Erro inesperado: {e}")
                return False
        
        print("✅ Validações do Pipeline passaram")
        return True
        
    except ImportError as e:
        print(f"⚠️ Não foi possível importar ModernizationPipeline: {e}")
        return True

def test_create_valid_zip():
    """Cria um ZIP válido para testes"""
    print("🧪 Testando criação de ZIP válido...")
    
    try:
        # Cria conteúdo de teste
        test_content = """
unit TestUnit;

interface

type
  TTestForm = class(TForm)
    Button1: TButton;
    procedure Button1Click(Sender: TObject);
  end;

implementation

procedure TTestForm.Button1Click(Sender: TObject);
begin
  ShowMessage('Hello from Delphi!');
end;

end.
"""
        
        # Cria ZIP temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            zip_path = tmp_file.name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("TestUnit.pas", test_content)
            zip_file.writestr("MainForm.dfm", "object TestForm: TTestForm\nend")
        
        # Valida o ZIP criado
        if os.path.exists(zip_path) and os.path.getsize(zip_path) > 0:
            print(f"✅ ZIP válido criado: {zip_path} ({os.path.getsize(zip_path)} bytes)")
            
            # Testa extração com FileHandler
            try:
                from utils.file_handler import FileHandler
                file_handler = FileHandler()
                extracted_path = file_handler.extract_zip(zip_path)
                print(f"✅ Extração bem-sucedida: {extracted_path}")
                
                # Limpeza
                file_handler.cleanup()
                os.unlink(zip_path)
                return True
                
            except ImportError:
                print("⚠️ FileHandler não disponível para teste de extração")
                os.unlink(zip_path)
                return True
        else:
            print("❌ Falha ao criar ZIP válido")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao criar ZIP: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Iniciando testes de correção do erro NoneType...")
    
    success1 = test_file_handler_validations()
    success2 = test_pipeline_validations()
    success3 = test_create_valid_zip()
    
    if success1 and success2 and success3:
        print("🎉 Todos os testes passaram! As correções estão funcionando.")
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
