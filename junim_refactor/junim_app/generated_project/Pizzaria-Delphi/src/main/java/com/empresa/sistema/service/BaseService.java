package com.empresa.sistema.service;

import com.empresa.sistema.entity.Base;
import com.empresa.sistema.repository.BaseRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class BaseService {

    @Autowired
    private BaseRepository repository;
    
    /**
     * Busca todos os registros ativos
     */
    @Transactional(readOnly = true)
    public List<Base> buscarTodos() {
        return repository.findByAtivoTrue();
    }
    
    /**
     * Busca por ID
     */
    @Transactional(readOnly = true)
    public Optional<Base> buscarPorId(Long id) {
        return repository.findById(id);
    }
    
    /**
     * Busca por nome
     */
    @Transactional(readOnly = true)
    public List<Base> buscarPorNome(String nome) {
        return repository.findByNomeContainingIgnoreCase(nome);
    }
    
    /**
     * Salva ou atualiza
     */
    public Base salvar(Base entity) {
        // Validações de negócio
        validar(entity);
        return repository.save(entity);
    }
    
    /**
     * Remove por ID
     */
    public void remover(Long id) {
        if (repository.existsById(id)) {
            repository.deleteById(id);
        } else {
            throw new RuntimeException("Registro não encontrado: " + id);
        }
    }
    
    /**
     * Validações de negócio
     */
    private void validar(Base entity) {
        if (entity.getNome() == null || entity.getNome().trim().isEmpty()) {
            throw new IllegalArgumentException("Nome é obrigatório");
        }
        
        // Verificar duplicação
        if (entity.getId() == null && repository.existsByNome(entity.getNome())) {
            throw new IllegalArgumentException("Já existe um registro com este nome");
        }
    }
}