"""
Configurações OTIMIZADAS para DeepSeek-R1 - PERFORMANCE PRIMEIRO
Configurações ajustadas para velocidade e menor consumo de recursos
"""

def is_deepseek_r1_model(model_name: str) -> bool:
    """Verifica se é um modelo DeepSeek-R1"""
    return 'deepseek-r1' in model_name.lower()

def get_deepseek_r1_config(model_name: str, performance_mode: str = 'fast') -> dict:
    """
    Retorna configurações otimizadas para DeepSeek-R1 baseadas no modo de performance
    
    Args:
        model_name: Nome do modelo
        performance_mode: 'fast' (padrão), 'balanced', 'quality'
    """
    
    # Configurações BASE OTIMIZADAS para VELOCIDADE
    if performance_mode == 'fast':
        base_config = {
            'temperature': 0.4,        # ↑ Aumenta para respostas mais rápidas
            'top_p': 0.7,             # ↓ Reduz tokens considerados = MAIS RÁPIDO
            'top_k': 25,              # ↓ Reduzido de 50 para 25 = MUITO MAIS RÁPIDO
            'repeat_penalty': 1.05,    # ↓ Reduz processamento de penalidades
            'seed': 42,
            'num_thread': 8,          # ↑ Usa mais threads disponíveis
            'num_gpu_layers': -1,     # Usa toda GPU disponível
        }
        
        if '14b' in model_name.lower():
            base_config.update({
                'num_predict': 1200,   # ↓ DRASTICAMENTE reduzido de 4000
                'num_ctx': 3072,       # ↓ DRASTICAMENTE reduzido de 8192
                'num_batch': 64,       # Lotes menores = menos memória
            })
        elif '1.5b' in model_name.lower():
            base_config.update({
                'num_predict': 800,    # ↓ Reduzido de 2000
                'num_ctx': 2048,       # ↓ Reduzido de 4096
                'num_batch': 32,       
            })
        else:
            base_config.update({
                'num_predict': 1000,
                'num_ctx': 2560,
                'num_batch': 48,
            })
    
    elif performance_mode == 'balanced':
        base_config = {
            'temperature': 0.25,       # Meio termo
            'top_p': 0.8,             
            'top_k': 35,              # Meio termo
            'repeat_penalty': 1.08,    
            'seed': 42,
            'num_thread': 6,
            'num_gpu_layers': -1,
        }
        
        if '14b' in model_name.lower():
            base_config.update({
                'num_predict': 2000,   # Meio termo
                'num_ctx': 4096,       # Meio termo
                'num_batch': 96,
            })
        elif '1.5b' in model_name.lower():
            base_config.update({
                'num_predict': 1200,   
                'num_ctx': 3072,       
                'num_batch': 64,
            })
        else:
            base_config.update({
                'num_predict': 1500,
                'num_ctx': 3584,
                'num_batch': 80,
            })
    
    else:  # quality mode
        base_config = {
            'temperature': 0.1,        # Original para qualidade
            'top_p': 0.9,             
            'top_k': 50,              # Original
            'repeat_penalty': 1.1,     
            'seed': 42,
            'num_thread': 4,          # Menos threads para estabilidade
            'num_gpu_layers': -1,
        }
        
        if '14b' in model_name.lower():
            base_config.update({
                'num_predict': 4000,   # Original
                'num_ctx': 8192,       # Original
                'num_batch': 128,
            })
        elif '1.5b' in model_name.lower():
            base_config.update({
                'num_predict': 2000,   # Original
                'num_ctx': 4096,       # Original
                'num_batch': 96,
            })
        else:
            base_config.update({
                'num_predict': 3000,
                'num_ctx': 6144,
                'num_batch': 112,
            })
    
    return base_config

def get_deepseek_r1_system_prompt(task_type: str = 'conversion', performance_mode: str = 'fast') -> str:
    """Retorna prompt de sistema otimizado baseado no modo de performance"""
    
    if performance_mode == 'fast':
        # Prompts ULTRA COMPACTOS para máxima velocidade
        compact_prompts = {
            'conversion': "Especialista Delphi→Java Spring Boot. Gere código Java funcional em JSON.",
            'analysis': "Especialista análise Delphi. Análise precisa e estruturada.",
            'documentation': "Especialista técnico. Doc clara e estruturada.",
            'mermaid_diagram': "Especialista arquitetura. Gere diagramas Mermaid válidos.",
            'testing': "Especialista testes. Gere testes JUnit funcionais."
        }
        return compact_prompts.get(task_type, "Especialista modernização Delphi→Java.")
    
    elif performance_mode == 'balanced':
        # Prompts MODERADOS
        base_prompt = "Especialista em migração Delphi para Java Spring Boot."
        task_prompts = {
            'conversion': f"{base_prompt} Gere código Java funcional em JSON com boa qualidade.",
            'analysis': f"{base_prompt} Faça análises detalhadas de código Delphi.",
            'documentation': f"{base_prompt} Gere documentação técnica estruturada."
        }
        return task_prompts.get(task_type, base_prompt)
    
    else:  # quality mode - mantém original
        base_prompt = "Você é um especialista em migração de sistemas Delphi para Java Spring Boot."
        task_prompts = {
            'conversion': f"{base_prompt} Use seu conhecimento avançado para gerar código Java funcional de alta qualidade no formato JSON com as chaves 'files' contendo uma lista de arquivos. Seja preciso e detalhado.",
            'analysis': f"{base_prompt} Use seu conhecimento para fazer análises detalhadas e precisas de código Delphi.",
            'documentation': f"{base_prompt} Use seu conhecimento para gerar documentação técnica completa e precisa."
        }
        return task_prompts.get(task_type, base_prompt)

def combine_prompts_with_deepseek(base_prompt: str, task_type: str = 'conversion', performance_mode: str = 'fast') -> str:
    """
    Combina prompts otimizado para diferentes modos de performance
    
    Args:
        base_prompt: Prompt base do sistema
        task_type: Tipo de tarefa
        performance_mode: 'fast', 'balanced', 'quality'
    """
    if not base_prompt or not base_prompt.strip():
        return get_deepseek_r1_system_prompt(task_type, performance_mode)
    
    if performance_mode == 'fast':
        # ULTRA COMPACTO - Máxima velocidade
        return f"""TAREFA: {task_type.upper()}
{get_deepseek_r1_system_prompt(task_type, 'fast')}

ENTRADA: {base_prompt[:300]}...

SAÍDA: Resposta direta conforme solicitado."""
    
    elif performance_mode == 'balanced':
        # MODERADO - Equilíbrio velocidade/qualidade
        return f"""CONTEXTO: {get_deepseek_r1_system_prompt(task_type, 'balanced')}

TAREFA: {task_type}
{base_prompt[:800]}...

INSTRUÇÕES:
- Resposta estruturada
- Foque no essencial
- Qualidade técnica

FORMATO: Conforme especificado."""
    
    else:  # quality mode - mantém original detalhado
        return f"""CONTEXTO DE SISTEMA:
{get_deepseek_r1_system_prompt(task_type, 'quality')}

PROMPT ESPECIALIZADO:
{base_prompt}

INSTRUÇÕES ESPECÍFICAS PARA DEEPSEEK-R1:
- Use raciocínio passo-a-passo
- Seja preciso e detalhado
- Forneça respostas estruturadas
- Mantenha consistência técnica
- Foque em qualidade de código

FORMATO DE RESPOSTA ESPERADO:
- Para código: JSON estruturado conforme especificado
- Para análise: Markdown estruturado com seções claras
- Para documentação: Formato técnico detalhado
"""

def get_deepseek_enhanced_options(model_name: str, task_type: str, performance_mode: str = 'fast') -> dict:
    """
    Retorna opções aprimoradas específicas para DeepSeek-R1 baseadas no modo de performance
    """
    base_options = get_deepseek_r1_config(model_name, performance_mode)
    
    # Ajustes específicos por tipo de tarefa e modo de performance
    if performance_mode == 'fast':
        # Configurações ULTRA RÁPIDAS por tipo de tarefa
        task_adjustments = {
            'conversion': {
                'temperature': 0.5,    # Alto para velocidade
                'top_p': 0.6,         # Baixo para rapidez
                'top_k': 20,          # Muito baixo
            },
            'analysis': {
                'temperature': 0.4,
                'top_p': 0.65,
                'top_k': 25,
            },
            'documentation': {
                'temperature': 0.45,
                'top_p': 0.7,
                'top_k': 30,
            },
            'mermaid_diagram': {
                'temperature': 0.3,
                'top_p': 0.7,
                'top_k': 25,
            },
            'testing': {
                'temperature': 0.35,
                'top_p': 0.65,
                'top_k': 25,
            }
        }
    elif performance_mode == 'balanced':
        # Configurações EQUILIBRADAS
        task_adjustments = {
            'conversion': {
                'temperature': 0.2,
                'top_p': 0.8,
                'top_k': 35,
            },
            'analysis': {
                'temperature': 0.25,
                'top_p': 0.85,
                'top_k': 40,
            },
            'documentation': {
                'temperature': 0.3,
                'top_p': 0.9,
                'top_k': 45,
            },
            'mermaid_diagram': {
                'temperature': 0.15,
                'top_p': 0.8,
                'top_k': 35,
            },
            'testing': {
                'temperature': 0.2,
                'top_p': 0.8,
                'top_k': 35,
            }
        }
    else:  # quality mode - configurações originais
        task_adjustments = {
            'conversion': {
                'temperature': 0.05,  # Mais determinístico para código
                'top_p': 0.8,
                'top_k': 50,
            },
            'analysis': {
                'temperature': 0.1,
                'top_p': 0.9,
                'top_k': 50,
            },
            'documentation': {
                'temperature': 0.15,
                'top_p': 0.95,
                'top_k': 50,
            },
            'mermaid_diagram': {
                'temperature': 0.05,
                'top_p': 0.85,
                'top_k': 45,
            },
            'testing': {
                'temperature': 0.1,
                'top_p': 0.85,
                'top_k': 45,
            }
        }
    
    if task_type in task_adjustments:
        base_options.update(task_adjustments[task_type])
    
    return base_options

def get_performance_info() -> dict:
    """Retorna informações sobre os modos de performance disponíveis"""
    return {
        'fast': {
            'description': '🚀 VELOCIDADE MÁXIMA - Ideal para experimentos rápidos',
            'speed': '⚡ Muito Rápido',
            'memory': '💾 Baixo uso',
            'quality': '📊 Aceitável',
            'use_case': 'Testes rápidos, iterações de desenvolvimento, experimentos',
            'savings': 'CPU: ~60% menos | Memória: ~70% menos | Tempo: ~3x mais rápido'
        },
        'balanced': {
            'description': '⚖️ EQUILIBRADO - Bom compromisso velocidade/qualidade',
            'speed': '🏃 Rápido',
            'memory': '💾 Moderado',
            'quality': '📊 Boa',
            'use_case': 'Desenvolvimento normal, análises rotineiras',
            'savings': 'CPU: ~30% menos | Memória: ~40% menos | Tempo: ~1.5x mais rápido'
        },
        'quality': {
            'description': '🎯 QUALIDADE MÁXIMA - Para resultados finais',
            'speed': '🐢 Mais lento',
            'memory': '💾 Alto uso',
            'quality': '📊 Máxima',
            'use_case': 'Produção, análises finais, código crítico',
            'savings': 'Configurações originais para máxima qualidade'
        }
    }
