# Fluxos de Dados - MeuProjeto

## 1. Fluxos de Banco de Dados

Fluxos de banco de dados serão mapeados durante análise detalhada.

## 2. Fluxos entre Formulários

- **De**: Classe.Calculadora **Para**: Classe.Dividir
  - Dados: Form communication
  - Método: Direct reference
- **De**: Classe.Calculadora **Para**: Classe.Somar
  - Dados: Form communication
  - Método: Direct reference
- **De**: Classe.Calculadora **Para**: Classe.Subtrair
  - Dados: Form communication
  - Método: Direct reference
- **De**: Classe.Calculadora **Para**: Classe.Multiplicar
  - Dados: Form communication
  - Método: Direct reference
- **De**: Unit4 **Para**: Classe.Calculadora
  - Dados: Form communication
  - Método: Direct reference
## 3. Fluxos entre Módulos

- **Classe.Calculadora** → **Classe.Interfaces**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Calculadora** → **Classe.helpers**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Calculadora** → **Classe.Dividir**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Calculadora** → **Classe.Somar**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Calculadora** → **Classe.Subtrair**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Calculadora** → **Classe.Multiplicar**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Calculadora** → **Classe.Eventos**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Dividir** → **Classe.Interfaces**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Dividir** → **Classe.Operacoes**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Interfaces** → **Classe.Eventos**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Multiplicar** → **Classe.Operacoes**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Multiplicar** → **Classe.helpers**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Multiplicar** → **Classe.Interfaces**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Operacoes** → **Classe.Interfaces**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Operacoes** → **Classe.Eventos**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Somar** → **Classe.helpers**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Somar** → **Classe.Operacoes**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Subtrair** → **Classe.Interfaces**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Subtrair** → **Classe.helpers**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Classe.Subtrair** → **Classe.Operacoes**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Unit4** → **Classe.Calculadora**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Unit4** → **Classe.helpers**
  - Interface: Uses clause
  - Dados: Unit dependency
- **Unit4** → **Classe.Interfaces**
  - Interface: Uses clause
  - Dados: Unit dependency
## 4. Fluxos Externos

Integrações externas serão identificadas durante análise.

