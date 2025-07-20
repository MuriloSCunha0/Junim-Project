"""
Sistema de prompts especializados LIMPO para modernização Delphi → Java Spring
VERSÃO SIMPLIFICADA - Apenas funções essenciais
"""

import os
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptManager:
    """Gerenciador SIMPLIFICADO de prompts especializados do JUNIM"""
    
    def __init__(self, performance_mode: str = 'fast', model_name: str = 'codellama:7b'):
        """Inicializa o gerenciador simplificado"""
        self.prompts_dir = Path(__file__).parent
        self.base_prompt = self._load_base_prompt()
        self._prompt_cache = {}
        self.model_name = model_name
        self.model_type = self._detect_model_type(model_name)
        self.performance_mode = performance_mode
        self._load_universal_config()
        
        logger.info(f"🚀 PromptManager LIMPO - Modelo: {model_name} - Modo: {performance_mode}")
    
    def set_model(self, model_name: str):
        """Altera o modelo dinamicamente"""
        self.model_name = model_name
        self.model_type = self._detect_model_type(model_name)
        self._load_universal_config()
        logger.info(f"🔄 Modelo alterado para: {model_name}")
    
    def _detect_model_type(self, model_name: str) -> str:
        """Detecta o tipo de modelo"""
        model_lower = model_name.lower()
        if 'deepseek-r1' in model_lower:
            return 'deepseek-r1'
        elif 'codellama' in model_lower:
            return 'codellama'
        elif 'llama3' in model_lower:
            return 'llama3'
        elif 'mistral' in model_lower:
            return 'mistral'
        else:
            return 'generic'
    
    def set_performance_mode(self, mode: str):
        """Altera o modo de performance"""
        if mode in ['fast', 'balanced', 'quality']:
            self.performance_mode = mode
            logger.info(f"🔄 Modo alterado para: {mode}")
    
    def _load_universal_config(self):
        """Carrega configurações universais"""
        try:
            import importlib.util
            config_file = Path(__file__).parent.parent / 'config' / 'universal_model_config.py'
            spec = importlib.util.spec_from_file_location("universal_model_config", config_file)
            universal_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(universal_module)
            
            self.combine_prompts_universal = universal_module.combine_prompts_universal
            logger.info(f"✅ Configurações universais carregadas")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar configurações: {str(e)}")
            self.combine_prompts_universal = lambda x, y, z, w: x
    
    def _load_prompt_from_file(self, filename: str) -> str:
        """Carrega prompt de arquivo com cache"""
        cache_key = f"prompt_{filename}"
        
        if cache_key in self._prompt_cache:
            return self._prompt_cache[cache_key]
            
        try:
            prompt_path = self.prompts_dir / f"{filename}.txt"
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._prompt_cache[cache_key] = content
                    return content
            else:
                logger.warning(f"Arquivo não encontrado: {filename}.txt")
                return ""
        except Exception as e:
            logger.error(f"Erro ao carregar prompt {filename}: {str(e)}")
            return ""
    
    def _load_base_prompt(self) -> str:
        """Carrega o prompt base"""
        try:
            base_path = self.prompts_dir / "prompt_base.txt"
            with open(base_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return """Você é um ESPECIALISTA em modernização de sistemas Delphi para Java Spring Boot.

MISSÃO: Analisar projetos Delphi e gerar código Java Spring Boot funcional.

RESPONSABILIDADES:
1. ANÁLISE: Extrair funcionalidades e regras de negócio
2. CONVERSÃO: Gerar código Java Spring Boot funcional
3. TESTES: Criar testes unitários abrangentes

TECNOLOGIAS ALVO:
- Java Spring Boot 3.x
- Spring Data JPA / Hibernate
- Spring Web (REST APIs)
- JUnit 5 + Mockito"""

    def _enhance_prompt_for_model(self, prompt: str, task_type: str = 'analysis') -> str:
        """Otimiza prompt para o modelo atual"""
        try:
            enhanced_prompt = self.combine_prompts_universal(prompt, task_type, self.model_name, self.performance_mode)
            logger.info(f"✅ Prompt otimizado para {self.model_name}")
            return enhanced_prompt
        except Exception as e:
            logger.warning(f"⚠️ Erro ao otimizar prompt: {str(e)}")
            return prompt
    
    # ============================================================================
    # FUNÇÕES PRINCIPAIS (apenas 4 essenciais)
    # ============================================================================

    def get_analysis_prompt(self) -> str:
        """Retorna prompt para análise de código Delphi"""
        base_prompt = self.get_backend_analysis_prompt()
        return self._enhance_prompt_for_model(base_prompt, 'analysis')

    def get_backend_analysis_prompt(self) -> str:
        """Prompt para análise de backend Delphi"""
        file_prompt = self._load_prompt_from_file("backend_analysis_prompt")
        if file_prompt:
            return f"{self.base_prompt}\\n\\n{file_prompt}"
        
        return f"""
{self.base_prompt}

## ANÁLISE DE BACKEND DELPHI

Analise o código Delphi focando EXCLUSIVAMENTE no backend:

### EXTRAIR:
1. **Entidades de Dados** - Estruturas, tabelas, relacionamentos
2. **Regras de Negócio** - Validações, cálculos, processamentos
3. **Operações CRUD** - Inserir, consultar, atualizar, deletar
4. **Integrações** - APIs, serviços externos, banco de dados

### MAPEAR PARA SPRING BOOT:
- Entidades JPA (@Entity)
- Repositories (@Repository)
- Services (@Service) 
- Controllers (@RestController)

**FORMATO JSON OBRIGATÓRIO:**
{{
  "entities": [{{ "name": "Cliente", "fields": ["id", "nome"], "relationships": [] }}],
  "business_rules": ["Validar CPF", "Calcular desconto"],
  "operations": ["cadastrar", "consultar", "atualizar"],
  "integrations": ["database", "api_externa"]
}}
"""

    def get_backend_conversion_prompt(self, docs_context: str = "") -> str:
        """Prompt para conversão de backend"""
        file_prompt = self._load_prompt_from_file("backend_conversion_prompt")
        if file_prompt:
            base_prompt = f"{self.base_prompt}\\n\\n{file_prompt}"
            if docs_context:
                return f"{base_prompt}\\n\\n## CONTEXTO:\\n{docs_context}"
            return base_prompt
        
        prompt = f"""
{self.base_prompt}

## CONVERSÃO DELPHI → SPRING BOOT

Execute conversão sistemática do backend:

### ESTRUTURA OBRIGATÓRIA:
```
src/main/java/com/empresa/sistema/
├── entity/          # Entidades JPA
├── repository/      # Repositories
├── service/         # Lógica de negócio
├── controller/      # Controllers REST
└── dto/            # DTOs
```

### IMPLEMENTAR:
1. **@Entity** - Mapeamento JPA com relacionamentos
2. **@Repository** - Interfaces com queries customizadas
3. **@Service** - Lógica de negócio com @Transactional
4. **@RestController** - APIs REST completas

**FORMATO JSON OBRIGATÓRIO:**
{{
  "files": [
    {{
      "path": "src/main/java/com/empresa/sistema/entity/Cliente.java",
      "content": "@Entity\\npublic class Cliente {{ ... }}"
    }}
  ]
}}
"""
        
        enhanced_prompt = self._enhance_prompt_for_model(prompt, 'conversion')
        if docs_context:
            return f"{enhanced_prompt}\\n\\n## CONTEXTO:\\n{docs_context}"
        return enhanced_prompt

    def get_testing_prompt(self) -> str:
        """Prompt para geração de testes"""
        file_prompt = self._load_prompt_from_file("testing_prompt")
        if file_prompt:
            base_prompt = f"{self.base_prompt}\\n\\n{file_prompt}"
        else:
            base_prompt = f"""
{self.base_prompt}

## GERAÇÃO DE TESTES UNITÁRIOS

Crie testes completos para o código Java:

### ESTRUTURA DE TESTES:
1. **Controller Tests** - @WebMvcTest, MockMvc
2. **Service Tests** - @ExtendWith(MockitoExtension.class)
3. **Repository Tests** - @DataJpaTest

### IMPLEMENTAR:
- Testes de todos os endpoints
- Mockagem de dependências
- Validação de entrada/saída
- Testes de exceções

**FORMATO JSON:**
{{
  "files": [
    {{
      "path": "src/test/java/.../ControllerTest.java",
      "content": "@SpringBootTest\\npublic class Test {{ ... }}"
    }}
  ]
}}
"""
        
        return self._enhance_prompt_for_model(base_prompt, 'testing')

    def get_functionality_mapping_prompt(self) -> str:
        """Prompt para mapeamento de funcionalidades"""
        file_prompt = self._load_prompt_from_file("functionality_mapping_prompt")
        if file_prompt:
            base_prompt = f"{self.base_prompt}\\n\\n{file_prompt}"
        else:
            base_prompt = f"""
{self.base_prompt}

## MAPEAMENTO DE FUNCIONALIDADES

Mapeie funcionalidades Delphi para Spring Boot:

### IDENTIFICAR:
1. **Formulários** → Controllers REST
2. **DataModules** → Services + Repositories
3. **Componentes DB** → Entidades JPA
4. **Validações** → Bean Validation

**FORMATO JSON:**
{{
  "mappings": [
    {{
      "delphi_component": "TClienteForm",
      "spring_equivalent": "ClienteController",
      "functionality": "CRUD de clientes"
    }}
  ]
}}
"""
        
        return self._enhance_prompt_for_model(base_prompt, 'functionality_mapping')

    # ============================================================================
    # COMPATIBILIDADE (aliases para manter código existente funcionando)
    # ============================================================================
    
    def get_spring_conversion_prompt(self, documentation_context: str = "") -> str:
        """Alias para compatibilidade"""
        return self.get_backend_conversion_prompt(documentation_context)
