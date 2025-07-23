package com.empresa.sistema.controller;

import com.empresa.sistema.entity.Produtos;
import com.empresa.sistema.service.ProdutosService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import javax.validation.Valid;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/produtos")
@CrossOrigin(origins = "*")
public class ProdutosController {

    @Autowired
    private ProdutosService service;
    
    /**
     * Lista todos os registros
     */
    @GetMapping
    public ResponseEntity<List<Produtos>> listarTodos() {
        try {
            List<Produtos> lista = service.buscarTodos();
            return ResponseEntity.ok(lista);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Busca por ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<Produtos> buscarPorId(@PathVariable Long id) {
        try {
            Optional<Produtos> registro = service.buscarPorId(id);
            return registro.map(ResponseEntity::ok)
                         .orElse(ResponseEntity.notFound().build());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Busca por nome
     */
    @GetMapping("/buscar")
    public ResponseEntity<List<Produtos>> buscarPorNome(@RequestParam String nome) {
        try {
            List<Produtos> lista = service.buscarPorNome(nome);
            return ResponseEntity.ok(lista);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Cria novo registro
     */
    @PostMapping
    public ResponseEntity<Produtos> criar(@Valid @RequestBody Produtos entity) {
        try {
            Produtos salvo = service.salvar(entity);
            return ResponseEntity.status(HttpStatus.CREATED).body(salvo);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Atualiza registro
     */
    @PutMapping("/{id}")
    public ResponseEntity<Produtos> atualizar(@PathVariable Long id, @Valid @RequestBody Produtos entity) {
        try {
            entity.setId(id);
            Produtos salvo = service.salvar(entity);
            return ResponseEntity.ok(salvo);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Remove registro
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> remover(@PathVariable Long id) {
        try {
            service.remover(id);
            return ResponseEntity.noContent().build();
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}