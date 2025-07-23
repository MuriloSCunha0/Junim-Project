package com.empresa.sistema.repository;

import com.empresa.sistema.entity.Show;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface ShowRepository extends JpaRepository<Show, Long> {

    // Busca por nome/descrição
    List<Show> findByNomeContainingIgnoreCase(String nome);
    
    // Busca por status ativo
    List<Show> findByAtivoTrue();
    
    // Query customizada
    @Query("SELECT e FROM Show e WHERE e.ativo = :ativo ORDER BY e.nome")
    List<Show> buscarPorStatus(@Param("ativo") Boolean ativo);
    
    // Existe por nome
    boolean existsByNome(String nome);
}