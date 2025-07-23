package com.empresa.sistema.repository;

import com.empresa.sistema.entity.Base;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface BaseRepository extends JpaRepository<Base, Long> {

    // Busca por nome/descrição
    List<Base> findByNomeContainingIgnoreCase(String nome);
    
    // Busca por status ativo
    List<Base> findByAtivoTrue();
    
    // Query customizada
    @Query("SELECT e FROM Base e WHERE e.ativo = :ativo ORDER BY e.nome")
    List<Base> buscarPorStatus(@Param("ativo") Boolean ativo);
    
    // Existe por nome
    boolean existsByNome(String nome);
}