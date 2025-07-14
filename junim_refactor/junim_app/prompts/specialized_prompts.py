"""
Sistema de prompts especializados para modernização Delphi → Java Spring
"""

import os
from typing import Dict, Any, List
from pathlib import Path

class PromptManager:
    """Gerenciador de prompts especializados do JUNIM"""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent
        self.base_prompt = self._load_base_prompt()
    
    def _load_base_prompt(self) -> str:
        """Carrega o prompt base do arquivo"""
        try:
            base_path = self.prompts_dir / "prompt_base.txt"
            with open(base_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return self._get_fallback_base_prompt()
    
    def _get_fallback_base_prompt(self) -> str:
        """Prompt base de fallback se arquivo não existir"""
        return """
Você é um especialista em modernização de sistemas legados, especificamente na conversão de projetos Delphi para Java Spring Boot.

Suas responsabilidades:
1. Analisar código Delphi existente
2. Criar equivalentes Java Spring modernos
3. Manter a lógica de negócio original
4. Aplicar as melhores práticas do Spring Boot
5. Garantir que o código seja limpo, testável e manutenível

Diretrizes gerais:
- Use anotações Spring apropriadas
- Implemente padrões Repository, Service e Controller
- Mantenha separação clara de responsabilidades
- Aplique injeção de dependências
- Use JPA/Hibernate para persistência
- Crie APIs REST bem estruturadas
"""

    def get_analysis_prompt(self) -> str:
        """Prompt aprimorado para análise de código Delphi focado em funcionalidades reais, entendimento do sistema e modernização."""
        return f"""
{self.base_prompt}

## TAREFA: ANÁLISE PROFUNDA DE SISTEMA DELPHI

Você deve atuar como um analista de sistemas experiente em modernização Delphi→Java, com foco em identificar e explicar as FUNCIONALIDADES REAIS do sistema, não apenas descrever o código.

### 1. FUNCIONALIDADES DO SISTEMA
- Liste e explique as principais funcionalidades do sistema, descrevendo o que cada uma faz, para quem é destinada e qual seu objetivo de negócio.
- Para cada funcionalidade, forneça um exemplo prático de uso (ex: "O usuário pode cadastrar um novo cliente preenchendo...", "O sistema gera relatórios financeiros mensais...").

### 2. CASOS DE USO E FLUXOS DE TRABALHO
- Identifique os principais casos de uso do sistema e descreva os fluxos de trabalho associados, passo a passo, em linguagem natural.
- Se possível, apresente diagramas textuais (ex: fluxogramas simples usando texto) para ilustrar os fluxos.

### 3. REGRAS DE NEGÓCIO
- Extraia e explique as regras de negócio explícitas e implícitas encontradas no código.
- Relacione essas regras às funcionalidades e casos de uso.

### 4. ENTIDADES E RELACIONAMENTOS
- Liste as principais entidades do sistema, seus atributos e relacionamentos.
- Explique como cada entidade se relaciona com as funcionalidades e fluxos.

### 5. REQUISITOS FUNCIONAIS E NÃO FUNCIONAIS
- Explicite requisitos funcionais (o que o sistema deve fazer) e não funcionais (performance, segurança, usabilidade, etc.) identificados.

### 6. RESUMO EXECUTIVO
- Gere um resumo executivo do sistema, explicando seu propósito, público-alvo e principais diferenciais, em linguagem acessível para gestores e desenvolvedores.

### 7. EXPLICAÇÕES DIDÁTICAS
- Sempre que possível, explique em linguagem natural o "porquê" de cada parte do sistema, facilitando o entendimento para quem não conhece Delphi.

---
Estruture a resposta em seções claras, com títulos, listas e exemplos. O objetivo é gerar documentação que facilite a modernização e o entendimento do sistema por humanos e por IA.
"""

    def get_spring_conversion_prompt(self, documentation_context: str = "") -> str:
        """Prompt para conversão para Spring Boot com contexto da documentação"""
        context_section = ""
        if documentation_context:
            context_section = f"""
## CONTEXTO DA DOCUMENTAÇÃO GERADA

{documentation_context}

Use essas informações como base para a conversão, garantindo que:
- Todos os requisitos funcionais sejam atendidos
- As características técnicas sejam preservadas
- Os fluxos de execução e dados sejam mantidos
- As correlações Delphi→Java sejam aplicadas
"""
        
        return f"""
{self.base_prompt}

{context_section}

## TAREFA: CONVERSÃO PARA JAVA SPRING BOOT

Converta o código Delphi fornecido para Java Spring Boot seguindo estas diretrizes:

### 1. ESTRUTURA DE PROJETO
```
src/main/java/com/projeto/
├── config/          # Configurações Spring
├── controller/      # REST Controllers
├── service/         # Lógica de negócio
├── repository/      # Acesso a dados
├── entity/          # Entidades JPA
├── dto/             # Data Transfer Objects
└── exception/       # Tratamento de exceções
```

### 2. MAPEAMENTOS PADRÃO

**TForm → @RestController**:
- Eventos de botão → Endpoints REST
- Validações de formulário → Bean Validation
- Navegação entre forms → Redirecionamentos HTTP

**TDataModule → @Repository + @Service**:
- Queries → Métodos Repository
- Transações → @Transactional
- Conexões → DataSource configurado

**Classes de negócio → @Service**:
- Procedimentos → Métodos públicos
- Validações → Métodos de validação
- Cálculos → Métodos utilitários

### 3. TECNOLOGIAS A USAR
- Spring Boot 3.x
- Spring Data JPA
- Spring Web MVC
- Bean Validation
- Lombok (opcional)
- H2/PostgreSQL para banco

### 4. PADRÕES A APLICAR
- Repository Pattern
- Service Layer Pattern
- DTO Pattern
- Exception Handling
- Dependency Injection

### 5. ESTRUTURA DE RESPOSTA
Para cada arquivo Delphi, forneça:
1. **Análise**: O que o arquivo faz
2. **Mapeamento**: Como converter para Spring
3. **Código Java**: Implementação completa
4. **Testes**: Testes unitários básicos
5. **Configuração**: Configurações necessárias

Gere código limpo, bem documentado e seguindo as melhores práticas do Spring Boot.
"""

    def get_entity_mapping_prompt(self) -> str:
        """Prompt para mapeamento de entidades de banco"""
        return f"""
{self.base_prompt}

## TAREFA: MAPEAMENTO DE ENTIDADES JPA

Analise as operações de banco de dados do código Delphi e crie:

### 1. ENTIDADES JPA
- Classes com anotações @Entity
- Mapeamento de campos com @Column
- Relacionamentos com @OneToMany, @ManyToOne, etc.
- Chaves primárias com @Id e @GeneratedValue

### 2. REPOSITORIES
- Interfaces estendendo JpaRepository
- Queries customizadas com @Query
- Métodos de busca por convenção

### 3. EXEMPLO DE ESTRUTURA
```java
@Entity
@Table(name = "customers")
public class Customer {{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    // ... outros campos
}}

@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {{
    List<Customer> findByActiveTrue();
    
    @Query("SELECT c FROM Customer c WHERE c.email = :email")
    Optional<Customer> findByEmail(@Param("email") String email);
}}
```

Mantenha a estrutura de dados original mas aplique as melhores práticas JPA.
"""

    def get_api_design_prompt(self) -> str:
        """Prompt para design de APIs REST"""
        return f"""
{self.base_prompt}

## TAREFA: DESIGN DE API REST

Converta as operações de formulário Delphi em APIs REST seguindo:

### 1. PADRÕES REST
- GET para consultas
- POST para criação
- PUT para atualização completa
- PATCH para atualização parcial
- DELETE para remoção

### 2. ESTRUTURA DE CONTROLLER
```java
@RestController
@RequestMapping("/api/customers")
@Validated
public class CustomerController {{
    
    @Autowired
    private CustomerService customerService;
    
    @GetMapping
    public ResponseEntity<List<CustomerDTO>> getAllCustomers() {{
        // implementação
    }}
    
    @PostMapping
    public ResponseEntity<CustomerDTO> createCustomer(@Valid @RequestBody CustomerDTO dto) {{
        // implementação
    }}
    
    // ... outros endpoints
}}
```

### 3. DTOs E VALIDAÇÃO
- Classes DTO para entrada e saída
- Validações com Bean Validation
- Mapeamento entre Entity e DTO

### 4. TRATAMENTO DE ERROS
- @ExceptionHandler para erros específicos
- ResponseEntity com códigos HTTP apropriados
- Mensagens de erro padronizadas

### 5. DOCUMENTAÇÃO
- Comentários Javadoc
- Preparação para Swagger/OpenAPI

Transforme cada ação de formulário em um endpoint REST bem estruturado.
"""

    def get_service_layer_prompt(self) -> str:
        """Prompt para camada de serviços"""
        return f"""
{self.base_prompt}

## TAREFA: IMPLEMENTAÇÃO DA CAMADA DE SERVIÇOS

Extraia a lógica de negócio do código Delphi para serviços Spring:

### 1. ESTRUTURA DE SERVICE
```java
@Service
@Transactional
public class CustomerService {{
    
    @Autowired
    private CustomerRepository customerRepository;
    
    public CustomerDTO createCustomer(CustomerDTO dto) {{
        // validações de negócio
        // conversão DTO → Entity
        // persistência
        // conversão Entity → DTO
        // retorno
    }}
}}
```

### 2. RESPONSABILIDADES
- Validações de negócio
- Orquestração de operações
- Transações
- Conversão entre DTOs e Entities
- Tratamento de exceções de negócio

### 3. PADRÕES A APLICAR
- Um serviço por agregado de negócio
- Métodos públicos para operações principais
- Métodos privados para lógica auxiliar
- Exceptions customizadas para erros de negócio

### 4. TRANSAÇÕES
- @Transactional em operações que modificam dados
- Propagação adequada de transações
- Rollback em exceções de negócio

Mantenha toda a lógica de negócio original mas organize de forma modular e testável.
"""

    def get_testing_prompt(self) -> str:
        """Prompt para geração de testes"""
        return f"""
{self.base_prompt}

## TAREFA: GERAÇÃO DE TESTES UNITÁRIOS

Crie testes abrangentes para o código Java gerado:

### 1. TESTES DE CONTROLLER
```java
@WebMvcTest(CustomerController.class)
class CustomerControllerTest {{
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private CustomerService customerService;
    
    @Test
    void shouldCreateCustomer() throws Exception {{
        // implementação do teste
    }}
}}
```

### 2. TESTES DE SERVICE
- Mocks de repositories
- Validação de lógica de negócio
- Cenários de sucesso e erro
- Validação de transações

### 3. TESTES DE REPOSITORY
- @DataJpaTest para testes de persistência
- Validação de queries customizadas
- Testes de relacionamentos

### 4. COBERTURA
- Teste todas as operações principais
- Cenários de erro e exceções
- Validações de entrada
- Regras de negócio

Gere testes que garantam a qualidade e confiabilidade do código convertido.
"""

    def get_documentation_enhanced_prompt(self, analysis_results: Dict[str, Any], 
                                        generated_docs: Dict[str, str]) -> str:
        """Prompt enriquecido com documentação gerada do projeto"""
        
        # Carrega conteúdo dos documentos principais
        doc_content = self._load_documentation_content(generated_docs)
        
        return f"""
{self.base_prompt}

## CONTEXTO COMPLETO DO PROJETO ANALISADO

### RESUMO DA ANÁLISE
- **Projeto**: {analysis_results.get('metadata', {}).get('project_name', 'N/A')}
- **Units Analisadas**: {len(analysis_results.get('units_analysis', {}))}
- **Complexidade**: {analysis_results.get('characteristics', {}).get('complexity_level', 'N/A')}
- **Prontidão**: {analysis_results.get('characteristics', {}).get('modernization_readiness', 'N/A')}

### DOCUMENTAÇÃO GERADA
{doc_content}

### CORRELAÇÕES IDENTIFICADAS
{self._format_correlations(analysis_results.get('correlations', {}))}

## INSTRUÇÕES PARA MODERNIZAÇÃO

Use TODA a informação acima para:

1. **Preservar Funcionalidades**: Garanta que cada funcionalidade documentada seja implementada
2. **Aplicar Correlações**: Use os mapeamentos Delphi→Java identificados
3. **Manter Fluxos**: Preserve os fluxos de execução e dados documentados
4. **Atender Requisitos**: Implemente todos os requisitos funcionais extraídos
5. **Seguir Características**: Respeite as características técnicas identificadas

A conversão deve ser fiel ao sistema original mas usando as melhores práticas do Spring Boot.
"""

    def _load_documentation_content(self, generated_docs: Dict[str, str]) -> str:
        """Carrega conteúdo resumido dos documentos gerados"""
        content_parts = []
        
        # Prioriza documentos mais importantes para o contexto
        priority_docs = ['executive_summary', 'requirements', 'correlations', 'characteristics']
        
        for doc_key in priority_docs:
            if doc_key in generated_docs:
                doc_path = generated_docs[doc_key]
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        doc_content = f.read()
                    
                    # Limita o tamanho para evitar prompt muito longo
                    if len(doc_content) > 2000:
                        doc_content = doc_content[:2000] + "...[conteúdo truncado]"
                    
                    content_parts.append(f"#### {doc_key.title()}\n{doc_content}\n")
                except Exception:
                    continue
        
        return "\n".join(content_parts) if content_parts else "Documentação não disponível"

    def _format_correlations(self, correlations: Dict[str, Any]) -> str:
        """Formata correlações para inclusão no prompt"""
        if not correlations:
            return "Correlações não disponíveis"
        
        formatted = []
        
        # Mapeamentos de componentes
        component_mappings = correlations.get('component_mappings', [])
        if component_mappings:
            formatted.append("**Mapeamentos de Componentes:**")
            for mapping in component_mappings[:5]:  # Limita a 5 principais
                formatted.append(f"- {mapping.get('delphi_component', 'N/A')} → {mapping.get('java_equivalent', 'N/A')}")
        
        # Mapeamentos de padrões
        pattern_mappings = correlations.get('pattern_mappings', [])
        if pattern_mappings:
            formatted.append("\n**Mapeamentos de Padrões:**")
            for pattern in pattern_mappings:
                formatted.append(f"- {pattern.get('delphi_pattern', 'N/A')} → {pattern.get('java_pattern', 'N/A')}")
        
        return "\n".join(formatted) if formatted else "Correlações não disponíveis"

    def get_specialized_prompt(self, prompt_type: str, **kwargs) -> str:
        """Retorna prompt especializado baseado no tipo"""
        prompt_methods = {
            'analysis': self.get_analysis_prompt,
            'conversion': lambda: self.get_spring_conversion_prompt(kwargs.get('documentation_context', '')),
            'entity_mapping': self.get_entity_mapping_prompt,
            'api_design': self.get_api_design_prompt,
            'service_layer': self.get_service_layer_prompt,
            'testing': self.get_testing_prompt,
            'documentation_enhanced': lambda: self.get_documentation_enhanced_prompt(
                kwargs.get('analysis_results', {}),
                kwargs.get('generated_docs', {})
            )
        }
        
        method = prompt_methods.get(prompt_type)
        if method:
            return method()
        else:
            return self.base_prompt

# Instância global do gerenciador
prompt_manager = PromptManager()
