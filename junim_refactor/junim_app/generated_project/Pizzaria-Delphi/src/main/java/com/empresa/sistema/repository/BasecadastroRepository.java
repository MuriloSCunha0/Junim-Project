package com.empresa.sistema.repository;

import com.empresa.sistema.entity.Basecadastro;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface BasecadastroRepository extends JpaRepository<Basecadastro, Long> {

    // Busca por nome/descrição
    List<Basecadastro> findByNomeContainingIgnoreCase(String nome);
    
    // Busca por status ativo
    List<Basecadastro> findByAtivoTrue();
    
    // Query customizada
    @Query("SELECT e FROM Basecadastro e WHERE e.ativo = :ativo ORDER BY e.nome")
    List<Basecadastro> buscarPorStatus(@Param("ativo") Boolean ativo);
    
    // Existe por nome
    boolean existsByNome(String nome);
}