# JUNIM - Java Unified Interoperability Migration

🚀 **Sistema de Modernização Automática de Projetos Delphi para Java Spring Boot**

JUNIM é uma aplicação web desenvolvida como parte de um TCC de Sistemas de Informação que utiliza IA generativa para modernizar sistemas legados Delphi, convertendo-os automaticamente para aplicações Java Spring Boot modernas.

## 🎯 Características Principais

- **Interface Web Intuitiva**: Desenvolvida com Streamlit para facilidade de uso
- **IA Generativa Avançada**: Utiliza Groq (cloud) e Ollama (local) para geração de código
- **Análise Completa**: Extração de estrutura de código, documentação automática e comparação
- **Modernização Funcional**: Geração de projeto Spring Boot completo com documentação
- **Download ZIP**: Projeto Java completo com documentação comparativa

## 🏗️ Arquitetura

```
junim_app/
├── main.py                          # Aplicação Streamlit principal
├── ui/
│   └── interface.py                 # Interface do usuário
├── core/
│   ├── legacy_project_analyzer.py   # Analisador de código Delphi
│   ├── documentation_generator.py   # Gerador de documentação
│   ├── modernization_service.py     # Serviço de modernização
│   └── llm_service.py              # Serviço de IA (Groq/Ollama)
├── utils/
│   └── file_handler.py             # Manipulação de arquivos
├── prompts/
│   └── specialized_prompts.py      # Prompts especializados
└── requirements.txt                 # Dependências Python
```

## 🚀 Como Usar

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- (Opcional) Conta Groq com API key
- (Opcional) Ollama instalado localmente

### Instalação e Execução

1. **Clone ou baixe o projeto**

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação:**
   ```bash
   streamlit run main.py
   ```

4. **Acesse no navegador:**
   ```
   http://localhost:8501
   ```
   run_junim.bat
   ```

   **Linux/Mac:**
   ```bash
   chmod +x run_junim.sh
   ./run_junim.sh
   ```

3. **Acesse a aplicação:**
   - Abra o navegador em: http://localhost:8501

### Instalação Manual

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run main.py
```

## 📋 Fluxo de Uso

1. **Configuração:** Insira sua chave API da Groq (opcional)
2. **Upload:** Faça upload do projeto Delphi (.zip)
3. **Modernização:** Clique em "Modernizar Projeto"
4. **Acompanhe:** Veja o progresso em tempo real
5. **Download:** Baixe o projeto Java Spring gerado

## 🔧 Pipeline de Modernização

### Passo 1: Análise do Sistema Legado
- Extração e análise de arquivos .pas, .dfm, .dpr
- Identificação de classes, métodos, queries SQL
- Mapeamento de componentes de banco de dados
- Extração de lógica de negócio

### Passo 2: Construção de Contexto RAG
- Recuperação de padrões relevantes da base de conhecimento
- Construção de contexto especializado para o LLM
- Mapeamento de tecnologias Delphi → Spring

### Passo 3: Geração com IA
- Prompt engineering especializado
- Geração de código Java com Groq (primário) ou Ollama (fallback)
- Estruturação do código em arquivos organizados

### Passo 4: Construção do Projeto Java
- Criação da estrutura Maven padrão
- Organização em camadas (Controller, Service, Repository)
- Geração de configurações (pom.xml, application.properties)

### Passo 5: Validação e Empacotamento
- Scripts de validação (mvn compile)
- Empacotamento em arquivo .zip
- Documentação automática

## 📊 Tecnologias Utilizadas

### Frontend
- **Streamlit**: Interface web interativa
- **HTML/CSS**: Customização da interface

### Backend/IA
- **Groq**: IA generativa cloud (modelos Llama3, Mixtral)
- **Ollama**: IA generativa local (CodeLlama, etc.)
- **Python**: Linguagem principal

### Processamento
- **Regex**: Parsing de código Delphi
- **RAG**: Geração aumentada por recuperação
- **File Handling**: Manipulação de arquivos e estruturas

### Saída
- **Java 17**: Linguagem alvo
- **Spring Boot 3.x**: Framework principal
- **Maven**: Gerenciamento de dependências
- **JPA/Hibernate**: Persistência de dados

## 🔑 Configuração de APIs

### Groq (Recomendado)
1. Acesse: https://console.groq.com
2. Crie uma conta e obtenha API key
3. Insira a chave na interface ou arquivo .env

### Ollama (Fallback Local)
1. Instale Ollama: https://ollama.com
2. Baixe modelo: `ollama pull codellama:34b`
3. Inicie serviço: `ollama serve`

## 📝 Mapeamentos Suportados

| Componente Delphi | Equivalente Java Spring |
|-------------------|-------------------------|
| TDataModule | @Service + @Repository |
| TForm | @RestController |
| TQuery/TADOQuery | JpaRepository methods |
| TButton.OnClick | @PostMapping/@GetMapping |
| TEdit/TDBEdit | DTO fields |
| ShowMessage | ResponseEntity |
| Exception handling | @ExceptionHandler |

## 🧪 Exemplo de Conversão

### Delphi (Input)
```pascal
procedure TDataModule1.LoadUsers;
begin
  QryUsers.Close;
  QryUsers.SQL.Clear;
  QryUsers.SQL.Add('SELECT * FROM USERS WHERE ACTIVE = 1');
  QryUsers.Open;
end;
```

### Java Spring (Output)
```java
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
    
    public List<User> loadUsers() {
        return userRepository.findByActiveTrue();
    }
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByActiveTrue();
}
```

## 🔍 Validação e Testes

O projeto gerado inclui:
- Scripts de validação (`validate.bat`/`validate.sh`)
- Configuração de testes com Spring Boot Test
- Verificação de compilação com Maven

## 📈 Limitações e Considerações

### Limitações Atuais
- Parser Delphi baseado em regex (não AST completo)
- Suporte limitado a recursos avançados do Delphi
- Necessita revisão manual da lógica de negócio convertida

### Recomendações
- Teste o código gerado antes de usar em produção
- Revise e ajuste a lógica de negócio conforme necessário
- Configure adequadamente o banco de dados
- Execute testes de validação

## 🤝 Contribuição

Este projeto foi desenvolvido como TCC e serve como base para:
- Pesquisa em modernização de sistemas legados
- Aplicação de IA generativa em engenharia de software
- Estudos de migração Delphi → Java

## 📄 Licença

Projeto acadêmico desenvolvido para TCC de Sistemas de Informação.

## 🆘 Suporte

Para questões técnicas:
1. Verifique os logs da aplicação
2. Revise a base de conhecimento em `knowledge_base/`
3. Teste a conectividade com APIs (Groq/Ollama)
4. Valide o projeto Delphi de entrada

## 🔮 Versões Futuras

Melhorias planejadas:
- Parser AST completo para Delphi
- Suporte a mais frameworks Delphi
- Interface para revisão e ajuste do código
- Métricas de qualidade da conversão
- Suporte a outros alvos além de Spring Boot

---

**JUNIM v1.0** - Transformando legado em modernidade através de IA 🚀
