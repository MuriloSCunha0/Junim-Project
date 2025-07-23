package com.empresa.sistema.repository;

import com.empresa.sistema.entity.Clientes;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface ClientesRepository extends JpaRepository<Clientes, Long> {

    // Busca por nome/descrição
    List<Clientes> findByNomeContainingIgnoreCase(String nome);
    
    // Busca por status ativo
    List<Clientes> findByAtivoTrue();
    
    // Query customizada
    @Query("SELECT e FROM Clientes e WHERE e.ativo = :ativo ORDER BY e.nome")
    List<Clientes> buscarPorStatus(@Param("ativo") Boolean ativo);
    
    // Existe por nome
    boolean existsByNome(String nome);
}