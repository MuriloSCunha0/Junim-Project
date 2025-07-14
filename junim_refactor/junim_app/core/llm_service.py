"""
Módulo para interação com LLMs (Groq e Ollama)
"""

import os
import time
import json
from typing import Dict, Any, Optional, List
import logging
import requests

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Biblioteca groq não instalada. Funcionalidade Groq desabilitada.")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Biblioteca ollama não instalada. Funcionalidade Ollama desabilitada.")

class LLMService:
    """Classe responsável por interação com LLMs (Groq e Ollama)"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o serviço LLM
        
        Args:
            config: Configuração com chaves de API e modelos
        """
        self.config = config
        self.groq_client = None
        self.ollama_client = None
        
        self._setup_groq()
        self._setup_ollama()
    
    def _setup_groq(self):
        """Configura cliente Groq"""
        try:
            if GROQ_AVAILABLE and self.config.get('groq_api_key'):
                self.groq_client = groq.Groq(
                    api_key=self.config['groq_api_key']
                )
                logger.info("Cliente Groq configurado com sucesso")
            else:
                logger.warning("Groq não disponível (chave API ausente ou biblioteca não instalada)")
        except Exception as e:
            logger.error(f"Erro ao configurar Groq: {str(e)}")
            self.groq_client = None
    
    def _setup_ollama(self):
        """Configura cliente Ollama"""
        try:
            if OLLAMA_AVAILABLE:
                ollama_url = self.config.get('ollama_url', 'http://localhost:11434')
                
                # Testa conexão com Ollama
                response = requests.get(f"{ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    self.ollama_client = ollama
                    logger.info("Cliente Ollama configurado com sucesso")
                else:
                    logger.warning("Ollama não está respondendo")
            else:
                logger.warning("Ollama não disponível (biblioteca não instalada)")
        except Exception as e:
            logger.warning(f"Ollama não disponível: {str(e)}")
            self.ollama_client = None
    
    def generate_code(self, 
                     delphi_structure: Dict[str, Any], 
                     rag_context: str,
                     progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Gera código Java a partir da estrutura Delphi e contexto RAG
        
        Args:
            delphi_structure: Estrutura analisada do projeto Delphi
            rag_context: Contexto RAG construído
            progress_callback: Callback para atualizar progresso
            
        Returns:
            Dicionário com código gerado e metadados
        """
        try:
            if progress_callback:
                progress_callback(3, 5, "Construindo prompt para LLM...")
            
            # Constrói prompt
            prompt = self._build_prompt(delphi_structure, rag_context)
            
            if progress_callback:
                progress_callback(3, 5, "Gerando código Java com IA...")
            
            # Tenta Groq primeiro, depois Ollama
            result = None
            
            if self.groq_client:
                logger.info("Tentando geração com Groq")
                result = self._generate_with_groq(prompt)
            
            if not result and self.ollama_client:
                logger.info("Tentando geração com Ollama (fallback)")
                result = self._generate_with_ollama(prompt)
            
            if not result:
                raise Exception("Nenhum LLM disponível para geração")
            
            # Processa e estrutura resultado
            processed_result = self._process_generated_code(result)
            
            logger.info("Código Java gerado com sucesso")
            return processed_result
            
        except Exception as e:
            logger.error(f"Erro na geração de código: {str(e)}")
            raise Exception(f"Falha na geração de código: {str(e)}")
    
    def _build_prompt(self, delphi_structure: Dict[str, Any], rag_context: str) -> str:
        """Constrói prompt para o LLM"""
        
        # Extrai informações principais do projeto Delphi
        project_info = self._extract_project_info(delphi_structure)
        
        prompt = f"""
Você é um especialista em migração de sistemas legados e desenvolvimento Java Spring Boot.

Sua tarefa é converter o seguinte projeto Delphi para Java Spring Boot, mantendo toda a lógica de negócio e funcionalidades.

{rag_context}

## PROJETO DELPHI A CONVERTER:

### Informações do Projeto:
{project_info}

### Estrutura Detalhada:
{self._format_delphi_structure(delphi_structure)}

## INSTRUÇÕES PARA CONVERSÃO:

1. **Estrutura do Projeto**: Crie um projeto Spring Boot completo com:
   - Classe principal (Application.java)
   - Controllers para endpoints REST
   - Services para lógica de negócio  
   - Repositories para acesso a dados
   - Entities/Models para dados
   - DTOs para transferência
   - Configurações necessárias

2. **Mapeamento de Componentes**:
   - DataModules → Services + Repositories
   - Forms → Controllers REST
   - Queries → JPA Repository methods
   - Event handlers → Endpoints HTTP
   - Validações → Bean Validation

3. **Tecnologias a Usar**:
   - Spring Boot 3.x
   - Spring Data JPA
   - Spring Web
   - Bean Validation
   - Maven como build tool

4. **Formato de Resposta**: Retorne o código Java organizado por arquivo, seguindo esta estrutura:

```json
{{
  "project_name": "nome_do_projeto",
  "package_name": "com.example.modernizedapp",
  "files": {{
    "src/main/java/com/example/modernizedapp/ModernizedAppApplication.java": "código da classe principal",
    "src/main/java/com/example/modernizedapp/controller/NomeController.java": "código do controller",
    "src/main/java/com/example/modernizedapp/service/NomeService.java": "código do service",
    "src/main/java/com/example/modernizedapp/repository/NomeRepository.java": "código do repository",
    "src/main/java/com/example/modernizedapp/model/NomeEntity.java": "código da entity",
    "src/main/resources/application.properties": "configurações do Spring",
    "pom.xml": "configuração Maven"
  }}
}}
```

5. **Qualidade do Código**:
   - Use boas práticas Java
   - Implemente tratamento de exceções
   - Adicione validações adequadas
   - Use anotações Spring apropriadas
   - Mantenha código limpo e comentado

IMPORTANTE: Mantenha TODA a lógica de negócio original. Converta fielmente os algoritmos e fluxos do Delphi.

Gere o código Java completo agora:
"""
        
        return prompt
    
    def _extract_project_info(self, delphi_structure: Dict[str, Any]) -> str:
        """Extrai informações resumidas do projeto"""
        summary = delphi_structure.get('summary', {})
        
        info_parts = []
        info_parts.append(f"- Units: {summary.get('total_units', 0)}")
        info_parts.append(f"- Forms: {summary.get('total_forms', 0)}")
        info_parts.append(f"- DataModules: {summary.get('total_datamodules', 0)}")
        
        technologies = summary.get('main_technologies', [])
        if technologies:
            info_parts.append(f"- Tecnologias: {', '.join(technologies)}")
        
        return "\n".join(info_parts)
    
    def _format_delphi_structure(self, delphi_structure: Dict[str, Any]) -> str:
        """Formata estrutura Delphi para o prompt"""
        formatted_parts = []
        
        # DataModules
        data_modules = delphi_structure.get('data_modules', {})
        if data_modules:
            formatted_parts.append("### DataModules:")
            for dm_name, dm_info in data_modules.items():
                formatted_parts.append(f"**{dm_name}**:")
                
                # Queries
                queries = dm_info.get('sql_queries', [])
                if queries:
                    formatted_parts.append("  Queries:")
                    for query in queries[:3]:  # Limita a 3 para não sobrecarregar
                        formatted_parts.append(f"    - {query.get('type', 'UNKNOWN')}: {query.get('sql', '')[:100]}...")
                
                # Métodos
                methods = dm_info.get('procedures', []) + dm_info.get('functions', [])
                if methods:
                    formatted_parts.append("  Métodos:")
                    for method in methods[:3]:
                        formatted_parts.append(f"    - {method.get('name', 'unnamed')}")
        
        # Forms
        forms = delphi_structure.get('forms', {})
        if forms:
            formatted_parts.append("\n### Forms:")
            for form_name, form_info in forms.items():
                formatted_parts.append(f"**{form_name}**:")
                
                # Event handlers
                handlers = form_info.get('event_handlers', [])
                if handlers:
                    formatted_parts.append("  Event Handlers:")
                    for handler in handlers[:3]:
                        formatted_parts.append(f"    - {handler.get('name', 'unnamed')} ({handler.get('type', 'UNKNOWN')})")
                
                # Classes
                classes = form_info.get('classes', [])
                for cls in classes:
                    if cls.get('is_form'):
                        methods = cls.get('methods', [])
                        if methods:
                            formatted_parts.append("  Métodos do Form:")
                            for method in methods[:3]:
                                if method.get('is_event_handler'):
                                    formatted_parts.append(f"    - {method.get('name', 'unnamed')} (Event Handler)")
        
        return "\n".join(formatted_parts) if formatted_parts else "Estrutura não disponível"
    
    def _generate_with_groq(self, prompt: str) -> Optional[str]:
        """Gera código usando Groq"""
        try:
            model = self.config.get('groq_model', 'llama3-70b-8192')
            
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em migração de sistemas Delphi para Java Spring Boot. Sempre retorne código completo e funcional."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model=model,
                temperature=0.1,  # Baixa temperatura para código mais determinístico
                max_tokens=4000
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro na geração com Groq: {str(e)}")
            return None
    
    def _generate_with_ollama(self, prompt: str) -> Optional[str]:
        """Gera código usando Ollama"""
        try:
            model = self.config.get('ollama_model', 'codellama:34b')
            
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'Você é um especialista em migração de sistemas Delphi para Java Spring Boot. Sempre retorne código completo e funcional.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.1,
                    'num_predict': 4000
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Erro na geração com Ollama: {str(e)}")
            return None
    
    def _process_generated_code(self, generated_content: str) -> Dict[str, Any]:
        """Processa e estrutura o código gerado"""
        try:
            # Tenta extrair JSON do conteúdo gerado
            json_match = self._extract_json_from_content(generated_content)
            
            if json_match:
                return json_match
            else:
                # Se não conseguir extrair JSON, cria estrutura básica
                return self._create_basic_structure(generated_content)
                
        except Exception as e:
            logger.warning(f"Erro ao processar código gerado: {str(e)}")
            return self._create_fallback_structure(generated_content)
    
    def _extract_json_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """Extrai JSON do conteúdo gerado pelo LLM"""
        try:
            # Procura por blocos JSON
            import re
            json_pattern = r'```json\s*\n(.*?)\n```'
            match = re.search(json_pattern, content, re.DOTALL)
            
            if match:
                json_content = match.group(1)
                return json.loads(json_content)
            
            # Tenta encontrar JSON solto no texto
            brace_start = content.find('{')
            brace_end = content.rfind('}')
            
            if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
                json_content = content[brace_start:brace_end + 1]
                return json.loads(json_content)
            
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao extrair JSON: {str(e)}")
            return None
    
    def _create_basic_structure(self, content: str) -> Dict[str, Any]:
        """Cria estrutura básica a partir do conteúdo gerado"""
        return {
            "project_name": "modernized_app",
            "package_name": "com.example.modernizedapp",
            "files": {
                "src/main/java/com/example/modernizedapp/ModernizedAppApplication.java": self._extract_main_class(content),
                "generated_content.txt": content
            }
        }
    
    def _create_fallback_structure(self, content: str) -> Dict[str, Any]:
        """Cria estrutura de fallback"""
        main_class = """
package com.example.modernizedapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ModernizedAppApplication {
    public static void main(String[] args) {
        SpringApplication.run(ModernizedAppApplication.class, args);
    }
}
"""
        
        return {
            "project_name": "modernized_app",
            "package_name": "com.example.modernizedapp",
            "files": {
                "src/main/java/com/example/modernizedapp/ModernizedAppApplication.java": main_class,
                "generated_content.txt": content,
                "README.md": "# Projeto Modernizado\n\nEste projeto foi gerado automaticamente pelo JUNIM.\n\nVerifique o arquivo generated_content.txt para o conteúdo completo gerado pela IA."
            }
        }
    
    def _extract_main_class(self, content: str) -> str:
        """Extrai ou cria classe principal Spring Boot"""
        # Procura por classe main no conteúdo
        import re
        main_pattern = r'class.*Application.*\{.*?public static void main.*?\}.*?\}'
        match = re.search(main_pattern, content, re.DOTALL)
        
        if match:
            return match.group(0)
        
        # Retorna classe padrão
        return """
package com.example.modernizedapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ModernizedAppApplication {
    public static void main(String[] args) {
        SpringApplication.run(ModernizedAppApplication.class, args);
    }
}
"""
    
    def test_connection(self) -> Dict[str, bool]:
        """Testa conexão com os LLMs disponíveis"""
        status = {
            'groq': False,
            'ollama': False
        }
        
        # Testa Groq
        if self.groq_client:
            try:
                # Testa com prompt simples
                completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": "Hello"}],
                    model=self.config.get('groq_model', 'llama3-70b-8192'),
                    max_tokens=10
                )
                status['groq'] = True
            except Exception:
                status['groq'] = False
        
        # Testa Ollama
        if self.ollama_client:
            try:
                ollama.chat(
                    model=self.config.get('ollama_model', 'codellama:34b'),
                    messages=[{'role': 'user', 'content': 'Hello'}],
                    options={'num_predict': 10}
                )
                status['ollama'] = True
            except Exception:
                status['ollama'] = False
        
        return status
