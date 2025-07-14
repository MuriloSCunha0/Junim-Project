"""
Módulo para análise e extração de estrutura do código Delphi
"""

import re
import os
from typing import Dict, List, Any, Optional
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DelphiParser:
    """Classe responsável por analisar e extrair estrutura de projetos Delphi"""
    
    def __init__(self):
        """Inicializa o parser Delphi"""
        self.parsed_units = {}
        self.data_modules = {}
        self.forms = {}
        self.business_logic = {}
        self.database_queries = {}
    
    def parse_project(self, delphi_files: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Analisa um projeto Delphi completo
        
        Args:
            delphi_files: Dicionário com listas de arquivos por extensão
            
        Returns:
            Estrutura analisada do projeto
        """
        try:
            logger.info("Iniciando análise do projeto Delphi")
            
            # Analisa arquivos .pas
            for pas_file in delphi_files.get('pas', []):
                self._parse_pascal_file(pas_file)
            
            # Analisa arquivos .dfm
            for dfm_file in delphi_files.get('dfm', []):
                self._parse_form_file(dfm_file)
            
            # Analisa arquivo de projeto principal
            for dpr_file in delphi_files.get('dpr', []):
                self._parse_project_file(dpr_file)
            
            # Constrói estrutura final
            project_structure = self._build_project_structure()
            
            logger.info(f"Análise concluída. Units encontradas: {len(self.parsed_units)}")
            return project_structure
            
        except Exception as e:
            logger.error(f"Erro ao analisar projeto: {str(e)}")
            raise Exception(f"Falha na análise do projeto Delphi: {str(e)}")
    
    def _parse_pascal_file(self, file_path: str):
        """Analisa um arquivo Pascal (.pas)"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            unit_name = self._extract_unit_name(content)
            if not unit_name:
                return
            
            logger.info(f"Analisando unit: {unit_name}")
            
            # Extrai informações da unit
            unit_info = {
                'name': unit_name,
                'file_path': file_path,
                'classes': self._extract_classes(content),
                'procedures': self._extract_procedures(content),
                'functions': self._extract_functions(content),
                'sql_queries': self._extract_sql_queries(content),
                'event_handlers': self._extract_event_handlers(content),
                'database_components': self._extract_database_components(content),
                'uses_clause': self._extract_uses_clause(content)
            }
            
            self.parsed_units[unit_name] = unit_info
            
            # Classifica tipo de unit
            if self._is_data_module(content):
                self.data_modules[unit_name] = unit_info
            elif self._is_form(content):
                self.forms[unit_name] = unit_info
            
        except Exception as e:
            logger.warning(f"Erro ao analisar arquivo Pascal {file_path}: {str(e)}")
    
    def _parse_form_file(self, file_path: str):
        """Analisa um arquivo de formulário (.dfm)"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            form_name = self._extract_form_name(content)
            if not form_name:
                return
            
            logger.info(f"Analisando formulário: {form_name}")
            
            # Extrai componentes do formulário
            form_info = {
                'name': form_name,
                'file_path': file_path,
                'components': self._extract_form_components(content),
                'data_sources': self._extract_data_sources(content),
                'queries': self._extract_form_queries(content)
            }
            
            # Associa com unit correspondente se existir
            if form_name in self.parsed_units:
                self.parsed_units[form_name]['form_info'] = form_info
            
        except Exception as e:
            logger.warning(f"Erro ao analisar arquivo DFM {file_path}: {str(e)}")
    
    def _parse_project_file(self, file_path: str):
        """Analisa arquivo de projeto principal (.dpr)"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            project_name = self._extract_project_name(content)
            logger.info(f"Projeto principal: {project_name}")
            
            # Extrai informações do projeto
            project_info = {
                'name': project_name,
                'file_path': file_path,
                'main_form': self._extract_main_form(content),
                'forms': self._extract_project_forms(content),
                'uses_clause': self._extract_uses_clause(content)
            }
            
            self.parsed_units['__PROJECT__'] = project_info
            
        except Exception as e:
            logger.warning(f"Erro ao analisar arquivo DPR {file_path}: {str(e)}")
    
    def _extract_unit_name(self, content: str) -> Optional[str]:
        """Extrai o nome da unit"""
        match = re.search(r'unit\s+(\w+)\s*;', content, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extrai definições de classes"""
        classes = []
        
        # Padrão para encontrar classes
        class_pattern = r'(\w+)\s*=\s*class\s*\(([^)]*)\)'
        matches = re.finditer(class_pattern, content, re.IGNORECASE)
        
        for match in matches:
            class_name = match.group(1)
            parent_class = match.group(2).strip() if match.group(2) else 'TObject'
            
            # Extrai métodos da classe
            class_methods = self._extract_class_methods(content, class_name)
            
            classes.append({
                'name': class_name,
                'parent': parent_class,
                'methods': class_methods,
                'is_form': 'TForm' in parent_class or 'TFrame' in parent_class,
                'is_datamodule': 'TDataModule' in parent_class
            })
        
        return classes
    
    def _extract_class_methods(self, content: str, class_name: str) -> List[Dict[str, str]]:
        """Extrai métodos de uma classe específica"""
        methods = []
        
        # Padrão para métodos de classe
        method_pattern = rf'(procedure|function)\s+{re.escape(class_name)}\.(\w+).*?;'
        matches = re.finditer(method_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            method_type = match.group(1)
            method_name = match.group(2)
            
            # Extrai corpo do método
            method_body = self._extract_method_body(content, class_name, method_name)
            
            methods.append({
                'type': method_type,
                'name': method_name,
                'body': method_body,
                'is_event_handler': self._is_event_handler(method_name)
            })
        
        return methods
    
    def _extract_method_body(self, content: str, class_name: str, method_name: str) -> str:
        """Extrai o corpo de um método"""
        try:
            # Padrão para encontrar início do método
            pattern = rf'(procedure|function)\s+{re.escape(class_name)}\.{re.escape(method_name)}.*?begin(.*?)end;'
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            
            if match:
                return match.group(2).strip()
            return ""
            
        except Exception:
            return ""
    
    def _extract_procedures(self, content: str) -> List[Dict[str, str]]:
        """Extrai procedures globais"""
        procedures = []
        
        # Padrão para procedures globais (não de classe)
        pattern = r'procedure\s+(\w+).*?;.*?begin(.*?)end;'
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            procedures.append({
                'name': match.group(1),
                'body': match.group(2).strip()
            })
        
        return procedures
    
    def _extract_functions(self, content: str) -> List[Dict[str, str]]:
        """Extrai functions globais"""
        functions = []
        
        # Padrão para functions globais
        pattern = r'function\s+(\w+).*?:.*?;.*?begin(.*?)end;'
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            functions.append({
                'name': match.group(1),
                'body': match.group(2).strip()
            })
        
        return functions
    
    def _extract_sql_queries(self, content: str) -> List[Dict[str, str]]:
        """Extrai queries SQL do código"""
        queries = []
        
        # Padrões para diferentes tipos de SQL
        patterns = [
            r'\.SQL\.Add\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
            r'\.SQL\.Text\s*:=\s*[\'"]([^\'"]*)[\'"]\s*;',
            r'ExecSQL\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                sql_text = match.group(1).strip()
                if sql_text and len(sql_text) > 5:  # Ignora strings muito pequenas
                    queries.append({
                        'sql': sql_text,
                        'type': self._classify_sql_type(sql_text)
                    })
        
        return queries
    
    def _classify_sql_type(self, sql: str) -> str:
        """Classifica o tipo de operação SQL"""
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'
    
    def _extract_event_handlers(self, content: str) -> List[Dict[str, str]]:
        """Extrai manipuladores de eventos"""
        handlers = []
        
        # Padrões comuns de event handlers
        event_patterns = [
            r'procedure\s+\w+\.(\w+Click)\s*\(.*?\);',
            r'procedure\s+\w+\.(\w+Change)\s*\(.*?\);',
            r'procedure\s+\w+\.(\w+Enter)\s*\(.*?\);',
            r'procedure\s+\w+\.(\w+Exit)\s*\(.*?\);',
            r'procedure\s+\w+\.(\w+KeyPress)\s*\(.*?\);'
        ]
        
        for pattern in event_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                event_name = match.group(1)
                handlers.append({
                    'name': event_name,
                    'type': self._classify_event_type(event_name)
                })
        
        return handlers
    
    def _classify_event_type(self, event_name: str) -> str:
        """Classifica o tipo de evento"""
        if 'Click' in event_name:
            return 'BUTTON_CLICK'
        elif 'Change' in event_name:
            return 'VALUE_CHANGE'
        elif 'Enter' in event_name or 'Exit' in event_name:
            return 'FOCUS'
        elif 'Key' in event_name:
            return 'KEYBOARD'
        else:
            return 'OTHER'
    
    def _extract_database_components(self, content: str) -> List[Dict[str, str]]:
        """Extrai componentes de banco de dados"""
        components = []
        
        # Padrões para componentes de BD
        db_patterns = [
            r'(\w+)\s*:\s*TQuery',
            r'(\w+)\s*:\s*TTable',
            r'(\w+)\s*:\s*TDataSource',
            r'(\w+)\s*:\s*TDatabase',
            r'(\w+)\s*:\s*TADOQuery',
            r'(\w+)\s*:\s*TADOTable'
        ]
        
        for pattern in db_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                component_name = match.group(1)
                component_type = pattern.split(':')[1].strip().replace('\\', '')
                
                components.append({
                    'name': component_name,
                    'type': component_type
                })
        
        return components
    
    def _extract_uses_clause(self, content: str) -> List[str]:
        """Extrai clausula uses"""
        uses_units = []
        
        pattern = r'uses\s+(.*?);'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            uses_text = match.group(1)
            # Remove comentários e quebras de linha
            uses_text = re.sub(r'\{.*?\}', '', uses_text)
            uses_text = re.sub(r'//.*', '', uses_text)
            
            # Separa units
            units = [unit.strip() for unit in uses_text.split(',')]
            uses_units = [unit for unit in units if unit and not unit.startswith('{')]
        
        return uses_units
    
    def _extract_form_name(self, dfm_content: str) -> Optional[str]:
        """Extrai nome do formulário do arquivo DFM"""
        match = re.search(r'object\s+(\w+)\s*:', dfm_content, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_form_components(self, dfm_content: str) -> List[Dict[str, Any]]:
        """Extrai componentes do formulário"""
        components = []
        
        # Padrão para componentes
        pattern = r'object\s+(\w+)\s*:\s*(\w+)'
        matches = re.finditer(pattern, dfm_content, re.IGNORECASE)
        
        for match in matches:
            component_name = match.group(1)
            component_type = match.group(2)
            
            components.append({
                'name': component_name,
                'type': component_type,
                'is_data_aware': self._is_data_aware_component(component_type)
            })
        
        return components
    
    def _extract_data_sources(self, dfm_content: str) -> List[str]:
        """Extrai DataSources do formulário"""
        datasources = []
        
        pattern = r'DataSource\s*=\s*(\w+)'
        matches = re.finditer(pattern, dfm_content, re.IGNORECASE)
        
        for match in matches:
            datasources.append(match.group(1))
        
        return list(set(datasources))  # Remove duplicatas
    
    def _extract_form_queries(self, dfm_content: str) -> List[str]:
        """Extrai queries do formulário"""
        queries = []
        
        pattern = r'(\w+)\s*:\s*T.*Query'
        matches = re.finditer(pattern, dfm_content, re.IGNORECASE)
        
        for match in matches:
            queries.append(match.group(1))
        
        return queries
    
    def _extract_project_name(self, dpr_content: str) -> Optional[str]:
        """Extrai nome do projeto"""
        match = re.search(r'program\s+(\w+)\s*;', dpr_content, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_main_form(self, dpr_content: str) -> Optional[str]:
        """Extrai formulário principal"""
        match = re.search(r'Application\.CreateForm\s*\(\s*(\w+)', dpr_content, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_project_forms(self, dpr_content: str) -> List[str]:
        """Extrai todos os formulários do projeto"""
        forms = []
        
        pattern = r'Application\.CreateForm\s*\(\s*(\w+)'
        matches = re.finditer(pattern, dpr_content, re.IGNORECASE)
        
        for match in matches:
            forms.append(match.group(1))
        
        return forms
    
    def _is_data_module(self, content: str) -> bool:
        """Verifica se é um DataModule"""
        return 'TDataModule' in content
    
    def _is_form(self, content: str) -> bool:
        """Verifica se é um Form"""
        return 'TForm' in content or 'TFrame' in content
    
    def _is_event_handler(self, method_name: str) -> bool:
        """Verifica se é um manipulador de evento"""
        event_suffixes = ['Click', 'Change', 'Enter', 'Exit', 'KeyPress', 'KeyDown', 'KeyUp']
        return any(method_name.endswith(suffix) for suffix in event_suffixes)
    
    def _is_data_aware_component(self, component_type: str) -> bool:
        """Verifica se é um componente data-aware"""
        data_aware_types = ['TDBEdit', 'TDBGrid', 'TDBComboBox', 'TDBMemo', 'TDBCheckBox']
        return component_type in data_aware_types
    
    def _build_project_structure(self) -> Dict[str, Any]:
        """Constrói a estrutura final do projeto analisado"""
        return {
            'units': self.parsed_units,
            'data_modules': self.data_modules,
            'forms': self.forms,
            'summary': {
                'total_units': len(self.parsed_units),
                'total_forms': len(self.forms),
                'total_datamodules': len(self.data_modules),
                'has_database': len(self.data_modules) > 0,
                'main_technologies': self._identify_technologies()
            }
        }
    
    def _identify_technologies(self) -> List[str]:
        """Identifica tecnologias usadas no projeto"""
        technologies = []
        
        # Verifica uses clauses para identificar tecnologias
        all_uses = []
        for unit in self.parsed_units.values():
            all_uses.extend(unit.get('uses_clause', []))
        
        if any('ADO' in use for use in all_uses):
            technologies.append('ADO')
        if any('BDE' in use for use in all_uses):
            technologies.append('BDE')
        if any('IBX' in use for use in all_uses):
            technologies.append('InterBase')
        if any('FireDAC' in use for use in all_uses):
            technologies.append('FireDAC')
        if any('DBXpress' in use for use in all_uses):
            technologies.append('dbExpress')
        
        return technologies
