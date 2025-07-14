"""
Módulo para manipulação de arquivos (zip, unzip, estrutura de projetos)
"""

import os
import zipfile
import tempfile
import shutil
from typing import List, Dict, Any
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileHandler:
    """Classe responsável pela manipulação de arquivos e estruturas de projeto"""
    
    def __init__(self):
        """Inicializa o manipulador de arquivos"""
        self.temp_dirs = []
    
    def extract_zip(self, zip_path: str) -> str:
        """
        Extrai um arquivo ZIP para um diretório temporário
        
        Args:
            zip_path: Caminho para o arquivo ZIP
            
        Returns:
            Caminho do diretório onde foi extraído
        """
        try:
            # Cria diretório temporário
            temp_dir = tempfile.mkdtemp(prefix='junim_delphi_')
            self.temp_dirs.append(temp_dir)
            
            # Extrai o arquivo
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            logger.info(f"Projeto extraído em: {temp_dir}")
            return temp_dir
            
        except Exception as e:
            logger.error(f"Erro ao extrair ZIP: {str(e)}")
            raise Exception(f"Falha ao extrair arquivo ZIP: {str(e)}")
    
    def find_delphi_files(self, project_dir: str) -> Dict[str, List[str]]:
        """
        Encontra todos os arquivos Delphi em um diretório
        
        Args:
            project_dir: Diretório do projeto
            
        Returns:
            Dicionário com listas de arquivos por extensão
        """
        delphi_files = {
            'pas': [],  # Arquivos Pascal
            'dfm': [],  # Arquivos de formulário
            'dpr': [],  # Arquivo de projeto principal
            'dpk': [],  # Arquivos de pacote
            'inc': []   # Arquivos include
        }
        
        try:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = file.split('.')[-1].lower()
                    
                    if file_ext in delphi_files:
                        delphi_files[file_ext].append(file_path)
            
            logger.info(f"Arquivos encontrados: {sum(len(files) for files in delphi_files.values())}")
            return delphi_files
            
        except Exception as e:
            logger.error(f"Erro ao buscar arquivos Delphi: {str(e)}")
            raise Exception(f"Falha ao localizar arquivos Delphi: {str(e)}")
    
    def read_file_content(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Lê o conteúdo de um arquivo
        
        Args:
            file_path: Caminho do arquivo
            encoding: Codificação do arquivo
            
        Returns:
            Conteúdo do arquivo como string
        """
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            # Tenta com codificação latin1 se UTF-8 falhar
            try:
                with open(file_path, 'r', encoding='latin1') as file:
                    return file.read()
            except Exception as e:
                logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
                return ""
        except Exception as e:
            logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
            return ""
    
    def create_java_project_structure(self, base_dir: str, package_name: str = "com.example.modernizedapp") -> Dict[str, str]:
        """
        Cria a estrutura padrão de um projeto Java Spring Boot
        
        Args:
            base_dir: Diretório base onde criar a estrutura
            package_name: Nome do pacote Java
            
        Returns:
            Dicionário com os caminhos das principais pastas
        """
        try:
            # Converte package name para path
            package_path = package_name.replace('.', os.sep)
            
            # Define estrutura de diretórios
            dirs_to_create = [
                'src/main/java/' + package_path,
                'src/main/java/' + package_path + '/controller',
                'src/main/java/' + package_path + '/service',
                'src/main/java/' + package_path + '/repository',
                'src/main/java/' + package_path + '/model',
                'src/main/java/' + package_path + '/config',
                'src/main/resources',
                'src/main/resources/static',
                'src/main/resources/templates',
                'src/test/java/' + package_path
            ]
            
            # Cria diretórios
            structure = {}
            for dir_name in dirs_to_create:
                full_path = os.path.join(base_dir, dir_name)
                os.makedirs(full_path, exist_ok=True)
                
                # Mapeia para estrutura retornada
                key = dir_name.split('/')[-1] if '/' in dir_name else dir_name
                structure[key] = full_path
            
            # Adiciona paths importantes
            structure['base'] = base_dir
            structure['src_main_java'] = os.path.join(base_dir, 'src/main/java/' + package_path)
            structure['src_main_resources'] = os.path.join(base_dir, 'src/main/resources')
            structure['package_name'] = package_name
            
            logger.info(f"Estrutura Java criada em: {base_dir}")
            return structure
            
        except Exception as e:
            logger.error(f"Erro ao criar estrutura Java: {str(e)}")
            raise Exception(f"Falha ao criar estrutura do projeto Java: {str(e)}")
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8'):
        """
        Escreve conteúdo em um arquivo
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo a escrever
            encoding: Codificação do arquivo
        """
        try:
            # Cria diretório se não existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as file:
                file.write(content)
                
        except Exception as e:
            logger.error(f"Erro ao escrever arquivo {file_path}: {str(e)}")
            raise Exception(f"Falha ao escrever arquivo: {str(e)}")
    
    def create_zip(self, source_dir: str, zip_path: str):
        """
        Cria um arquivo ZIP de um diretório
        
        Args:
            source_dir: Diretório fonte
            zip_path: Caminho do arquivo ZIP a criar
        """
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, source_dir)
                        zip_file.write(file_path, arc_name)
            
            logger.info(f"ZIP criado: {zip_path}")
            
        except Exception as e:
            logger.error(f"Erro ao criar ZIP: {str(e)}")
            raise Exception(f"Falha ao criar arquivo ZIP: {str(e)}")
    
    def cleanup_temp_dirs(self):
        """Remove todos os diretórios temporários criados"""
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.info(f"Diretório temporário removido: {temp_dir}")
            except Exception as e:
                logger.warning(f"Erro ao remover diretório temporário {temp_dir}: {str(e)}")
        
        self.temp_dirs.clear()
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de um arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dicionário com estatísticas do arquivo
        """
        try:
            stat = os.stat(file_path)
            content = self.read_file_content(file_path)
            
            return {
                'size': stat.st_size,
                'lines': len(content.splitlines()) if content else 0,
                'chars': len(content) if content else 0,
                'modified': stat.st_mtime,
                'name': os.path.basename(file_path),
                'extension': os.path.splitext(file_path)[1],
                'path': file_path
            }
            
        except Exception as e:
            logger.warning(f"Erro ao obter estatísticas do arquivo {file_path}: {str(e)}")
            return {
                'size': 0,
                'lines': 0,
                'chars': 0,
                'modified': 0,
                'name': os.path.basename(file_path),
                'extension': os.path.splitext(file_path)[1],
                'path': file_path
            }
    
    def __del__(self):
        """Destrutor - limpa diretórios temporários"""
        self.cleanup_temp_dirs()
