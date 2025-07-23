# Delphi Java Mapping - Projeto Original

> **Nota:** Este documento foi gerado durante a análise do projeto Delphi original.
> Ele serve como referência para entender a estrutura e funcionalidades que foram
> modernizadas para Java Spring Boot no projeto **ProjetoModernizadoModern**.

---

Documentação Técnica para Pizzaria-DELPHI
=====================================

Introdução
------------

Este documento tem como objetivo fornecer informações técnicas específicas para o projeto Pizzaria-DELPHI, migrado para Java Spring Boot. A análise foi realizada em 2025-07-22T14:55:28.388723 e identificou 16 classes, 85 funções e 16 formulários.

Estatísticas Reais
-------------------

* Total de linhas: 1017
* Total de funções: 85
* Total de classes: 16
* Total de eventos: 23
* Formulários (Forms): 15
* Units utilitárias: 0
* Data Modules: 1

Arquivos Identificados
----------------------

* Forms: frmBase.pas, frmBaseCadastro.pas, frmBasePesquisa.pas
* Data Modules: udmDados.pas

Funções Identificadas
--------------------

* ActVoltarExecute() [procedure] em frmBaseCadastro.pas
* ActSalvarExecute() [procedure] em frmBaseCadastro.pas
* ActCancelarExecute() [procedure] em frmBaseCadastro.pas
* ActExcluirExecute() [procedure] em frmBaseCadastro.pas
* dtsDataChange() [procedure] em frmBaseCadastro.pas
* FormClose() [procedure] em frmBaseCadastro.pas
* FormShow() [procedure] em frmBaseCadastro.pas
* ActCancelarExecute() [procedure] - method em frmBaseCadastro.pas
* ... e mais 77 funções

Classes Identificadas
-------------------

* TFormBase extends TForm [form] em frmBase.pas
* TFormBaseCadastro extends TFormBase [form] em frmBaseCadastro.pas
  - Métodos: ActVoltarExecute, ActSalvarExecute, ActCancelarExecute
* TFormBasePesquisa extends TFormBase [form] em frmBasePesquisa.pas
  - Métodos: ActVoltarExecute, ActIncluirExecute, ActAlterarExecute
* TFormAbertura extends TFormBase [form] em untAbertura.pas
  - Métodos: Timer1Timer
* TFormCadastroClientes extends TFormBaseCadastro [form] em untCadastroClientes.pas
* ... e mais 11 classes

Instruções Críticas para IA
-----------------------------

1. Use EXCLUSIVAMENTE os dados fornecidos acima - não invente nada
2. Mencione nomes ESPECÍFICOS de classes, métodos e arquivos identificados
3. Foque em aspectos de backend e modernização para Java Spring Boot
4. Use formatação Markdown clara com títulos, subtítulos e listas
5. Seja técnico e preciso - EVITE descrições genéricas
6. Inclua exemplos práticos baseados APENAS no código analisado

Formato Esperado
-----------------

O documento deve ser escrito em formato Markdown e segu

---

## 🔄 Correspondência no Projeto Modernizado

Este documento descreve o projeto original em Delphi. Para ver como estes componentes
foram convertidos para Java Spring Boot, consulte:

- [README.md](../README.md) - Visão geral do projeto modernizado
- [ARQUITETURA.md](../ARQUITETURA.md) - Arquitetura do sistema Java
- [COMPARACAO_DELPHI_JAVA.md](../COMPARACAO_DELPHI_JAVA.md) - Comparação detalhada

*Documento original preservado pelo sistema JUNIM durante a modernização*
