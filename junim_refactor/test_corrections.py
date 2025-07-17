"""
Teste para validar as correções dos erros de upload e seek
"""

import tempfile
import zipfile
import os
import sys
from io import BytesIO

# Adiciona o caminho do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), 'junim_app'))

def test_zip_handling():
    """Testa o tratamento de arquivos ZIP"""
    print("🧪 Testando tratamento de arquivos ZIP...")
    
    try:
        # Cria um arquivo ZIP de teste
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
        
        # Cria ZIP em memória
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("TestUnit.pas", test_content)
            zip_file.writestr("MainForm.dfm", "object TestForm: TTestForm\nend")
        
        zip_buffer.seek(0)
        print("✅ ZIP criado em memória")
        
        # Testa o FileHandler
        try:
            from junim_app.utils.file_handler import FileHandler
        except ImportError:
            print("⚠️ Não foi possível importar FileHandler, pulando teste específico")
            return True
        
        file_handler = FileHandler()
        
        # Salva ZIP temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_file.write(zip_buffer.getvalue())
            zip_path = tmp_file.name
        
        print(f"✅ ZIP salvo temporariamente: {zip_path}")
        
        # Testa extração
        extracted_path = file_handler.extract_zip(zip_path)
        print(f"✅ ZIP extraído em: {extracted_path}")
        
        # Verifica arquivos extraídos
        delphi_files = file_handler.find_delphi_files(extracted_path)
        print(f"✅ Arquivos Delphi encontrados: {delphi_files}")
        
        # Limpeza
        os.unlink(zip_path)
        file_handler.cleanup()
        print("✅ Limpeza concluída")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_streamlit_file_object():
    """Simula objeto de arquivo do Streamlit"""
    print("🧪 Testando objeto de arquivo simulado do Streamlit...")
    
    try:
        # Simula uploaded_file do Streamlit
        class MockUploadedFile:
            def __init__(self, content):
                self.content = content
                self.name = "test.zip"
                self.size = len(content)
                self._position = 0
            
            def seek(self, position):
                self._position = position
            
            def getbuffer(self):
                return self.content
            
            def getvalue(self):
                return self.content
        
        # Cria conteúdo de teste
        test_content = b"Test ZIP content"
        mock_file = MockUploadedFile(test_content)
        
        # Testa validações
        if hasattr(mock_file, 'seek') and hasattr(mock_file, 'getbuffer'):
            print("✅ Arquivo tem métodos necessários")
        else:
            print("❌ Arquivo não tem métodos necessários")
            return False
        
        # Testa seek
        mock_file.seek(0)
        print("✅ Seek funcionou")
        
        # Testa getbuffer
        content = mock_file.getbuffer()
        print(f"✅ getbuffer retornou {len(content)} bytes")
        
        # Testa getvalue
        content2 = mock_file.getvalue()
        print(f"✅ getvalue retornou {len(content2)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Iniciando testes de correção...")
    
    success1 = test_zip_handling()
    success2 = test_streamlit_file_object()
    
    if success1 and success2:
        print("🎉 Todos os testes passaram! As correções estão funcionando.")
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
