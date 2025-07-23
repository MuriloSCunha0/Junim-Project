# 🔄 Sistema de Análise Comparativa - Manual de Uso

Sistema completo para análise de projetos legados (Delphi) e modernizados (Java Spring Boot), com capacidade de comparação, validação de migração e geração automática de documentação.

## 🚀 Como Executar

### Método Simples
```bash
# Execute a aplicação Streamlit
streamlit run main.py
```

### Acesso
- **Interface Principal:** http://localhost:8501

## 📊 Funcionalidades Principais

### 1. 🏛️ Análise de Projetos Delphi
**O que faz:**
- Analisa estrutura de código Delphi (.pas, .dpr, .dfm)
- Extrai funções, classes, procedures e components
- Gera documentação técnica completa
- Cria diagramas de arquitetura (Mermaid)

**Como usar:**
1. Vá para aba "🏛️ Análise Delphi"
2. Faça upload do arquivo ZIP do projeto
3. Aguarde a análise
4. Visualize estatísticas e baixe documentos

**Documentação gerada:**
- 📊 Análise estrutural
- 🏗️ Arquitetura do sistema
- 📈 Métricas de complexidade
- 🗺️ Diagrama do sistema
- 📋 Catálogo de componentes

### 2. ☕ Análise de Projetos Java Spring Boot
**O que faz:**
- Analisa código Java Spring Boot
- Identifica Controllers, Services, Repositories, Entities
- Mapeia estrutura de arquivos e componentes
- Analisa padrões arquiteturais

**Como usar:**
1. Vá para aba "☕ Análise Java"
2. Faça upload do projeto Java (ZIP)
3. Visualize componentes Spring
4. Baixe documentação técnica

**Documentação gerada:**
- 🌐 Documentação de componentes
- 🏗️ Arquitetura Spring
- 📦 Catálogo de componentes
- 🗂️ Schema de banco de dados
- 🗺️ Diagrama do sistema

### 3. 🔄 Comparação de Projetos
**O que faz:**
- Compara projeto Delphi original com versão Java
- Mapeia funcionalidades equivalentes
- Calcula cobertura de migração
- Identifica gaps e problemas
- Gera recomendações

**Como usar:**
1. Vá para aba "🔄 Comparação"
2. Faça upload do projeto Delphi (ZIP)
3. Faça upload do projeto Java (ZIP)
4. Analise resultados da comparação

**Resultados:**
- 📊 **Métricas de Cobertura**
  - Cobertura geral da migração
  - Percentual de funções migradas
  - Percentual de classes migradas

- ✅ **Validação da Migração**
  - Status geral (PASS/WARNING/FAIL)
  - Validações por aspecto
  - Mensagens detalhadas

- 🗺️ **Mapeamento Funcional**
  - Funções Delphi → Métodos Java
  - Componentes mapeados
  - Elementos não migrados

- 💡 **Recomendações Priorizadas**
  - Críticas (bloqueadores)
  - Altas (importantes)
  - Médias (melhorias)
  - Baixas (opcionais)

### 4. 🚀 Análise Completa de Modernização
**O que faz:**
- Gera estratégia completa de modernização
- Define fases de migração com cronograma
- Recomenda stack tecnológico
- Valida projeto modernizado (se fornecido)

**Como usar:**
1. Vá para aba "🚀 Modernização Completa"
2. Faça upload do projeto Delphi (obrigatório)
3. Opcionalmente, forneça projeto Java para validação
4. Receba estratégia completa

**Sem projeto Java (Estratégia):**
- 📋 Estratégia de modernização
- 📊 Análise de complexidade e riscos
- 📅 Fases de migração (cronograma)
- 💻 Stack tecnológico recomendado
- 🎯 Componentes prioritários

**Com projeto Java (Validação):**
- Tudo da estratégia +
- 🎯 Validação da modernização
- 📊 Score de sucesso
- 📈 Percentual de conclusão
- 🔍 Próximos passos específicos

## 📋 Formatos de Arquivo Aceitos

### Projetos Delphi
- **Extensão:** `.zip`
- **Conteúdo esperado:**
  - Arquivos `.pas` (unidades Pascal)
  - Arquivos `.dpr` (projeto principal)
  - Arquivos `.dfm` (formulários)
  - Arquivos `.dpk` (pacotes)
- **Estrutura:** Mantenha a estrutura de pastas original

### Projetos Java Spring Boot
- **Extensão:** `.zip`
- **Conteúdo esperado:**
  - Arquivos `.java` (código fonte)
  - Estrutura Maven (`src/main/java/`)
  - Anotações Spring (@Controller, @Service, etc.)
- **Estrutura:** Estrutura padrão Maven/Gradle

## 📈 Interpretando os Resultados

### Cobertura de Migração
- **90-100%**: Migração excelente
- **70-89%**: Migração boa, poucos ajustes
- **50-69%**: Migração parcial, requer atenção
- **< 50%**: Migração incompleta, revisão necessária

### Status de Validação
- **🟢 PASS**: Critério atendido completamente
- **🟡 WARNING**: Critério parcialmente atendido
- **🔴 FAIL**: Critério não atendido

### Prioridades de Recomendação
- **🚨 CRITICAL**: Resolver imediatamente
- **🔴 HIGH**: Resolver em 1-2 semanas
- **🟡 MEDIUM**: Resolver em 1 mês
- **🟢 LOW**: Resolver quando possível

## 🛠️ Solução de Problemas

### Erro na Interface
```bash
# Verifique se todos os módulos estão instalados
pip install -r requirements.txt

# Se ainda houver problemas, execute com debug
streamlit run ui/interface.py --logger.level=debug
```

### Upload falha
- Verifique se o arquivo é um ZIP válido
- Máximo 200MB por arquivo
- Certifique-se que contém arquivos do tipo correto

### Interface não carrega
```bash
# Execute apenas o Streamlit
streamlit run ui/comparative_analysis_interface.py --server.port 8501
```

### Dependências faltando
```bash
# Reinstale todas as dependências
pip install -r requirements.txt --upgrade
```

## 📞 Recursos Adicionais

### Logs e Debug
- Logs detalhados aparecem no terminal
- Streamlit: logs aparecem na aba "Debug" da sidebar
- Erros detalhados aparecem nas mensagens da interface

### Downloads
Todos os documentos gerados podem ser baixados:
- 📄 **Markdown**: Documentação técnica
- 📊 **JSON**: Dados brutos da análise
- 🗺️ **Mermaid**: Diagramas (copie o código)
- 📦 **ZIP**: Projeto Spring Boot completo com documentação

---

**Sistema de Análise Comparativa v2.0**  
Transforme seus projetos legados em sistemas modernos com confiança e precisão.

🏛️ **Analise** → ☕ **Modernize** → 🔄 **Compare** → 🚀 **Valide**
