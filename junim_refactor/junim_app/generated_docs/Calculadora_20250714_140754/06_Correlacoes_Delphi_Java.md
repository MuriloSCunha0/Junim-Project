# Correlações Delphi → Java Spring - Calculadora

## Introdução

Este documento mapeia como cada componente/funcionalidade do sistema Delphi deve ser implementado no Java Spring Boot.

## 1. Mapeamento de Componentes

### TDataModule → Service + Repository

**Delphi**: Módulo de dados com queries e lógica de acesso
**Java Spring**: Separação em Service (lógica) e Repository (acesso)

```java
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
    
    public List<User> findActiveUsers() {
        return userRepository.findByActiveTrue();
    }
}
```

### TForm → RestController

**Delphi**: Formulário com eventos de botão
**Java Spring**: Controller REST com endpoints

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private UserService userService;
    
    @GetMapping
    public ResponseEntity<List<User>> getUsers() {
        return ResponseEntity.ok(userService.findActiveUsers());
    }
}
```

## 2. Mapeamento de Padrões

Padrões de migração serão definidos durante implementação.

## 3. Mapeamento de Tecnologias

- **Delphi VCL** → **Spring Boot REST API + Frontend**
- **ADO/DBExpress** → **Spring Data JPA**
- **TQuery** → **JpaRepository methods**
- **TDataSource** → **Service layer**
- **Exception handling** → **@ExceptionHandler**

