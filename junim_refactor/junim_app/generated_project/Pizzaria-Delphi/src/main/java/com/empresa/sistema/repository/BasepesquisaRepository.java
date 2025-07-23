package com.empresa.sistema.repository;

import com.empresa.sistema.entity.Basepesquisa;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface BasepesquisaRepository extends JpaRepository<Basepesquisa, Long> {

    // Busca por nome/descrição
    List<Basepesquisa> findByNomeContainingIgnoreCase(String nome);
    
    // Busca por status ativo
    List<Basepesquisa> findByAtivoTrue();
    
    // Query customizada
    @Query("SELECT e FROM Basepesquisa e WHERE e.ativo = :ativo ORDER BY e.nome")
    List<Basepesquisa> buscarPorStatus(@Param("ativo") Boolean ativo);
    
    // Existe por nome
    boolean existsByNome(String nome);
}