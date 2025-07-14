"""
Carregador simples de prompts do JUNIM
"""

import os
from pathlib import Path

class SimplePromptLoader:
    """Carregador simples de prompts para o JUNIM"""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent
    
    def load_prompt(self, prompt_name: str) -> str:
        """Carrega um prompt específico"""
        try:
            prompt_file = self.prompts_dir / f"{prompt_name}.txt"
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return self._get_default_prompt(prompt_name)
        except Exception:
            return self._get_default_prompt(prompt_name)
    
    def _get_default_prompt(self, prompt_name: str) -> str:
        """Prompt padrão caso o arquivo não exista"""
        if 'analysis' in prompt_name:
            return """
Analise o código Delphi fornecido e extraia informações estruturais e funcionais.
Identifique classes, lógica de negócio, operações de banco e fluxos principais.
"""
        elif 'conversion' in prompt_name:
            return """
Converta o código Delphi para Java Spring Boot.
Use @RestController para Forms, @Service para lógica de negócio e @Repository para dados.
Mantenha a funcionalidade original mas aplique padrões Spring modernos.
"""
        else:
            return """
Você é um especialista em modernização de sistemas Delphi para Java Spring Boot.
Analise o código fornecido e forneça uma solução adequada.
"""
    
    def get_base_prompt(self) -> str:
        """Retorna prompt base"""
        return self.load_prompt("prompt_base")
    
    def get_analysis_prompt(self) -> str:
        """Retorna prompt de análise"""
        return self.load_prompt("simple_analysis_prompt")
    
    def get_conversion_prompt(self) -> str:
        """Retorna prompt de conversão"""
        return self.load_prompt("simple_conversion_prompt")

# Instância global simples
simple_prompt_loader = SimplePromptLoader()
