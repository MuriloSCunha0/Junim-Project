# 📋 Projeto Delphi Simples - Prova de Conceito

## 🎯 Objetivo
Este é um projeto Delphi simples para testar a funcionalidade de modernização do JUNIM. 
Implementa um sistema CRUD básico com três entidades principais.

## 🗂️ Estrutura do Projeto

### 📄 Arquivos Principais
- **SimpleCRUD.dpr** - Arquivo principal do projeto
- **uDataModule.pas** - Módulo de dados com queries e conexão
- **uMainForm.pas** - Formulário principal com menu
- **uClientForm.pas** - Formulário de cadastro de clientes  
- **uProductForm.pas** - Formulário de cadastro de produtos

### 🏗️ Entidades de Negócio

#### 👥 Clientes
- **ID** (Integer, AutoIncrement)
- **Nome** (String, 100 chars, obrigatório)
- **Email** (String, 100 chars)
- **Telefone** (String, 20 chars)
- **DataCadastro** (Date)

#### 📦 Produtos
- **ID** (Integer, AutoIncrement)
- **Nome** (String, 100 chars, obrigatório)
- **Descricao** (Text)
- **Preco** (Real, obrigatório)
- **Estoque** (Integer)
- **Ativo** (Boolean, padrão True)

#### 🛒 Vendas
- **ID** (Integer, AutoIncrement)
- **ClienteID** (Integer, FK para Clientes)
- **ProdutoID** (Integer, FK para Produtos)
- **Quantidade** (Integer)
- **ValorTotal** (Real)
- **DataVenda** (Date)

## 🔧 Funcionalidades Implementadas

### ✅ CRUD Completo
- **Create** - Inserção de novos registros
- **Read** - Listagem e consulta
- **Update** - Edição de registros existentes
- **Delete** - Exclusão com confirmação

### ✅ Validações de Negócio
- Campos obrigatórios (Nome do cliente, Nome do produto)
- Validação de preço (deve ser maior que zero)
- Confirmação antes de excluir
- Data de cadastro automática

### ✅ Interface de Usuário
- Menu principal organizado
- Formulários de cadastro com DBEdits
- Grids para listagem
- Navegação com DBNavigator
- Botões de ação (Novo, Salvar, Cancelar, Excluir)

## 🎯 Resultado Esperado da Modernização

Quando este projeto for processado pelo JUNIM, deve gerar:

### ☕ Entidades JPA (Java)
```java
// Cliente.java
@Entity
public class Cliente {
    @Id @GeneratedValue
    private Long id;
    
    @NotBlank
    private String nome;
    
    private String email;
    private String telefone;
    private LocalDate dataCadastro;
}

// Produto.java  
@Entity
public class Produto {
    @Id @GeneratedValue
    private Long id;
    
    @NotBlank
    private String nome;
    
    private String descricao;
    
    @Positive
    private BigDecimal preco;
    
    private Integer estoque;
    private Boolean ativo;
}

// Venda.java
@Entity
public class Venda {
    @Id @GeneratedValue
    private Long id;
    
    @ManyToOne
    private Cliente cliente;
    
    @ManyToOne  
    private Produto produto;
    
    private Integer quantidade;
    private BigDecimal valorTotal;
    private LocalDate dataVenda;
}
```

### 🌐 Controllers REST
- `ClienteController` - CRUD endpoints para clientes
- `ProdutoController` - CRUD endpoints para produtos  
- `VendaController` - CRUD endpoints para vendas

### 💼 Services  
- `ClienteService` - Lógica de negócio para clientes
- `ProdutoService` - Lógica de negócio para produtos
- `VendaService` - Lógica de negócio para vendas

### 📊 Métricas Esperadas
- **Pass@k Score:** ~85-90% (estrutura bem definida)
- **SonarQube Rating:** A ou B (código limpo e organizado)
- **Complexidade Ciclomática:** ~2-3 (baixa complexidade)
- **Manutenibilidade:** 90%+ (padrões Spring Boot)

## 🧪 Como Testar no JUNIM

1. **Compactar o projeto** em um arquivo ZIP
2. **Fazer upload** na interface do JUNIM
3. **Executar análise** - deve identificar as 3 entidades
4. **Gerar documentação** - deve criar documentos detalhados  
5. **Modernizar para Java** - deve criar projeto Spring Boot completo
6. **Verificar métricas** - devem mostrar alta qualidade

## ✅ Critérios de Sucesso

- [ ] **3 entidades** JPA geradas (Cliente, Produto, Venda)
- [ ] **3 controllers** REST funcionais
- [ ] **3 services** com lógica de negócio
- [ ] **Relacionamentos** mapeados corretamente (FK)
- [ ] **Validações** mantidas (@NotBlank, @Positive)
- [ ] **Configuração** Spring Boot completa
- [ ] **Documentação** gerada com diagramas
- [ ] **Métricas** de qualidade positivas

---

*Este projeto serve como baseline para validar a funcionalidade de modernização do JUNIM.*
