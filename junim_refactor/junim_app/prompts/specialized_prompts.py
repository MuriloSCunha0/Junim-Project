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
        """Prompt para análise inicial do sistema legacy"""
        return f"""
{self.base_prompt}

## TAREFA: ANÁLISE COMPLETA DO SISTEMA LEGACY

Analise o código Delphi fornecido e extraia informações estruturadas sobre o sistema.

### ANÁLISE OBRIGATÓRIA:

#### 1. IDENTIFICAÇÃO DE FUNCIONALIDADES
Para cada funcionalidade encontrada, descreva:
- **Nome da Funcionalidade**: Identificação clara
- **Propósito**: O que ela faz na prática
- **Exemplo de Uso**: Como o usuário interage com ela
- **Componentes Envolvidos**: Forms, botões, campos, procedures
- **Fluxo de Execução**: Passo a passo da funcionalidade

#### 2. ESTRUTURA DO SISTEMA
- **Forms/Telas**: Liste todos os formulários e sua finalidade
- **Unidades/Módulos**: Organize por área funcional
- **Banco de Dados**: Tabelas, procedures, triggers identificados
- **Componentes**: Grids, relatórios, menus principais

#### 3. REGRAS DE NEGÓCIO
- **Validações**: Que dados são validados e como
- **Cálculos**: Fórmulas e algoritmos encontrados
- **Fluxos Condicionais**: Decisões baseadas em dados
- **Integrações**: Conexões com sistemas externos

#### 4. DEPENDÊNCIAS E CORRELAÇÕES
- **Relacionamentos**: Como as funcionalidades se conectam
- **Ordem de Execução**: Que funcionalidades dependem de outras
- **Dados Compartilhados**: Informações usadas em múltiplos lugares

### FORMATO DE RESPOSTA:

Organize a resposta em seções claras:

```
## FUNCIONALIDADES IDENTIFICADAS

### [Nome da Funcionalidade 1]
- **Descrição**: [O que faz]
- **Exemplo de uso**: [Cenário prático]
- **Componentes**: [Forms, botões, etc.]
- **Fluxo**: [Passo a passo]

### [Nome da Funcionalidade 2]
...

## ESTRUTURA DO SISTEMA
- **Forms**: [Lista de formulários]
- **Módulos**: [Organização do código]
- **Banco**: [Estruturas de dados]

## REGRAS DE NEGÓCIO
- **Validações**: [Que dados são validados]
- **Cálculos**: [Algoritmos encontrados]
- **Fluxos**: [Lógicas condicionais]

## CORRELAÇÕES
- **Dependências**: [Como funcionalidades se relacionam]
```

Seja detalhado e focado na compreensão funcional do sistema.
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

## TAREFA: CONVERSÃO PARA JAVA SPRING BOOT COM MAPEAMENTO DETALHADO DE FUNCIONALIDADES

Converta o código Delphi fornecido para Java Spring Boot seguindo estas diretrizes:

### 1. MAPEAMENTO OBRIGATÓRIO DE FUNCIONALIDADES

{self.get_functionality_mapping_prompt()}

### 2. ESTRUTURA DE PROJETO
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

### 3. MAPEAMENTOS TÉCNICOS DETALHADOS

**TForm → @RestController**:
- Cada botão/ação → Endpoint REST específico
- Validações de formulário → Bean Validation
- Eventos de interface → Métodos de controller
- Mensagens de feedback → ResponseEntity com status apropriado

**TDataModule → @Repository + @Service**:
- Cada query SQL → Método Repository com nome descritivo
- Transações complexas → @Transactional em services
- Procedimentos de negócio → Métodos de service

### 4. ESTRUTURA DE RESPOSTA OBRIGATÓRIA

Para cada funcionalidade encontrada:

1. **ANÁLISE FUNCIONAL**:
   - Descrição clara do que a funcionalidade faz
   - Exemplo prático de uso no sistema original
   - Regras de negócio envolvidas

2. **MAPEAMENTO DETALHADO**:
   - Como será implementado em Java Spring
   - Qual(is) endpoint(s) REST serão criados
   - Exemplo de requisição/resposta HTTP

3. **CÓDIGO JAVA COMENTADO**:
   - Implementação completa com comentários explicativos
   - Relacione cada linha/bloco ao comportamento original

4. **VALIDAÇÃO DE EQUIVALÊNCIA**:
   - Confirme que a funcionalidade Java produz o mesmo resultado
   - Liste diferenças (se houver) e justifique

5. **TESTES FUNCIONAIS**:
   - Testes que validam o comportamento esperado
   - Cenários baseados nos exemplos de uso originais

### EXEMPLO ESPERADO:

**FUNCIONALIDADE ORIGINAL**: "Botão Calcular Desconto"
- O que faz: Calcula desconto baseado no valor total e tipo de cliente
- Exemplo: Cliente VIP com compra de R$ 1000 → aplica 10% desconto → mostra R$ 900
- Fluxo: Click → valida campos → calcula desconto → atualiza tela

**FUNCIONALIDADE MODERNIZADA**: 
- Endpoint: POST /api/vendas/calcular-desconto
- Request: {"valorTotal": 1000, "tipoCliente": "VIP"}
- Response: {"valorComDesconto": 900, "descontoAplicado": 10}
- Código: VendaController.calcularDesconto() → DescontoService.aplicar()

Gere código limpo, bem documentado e que preserve EXATAMENTE o comportamento funcional original.
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
        """Retorna prompt especializado baseado no tipo solicitado"""
        if prompt_type == 'conversion':
            # Se há documentação disponível, enriquece o prompt
            if 'analysis_results' in kwargs and 'generated_docs' in kwargs:
                docs_context = str(kwargs.get('generated_docs', ''))
                return self.get_spring_conversion_prompt(docs_context)
            else:
                return self.get_spring_conversion_prompt()
        
        elif prompt_type == 'analysis':
            return self.get_analysis_prompt()
        
        elif prompt_type == 'documentation':
            return self.get_documentation_generation_prompt()
        
        elif prompt_type == 'functionality_mapping':
            return self.get_functionality_mapping_prompt()
        
        elif prompt_type == 'entity_mapping':
            return f"""
{self.base_prompt}

## TAREFA: MAPEAMENTO ESPECÍFICO DE ENTIDADES

Você deve focar APENAS na criação de entidades JPA e DTOs para o sistema Java Spring.

{self.get_functionality_mapping_prompt()}

### FOCO EM ENTIDADES:
- Identifique todas as estruturas de dados do Delphi
- Crie entidades JPA correspondentes
- Defina DTOs para transferência de dados
- Mapeie relacionamentos entre entidades
- Configure validações Bean Validation
"""
        
        elif prompt_type == 'api_design':
            return f"""
{self.base_prompt}

## TAREFA: DESIGN DE APIs REST

Você deve focar APENAS na criação de Controllers REST para exposição de APIs.

{self.get_functionality_mapping_prompt()}

### FOCO EM APIs:
- Crie Controllers REST para cada funcionalidade
- Defina endpoints seguindo padrões RESTful
- Configure documentação OpenAPI/Swagger
- Implemente tratamento de erros
- Configure validação de entrada
"""
        
        elif prompt_type == 'service_layer':
            return f"""
{self.base_prompt}

## TAREFA: CAMADA DE SERVIÇOS

Você deve focar APENAS na implementação da lógica de negócio em Services.

{self.get_functionality_mapping_prompt()}

### FOCO EM SERVIÇOS:
- Implemente Services com lógica de negócio
- Configure transações
- Implemente validações de negócio
- Configure injeção de dependências
- Implemente padrões de design adequados
"""
        
        elif prompt_type == 'testing':
            return f"""
{self.base_prompt}

## TAREFA: GERAÇÃO DE TESTES

Você deve focar APENAS na criação de testes abrangentes.

{self.get_functionality_mapping_prompt()}

### FOCO EM TESTES:
- Crie testes unitários para Services
- Crie testes de integração para Controllers
- Configure mocks e fixtures
- Implemente testes de cenários de funcionalidades
- Configure relatórios de cobertura
"""
        
        else:
            # Retorna prompt base como fallback
            return self.base_prompt

    def get_functionality_mapping_prompt(self) -> str:
        """Prompt específico para mapeamento detalhado de funcionalidades"""
        return f"""
{self.base_prompt}

## TAREFA: MAPEAMENTO DETALHADO DE FUNCIONALIDADES

Você deve criar um mapeamento completo e detalhado das funcionalidades entre o sistema original (Delphi) e o sistema modernizado (Java Spring).

### INSTRUÇÕES OBRIGATÓRIAS:

Para CADA funcionalidade identificada, forneça:

#### 1. FUNCIONALIDADE ORIGINAL (Sistema Delphi)
- **Nome/Identificação**: Nome claro da funcionalidade
- **Descrição Funcional**: O que ela faz em linguagem natural
- **Exemplo Prático**: Cenário real de uso (ex: "Usuário clica em 'Salvar' → sistema valida dados → salva no banco → exibe confirmação")
- **Componentes Técnicos**: Forms, botões, campos, procedures envolvidos
- **Regras de Negócio**: Validações, cálculos, fluxos condicionais
- **Entradas/Saídas**: O que recebe e o que produz

#### 2. FUNCIONALIDADE MODERNIZADA (Sistema Java Spring)
- **Implementação Java**: Como a mesma funcionalidade será implementada em Java
- **Endpoints REST**: Quais APIs serão criadas
- **Exemplo de Uso**: Como será acessada (ex: "POST /api/usuarios → UserController.create() → retorna 201")
- **Fluxo Técnico**: Request → Controller → Service → Repository → Response
- **Estrutura de Dados**: DTOs, Entities envolvidas
- **Tratamento de Erros**: Como erros serão gerenciados

#### 3. VALIDAÇÃO DE EQUIVALÊNCIA
- **Comportamento Idêntico**: Confirme que o resultado final é o mesmo
- **Diferenças Justificadas**: Se houver mudanças, explique o porquê
- **Vantagens da Modernização**: Melhorias obtidas com Java Spring

### FORMATO DE RESPOSTA:

```
## FUNCIONALIDADE: [Nome da Funcionalidade]

### SISTEMA ORIGINAL (Delphi)
- **O que faz**: [Descrição clara]
- **Exemplo prático**: [Cenário de uso]
- **Componentes**: [Forms, botões, etc.]
- **Fluxo**: [Passo a passo]

### SISTEMA MODERNIZADO (Java Spring)
- **Implementação**: [Controllers, Services, Repositories]
- **API**: [Endpoint(s) REST]
- **Exemplo de uso**: [Request/Response]
- **Fluxo técnico**: [Arquitetura Spring]

### VALIDAÇÃO
- **Equivalência**: [Sim/Não e justificativa]
- **Melhorias**: [Benefícios da modernização]
```

### EXEMPLOS DE MAPEAMENTO ESPERADO:

#### FUNCIONALIDADE: Cadastro de Cliente
**ORIGINAL**: Formulário com campos nome, email → botão Salvar → valida campos → insere no banco → mensagem "Cliente salvo com sucesso"
**MODERNIZADO**: POST /api/clientes → CustomerController.create() → valida DTO → CustomerService.save() → retorna {"id": 123, "message": "Cliente criado"}

#### FUNCIONALIDADE: Busca de Produtos
**ORIGINAL**: Campo de pesquisa → botão Buscar → query no banco → popula grid com resultados
**MODERNIZADO**: GET /api/produtos?nome=filtro → ProductController.search() → ProductService.findByName() → retorna List<ProductDTO>

Seja específico, detalhado e mantenha foco na preservação funcional com melhoria técnica.
"""

    def get_documentation_generation_prompt(self) -> str:
        """Prompt para geração de documentação com foco em funcionalidades"""
        return f"""
{self.base_prompt}

## TAREFA: GERAÇÃO DE DOCUMENTAÇÃO FOCADA EM FUNCIONALIDADES

Baseado na análise do sistema legacy, gere documentação técnica completa com foco especial no mapeamento de funcionalidades.

### ESTRUTURAS OBRIGATÓRIAS:

#### 1. REQUISITOS FUNCIONAIS
Para cada funcionalidade identificada:
- **RF[ID] - Nome da Funcionalidade**
- **Descrição**: O que ela faz na prática
- **Exemplo de Uso**: Cenário real de interação
- **Critérios de Aceitação**: Como validar se funciona corretamente
- **Prioridade**: Crítica/Alta/Média/Baixa

#### 2. ARQUITETURA FUNCIONAL
- **Módulos por Área de Negócio**: Agrupamento lógico das funcionalidades
- **Fluxos de Processo**: Como as funcionalidades se conectam
- **Dados Compartilhados**: Informações usadas por múltiplas funcionalidades
- **Integrações**: Comunicação entre módulos

#### 3. ESPECIFICAÇÃO TÉCNICA DETALHADA
Para cada componente:
- **Funcionalidade Principal**: O que o componente faz
- **Entradas e Saídas**: Dados recebidos e produzidos
- **Regras de Negócio**: Validações e cálculos específicos
- **Dependências**: O que precisa para funcionar

#### 4. MAPEAMENTO DE EQUIVALÊNCIAS
Use o prompt específico de mapeamento para criar correlações detalhadas:

{self.get_functionality_mapping_prompt()}

### FORMATO DA DOCUMENTAÇÃO:

```markdown
# DOCUMENTAÇÃO DO SISTEMA - [Nome do Projeto]

## 1. VISÃO GERAL
- Propósito do sistema
- Principais funcionalidades
- Usuários alvo

## 2. FUNCIONALIDADES IDENTIFICADAS

### [Nome da Funcionalidade 1]
- **Descrição**: [O que faz]
- **Exemplo prático**: [Como é usada]
- **Componentes envolvidos**: [Forms, botões, etc.]
- **Regras de negócio**: [Validações, cálculos]

## 3. ARQUITETURA FUNCIONAL
- **Módulos**: [Organização por área]
- **Fluxos**: [Como se conectam]
- **Dados**: [Estruturas compartilhadas]

## 4. REQUISITOS FUNCIONAIS
- RF001 - [Funcionalidade crítica]
- RF002 - [Funcionalidade importante]
...

## 5. ESPECIFICAÇÕES TÉCNICAS
[Detalhes de implementação por componente]

## 6. MAPEAMENTO PARA MODERNIZAÇÃO
[Equivalências Delphi → Java Spring]
```

Mantenha foco na compreensão prática das funcionalidades e sua aplicação real.
"""

# Instância global do PromptManager para uso em todo o sistema
prompt_manager = PromptManager()
