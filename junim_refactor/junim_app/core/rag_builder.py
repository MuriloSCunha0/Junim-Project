"""
Módulo para construção de contexto RAG (Retrieval-Augmented Generation)
"""

import os
import re
from typing import Dict, List, Any, Optional
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGBuilder:
    """Classe responsável por construir contexto RAG para geração de código"""
    
    def __init__(self, knowledge_base_path: str = None):
        """
        Inicializa o construtor RAG
        
        Args:
            knowledge_base_path: Caminho para a base de conhecimento
        """
        if knowledge_base_path is None:
            # Usa caminho padrão relativo ao módulo
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            knowledge_base_path = os.path.join(project_root, 'knowledge_base')
        
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = {}
        self.mappings = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Carrega a base de conhecimento em memória"""
        try:
            mappings_file = os.path.join(self.knowledge_base_path, 'delphi_to_spring_mappings.md')
            
            if os.path.exists(mappings_file):
                with open(mappings_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self._parse_knowledge_base(content)
                    logger.info("Base de conhecimento carregada com sucesso")
            else:
                logger.warning(f"Arquivo de mapeamentos não encontrado: {mappings_file}")
                
        except Exception as e:
            logger.error(f"Erro ao carregar base de conhecimento: {str(e)}")
    
    def _parse_knowledge_base(self, content: str):
        """Analisa e estrutura a base de conhecimento"""
        try:
            # Divide o conteúdo em seções
            sections = self._split_into_sections(content)
            
            for section_title, section_content in sections.items():
                # Extrai exemplos de código Delphi e Java
                delphi_examples = self._extract_code_blocks(section_content, 'pascal')
                java_examples = self._extract_code_blocks(section_content, 'java')
                
                self.knowledge_base[section_title] = {
                    'content': section_content,
                    'delphi_examples': delphi_examples,
                    'java_examples': java_examples,
                    'keywords': self._extract_keywords(section_title, section_content)
                }
            
            logger.info(f"Base de conhecimento estruturada: {len(self.knowledge_base)} seções")
            
        except Exception as e:
            logger.error(f"Erro ao analisar base de conhecimento: {str(e)}")
    
    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """Divide o conteúdo em seções baseadas nos cabeçalhos"""
        sections = {}
        
        # Padrão para cabeçalhos markdown (## Título)
        pattern = r'^## (.+)$'
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start_pos = match.end()
            
            # Determina fim da seção
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(content)
            
            section_content = content[start_pos:end_pos].strip()
            sections[title] = section_content
        
        return sections
    
    def _extract_code_blocks(self, content: str, language: str) -> List[str]:
        """Extrai blocos de código de uma linguagem específica"""
        code_blocks = []
        
        # Padrão para blocos de código markdown
        pattern = rf'```{language}\s*\n(.*?)\n```'
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            code_block = match.group(1).strip()
            if code_block:
                code_blocks.append(code_block)
        
        return code_blocks
    
    def _extract_keywords(self, title: str, content: str) -> List[str]:
        """Extrai palavras-chave de uma seção"""
        keywords = []
        
        # Palavras-chave do título
        title_words = re.findall(r'\b\w+\b', title.lower())
        keywords.extend(title_words)
        
        # Componentes Delphi mencionados
        delphi_components = re.findall(r'\bT\w+\b', content)
        keywords.extend([comp.lower() for comp in delphi_components])
        
        # Anotações Spring mencionadas
        spring_annotations = re.findall(r'@\w+', content)
        keywords.extend([ann.lower() for ann in spring_annotations])
        
        # Classes Java mencionadas
        java_classes = re.findall(r'\b[A-Z]\w*Repository\b|\b[A-Z]\w*Service\b|\b[A-Z]\w*Controller\b', content)
        keywords.extend([cls.lower() for cls in java_classes])
        
        return list(set(keywords))  # Remove duplicatas
    
    def build_context(self, delphi_structure: Dict[str, Any]) -> str:
        """
        Constrói contexto RAG baseado na estrutura do projeto Delphi
        
        Args:
            delphi_structure: Estrutura analisada do projeto Delphi
            
        Returns:
            Contexto formatado para o LLM
        """
        try:
            logger.info("Construindo contexto RAG")
            
            # Analisa estrutura para identificar padrões relevantes
            relevant_patterns = self._identify_relevant_patterns(delphi_structure)
            
            # Recupera seções relevantes da base de conhecimento
            relevant_sections = self._retrieve_relevant_sections(relevant_patterns)
            
            # Constrói contexto final
            context = self._build_final_context(delphi_structure, relevant_sections)
            
            logger.info(f"Contexto RAG construído: {len(context)} caracteres")
            return context
            
        except Exception as e:
            logger.error(f"Erro ao construir contexto RAG: {str(e)}")
            return self._get_fallback_context()
    
    def _identify_relevant_patterns(self, delphi_structure: Dict[str, Any]) -> List[str]:
        """Identifica padrões relevantes na estrutura Delphi"""
        patterns = []
        
        try:
            # Verifica presença de DataModules
            if delphi_structure.get('data_modules'):
                patterns.append('datamodule')
                patterns.append('repository')
                patterns.append('database')
            
            # Verifica presença de Forms
            if delphi_structure.get('forms'):
                patterns.append('form')
                patterns.append('controller')
                patterns.append('button')
                patterns.append('event')
            
            # Verifica componentes de banco de dados
            for unit in delphi_structure.get('units', {}).values():
                db_components = unit.get('database_components', [])
                if db_components:
                    for comp in db_components:
                        comp_type = comp.get('type', '').lower()
                        if 'query' in comp_type:
                            patterns.append('query')
                            patterns.append('jpa')
                        elif 'table' in comp_type:
                            patterns.append('table')
                            patterns.append('entity')
                        elif 'datasource' in comp_type:
                            patterns.append('datasource')
                            patterns.append('service')
            
            # Verifica queries SQL
            for unit in delphi_structure.get('units', {}).values():
                sql_queries = unit.get('sql_queries', [])
                if sql_queries:
                    patterns.append('sql')
                    patterns.append('repository')
                    for query in sql_queries:
                        query_type = query.get('type', '').lower()
                        patterns.append(query_type)
            
            # Verifica event handlers
            for unit in delphi_structure.get('units', {}).values():
                event_handlers = unit.get('event_handlers', [])
                if event_handlers:
                    patterns.append('event')
                    patterns.append('controller')
                    for handler in event_handlers:
                        handler_type = handler.get('type', '').lower()
                        if 'click' in handler_type:
                            patterns.append('button')
                            patterns.append('endpoint')
            
            return list(set(patterns))  # Remove duplicatas
            
        except Exception as e:
            logger.warning(f"Erro ao identificar padrões: {str(e)}")
            return ['basic', 'controller', 'service', 'repository']
    
    def _retrieve_relevant_sections(self, patterns: List[str]) -> List[Dict[str, Any]]:
        """Recupera seções relevantes da base de conhecimento"""
        relevant_sections = []
        
        try:
            for section_title, section_data in self.knowledge_base.items():
                section_keywords = section_data.get('keywords', [])
                
                # Calcula score de relevância
                relevance_score = 0
                for pattern in patterns:
                    if pattern in section_keywords:
                        relevance_score += 1
                    
                    # Verifica se padrão está no título ou conteúdo
                    if pattern in section_title.lower():
                        relevance_score += 2
                    if pattern in section_data.get('content', '').lower():
                        relevance_score += 0.5
                
                if relevance_score > 0:
                    section_data['relevance_score'] = relevance_score
                    relevant_sections.append({
                        'title': section_title,
                        'data': section_data
                    })
            
            # Ordena por relevância
            relevant_sections.sort(key=lambda x: x['data']['relevance_score'], reverse=True)
            
            # Limita a top 5 seções mais relevantes
            return relevant_sections[:5]
            
        except Exception as e:
            logger.warning(f"Erro ao recuperar seções relevantes: {str(e)}")
            return []
    
    def _build_final_context(self, delphi_structure: Dict[str, Any], relevant_sections: List[Dict[str, Any]]) -> str:
        """Constrói o contexto final para o LLM"""
        context_parts = []
        
        # Introdução
        context_parts.append("# Contexto de Conversão Delphi → Java Spring\n")
        
        # Resumo do projeto Delphi
        summary = delphi_structure.get('summary', {})
        context_parts.append("## Análise do Projeto Delphi:")
        context_parts.append(f"- Total de Units: {summary.get('total_units', 0)}")
        context_parts.append(f"- Total de Forms: {summary.get('total_forms', 0)}")
        context_parts.append(f"- Total de DataModules: {summary.get('total_datamodules', 0)}")
        context_parts.append(f"- Possui Banco de Dados: {'Sim' if summary.get('has_database') else 'Não'}")
        
        technologies = summary.get('main_technologies', [])
        if technologies:
            context_parts.append(f"- Tecnologias Identificadas: {', '.join(technologies)}")
        
        context_parts.append("\n## Padrões de Conversão Relevantes:\n")
        
        # Adiciona seções relevantes
        for section in relevant_sections:
            title = section['title']
            content = section['data']['content']
            
            context_parts.append(f"### {title}")
            context_parts.append(content)
            context_parts.append("")  # Linha em branco
        
        # Diretrizes gerais
        context_parts.append("\n## Diretrizes de Conversão:")
        context_parts.append("1. Mantenha a lógica de negócio original")
        context_parts.append("2. Use Spring Boot com arquitetura em camadas")
        context_parts.append("3. Converta DataModules em Services e Repositories")
        context_parts.append("4. Converta Forms em Controllers REST")
        context_parts.append("5. Use JPA para acesso a dados")
        context_parts.append("6. Implemente validação adequada")
        context_parts.append("7. Use DTOs para transferência de dados")
        context_parts.append("8. Mantenha tratamento de exceções")
        
        return "\n".join(context_parts)
    
    def _get_fallback_context(self) -> str:
        """Retorna contexto de fallback em caso de erro"""
        return """
# Contexto Básico de Conversão Delphi → Java Spring

## Mapeamentos Fundamentais:
- TDataModule → @Service + @Repository classes
- TForm → @RestController class
- TQuery/TADOQuery → JpaRepository methods
- TButton.OnClick → @PostMapping/@GetMapping methods
- Database queries → JPA @Query annotations
- ShowMessage → ResponseEntity with message

## Estrutura Spring Boot Padrão:
- controller/ - REST controllers
- service/ - Business logic
- repository/ - Data access
- model/ - JPA entities
- config/ - Configuration classes

## Dependências Necessárias:
- spring-boot-starter-web
- spring-boot-starter-data-jpa
- spring-boot-starter-validation
- Database driver (conforme necessário)
"""
    
    def get_knowledge_base_summary(self) -> Dict[str, Any]:
        """Retorna resumo da base de conhecimento carregada"""
        return {
            'total_sections': len(self.knowledge_base),
            'sections': list(self.knowledge_base.keys()),
            'status': 'loaded' if self.knowledge_base else 'empty'
        }
