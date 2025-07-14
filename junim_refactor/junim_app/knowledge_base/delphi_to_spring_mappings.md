# Mapeamento de Padrões Delphi para Java Spring

Este documento contém padrões e exemplos de conversão de código Delphi para Java Spring Boot.

## TDataModule → Spring Data JPA Repository + Service

Um `TDataModule` em Delphi que gerencia acesso a dados é análogo a uma combinação de `@Repository` e `@Service` no Spring.

### Delphi (DataModule):
```pascal
unit DataModule1;

interface

uses
  SysUtils, Classes, DB, ADODB;

type
  TDataModule1 = class(TDataModule)
    Connection1: TADOConnection;
    QryUsers: TADOQuery;
    QryProducts: TADOQuery;
    DsUsers: TDataSource;
    DsProducts: TDataSource;
  private
  public
    procedure LoadUsers;
    procedure LoadUserById(Id: Integer);
    function SaveUser(Name, Email: string): Boolean;
  end;

var
  DataModule1: TDataModule1;

implementation

procedure TDataModule1.LoadUsers;
begin
  QryUsers.Close;
  QryUsers.SQL.Clear;
  QryUsers.SQL.Add('SELECT * FROM USERS WHERE ACTIVE = 1');
  QryUsers.Open;
end;

procedure TDataModule1.LoadUserById(Id: Integer);
begin
  QryUsers.Close;
  QryUsers.SQL.Clear;
  QryUsers.SQL.Add('SELECT * FROM USERS WHERE ID = :ID');
  QryUsers.Parameters.ParamByName('ID').Value := Id;
  QryUsers.Open;
end;

function TDataModule1.SaveUser(Name, Email: string): Boolean;
begin
  try
    QryUsers.Close;
    QryUsers.SQL.Clear;
    QryUsers.SQL.Add('INSERT INTO USERS (NAME, EMAIL) VALUES (:NAME, :EMAIL)');
    QryUsers.Parameters.ParamByName('NAME').Value := Name;
    QryUsers.Parameters.ParamByName('EMAIL').Value := Email;
    QryUsers.ExecSQL;
    Result := True;
  except
    Result := False;
  end;
end;
```

### Java Spring (Entity + Repository + Service):

**User.java (Entity)**:
```java
package com.example.modernizedapp.model;

import jakarta.persistence.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "name")
    private String name;
    
    @Column(name = "email")
    private String email;
    
    @Column(name = "active")
    private Boolean active = true;
    
    // Constructors, getters, setters
    public User() {}
    
    public User(String name, String email) {
        this.name = name;
        this.email = email;
        this.active = true;
    }
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public Boolean getActive() { return active; }
    public void setActive(Boolean active) { this.active = active; }
}
```

**UserRepository.java (Repository)**:
```java
package com.example.modernizedapp.repository;

import com.example.modernizedapp.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    @Query("SELECT u FROM User u WHERE u.active = true")
    List<User> findActiveUsers();
    
    @Query("SELECT u FROM User u WHERE u.id = :id")
    Optional<User> findUserById(@Param("id") Long id);
}
```

**UserService.java (Service)**:
```java
package com.example.modernizedapp.service;

import com.example.modernizedapp.model.User;
import com.example.modernizedapp.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public List<User> loadUsers() {
        return userRepository.findActiveUsers();
    }
    
    public Optional<User> loadUserById(Long id) {
        return userRepository.findUserById(id);
    }
    
    public boolean saveUser(String name, String email) {
        try {
            User user = new User(name, email);
            userRepository.save(user);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
```

## TForm com TButton.OnClick → @RestController

A lógica de negócio dentro de um manipulador de evento de botão deve ser extraída para um endpoint REST.

### Delphi (Form):
```pascal
unit MainForm;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Grids, DBGrids, DB;

type
  TMainForm = class(TForm)
    BtnLoadUsers: TButton;
    BtnSaveUser: TButton;
    EditName: TEdit;
    EditEmail: TEdit;
    DBGrid1: TDBGrid;
    procedure BtnLoadUsersClick(Sender: TObject);
    procedure BtnSaveUserClick(Sender: TObject);
  private
  public
  end;

var
  MainForm: TMainForm;

implementation

uses DataModule1;

procedure TMainForm.BtnLoadUsersClick(Sender: TObject);
begin
  DataModule1.LoadUsers;
end;

procedure TMainForm.BtnSaveUserClick(Sender: TObject);
begin
  if (EditName.Text <> '') and (EditEmail.Text <> '') then
  begin
    if DataModule1.SaveUser(EditName.Text, EditEmail.Text) then
    begin
      ShowMessage('Usuário salvo com sucesso!');
      DataModule1.LoadUsers; // Recarrega lista
      EditName.Clear;
      EditEmail.Clear;
    end
    else
      ShowMessage('Erro ao salvar usuário!');
  end
  else
    ShowMessage('Preencha todos os campos!');
end;
```

### Java Spring (Controller):

**UserController.java**:
```java
package com.example.modernizedapp.controller;

import com.example.modernizedapp.model.User;
import com.example.modernizedapp.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public ResponseEntity<List<User>> loadUsers() {
        List<User> users = userService.loadUsers();
        return ResponseEntity.ok(users);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        return userService.loadUserById(id)
                .map(user -> ResponseEntity.ok(user))
                .orElse(ResponseEntity.notFound().build());
    }
    
    @PostMapping
    public ResponseEntity<String> saveUser(@RequestBody UserRequest request) {
        if (request.getName() == null || request.getName().isEmpty() ||
            request.getEmail() == null || request.getEmail().isEmpty()) {
            return ResponseEntity.badRequest().body("Preencha todos os campos!");
        }
        
        boolean success = userService.saveUser(request.getName(), request.getEmail());
        
        if (success) {
            return ResponseEntity.ok("Usuário salvo com sucesso!");
        } else {
            return ResponseEntity.internalServerError().body("Erro ao salvar usuário!");
        }
    }
}

// DTO para request
class UserRequest {
    private String name;
    private String email;
    
    // Getters and Setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
}
```

## TQuery com SQL → Spring Data JPA Query Methods

Queries SQL em componentes TQuery são convertidas para métodos de repository.

### Delphi:
```pascal
procedure SearchUsersByName(Name: string);
begin
  QryUsers.Close;
  QryUsers.SQL.Clear;
  QryUsers.SQL.Add('SELECT * FROM USERS WHERE NAME LIKE :NAME AND ACTIVE = 1');
  QryUsers.Parameters.ParamByName('NAME').Value := '%' + Name + '%';
  QryUsers.Open;
end;
```

### Java Spring:
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    @Query("SELECT u FROM User u WHERE u.name LIKE %:name% AND u.active = true")
    List<User> findActiveUsersByNameContaining(@Param("name") String name);
    
    // Ou usando método derivado
    List<User> findByNameContainingAndActiveTrue(String name);
}
```

## Manipulação de Exceções

### Delphi:
```pascal
try
  QryUsers.ExecSQL;
  ShowMessage('Operação realizada com sucesso!');
except
  on E: Exception do
    ShowMessage('Erro: ' + E.Message);
end;
```

### Java Spring:
```java
@Service
public class UserService {
    
    @Transactional
    public ResponseDto saveUser(UserDto userDto) {
        try {
            User user = new User(userDto.getName(), userDto.getEmail());
            userRepository.save(user);
            return new ResponseDto(true, "Operação realizada com sucesso!");
        } catch (Exception e) {
            return new ResponseDto(false, "Erro: " + e.getMessage());
        }
    }
}
```

## Validação de Dados

### Delphi:
```pascal
function ValidateEmail(Email: string): Boolean;
begin
  Result := (Pos('@', Email) > 0) and (Pos('.', Email) > 0);
end;

procedure TMainForm.BtnSaveUserClick(Sender: TObject);
begin
  if EditName.Text = '' then
  begin
    ShowMessage('Nome é obrigatório!');
    EditName.SetFocus;
    Exit;
  end;
  
  if not ValidateEmail(EditEmail.Text) then
  begin
    ShowMessage('Email inválido!');
    EditEmail.SetFocus;
    Exit;
  end;
  
  // Salvar usuário...
end;
```

### Java Spring:
```java
// DTO com validações
public class UserDto {
    @NotBlank(message = "Nome é obrigatório!")
    private String name;
    
    @Email(message = "Email inválido!")
    @NotBlank(message = "Email é obrigatório!")
    private String email;
    
    // Getters and Setters...
}

// Controller com validação
@PostMapping
public ResponseEntity<?> saveUser(@Valid @RequestBody UserDto userDto, BindingResult result) {
    if (result.hasErrors()) {
        List<String> errors = result.getAllErrors().stream()
                .map(DefaultMessageSourceResolvable::getDefaultMessage)
                .collect(Collectors.toList());
        return ResponseEntity.badRequest().body(errors);
    }
    
    return userService.saveUser(userDto);
}
```

## Configuração de Banco de Dados

### Delphi (Connection):
```pascal
procedure TDataModule1.DataModuleCreate(Sender: TObject);
begin
  Connection1.ConnectionString := 'Provider=SQLOLEDB;Data Source=localhost;' +
                                  'Initial Catalog=MyDatabase;User ID=sa;Password=123456;';
  Connection1.Connected := True;
end;
```

### Java Spring (application.properties):
```properties
# Database Configuration
spring.datasource.url=jdbc:sqlserver://localhost:1433;databaseName=MyDatabase
spring.datasource.username=sa
spring.datasource.password=123456
spring.datasource.driver-class-name=com.microsoft.sqlserver.jdbc.SQLServerDriver

# JPA Configuration
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.SQLServerDialect
```

## Estrutura de Projeto Spring Boot

### Estrutura de diretórios:
```
src/
  main/
    java/
      com/example/modernizedapp/
        ModernizedAppApplication.java (Main class)
        controller/
          UserController.java
        service/
          UserService.java
        repository/
          UserRepository.java
        model/
          User.java
        config/
          DatabaseConfig.java
    resources/
      application.properties
      static/ (arquivos estáticos)
      templates/ (templates se usar Thymeleaf)
  test/
    java/
      com/example/modernizedapp/
        UserServiceTest.java
pom.xml
```

### Classe Principal (Application):
```java
package com.example.modernizedapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ModernizedAppApplication {
    public static void main(String[] args) {
        SpringApplication.run(ModernizedAppApplication.class, args);
    }
}
```

## Mapeamentos Comuns de Componentes

| Delphi | Java Spring |
|--------|-------------|
| TDataModule | @Service + @Repository |
| TForm | @RestController |
| TQuery/TADOQuery | JpaRepository methods |
| TDataSource | @Autowired Service |
| TButton.OnClick | @PostMapping/@GetMapping |
| TEdit/TDBEdit | @RequestBody DTO fields |
| TDBGrid | JSON Response Array |
| ShowMessage | ResponseEntity with message |
| Exception handling | @ExceptionHandler |
| TTimer | @Scheduled methods |
| TStringList | List&lt;String&gt; |

## Dependências Maven (pom.xml)

```xml
<dependencies>
    <!-- Spring Boot Starter Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Spring Boot Starter Data JPA -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    
    <!-- SQL Server Driver -->
    <dependency>
        <groupId>com.microsoft.sqlserver</groupId>
        <artifactId>mssql-jdbc</artifactId>
    </dependency>
    
    <!-- Validation -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    
    <!-- Test -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```
