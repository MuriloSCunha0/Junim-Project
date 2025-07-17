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
            if GROQ_AVAILABLE:
                groq_api_key = self.config.get('groq_api_key', '')
                
                if groq_api_key:
                    logger.info(f"Tentando configurar Groq com chave API: {groq_api_key[:4]}...{groq_api_key[-4:] if len(groq_api_key) > 8 else ''}")
                    self.groq_client = groq.Groq(
                        api_key=groq_api_key
                    )
                    logger.info("Cliente Groq configurado com sucesso")
                else:
                    logger.warning("Chave API Groq ausente na configuração")
                    self.groq_client = None
            else:
                logger.warning("Biblioteca groq não instalada")
                self.groq_client = None
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
                     progress_callback: Optional[callable] = None,
                     prompt_config: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Gera código Java a partir da estrutura Delphi e contexto RAG
        
        Args:
            delphi_structure: Estrutura analisada do projeto Delphi
            rag_context: Contexto RAG construído
            progress_callback: Callback para atualizar progresso
            prompt_config: Configuração com prompts especializados
            
        Returns:
            Dicionário com código gerado e metadados
        """
        try:
            if progress_callback:
                progress_callback(3, 5, "Construindo prompt para LLM...")
            
            # Constrói prompt
            prompt = self._build_prompt(delphi_structure, rag_context, prompt_config)
            
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
            
            # Tenta identificar o tipo de erro para fornecer mensagens mais úteis
            error_msg = str(e)
            if "format specifier" in error_msg or "formatting" in error_msg:
                error_msg = "Erro de formatação de string no resultado da IA. Tentando novamente com outro modelo ou configuração pode resolver o problema."
            elif "JSONDecodeError" in error_msg or "JSON" in error_msg:
                error_msg = "Erro ao decodificar resposta da IA. O formato retornado não está correto."
            elif "api_key" in error_msg.lower() or "apikey" in error_msg.lower():
                error_msg = "Problema com a chave API. Verifique se a chave API do Groq está configurada corretamente."
            
            raise Exception(f"Falha na geração de código Java: {error_msg}")
    
    def _build_prompt(self, delphi_structure: Dict[str, Any], rag_context: str, prompt_config: Optional[Dict[str, str]] = None) -> str:
        """
        Constrói prompt para o LLM
        
        Args:
            delphi_structure: Estrutura analisada do projeto Delphi
            rag_context: Contexto RAG construído
            prompt_config: Configuração com prompts especializados
            
        Returns:
            Prompt completo para o LLM
        """
        
        # Se há configuração de prompt especializado, usa-o
        if prompt_config and 'enhanced_prompt' in prompt_config:
            logger.info("✅ Usando prompt enriquecido com documentação gerada")
            return prompt_config['enhanced_prompt']
        
        if prompt_config and 'primary_prompt' in prompt_config:
            logger.info("✅ Usando prompt especializado para geração de código")
            
            # Substituição de placeholders no prompt especializado
            prompt_template = prompt_config['primary_prompt']
            project_info = self._extract_project_info(delphi_structure)
            delphi_structure_formatted = self._format_delphi_structure(delphi_structure)
            
            # Sanitiza os dados antes de substituir para evitar problemas de formatação
            project_info_safe = self._sanitize_template_data(project_info)
            delphi_structure_safe = self._sanitize_template_data(delphi_structure_formatted)
            rag_context_safe = self._sanitize_template_data(rag_context)
            
            # Substitui marcadores no template
            prompt = prompt_template.replace("{PROJECT_INFO}", project_info_safe)
            prompt = prompt.replace("{DELPHI_STRUCTURE}", delphi_structure_safe)
            prompt = prompt.replace("{RAG_CONTEXT}", rag_context_safe)
            
            # Adiciona prompts de teste se solicitado
            if 'testing_prompt' in prompt_config:
                prompt += f"\n\n## TESTES:\n{prompt_config['testing_prompt']}"
                logger.info("Prompt de testes adicionado")
                
            logger.info(f"Prompt especializado construído com {len(prompt)} caracteres")
            return prompt
        
        # Caso contrário, usa prompt padrão
        logger.info("⚠️ Usando prompt padrão (prompts especializados não disponíveis)")
        
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
    
    def _sanitize_template_data(self, data: str) -> str:
        """
        Sanitiza dados antes de inserir em templates para evitar problemas de formatação
        
        Args:
            data: String com dados que serão inseridos no template
            
        Returns:
            String sanitizada sem caracteres problemáticos de formatação
        """
        try:
            import re
            
            if not isinstance(data, str):
                data = str(data)
            
            # Remove ou substitui sequências problemáticas específicas
            # Padrão que está causando o erro: % 123, "message": "Cliente criado"
            problem_pattern = r'%\s*(\d+),\s*"([^"]*)":\s*"([^"]*)"'
            
            def replace_problematic_format(match):
                number = match.group(1)
                key = match.group(2)
                value = match.group(3)
                # Converte para formato seguro
                return f'[Status: {number}, {key}: "{value}"]'
            
            data = re.sub(problem_pattern, replace_problematic_format, data)
            
            # Remove outros padrões de formatação problemáticos
            # Remove % seguido de espaços e números
            data = re.sub(r'%\s+(\d+)', r'Codigo_\1', data)
            
            # Substitui %d e %s por placeholders seguros
            data = re.sub(r'%d', 'NUMERO', data)
            data = re.sub(r'%s', 'TEXTO', data)
            data = re.sub(r'%[a-zA-Z]', 'VALOR', data)
            
            # Remove % isolados que podem causar problemas
            data = re.sub(r'%(?![0-9A-Fa-f]{2})', 'PERCENT', data)
            
            # Escapa caracteres que podem ser interpretados como formatação
            data = data.replace('{', '{{').replace('}', '}}')
            
            # Remove caracteres de escape duplos
            data = data.replace('\\\\', '\\')
            
            logger.debug(f"Dados sanitizados para template: {len(data)} caracteres")
            return data
            
        except Exception as e:
            logger.warning(f"Erro ao sanitizar dados do template: {str(e)}")
            # Fallback: conversão básica para string segura
            try:
                safe_data = str(data).replace('%', 'PERCENT').replace('{', '{{').replace('}', '}}')
                return safe_data
            except:
                return "DADOS_NAO_DISPONIVEIS"

    def _extract_project_info(self, delphi_structure: Dict[str, Any]) -> str:
        """Extrai informações resumidas do projeto"""
        try:
            summary = delphi_structure.get('summary', {})
            
            info_parts = []
            info_parts.append(f"- Units: {summary.get('total_units', 0)}")
            info_parts.append(f"- Forms: {summary.get('total_forms', 0)}")
            info_parts.append(f"- DataModules: {summary.get('total_datamodules', 0)}")
            
            technologies = summary.get('main_technologies', [])
            if technologies:
                info_parts.append(f"- Tecnologias: {', '.join(technologies)}")
            
            # Sanitiza o resultado antes de retornar
            result = "\n".join(info_parts)
            return self._sanitize_template_data(result)
            
        except Exception as e:
            logger.warning(f"Erro ao extrair informações do projeto: {str(e)}")
            return "Informações do projeto não disponíveis"
    
    def _format_delphi_structure(self, delphi_structure: Dict[str, Any]) -> str:
        """Formata estrutura Delphi para o prompt"""
        try:
            formatted_parts = []
            
            # DataModules
            data_modules = delphi_structure.get('data_modules', {})
            if data_modules:
                formatted_parts.append("### DataModules:")
                for dm_name, dm_info in data_modules.items():
                    # Sanitiza o nome do DataModule
                    safe_dm_name = self._sanitize_template_data(str(dm_name))
                    formatted_parts.append(f"**{safe_dm_name}**:")
                    
                    # Queries
                    queries = dm_info.get('sql_queries', [])
                    if queries:
                        formatted_parts.append("  Queries:")
                        for query in queries[:3]:  # Limita a 3 para não sobrecarregar
                            query_type = self._sanitize_template_data(str(query.get('type', 'UNKNOWN')))
                            query_sql = self._sanitize_template_data(str(query.get('sql', ''))[:100])
                            formatted_parts.append(f"    - {query_type}: {query_sql}...")
                    
                    # Métodos
                    procedures = dm_info.get('procedures', [])
                    functions = dm_info.get('functions', [])
                    methods = procedures + functions
                    if methods:
                        formatted_parts.append("  Métodos:")
                        for method in methods[:3]:
                            method_name = self._sanitize_template_data(str(method.get('name', 'unnamed')))
                            formatted_parts.append(f"    - {method_name}")
            
            # Forms
            forms = delphi_structure.get('forms', {})
            if forms:
                formatted_parts.append("\n### Forms:")
                for form_name, form_info in forms.items():
                    safe_form_name = self._sanitize_template_data(str(form_name))
                    formatted_parts.append(f"**{safe_form_name}**:")
                    
                    # Event handlers
                    handlers = form_info.get('event_handlers', [])
                    if handlers:
                        formatted_parts.append("  Event Handlers:")
                        for handler in handlers[:3]:
                            handler_name = self._sanitize_template_data(str(handler.get('name', 'unnamed')))
                            handler_type = self._sanitize_template_data(str(handler.get('type', 'UNKNOWN')))
                            formatted_parts.append(f"    - {handler_name} ({handler_type})")
                    
                    # Classes
                    classes = form_info.get('classes', [])
                    for cls in classes:
                        if cls.get('is_form'):
                            methods = cls.get('methods', [])
                            if methods:
                                formatted_parts.append("  Métodos do Form:")
                                for method in methods[:3]:
                                    method_name = self._sanitize_template_data(str(method.get('name', 'unnamed')))
                                    if method.get('is_event_handler'):
                                        formatted_parts.append(f"    - {method_name} (Event Handler)")
            
            result = "\n".join(formatted_parts) if formatted_parts else "Estrutura não disponível"
            
            # Sanitiza o resultado final
            return self._sanitize_template_data(result)
            
        except Exception as e:
            logger.warning(f"Erro ao formatar estrutura Delphi: {str(e)}")
            return "Estrutura Delphi não disponível devido a erro de formatação"
    
    def _generate_with_groq(self, prompt: str) -> Optional[str]:
        """Gera código usando Groq"""
        try:
            # Verifica modelo especificado
            model = self.config.get('groq_model', 'llama3-70b-8192')
            logger.info(f"Tentando gerar com Groq usando modelo: {model}")
            
            # Garante que client existe
            if not self.groq_client:
                logger.error("Groq client não configurado")
                return None
                
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
            
            logger.info(f"Geração com Groq concluída: {len(completion.choices[0].message.content)} caracteres")
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
            # Tenta sanitizar o conteúdo para evitar problemas de formatação
            sanitized_content = self._sanitize_content(generated_content)
            
            # Tenta extrair JSON do conteúdo gerado
            json_match = self._extract_json_from_content(sanitized_content)
            
            if json_match:
                logger.info("JSON extraído com sucesso do conteúdo gerado")
                return json_match
            else:
                # Se não conseguir extrair JSON, cria estrutura básica
                logger.info("Não foi possível extrair JSON. Criando estrutura básica.")
                return self._create_basic_structure(sanitized_content)
                
        except Exception as e:
            logger.warning(f"Erro ao processar código gerado: {str(e)}")
            return self._create_fallback_structure(generated_content)
            
    def _sanitize_content(self, content: str) -> str:
        """Sanitiza o conteúdo para evitar problemas de formatação"""
        try:
            # Substitui caracteres de formatação que podem causar problemas
            import re
            
            sanitized = content
            
            # Remove ou substitui sequências problemáticas de formatação
            # Padrão que está causando o erro: % 123, "message": "Cliente criado"
            problem_pattern = r'%\s*(\d+),\s*"([^"]*)":\s*"([^"]*)"'
            matches = re.finditer(problem_pattern, sanitized)
            
            for match in matches:
                full_match = match.group(0)
                number = match.group(1)
                key = match.group(2)
                value = match.group(3)
                
                # Substitui por formato JSON válido
                replacement = f'"{key}": "{value}", "status": {number}'
                sanitized = sanitized.replace(full_match, replacement)
                logger.info(f"Corrigido formato problemático: {full_match} -> {replacement}")
            
            # Outras correções gerais
            # Remove % seguido de espaços e números isolados
            sanitized = re.sub(r'%\s+(\d+)', r'\1', sanitized)
            
            # Corrige strings com formatação dentro de JSON
            sanitized = re.sub(r'"([^"]*%[ds][^"]*)"', lambda m: f'"{m.group(1).replace("%d", "0").replace("%s", "string")}"', sanitized)
            
            # Remove caracteres de escape duplos problemáticos
            sanitized = sanitized.replace('\\\\', '\\')
            
            return sanitized
            
        except Exception as e:
            logger.warning(f"Erro ao sanitizar conteúdo: {str(e)}")
            # Se a sanitização falhar, pelo menos remove % isolados
            try:
                simple_fix = content.replace('% ', '')
                return simple_fix
            except:
                return content
    
    def _extract_json_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """Extrai JSON do conteúdo gerado pelo LLM"""
        try:
            # Procura por blocos JSON
            import re
            json_pattern = r'```json\s*\n(.*?)\n```'
            match = re.search(json_pattern, content, re.DOTALL)
            
            if match:
                json_content = match.group(1)
                try:
                    # Primeira tentativa: JSON direto
                    return json.loads(json_content)
                except (json.JSONDecodeError, ValueError) as json_err:
                    logger.warning(f"Erro ao decodificar JSON do bloco marcado: {str(json_err)}")
                    # Segunda tentativa: limpa o JSON antes de tentar novamente
                    try:
                        cleaned_json = self._clean_json_content(json_content)
                        return json.loads(cleaned_json)
                    except (json.JSONDecodeError, ValueError) as clean_err:
                        logger.warning(f"Erro mesmo após limpeza: {str(clean_err)}")
                        # Terceira tentativa: extração manual de campos básicos
                        return self._extract_basic_fields(json_content)
            
            # Tenta encontrar JSON solto no texto
            brace_start = content.find('{')
            brace_end = content.rfind('}')
            
            if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
                json_content = content[brace_start:brace_end + 1]
                try:
                    return json.loads(json_content)
                except (json.JSONDecodeError, ValueError) as json_err:
                    logger.warning(f"Erro ao decodificar JSON solto: {str(json_err)}")
                    # Tenta limpar e reprocessar
                    try:
                        cleaned_json = self._clean_json_content(json_content)
                        return json.loads(cleaned_json)
                    except (json.JSONDecodeError, ValueError):
                        # Fallback: extração básica
                        return self._extract_basic_fields(json_content)
            
            logger.warning("Nenhum JSON válido encontrado no conteúdo")
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao extrair JSON: {str(e)}")
            return None
    
    def _extract_basic_fields(self, content: str) -> Dict[str, Any]:
        """Extrai campos básicos quando JSON completo falha"""
        try:
            import re
            basic_structure = {
                "project_name": "modernized_app",
                "package_name": "com.example.modernizedapp",
                "files": {}
            }
            
            # Tenta extrair nome do projeto
            project_match = re.search(r'"project_name"\s*:\s*"([^"]*)"', content)
            if project_match:
                basic_structure["project_name"] = project_match.group(1)
            
            # Tenta extrair package name
            package_match = re.search(r'"package_name"\s*:\s*"([^"]*)"', content)
            if package_match:
                basic_structure["package_name"] = package_match.group(1)
            
            # Adiciona conteúdo bruto como fallback
            basic_structure["files"]["generated_content.txt"] = content
            basic_structure["files"]["src/main/java/com/example/modernizedapp/ModernizedAppApplication.java"] = self._get_default_main_class()
            
            logger.info("JSON básico extraído com sucesso usando fallback")
            return basic_structure
            
        except Exception as e:
            logger.error(f"Erro na extração básica: {str(e)}")
            return {
                "project_name": "modernized_app",
                "package_name": "com.example.modernizedapp", 
                "files": {
                    "error.txt": f"Erro na extração: {str(e)}",
                    "raw_content.txt": content
                }
            }
    
    def _get_default_main_class(self) -> str:
        """Retorna classe principal padrão"""
        return """package com.example.modernizedapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ModernizedAppApplication {
    public static void main(String[] args) {
        SpringApplication.run(ModernizedAppApplication.class, args);
    }
}"""
    
    def _clean_json_content(self, json_content: str) -> str:
        """Limpa conteúdo JSON para evitar erros de formatação"""
        try:
            import re
            
            # Primeiro, trata o caso específico que está causando erro
            # Padrão: % 123, "message": "Cliente criado"
            specific_pattern = r'%\s*(\d+),\s*"([^"]*)":\s*"([^"]*)"'
            json_content = re.sub(specific_pattern, r'"\2": "\3", "status": \1', json_content)
            
            # Remove outros % problemáticos
            json_content = re.sub(r'%\s*(\d+)', r'\1', json_content)
            json_content = re.sub(r'%\s*"([^"]*)"', r'"\1"', json_content)
            
            # Substitui sequências de escape problemáticas
            json_content = re.sub(r'%([^d\s])', r'%%\1', json_content)
            
            # Limpa formatações em strings JSON
            # Procura por "%d" ou "%s" dentro de strings e substitui
            pattern = r'("[^"]*%[ds][^"]*")'
            for match in re.finditer(pattern, json_content):
                original = match.group(1)
                # Substitui %d e %s por valores placeholders
                fixed = original.replace('%d', '0').replace('%s', 'value')
                json_content = json_content.replace(original, fixed)
            
            # Remove escape de aspas que podem causar problemas
            json_content = json_content.replace('\\"', '"')
            
            # Garante que aspas duplas são usadas para chaves e valores
            json_content = re.sub(r"'([^']*)':", r'"\1":', json_content)
            json_content = re.sub(r':\s*\'([^\']*)\'', r': "\1"', json_content)
            
            # Remove vírgulas trailing que podem quebrar JSON
            json_content = re.sub(r',\s*}', '}', json_content)
            json_content = re.sub(r',\s*]', ']', json_content)
            
            logger.info(f"JSON limpo com sucesso. Tamanho: {len(json_content)} caracteres")
            return json_content
            
        except Exception as e:
            logger.error(f"Erro ao limpar JSON: {str(e)}")
            # Fallback mais simples: remove todos os % que não são parte de URLs
            try:
                fallback = re.sub(r'%(?![0-9A-Fa-f]{2})', '', json_content)
                return fallback
            except:
                return json_content
    
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
