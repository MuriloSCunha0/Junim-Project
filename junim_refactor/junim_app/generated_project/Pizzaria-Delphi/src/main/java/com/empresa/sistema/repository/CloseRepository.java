package com.empresa.sistema.repository;

import com.empresa.sistema.entity.Close;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface CloseRepository extends JpaRepository<Close, Long> {

    // Busca por nome/descrição
    List<Close> findByNomeContainingIgnoreCase(String nome);
    
    // Busca por status ativo
    List<Close> findByAtivoTrue();
    
    // Query customizada
    @Query("SELECT e FROM Close e WHERE e.ativo = :ativo ORDER BY e.nome")
    List<Close> buscarPorStatus(@Param("ativo") Boolean ativo);
    
    // Existe por nome
    boolean existsByNome(String nome);
}