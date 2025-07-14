# Correlações Delphi → Java Spring - MeuProjeto

## Introdução

Este documento mapeia como cada componente/funcionalidade do sistema Delphi deve ser implementado no Java Spring Boot.

## 1. Mapeamento de Componentes

### TForm (Classe.Calculadora)
**Delphi**: Form with UI controls and event handlers
**Java Spring**: @RestController + @Service
**Justificativa**: Separate UI logic (REST endpoints) from business logic (Service)
**Exemplo de Implementação**:
```java
@RestController
@RequestMapping("/api/classe.calculadora")
public class Classe.CalculadoraController {
    @Autowired
    private Classe.CalculadoraService service;
    
    @GetMapping
    public ResponseEntity<List<Object>> getData() {
        return ResponseEntity.ok(service.getData());
    }
}
```

### TForm (Classe.Dividir)
**Delphi**: Form with UI controls and event handlers
**Java Spring**: @RestController + @Service
**Justificativa**: Separate UI logic (REST endpoints) from business logic (Service)
**Exemplo de Implementação**:
```java
@RestController
@RequestMapping("/api/classe.dividir")
public class Classe.DividirController {
    @Autowired
    private Classe.DividirService service;
    
    @GetMapping
    public ResponseEntity<List<Object>> getData() {
        return ResponseEntity.ok(service.getData());
    }
}
```

### TForm (Classe.Multiplicar)
**Delphi**: Form with UI controls and event handlers
**Java Spring**: @RestController + @Service
**Justificativa**: Separate UI logic (REST endpoints) from business logic (Service)
**Exemplo de Implementação**:
```java
@RestController
@RequestMapping("/api/classe.multiplicar")
public class Classe.MultiplicarController {
    @Autowired
    private Classe.MultiplicarService service;
    
    @GetMapping
    public ResponseEntity<List<Object>> getData() {
        return ResponseEntity.ok(service.getData());
    }
}
```

### TForm (Classe.Somar)
**Delphi**: Form with UI controls and event handlers
**Java Spring**: @RestController + @Service
**Justificativa**: Separate UI logic (REST endpoints) from business logic (Service)
**Exemplo de Implementação**:
```java
@RestController
@RequestMapping("/api/classe.somar")
public class Classe.SomarController {
    @Autowired
    private Classe.SomarService service;
    
    @GetMapping
    public ResponseEntity<List<Object>> getData() {
        return ResponseEntity.ok(service.getData());
    }
}
```

### TForm (Classe.Subtrair)
**Delphi**: Form with UI controls and event handlers
**Java Spring**: @RestController + @Service
**Justificativa**: Separate UI logic (REST endpoints) from business logic (Service)
**Exemplo de Implementação**:
```java
@RestController
@RequestMapping("/api/classe.subtrair")
public class Classe.SubtrairController {
    @Autowired
    private Classe.SubtrairService service;
    
    @GetMapping
    public ResponseEntity<List<Object>> getData() {
        return ResponseEntity.ok(service.getData());
    }
}
```

### TForm (Unit4)
**Delphi**: Form with UI controls and event handlers
**Java Spring**: @RestController + @Service
**Justificativa**: Separate UI logic (REST endpoints) from business logic (Service)
**Exemplo de Implementação**:
```java
@RestController
@RequestMapping("/api/unit4")
public class Unit4Controller {
    @Autowired
    private Unit4Service service;
    
    @GetMapping
    public ResponseEntity<List<Object>> getData() {
        return ResponseEntity.ok(service.getData());
    }
}
```

## 2. Mapeamento de Padrões

### Event-Driven Programming
**Padrão Delphi**: Button clicks and form events trigger procedures
**Padrão Java**: REST API + Event Listeners
**Vantagens**: Decoupled, testable, scalable architecture

### Data Module Pattern
**Padrão Delphi**: Centralized data access in TDataModule
**Padrão Java**: Repository Pattern + Service Layer
**Vantagens**: Clean separation of concerns, dependency injection

## 3. Mapeamento de Tecnologias

- **VCL Forms** → **REST API + Modern Frontend**
  - Motivo: Web-based UI is more flexible and maintainable
- **ADO/DBExpress** → **Spring Data JPA**
  - Motivo: ORM approach simplifies database operations
- **Exception Handling** → **@ExceptionHandler + Custom Exceptions**
  - Motivo: Centralized, consistent error handling
