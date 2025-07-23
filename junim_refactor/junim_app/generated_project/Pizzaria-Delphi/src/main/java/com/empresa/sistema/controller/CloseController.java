package com.empresa.sistema.controller;

import com.empresa.sistema.entity.Close;
import com.empresa.sistema.service.CloseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import javax.validation.Valid;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/close")
@CrossOrigin(origins = "*")
public class CloseController {

    @Autowired
    private CloseService service;
    
    /**
     * Lista todos os registros
     */
    @GetMapping
    public ResponseEntity<List<Close>> listarTodos() {
        try {
            List<Close> lista = service.buscarTodos();
            return ResponseEntity.ok(lista);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Busca por ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<Close> buscarPorId(@PathVariable Long id) {
        try {
            Optional<Close> registro = service.buscarPorId(id);
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
    public ResponseEntity<List<Close>> buscarPorNome(@RequestParam String nome) {
        try {
            List<Close> lista = service.buscarPorNome(nome);
            return ResponseEntity.ok(lista);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Cria novo registro
     */
    @PostMapping
    public ResponseEntity<Close> criar(@Valid @RequestBody Close entity) {
        try {
            Close salvo = service.salvar(entity);
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
    public ResponseEntity<Close> atualizar(@PathVariable Long id, @Valid @RequestBody Close entity) {
        try {
            entity.setId(id);
            Close salvo = service.salvar(entity);
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