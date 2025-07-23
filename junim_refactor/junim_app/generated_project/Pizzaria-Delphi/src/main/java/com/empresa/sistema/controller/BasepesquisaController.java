package com.empresa.sistema.controller;

import com.empresa.sistema.entity.Basepesquisa;
import com.empresa.sistema.service.BasepesquisaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import javax.validation.Valid;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/basepesquisa")
@CrossOrigin(origins = "*")
public class BasepesquisaController {

    @Autowired
    private BasepesquisaService service;
    
    /**
     * Lista todos os registros
     */
    @GetMapping
    public ResponseEntity<List<Basepesquisa>> listarTodos() {
        try {
            List<Basepesquisa> lista = service.buscarTodos();
            return ResponseEntity.ok(lista);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Busca por ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<Basepesquisa> buscarPorId(@PathVariable Long id) {
        try {
            Optional<Basepesquisa> registro = service.buscarPorId(id);
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
    public ResponseEntity<List<Basepesquisa>> buscarPorNome(@RequestParam String nome) {
        try {
            List<Basepesquisa> lista = service.buscarPorNome(nome);
            return ResponseEntity.ok(lista);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Cria novo registro
     */
    @PostMapping
    public ResponseEntity<Basepesquisa> criar(@Valid @RequestBody Basepesquisa entity) {
        try {
            Basepesquisa salvo = service.salvar(entity);
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
    public ResponseEntity<Basepesquisa> atualizar(@PathVariable Long id, @Valid @RequestBody Basepesquisa entity) {
        try {
            entity.setId(id);
            Basepesquisa salvo = service.salvar(entity);
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