package com.empresa.sistema.repository;

import com.empresa.sistema.entity.Produtos;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface ProdutosRepository extends JpaRepository<Produtos, Long> {

    // Busca por nome/descrição
    List<Produtos> findByNomeContainingIgnoreCase(String nome);
    
    // Busca por status ativo
    List<Produtos> findByAtivoTrue();
    
    // Query customizada
    @Query("SELECT e FROM Produtos e WHERE e.ativo = :ativo ORDER BY e.nome")
    List<Produtos> buscarPorStatus(@Param("ativo") Boolean ativo);
    
    // Existe por nome
    boolean existsByNome(String nome);
}