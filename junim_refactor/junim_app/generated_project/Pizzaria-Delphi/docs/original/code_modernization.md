# Code Modernization - Projeto Original

> **Nota:** Este documento foi gerado durante a análise do projeto Delphi original.
> Ele serve como referência para entender a estrutura e funcionalidades que foram
> modernizadas para Java Spring Boot no projeto **ProjetoModernizadoModern**.

---

Bem-vindo ao nosso assistente de conversão de código Delphi para Java Spring Boot! Vamos começar com a análise do projeto Pizzaria-DELPHI.

Com base nas informações fornecidas, podemos identificar as seguintes entidades JPA:

1. `Pizza`
2. `Cliente`
3. `Pedido`
4. `ItemPedido`

E também os seguintes repositórios JPA:

1. `PizzaRepository`
2. `ClienteRepository`
3. `PedidoRepository`
4. `ItemPedidoRepository`

Além disso, podemos identificar as seguintes classes de serviço:

1. `PizzaService`
2. `ClienteService`
3. `PedidoService`
4. `ItemPedidoService`

E os seguintes controllers REST:

1. `PizzaController`
2. `ClienteController`
3. `PedidoController`
4. `ItemPedidoController`

Agora, vamos gerar o código Java Spring Boot para cada uma dessas entidades, repositórios, serviços e controllers.

Para começar, vamos com a entidade `Pizza`. Aqui está o código Java Spring Boot para essa entidade:
```java
@Entity
@Table(name = "pizzas")
public class Pizza {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "nome")
    private String nome;
    
    @Column(name = "preco")
    private BigDecimal preco;
    
    @Column(name = "descricao")
    private String descricao;
    
    @ManyToOne
    @JoinColumn(name = "cliente_id")
    private Cliente cliente;
    
    @OneToMany(mappedBy = "pizza")
    private List<ItemPedido> itensPedido;
    
    // getters e setters
}
```
Observe que a anotação `@Entity` indica que essa classe é uma entidade JPA. A anotação `@Table(name = "pizzas")` indica que essa entidade deve ser mapeada para uma tabela chamada "pizzas" no banco de dados.

A anotação `@Id` indica que o campo `id` é a chave primária da entidade. A anotação `@GeneratedValue(strategy = GenerationType.IDENTITY)` indica que o valor da chave primária deve ser gerado automaticamente pelo banco de dados.

A anotação `@Column(name = "nome")` indica que o campo `nome` é uma coluna na tabela "pizzas". A anotação `@Column(name = "preco")` indica que o campo `preco` é uma coluna na tabela "pizzas".

A anotação `@ManyToOne` indica que a relação entre a entidade `Pizza` e a entidade `Cliente` é muitos-para-um. A anotação `@JoinColumn(name = "cliente_id")` indica que a chave estrangeira da entidade `Pizza` deve ser mapeada para uma coluna chamada "cliente_id

---

## 🔄 Correspondência no Projeto Modernizado

Este documento descreve o projeto original em Delphi. Para ver como estes componentes
foram convertidos para Java Spring Boot, consulte:

- [README.md](../README.md) - Visão geral do projeto modernizado
- [ARQUITETURA.md](../ARQUITETURA.md) - Arquitetura do sistema Java
- [COMPARACAO_DELPHI_JAVA.md](../COMPARACAO_DELPHI_JAVA.md) - Comparação detalhada

*Documento original preservado pelo sistema JUNIM durante a modernização*
