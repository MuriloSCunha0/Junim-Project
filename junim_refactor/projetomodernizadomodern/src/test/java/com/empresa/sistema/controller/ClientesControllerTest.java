package com.empresa.sistema.controller;

import com.empresa.sistema.service.ClientesService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(ClientesController.class)
public class ClientesControllerTest {

    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private ClientesService service;
    
    @Test
    public void testListarTodos() throws Exception {
        mockMvc.perform(get("/api/clientes"))
               .andExpect(status().isOk());
    }
}