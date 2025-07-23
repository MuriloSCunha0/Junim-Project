package com.empresa.projetomodernizadomodern;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.CrossOrigin;

/**
 * Classe principal da aplicação ProjetoModernizadoModern
 * Projeto modernizado do Delphi para Java Spring Boot
 */
@SpringBootApplication
@CrossOrigin(origins = "*")
public class Application {
    
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
        System.out.println("🚀 ProjetoModernizadoModern iniciado com sucesso!");
        System.out.println("📊 H2 Console: http://localhost:8080/h2-console");
        System.out.println("🌐 API: http://localhost:8080/api");
    }
}