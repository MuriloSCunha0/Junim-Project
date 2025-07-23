"""
Módulo para interação com LLMs (Groq e Ollama)
"""

import os
import re
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
    
    def __init__(self, config: Dict[str, Any], prompt_manager=None):
        """
        Inicializa o serviço LLM
        
        Args:
            config: Configuração com chaves de API e modelos
            prompt_manager: Gerenciador de prompts para usar prompts do diretório
        """
        self.config = config
        self.groq_client = None
        self.ollama_client = None
        self.prompt_manager = prompt_manager
        
        # ✅ GARANTIR USO DAS CONFIGURAÇÕES DEEPSEEK-R1
        self._setup_model_config()
        
        self._setup_groq()
        self._setup_ollama()
    
    def _setup_model_config(self):
        """Configura modelo com otimizações universais para múltiplos LLMs"""
        model_name = self.config.get('ollama_model', 'codellama:7b')
        
        try:
            # Importa configurações universais
            from config.universal_model_config import (
                get_universal_config, 
                get_performance_info_universal,
                detect_model_type,
                get_available_models
            )
            
            # Aplica configurações otimizadas baseadas na sessão
            performance_mode = self.config.get('performance_mode', 'fast')
            optimized_config = get_universal_config(model_name, performance_mode)
            model_type = detect_model_type(model_name)
            
            # Atualiza configuração com otimizações
            self.config.update(optimized_config)
            
            logger.info(f"🚀 {model_name} ({model_type}) configurado em modo: {performance_mode}")
            logger.info(f"⚡ Config aplicada: {optimized_config}")
            
        except ImportError:
            logger.warning("⚠️ Configurações universais não encontradas, tentando DeepSeek fallback")
            
            # Fallback para configurações antigas do DeepSeek
            if 'deepseek-r1' in model_name.lower():
                try:
                    from config.deepseek_r1_config import (
                        get_deepseek_r1_config, 
                        get_performance_info
                    )
                    
                    performance_mode = self.config.get('performance_mode', 'fast')
                    optimized_config = get_deepseek_r1_config(model_name, performance_mode)
                    self.config.update(optimized_config)
                    
                    logger.info(f"🔄 DeepSeek-R1 fallback configurado em modo: {performance_mode}")
                    
                except ImportError:
                    logger.warning("⚠️ Todas as configurações falharam, usando padrão básico")
        
        except Exception as e:
            logger.error(f"❌ Erro ao configurar modelo {model_name}: {str(e)}")
            logger.info("🔄 Usando configurações padrão básicas")
    
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
    
    def _sanitize_json_response(self, response_text) -> str:
        """
        Sanitiza a resposta da LLM para evitar problemas de formatação JSON
        """
        try:
            # Se for um dicionário, retorna como está
            if isinstance(response_text, dict):
                return response_text
            
            # Verifica se response_text é None
            if response_text is None:
                logger.warning("response_text é None, retornando string vazia")
                return ""
            
            # Converte para string se não for, mas garantindo que não é None
            if not isinstance(response_text, str):
                response_text = str(response_text) if response_text is not None else ""
            
            import re
            
            # Remove o padrão específico que está causando o erro
            # Padrão: % 123, "message": "Cliente criado"
            problematic_pattern = r'%\s*(\d+),\s*"([^"]*)":\s*"([^"]*)"'
            
            def replace_match(match):
                number = match.group(1)
                key = match.group(2)  
                value = match.group(3)
                # Substitui por formato seguro
                return f'[Code: {number}, {key}: "{value}"]'
            
            # Aplica a correção
            cleaned_text = re.sub(problematic_pattern, replace_match, response_text)
            
            # Remove outros padrões problemáticos
            cleaned_text = re.sub(r'%[ds]', 'VALUE', cleaned_text)
            cleaned_text = re.sub(r'%\s+\d+', 'CODE', cleaned_text)
            
            # Escapa caracteres que podem causar problemas em JSON
            cleaned_text = cleaned_text.replace('\\', '\\\\')
            cleaned_text = cleaned_text.replace('\n', '\\n')
            cleaned_text = cleaned_text.replace('\r', '\\r')
            cleaned_text = cleaned_text.replace('\t', '\\t')
            
            return cleaned_text
            
        except Exception as e:
            logger.warning(f"Erro ao sanitizar resposta JSON: {str(e)}")
            return str(response_text) if response_text is not None else ""

    def _extract_json_from_content(self, content: str) -> Dict[str, Any]:
        """
        Extrai JSON do conteúdo da resposta da LLM com tratamento robusto de erros
        """
        try:
            import json
            import re
            
            # Primeiro sanitiza o conteúdo
            content = self._sanitize_json_response(content)
            
            # Tenta encontrar JSON válido no conteúdo
            json_patterns = [
                r'```json\s*(\{.*?\})\s*```',
                r'```\s*(\{.*?\})\s*```',
                r'(\{.*?\})',
                r'(\[.*?\])'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        # Sanitiza o match antes de fazer parse
                        clean_match = self._sanitize_json_response(match)
                        return json.loads(clean_match)
                    except json.JSONDecodeError:
                        continue
            
            # Se não encontrou JSON válido, tenta parse direto
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
            
            # Fallback: retorna estrutura básica
            logger.warning("Não foi possível extrair JSON válido, usando estrutura básica")
            return {
                "files": {
                    "src/main/java/com/example/Application.java": {
                        "content": "// Código gerado com problemas de formatação\n// Conteúdo original preservado abaixo\n\n" + content[:1000]
                    }
                },
                "message": "Resposta processada com limitações devido a problemas de formatação"
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair JSON: {str(e)}")
            return {
                "files": {},
                "error": f"Erro no processamento: {str(e)}"
            }

    def _generate_with_groq(self, prompt: str) -> Optional[str]:
        """
        Gera código usando Groq API
        """
        try:
            # Verifica se a chave API está disponível
            api_key = self.config.get('groq_api_key')
            if not api_key:
                logger.error("❌ Chave API do Groq não configurada")
                return None
            
            import groq
            
            # Inicializa cliente Groq
            client = groq.Groq(api_key=api_key)
            
            # Modelo a ser usado
            model = self.config.get('groq_model', 'llama3-70b-8192')
            
            logger.info(f"🚀 Gerando código usando Groq API com modelo: {model}")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em migração de sistemas Delphi para Java Spring Boot. Sempre retorne código completo e funcional em formato JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            if response.choices and response.choices[0].message:
                result = response.choices[0].message.content
                logger.info(f"✅ Código gerado com sucesso via Groq: {len(result)} caracteres")
                return result
            else:
                logger.error("❌ Resposta vazia do Groq")
                return None
                
        except ImportError:
            logger.error("❌ Biblioteca 'groq' não instalada. Execute: pip install groq")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao gerar código com Groq: {str(e)}")
            return None
    
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
                progress_callback(1, 3, "Construindo prompt para LLM...")
            
            # Constrói prompt
            prompt = self._build_prompt(delphi_structure, rag_context, prompt_config)
            
            if progress_callback:
                progress_callback(2, 3, "Gerando código Java...")
            
            # Tenta gerar com Groq primeiro (se configurado)
            response = None
            groq_key = self.config.get('groq_api_key', '') or ''
            groq_key = groq_key.strip() if groq_key else ''
            
            if groq_key:
                logger.info("🚀 Tentando geração com Groq API...")
                try:
                    response = self._generate_with_groq(prompt)
                except Exception as e:
                    error_msg = str(e)
                    # Se falhou por tamanho, tenta prompt reduzido
                    if "413" in error_msg or "too large" in error_msg.lower():
                        logger.info("🔄 Tentando com prompt reduzido devido ao limite de tokens...")
                        reduced_prompt = self._reduce_prompt_size(prompt)
                        try:
                            response = self._generate_with_groq(reduced_prompt)
                        except Exception as e2:
                            logger.error(f"Erro também com prompt reduzido: {str(e2)}")
                    else:
                        logger.error(f"Erro na geração com Groq: {error_msg}")
            else:
                logger.info("🔄 Chave Groq não configurada, usando Ollama...")
                
            # Se Groq falhou ou não estava configurado, tenta Ollama
            if not response and self.ollama_client:
                logger.info("🔄 Tentando geração com Ollama...")
                response = self._generate_with_ollama(prompt)
            
            # Se ambos falharam, usa análise offline baseada no projeto real
            if not response:
                groq_key_check = self.config.get('groq_api_key', '') or ''
                groq_key_check = groq_key_check.strip() if groq_key_check else ''
                if not groq_key_check and not self.ollama_client:
                    logger.info("🔧 Nenhuma API configurada, usando análise offline baseada no projeto real")
                else:
                    logger.warning("⚠️ Todas as APIs falharam, usando análise offline")
                response = self._generate_analysis_based_response(delphi_structure)

            if progress_callback:
                progress_callback(3, 3, "Processando código gerado...")

            # Processa resposta
            return self._process_generated_code(response)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Erro na geração de código: {error_msg}")

            # Tratamento específico para erro de formatação
            if "Invalid format specifier" in error_msg:
                logger.info("🔧 Detectado erro de formatação, tentando correção...")
                try:
                    # Tenta gerar resposta corrigida
                    corrected_response = self._generate_corrected_response(delphi_structure)
                    return self._process_generated_code(corrected_response)
                except Exception as correction_error:
                    logger.error(f"❌ Falha na correção: {str(correction_error)}")
            
            # Fallback final
            return {
                "files": {},
                "error": f"Falha na geração: {error_msg}",
                "fallback_used": True
            }
    
    def _generate_corrected_response(self, delphi_structure: Dict[str, Any]) -> str:
        """
        Gera resposta corrigida quando há erro de formatação
        """
        try:
            project_name = delphi_structure.get('metadata', {}).get('project_name', 'ModernizedApp')
            
            # Gera código básico sem formatação problemática
            basic_code = f"""
package com.example.{project_name.lower().replace(' ', '')};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

@SpringBootApplication
public class Application {{
    public static void main(String[] args) {{
        SpringApplication.run(Application.class, args);
    }}
}}

@RestController
@RequestMapping("/api")
public class MainController {{
    
    @GetMapping("/health")
    public String health() {{
        return "Application is running";
    }}
    
    @GetMapping("/info")
    public String info() {{
        return "Modernized from Delphi project: {project_name}";
    }}
}}
"""
            
            # Retorna em formato JSON seguro
            return f'''{{
    "files": {{
        "src/main/java/com/example/{project_name.lower().replace(' ', '')}/Application.java": {{
            "content": {json.dumps(basic_code)}
        }}
    }},
    "message": "Código gerado com correção de formatação"
}}'''
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta corrigida: {str(e)}")
            return '{"files": {}, "error": "Falha na correção de formatação"}'
    
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
            
            # Verifica se data é None primeiro
            if data is None:
                logger.warning("data é None em _sanitize_template_data, retornando fallback")
                return "DADOS_NAO_DISPONIVEIS"
            
            # Converte para string de forma segura
            if not isinstance(data, str):
                data = str(data) if data is not None else ""
            
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
                if data is not None:
                    safe_data = str(data).replace('%', 'PERCENT').replace('{', '{{').replace('}', '}}')
                    return safe_data
                else:
                    return "DADOS_NAO_DISPONIVEIS"
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
        """Gera código usando Ollama com configurações universais otimizadas"""
        try:
            # Usa o modelo configurado (padrão: codellama:7b)
            model = self.config.get('ollama_model', 'codellama:7b')
            
            logger.info(f"🔄 Tentando geração com Ollama usando modelo: {model}")
            
            # Tenta usar configurações universais
            try:
                from config.universal_model_config import (
                    get_universal_config, 
                    get_model_system_prompt,
                    detect_model_type,
                    get_enhanced_options_universal
                )
                
                # Aplica configurações otimizadas
                performance_mode = self.config.get('performance_mode', 'fast')
                options = get_universal_config(model, performance_mode)
                
                # Obtém prompt de sistema específico para o modelo
                system_prompt = get_model_system_prompt(model, 'conversion', performance_mode)
                
                # Determina se deve reduzir o prompt baseado no tamanho do modelo
                model_type = detect_model_type(model)
                
                if '1.5b' in model.lower() or '1b' in model.lower():
                    # Modelos pequenos - reduz prompt
                    final_prompt = self._reduce_prompt_for_ollama(prompt)
                    logger.info(f"📦 Prompt reduzido para modelo pequeno: {model}")
                elif '7b' in model.lower():
                    # Modelos médios - prompt moderado
                    final_prompt = prompt[:4000] if len(prompt) > 4000 else prompt
                    logger.info(f"⚖️ Prompt moderado para modelo médio: {model}")
                else:
                    # Modelos grandes - prompt completo
                    final_prompt = prompt
                    logger.info(f"🚀 Prompt completo para modelo grande: {model}")
                    
                logger.info(f"🚀 Usando configurações universais para {model} ({model_type}) - Modo: {performance_mode}")
                
            except ImportError:
                logger.warning("⚠️ Configurações universais não disponíveis, tentando DeepSeek fallback")
                
                # Fallback para configurações antigas do DeepSeek
                try:
                    from config.deepseek_r1_config import get_deepseek_r1_config, get_deepseek_r1_system_prompt, is_deepseek_r1_model
                    
                    if is_deepseek_r1_model(model):
                        # Usa configurações otimizadas para DeepSeek-R1
                        options = get_deepseek_r1_config(model)
                        system_prompt = get_deepseek_r1_system_prompt('conversion')
                        final_prompt = prompt
                        logger.info(f"� DeepSeek-R1 fallback para {model}")
                    else:
                        # Configurações padrão
                        options = {
                            'temperature': 0.1,
                            'num_predict': 2000,
                            'top_p': 0.9,
                            'top_k': 40
                        }
                        system_prompt = 'Especialista em migração Delphi→Java Spring Boot. Retorne código funcional em formato JSON.'
                        final_prompt = self._reduce_prompt_for_ollama(prompt)
                        logger.info(f"🔄 Configurações padrão para {model}")
                        
                except ImportError:
                    logger.warning("⚠️ Todas as configurações falharam, usando configuração básica")
                    
                    # Configurações básicas de último recurso
                    if 'deepseek-r1:14b' in model:
                        options = {
                            'temperature': 0.1,
                            'num_predict': 4000,
                            'top_p': 0.9,
                            'top_k': 50,
                            'repeat_penalty': 1.1,
                            'seed': 42,
                            'num_ctx': 8192,
                        }
                        system_prompt = 'Expert Delphi→Java Spring Boot migration specialist. Generate functional Java code in JSON format.'
                        final_prompt = prompt
                    elif 'codellama' in model.lower():
                        options = {
                            'temperature': 0.05,  # Mais determinístico para código
                            'num_predict': 2500,
                            'top_p': 0.8,
                            'top_k': 30,
                            'repeat_penalty': 1.1,
                            'seed': 42,
                            'num_ctx': 4096,
                        }
                        system_prompt = 'Expert code generation assistant for Delphi to Java Spring Boot migration. Generate clean, functional Java code in JSON format.'
                        final_prompt = prompt[:3000] if len(prompt) > 3000 else prompt
                    else:
                        options = {
                            'temperature': 0.1,
                            'num_predict': 2000,
                            'top_p': 0.9,
                            'top_k': 40
                        }
                        system_prompt = 'Software migration specialist. Generate Java Spring Boot code in JSON format.'
                        final_prompt = self._reduce_prompt_for_ollama(prompt)
            
            # Executa a geração
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': final_prompt
                    }
                ],
                options=options
            )
            
            logger.info(f"✅ Resposta gerada com sucesso pelo Ollama ({model})")
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"❌ Erro na geração com Ollama: {str(e)}")
            return None
    
    def _process_generated_code(self, generated_content: str) -> Dict[str, Any]:
        """Processa e estrutura o código gerado"""
        try:
            # Verifica se o conteúdo é None
            if generated_content is None:
                logger.warning("Conteúdo gerado é None, usando fallback")
                return self._create_fallback_structure("")
            
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
            return self._create_fallback_structure(generated_content or "")
            
    def _sanitize_content(self, content) -> str:
        """Sanitiza o conteúdo para evitar problemas de formatação"""
        try:
            # Verifica se o conteúdo é None
            if content is None:
                logger.warning("Conteúdo é None, retornando string vazia")
                return ""
            
            # Se o conteúdo for um dicionário, retorna como está
            if isinstance(content, dict):
                return content
            
            # Converte para string de forma segura
            if not isinstance(content, str):
                content = str(content) if content is not None else ""
            
            # Garante que content não é None antes de fazer strip
            if content is None:
                content = ""
            
            # Remove caracteres problemáticos e faz strip seguro
            sanitized = content.strip() if content else ""
            
            # Remove possíveis caracteres de controle
            sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
            
            # Substitui caracteres de formatação que podem causar problemas
            import re
            
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
            logger.error(f"Erro ao sanitizar conteúdo: {str(e)}")
            # Se a sanitização falhar, pelo menos remove % isolados
            try:
                if content is not None and isinstance(content, str):
                    simple_fix = content.replace('% ', '')
                    return simple_fix
                else:
                    return str(content) if content is not None else ""
            except:
                return ""
    
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
                    model=self.config.get('ollama_model', 'deepseek-r1:14b'),
                    messages=[{'role': 'user', 'content': 'Hello'}],
                    options={'num_predict': 10}
                )
                status['ollama'] = True
            except Exception:
                status['ollama'] = False
        
        return status
    
    def _generate_analysis_based_response(self, delphi_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera resposta baseada na análise real do projeto quando APIs não estão disponíveis
        
        Args:
            delphi_structure: Estrutura do projeto Delphi
            
        Returns:
            Resposta com estrutura Java Spring Boot baseada na análise real
        """
        logger.info("🔧 Gerando análise baseada no projeto real (modo offline)")
        
        # Extrai informações reais da estrutura
        project_name = delphi_structure.get('project_name', 'ModernizedProject')
        units_analysis = delphi_structure.get('units_analysis', {})
        forms_analysis = delphi_structure.get('forms_analysis', {})
        
        # Constrói resposta baseada nos dados reais
        response = {
            "project_name": project_name,
            "package_name": f"com.modernized.{project_name.lower().replace(' ', '')}",
            "generated_files": {},
            "analysis_source": "real_project_analysis",
            "units_processed": len(units_analysis),
            "forms_processed": len(forms_analysis)
        }
        
        # Gera arquivo principal da aplicação
        main_class_name = f"{project_name.replace(' ', '')}Application"
        response["generated_files"][f"src/main/java/com/modernized/{main_class_name}.java"] = f"""package com.modernized;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Aplicação Spring Boot modernizada do projeto Delphi: {project_name}
 * 
 * Projeto original possuía:
 * - {len(units_analysis)} unidades analisadas
 * - {len(forms_analysis)} formulários processados
 */
@SpringBootApplication
public class {main_class_name} {{
    public static void main(String[] args) {{
        SpringApplication.run({main_class_name}.class, args);
    }}
}}"""
        
        # Gera controllers baseados nas forms reais
        for form_name, form_data in forms_analysis.items():
            if isinstance(form_data, dict):
                controller_name = f"{form_name.replace('.', '').title()}Controller"
                entity_name = form_name.replace('.', '').title()
                
                response["generated_files"][f"src/main/java/com/modernized/controller/{controller_name}.java"] = f"""package com.modernized.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Autowired;
import com.modernized.service.{entity_name}Service;
import com.modernized.dto.{entity_name}DTO;
import java.util.List;

/**
 * Controller para {form_name}
 * Modernizado do formulário Delphi original
 */
@RestController
@RequestMapping("/api/{entity_name.lower()}")
@CrossOrigin(origins = "*")
public class {controller_name} {{
    
    @Autowired
    private {entity_name}Service service;
    
    @GetMapping
    public ResponseEntity<List<{entity_name}DTO>> getAll() {{
        return ResponseEntity.ok(service.findAll());
    }}
    
    @GetMapping("/{{id}}")
    public ResponseEntity<{entity_name}DTO> getById(@PathVariable Long id) {{
        return ResponseEntity.ok(service.findById(id));
    }}
    
    @PostMapping
    public ResponseEntity<{entity_name}DTO> create(@RequestBody {entity_name}DTO dto) {{
        return ResponseEntity.ok(service.save(dto));
    }}
    
    @PutMapping("/{{id}}")
    public ResponseEntity<{entity_name}DTO> update(@PathVariable Long id, @RequestBody {entity_name}DTO dto) {{
        dto.setId(id);
        return ResponseEntity.ok(service.save(dto));
    }}
    
    @DeleteMapping("/{{id}}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {{
        service.deleteById(id);
        return ResponseEntity.noContent().build();
    }}
}}"""
        
        # Gera services baseados nas units reais
        for unit_name, unit_data in units_analysis.items():
            if isinstance(unit_data, dict):
                service_name = f"{unit_name.replace('.', '').title()}Service"
                entity_name = unit_name.replace('.', '').title()
                
                response["generated_files"][f"src/main/java/com/modernized/service/{service_name}.java"] = f"""package com.modernized.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import com.modernized.repository.{entity_name}Repository;
import com.modernized.entity.{entity_name};
import com.modernized.dto.{entity_name}DTO;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Service para {unit_name}
 * Contém lógica de negócio modernizada da unit Delphi original
 */
@Service
public class {service_name} {{
    
    @Autowired
    private {entity_name}Repository repository;
    
    public List<{entity_name}DTO> findAll() {{
        return repository.findAll().stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
    }}
    
    public {entity_name}DTO findById(Long id) {{
        return repository.findById(id)
                .map(this::toDTO)
                .orElseThrow(() -> new RuntimeException("{entity_name} não encontrado"));
    }}
    
    public {entity_name}DTO save({entity_name}DTO dto) {{
        {entity_name} entity = toEntity(dto);
        return toDTO(repository.save(entity));
    }}
    
    public void deleteById(Long id) {{
        repository.deleteById(id);
    }}
    
    private {entity_name}DTO toDTO({entity_name} entity) {{
        // Implementar conversão Entity -> DTO
        return new {entity_name}DTO();
    }}
    
    private {entity_name} toEntity({entity_name}DTO dto) {{
        // Implementar conversão DTO -> Entity
        return new {entity_name}();
    }}
}}"""
        
        # Adiciona configuração baseada no projeto real
        response["generated_files"]["src/main/resources/application.yml"] = f"""# Configuração para projeto modernizado: {project_name}
# Baseado na análise de {len(units_analysis)} units e {len(forms_analysis)} forms

spring:
  application:
    name: {project_name.lower().replace(' ', '-')}
  
  datasource:
    url: jdbc:h2:mem:testdb
    driverClassName: org.h2.Driver
    username: sa
    password: 
    
  jpa:
    database-platform: org.hibernate.dialect.H2Dialect
    hibernate:
      ddl-auto: create-drop
    show-sql: true
    
  h2:
    console:
      enabled: true
      path: /h2-console
      
server:
  port: 8080
  
logging:
  level:
    com.modernized: DEBUG
    org.springframework.web: DEBUG
"""
        
        logger.info(f"✅ Análise offline concluída - {len(response['generated_files'])} arquivos gerados")
        return response

    def _generate_mock_response(self, delphi_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera resposta mock quando APIs falham
        
        Args:
            delphi_structure: Estrutura do projeto Delphi
            
        Returns:
            Resposta mock com estrutura básica Java Spring Boot
        """
        logger.info("🔄 Gerando código mock devido a falhas nas APIs")
        
        # Extrai informações básicas da estrutura
        project_name = delphi_structure.get('project_name', 'ModernizedProject')
        
        mock_response = {
            "project_name": project_name,
            "package_name": f"com.modernized.{project_name.lower()}",
            "generated_files": {
                "src/main/java/com/modernized/ModernizedApplication.java": """package com.modernized;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ModernizedApplication {
    public static void main(String[] args) {
        SpringApplication.run(ModernizedApplication.class, args);
    }
}""",
                "src/main/java/com/modernized/controller/MainController.java": """package com.modernized.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.ResponseEntity;

@RestController
@RequestMapping("/api")
public class MainController {
    
    @GetMapping("/status")
    public ResponseEntity<String> getStatus() {
        return ResponseEntity.ok("Sistema modernizado funcionando");
    }
}""",
                "src/main/resources/application.properties": """# Database configuration
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=password
spring.h2.console.enabled=true

# JPA configuration
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true

# Server configuration
server.port=8080""",
                "pom.xml": """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.modernized</groupId>
    <artifactId>modernized-project</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>Modernized Project</name>
    <description>Projeto modernizado do Delphi para Java Spring Boot</description>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>"""
            },
            "conversion_notes": [
                "⚠️ Este é um código mock gerado devido a falhas nas APIs",
                "🔄 Estrutura básica Java Spring Boot criada",
                "📝 Contém aplicação principal, controller básico e configurações",
                "🚀 Projeto pronto para executar com 'mvn spring-boot:run'",
                "💡 Para conversão completa, configure as APIs Groq ou Ollama"
            ],
            "generated_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "generation_method": "mock_fallback"
        }
        
        return mock_response
    
    def _reduce_prompt_size(self, prompt: str) -> str:
        """
        Reduz o tamanho do prompt removendo partes menos críticas
        
        Args:
            prompt: Prompt original
            
        Returns:
            Prompt reduzido mantendo informações essenciais
        """
        logger.info("🔄 Reduzindo tamanho do prompt...")
        
        # Divide o prompt em seções
        sections = prompt.split('\n\n')
        
        # Identifica seções críticas (que devem ser mantidas)
        critical_sections = []
        optional_sections = []
        
        for section in sections:
            section_lower = section.lower()
            
            # Seções críticas que devem ser mantidas
            if any(keyword in section_lower for keyword in [
                'você é um especialista', 'sua tarefa', 'objetivo',
                'projeto delphi', 'estrutura java', 'formato de saída'
            ]):
                critical_sections.append(section)
            else:
                optional_sections.append(section)
        
        # Reconstrói o prompt com seções críticas
        reduced_prompt = '\n\n'.join(critical_sections)
        
        # Adiciona seções opcionais até um limite razoável
        max_size = 4000  # Limite conservador para tokens
        current_size = len(reduced_prompt)
        
        for section in optional_sections:
            if current_size + len(section) < max_size:
                reduced_prompt += '\n\n' + section
                current_size += len(section)
            else:
                break
        
        # Se ainda estiver muito grande, reduz mais drasticamente
        if len(reduced_prompt) > max_size:
            reduced_prompt = reduced_prompt[:max_size] + "\n\n[...conteúdo truncado para atender limite de tokens...]"
        
        logger.info(f"Prompt reduzido de {len(prompt)} para {len(reduced_prompt)} caracteres")
        return reduced_prompt
    
    def _reduce_prompt_for_ollama(self, prompt: str) -> str:
        """
        Reduz o prompt especificamente para o modelo Ollama menor (deepseek-r1:1.5b)
        """
        try:
            # Limite mais agressivo para o modelo menor
            max_size = 2000  # Limite mais conservador para o modelo 1.5b
            
            if len(prompt) <= max_size:
                return prompt
            
            logger.info(f"🔄 Reduzindo prompt para Ollama de {len(prompt)} caracteres")
            
            # Seções críticas que devem ser mantidas
            critical_sections = []
            
            # Adiciona contexto básico
            if "JUNIM" in prompt:
                critical_sections.append("CONTEXTO: Migração Delphi para Java Spring Boot usando JUNIM")
            
            # Extrai apenas as informações mais essenciais
            lines = prompt.split('\n')
            essential_lines = []
            
            for line in lines:
                if line is not None:
                    line = line.strip()
                    # Mantém linhas com informações estruturais importantes
                    if any(keyword in line.lower() for keyword in [
                        'class ', 'procedure ', 'function ', 'form', 'datamodule',
                        'controller', 'service', 'repository', 'entity'
                    ]):
                        essential_lines.append(line)
                # Mantém definições de campos/propriedades
                elif ':' in line and any(keyword in line.lower() for keyword in [
                    'string', 'integer', 'boolean', 'tfield', 'tquery'
                ]):
                    essential_lines.append(line)
            
            # Reconstrói prompt essencial
            reduced_prompt = '\n'.join(essential_lines)
            
            # Adiciona instruções básicas
            basic_instructions = """
TAREFA: Gere código Java Spring Boot baseado no código Delphi fornecido.
FORMATO: Retorne JSON com estrutura: {"files": [{"name": "nome.java", "content": "código"}]}
FOCO: Mantenha a lógica de negócio principal e use padrões Spring Boot.
"""
            
            # Combina tudo respeitando o limite
            final_prompt = basic_instructions + "\n\nCÓDIGO DELPHI:\n" + reduced_prompt
            
            # Trunca se ainda estiver muito grande
            if len(final_prompt) > max_size:
                final_prompt = final_prompt[:max_size - 100] + "\n\n[...truncado para modelo menor...]"
            
            logger.info(f"✅ Prompt reduzido para {len(final_prompt)} caracteres para Ollama")
            return final_prompt
            
        except Exception as e:
            logger.error(f"Erro ao reduzir prompt para Ollama: {str(e)}")
            # Retorna uma versão muito simplificada
            return f"Converta este código Delphi para Java Spring Boot:\n\n{prompt[:1000]}"
    
    def _get_prompt_from_manager(self, prompt_type: str, context: str = "") -> str:
        """Obtém prompt do gerenciador de prompts se disponível"""
        if not self.prompt_manager:
            return ""
        
        try:
            # Mapeia tipos de prompt para métodos do PromptManager
            prompt_methods = {
                'analysis': 'get_analysis_prompt',
                'backend_analysis': 'get_backend_analysis_prompt',
                'conversion': 'get_spring_conversion_prompt',
                'backend_conversion': 'get_backend_conversion_prompt',
                'modernization': 'get_modernization_prompt',
                'testing': 'get_testing_prompt',
                'functionality_mapping': 'get_functionality_mapping_prompt',
                'mermaid_diagram': 'get_mermaid_diagram_prompt',
                'documentation': 'get_documentation_enhanced_prompt'
            }
            
            method_name = prompt_methods.get(prompt_type)
            if method_name and hasattr(self.prompt_manager, method_name):
                method = getattr(self.prompt_manager, method_name)
                if context and method_name in ['get_spring_conversion_prompt', 'get_backend_conversion_prompt']:
                    return method(context)
                else:
                    return method()
            else:
                logger.warning(f"Método de prompt não encontrado para tipo: {prompt_type}")
                return ""
                
        except Exception as e:
            logger.error(f"Erro ao obter prompt do gerenciador: {str(e)}")
            return ""

    def generate_analysis(self, project_data: str, prompt_type: str = "analysis") -> str:
        """
        Gera análise do projeto usando prompts do diretório
        
        Args:
            project_data: Dados do projeto analisado
            prompt_type: Tipo de prompt a ser usado
            
        Returns:
            Análise gerada
        """
        try:
            # Obtém prompt do gerenciador
            prompt = self._get_prompt_from_manager(prompt_type)
            
            if not prompt:
                # Fallback para prompt padrão
                prompt = """
Analise o projeto Delphi fornecido e gere uma análise técnica detalhada em formato Markdown.

INSTRUÇÕES:
- Foque em aspectos de backend
- Identifique funcionalidades específicas
- Documente padrões arquiteturais
- Sugira modernização para Java Spring Boot
- Seja específico e use dados reais do projeto
"""
            
            # Combina prompt com dados do projeto
            full_prompt = f"{prompt}\n\n## DADOS DO PROJETO:\n{project_data}"
            
            # Gera resposta
            response = self.generate_response(full_prompt)
            return response if response else "Erro ao gerar análise"
            
        except Exception as e:
            logger.error(f"Erro ao gerar análise: {str(e)}")
            return f"Erro ao gerar análise: {str(e)}"

    def generate_modernization(self, project_data: str, analysis_context: str = "", prompt_type: str = "modernization") -> str:
        """
        Gera código modernizado usando prompts do diretório
        
        Args:
            project_data: Dados do projeto Delphi
            analysis_context: Contexto da análise prévia
            prompt_type: Tipo de prompt a ser usado
            
        Returns:
            Código modernizado gerado
        """
        try:
            # Obtém prompt do gerenciador
            prompt = self._get_prompt_from_manager(prompt_type, analysis_context)
            
            if not prompt:
                # Fallback para prompt padrão
                prompt = """
Converta o código Delphi fornecido para Java Spring Boot.

INSTRUÇÕES:
- Gere código Java funcional
- Use padrões Spring Boot
- Implemente arquitetura em camadas
- Mantenha funcionalidades originais
- Foque apenas em backend
"""
            
            # Combina prompt com dados do projeto
            context = f"## DADOS DO PROJETO:\n{project_data}"
            if analysis_context:
                context += f"\n\n## CONTEXTO DA ANÁLISE:\n{analysis_context}"
            
            full_prompt = f"{prompt}\n\n{context}"
            
            # Gera resposta
            response = self.generate_response(full_prompt)
            return response if response else "Erro ao gerar código modernizado"
            
        except Exception as e:
            logger.error(f"Erro ao gerar código modernizado: {str(e)}")
            return f"Erro ao gerar código modernizado: {str(e)}"

    def generate_documentation(self, project_data: str, analysis_results: Dict[str, Any] = None, prompt_type: str = "documentation") -> str:
        """
        Gera documentação usando prompts do diretório
        
        Args:
            project_data: Dados do projeto
            analysis_results: Resultados da análise
            prompt_type: Tipo de prompt a ser usado
            
        Returns:
            Documentação gerada
        """
        try:
            # Obtém prompt do gerenciador
            if self.prompt_manager and hasattr(self.prompt_manager, 'get_documentation_enhanced_prompt'):
                prompt = self.prompt_manager.get_documentation_enhanced_prompt(analysis_results)
            else:
                prompt = self._get_prompt_from_manager(prompt_type)
            
            if not prompt:
                # Fallback para prompt padrão
                prompt = """
Gere documentação técnica detalhada do projeto em formato Markdown.

INSTRUÇÕES:
- Use dados reais do projeto
- Seja específico e objetivo
- Foque em aspectos técnicos
- Documente funcionalidades identificadas
"""
            
            # Combina prompt com dados do projeto
            full_prompt = f"{prompt}\n\n## DADOS DO PROJETO:\n{project_data}"
            
            # Gera resposta
            response = self.generate_response(full_prompt)
            return response if response else "Erro ao gerar documentação"
            
        except Exception as e:
            logger.error(f"Erro ao gerar documentação: {str(e)}")
            return f"Erro ao gerar documentação: {str(e)}"

    def generate_tests(self, java_code: str, prompt_type: str = "testing") -> str:
        """
        Gera testes usando prompts do diretório
        
        Args:
            java_code: Código Java para gerar testes
            prompt_type: Tipo de prompt a ser usado
            
        Returns:
            Testes gerados
        """
        try:
            # Obtém prompt do gerenciador
            prompt = self._get_prompt_from_manager(prompt_type)
            
            if not prompt:
                # Fallback para prompt padrão
                prompt = """
Gere testes unitários e de integração para o código Java fornecido.

INSTRUÇÕES:
- Use JUnit 5 e Mockito
- Implemente testes de Controllers, Services e Repositories
- Cubra cenários positivos e negativos
- Use TestContainers para testes de integração
- Garanta cobertura adequada
"""
            
            # Combina prompt com código Java
            full_prompt = f"{prompt}\n\n## CÓDIGO JAVA:\n{java_code}"
            
            # Gera resposta
            response = self.generate_response(full_prompt)
            return response if response else "Erro ao gerar testes"
            
        except Exception as e:
            logger.error(f"Erro ao gerar testes: {str(e)}")
            return f"Erro ao gerar testes: {str(e)}"
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Gera resposta usando LLM"""
        try:
            # Validação básica
            if not prompt or not prompt.strip():
                raise ValueError("Prompt não pode estar vazio")
            
            # Limita tamanho do prompt para evitar erros
            if len(prompt) > 30000:
                prompt = prompt[:30000] + "..."
                logger.warning("⚠️ Prompt truncado para 30k caracteres")
            
            # Gera resposta
            response = self._generate_response_internal(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro na geração otimizada: {str(e)}")
            return None

    def _generate_response_internal(self, prompt: str) -> Optional[str]:
        """
        Método interno para geração de resposta usando prompts especializados
        
        Args:
            prompt: Prompt para o LLM
            
        Returns:
            Resposta gerada ou None se falhar
        """
        try:
            # Verifica se prompt é None ou vazio
            if not prompt:
                logger.error("❌ Prompt vazio ou None fornecido")
                return None
                
            # Garante que prompt seja string e não None antes de strip
            prompt_str = str(prompt) if prompt is not None else ""
            if not prompt_str.strip():
                logger.error("❌ Prompt vazio fornecido")
                return None
            
            logger.info(f"🚀 Gerando resposta com prompt de {len(prompt_str)} caracteres")
            
            # Se tem prompt_manager, usa configurações otimizadas
            if self.prompt_manager:
                logger.info("✅ Usando prompts especializados")
            else:
                logger.info("⚠️ Usando prompt padrão (prompts especializados não disponíveis)")
            
            # Tenta gerar com Groq primeiro (se configurado)
            response = None
            groq_key = self.config.get('groq_api_key', '') or ''
            groq_key = groq_key.strip() if groq_key else ''
            
            if groq_key:
                logger.info("🚀 Tentando geração com Groq API...")
                try:
                    response = self._generate_with_groq(prompt_str)
                    if response and isinstance(response, str) and response.strip():
                        logger.info("✅ Resposta gerada com sucesso via Groq")
                        return response.strip()
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"❌ Erro na geração com Groq: {error_msg}")
                    
                    # Se falhou por tamanho, tenta prompt reduzido
                    if "413" in error_msg or "too large" in error_msg.lower():
                        logger.info("🔄 Tentando com prompt reduzido devido ao limite de tokens...")
                        reduced_prompt = self._reduce_prompt_size(prompt_str)
                        try:
                            response = self._generate_with_groq(reduced_prompt)
                            if response and isinstance(response, str) and response.strip():
                                logger.info("✅ Resposta gerada com prompt reduzido via Groq")
                                return response.strip()
                        except Exception as e2:
                            logger.error(f"❌ Erro também com prompt reduzido: {str(e2)}")
            else:
                logger.info("🔄 Chave Groq não configurada, tentando Ollama...")
                
            # Se Groq falhou ou não estava configurado, tenta Ollama
            if not response and self.ollama_client:
                logger.info("🔄 Tentando geração com Ollama...")
                try:
                    response = self._generate_with_ollama(prompt_str)
                    if response and isinstance(response, str) and response.strip():
                        logger.info("✅ Resposta gerada com sucesso via Ollama")
                        return response.strip()
                except Exception as e:
                    logger.error(f"❌ Erro na geração com Ollama: {str(e)}")
            
            # Se ambos falharam
            if not response:
                if not groq_key and not self.ollama_client:
                    logger.error("❌ Nenhuma API configurada! Configure Groq API key ou inicie o Ollama.")
                    return "Erro: Nenhuma API de LLM configurada. Configure Groq API key ou inicie o Ollama."
                else:
                    logger.error("❌ Todas as APIs falharam na geração")
                    return "Erro: Falha na geração com todas as APIs disponíveis."
            
            # Se chegou aqui, algo deu errado
            logger.error("❌ Resposta vazia ou nula")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de resposta: {str(e)}")
            return f"Erro na geração: {str(e)}"
    
    def generate_content(self, prompt: str) -> str:
        """
        Método de compatibilidade para generate_content
        Usa o método generate_response internamente
        """
        try:
            result = self.generate_response(prompt)
            if result is None:
                return "Erro: Não foi possível gerar conteúdo"
            return result
        except Exception as e:
            logger.error(f"❌ Erro no generate_content: {str(e)}")
            return f"Erro na geração de conteúdo: {str(e)}"
