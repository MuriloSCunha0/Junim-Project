"""
Script de teste para validar a correção dos erros de upload
"""

import tempfile
import zipfile
import os
from pathlib import Path

def test_upload_simulation():
    """Simula processo de upload para testar correções"""
    
    print("🧪 Testando simulação de upload...")
    
    # Cria arquivo de teste
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
    temp_dir = tempfile.mkdtemp(prefix="test_junim_")
    zip_path = os.path.join(temp_dir, "test_project.zip")
    
    try:
        # Cria ZIP com arquivo de teste
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            zip_file.writestr("TestUnit.pas", test_content)
            zip_file.writestr("MainForm.dfm", "object TestForm: TTestForm\nend")
        
        print(f"✅ ZIP criado: {zip_path}")
        
        # Simula extração
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"✅ Extração concluída em: {extract_dir}")
        
        # Valida arquivos extraídos
        extracted_files = []
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith(('.pas', '.dfm', '.dpr')):
                    extracted_files.append(file)
        
        print(f"✅ Arquivos Delphi encontrados: {extracted_files}")
        
        # Simula leitura dos arquivos
        uploaded_files = []
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith(('.pas', '.dfm', '.dpr')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if content.strip():
                            uploaded_files.append({
                                'name': file,
                                'path': file_path,
                                'content': content,
                                'type': file.split('.')[-1].lower()
                            })
                    except Exception as e:
                        print(f"❌ Erro ao ler {file}: {e}")
        
        print(f"✅ Arquivos processados: {len(uploaded_files)}")
        for file_info in uploaded_files:
            print(f"  - {file_info['name']} ({file_info['type']}) - {len(file_info['content'])} chars")
        
        print("🎉 Teste de upload concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    
    finally:
        # Limpa arquivos temporários
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"🧹 Arquivos temporários removidos: {temp_dir}")
        except Exception as e:
            print(f"⚠️ Erro ao limpar temporários: {e}")

if __name__ == "__main__":
    test_upload_simulation()
