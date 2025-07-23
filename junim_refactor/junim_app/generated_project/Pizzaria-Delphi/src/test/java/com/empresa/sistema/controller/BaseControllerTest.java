package com.empresa.sistema.controller;

import com.empresa.sistema.service.BaseService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(BaseController.class)
public class BaseControllerTest {

    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private BaseService service;
    
    @Test
    public void testListarTodos() throws Exception {
        mockMvc.perform(get("/api/base"))
               .andExpect(status().isOk());
    }
}