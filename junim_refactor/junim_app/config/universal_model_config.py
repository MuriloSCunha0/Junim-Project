"""
Configurações UNIVERSAIS OTIMIZADAS para Múltiplos Modelos LLM
Suporte para: DeepSeek-R1, CodeLlama, Llama2, Mistral, Gemma, etc.
Configurações ajustadas para velocidade e menor consumo de recursos
"""

def detect_model_type(model_name: str) -> str:
    """Detecta o tipo de modelo baseado no nome"""
    model_lower = model_name.lower()
    
    if 'deepseek-r1' in model_lower:
        return 'deepseek-r1'
    elif 'codellama' in model_lower:
        return 'codellama'
    elif 'llama2' in model_lower or 'llama-2' in model_lower:
        return 'llama2'
    elif 'llama3' in model_lower or 'llama-3' in model_lower:
        return 'llama3'
    elif 'mistral' in model_lower:
        return 'mistral'
    elif 'gemma' in model_lower:
        return 'gemma'
    elif 'qwen' in model_lower:
        return 'qwen'
    elif 'phi' in model_lower:
        return 'phi'
    else:
        return 'generic'

def get_model_size(model_name: str) -> str:
    """Detecta o tamanho do modelo baseado no nome"""
    model_lower = model_name.lower()
    
    if '1.5b' in model_lower or '1b' in model_lower:
        return 'small'
    elif '7b' in model_lower:
        return 'medium'
    elif '13b' in model_lower or '14b' in model_lower:
        return 'large'
    elif '30b' in model_lower or '34b' in model_lower or '70b' in model_lower:
        return 'xlarge'
    else:
        return 'medium'  # padrão

def get_universal_config(model_name: str, performance_mode: str = 'fast') -> dict:
    """
    Retorna configurações otimizadas universais baseadas no modelo e modo de performance
    
    Args:
        model_name: Nome do modelo (ex: codellama:7b, deepseek-r1:14b)
        performance_mode: 'fast' (padrão), 'balanced', 'quality'
    """
    
    model_type = detect_model_type(model_name)
    model_size = get_model_size(model_name)
    
    # Configurações BASE por modo de performance
    base_configs = {
        'fast': {
            'temperature': 0.3,        # Rápido e determinístico
            'top_p': 0.7,             # Menos tokens considerados
            'top_k': 25,              # Reduzido drasticamente
            'repeat_penalty': 1.05,    # Penalidade baixa
            'seed': 42,
            'num_thread': 8,          # Mais threads
            'num_gpu_layers': -1,     # Usa GPU se disponível
        },
        'balanced': {
            'temperature': 0.2,        # Meio termo
            'top_p': 0.8,             
            'top_k': 35,              
            'repeat_penalty': 1.08,    
            'seed': 42,
            'num_thread': 6,
            'num_gpu_layers': -1,
        },
        'quality': {
            'temperature': 0.1,        # Mais determinístico
            'top_p': 0.9,             
            'top_k': 50,              
            'repeat_penalty': 1.1,     
            'seed': 42,
            'num_thread': 4,
            'num_gpu_layers': -1,
        }
    }
    
    # Configurações específicas por tamanho do modelo
    size_configs = {
        'small': {  # 1-2B parâmetros
            'fast': {'num_predict': 600, 'num_ctx': 1536, 'num_batch': 32},
            'balanced': {'num_predict': 1000, 'num_ctx': 2048, 'num_batch': 48},
            'quality': {'num_predict': 1500, 'num_ctx': 3072, 'num_batch': 64}
        },
        'medium': {  # 7B parâmetros  
            'fast': {'num_predict': 800, 'num_ctx': 2048, 'num_batch': 48},
            'balanced': {'num_predict': 1200, 'num_ctx': 3072, 'num_batch': 64},
            'quality': {'num_predict': 2000, 'num_ctx': 4096, 'num_batch': 96}
        },
        'large': {  # 13-14B parâmetros
            'fast': {'num_predict': 1000, 'num_ctx': 2560, 'num_batch': 64},
            'balanced': {'num_predict': 1800, 'num_ctx': 4096, 'num_batch': 96},
            'quality': {'num_predict': 3000, 'num_ctx': 6144, 'num_batch': 128}
        },
        'xlarge': {  # 30B+ parâmetros
            'fast': {'num_predict': 1200, 'num_ctx': 3072, 'num_batch': 96},
            'balanced': {'num_predict': 2000, 'num_ctx': 4096, 'num_batch': 128},
            'quality': {'num_predict': 4000, 'num_ctx': 8192, 'num_batch': 256}
        }
    }
    
    # Ajustes específicos por tipo de modelo
    model_adjustments = {
        'codellama': {
            # CodeLlama é otimizado para código, pode ser mais determinístico
            'temperature_adjustment': -0.05,
            'top_p_adjustment': -0.1,
            'special_tokens': True
        },
        'deepseek-r1': {
            # DeepSeek-R1 funciona melhor com configurações específicas
            'temperature_adjustment': 0.0,
            'top_p_adjustment': 0.0,
            'reasoning_mode': True
        },
        'mistral': {
            # Mistral é eficiente, pode usar configurações mais agressivas
            'temperature_adjustment': 0.05,
            'top_p_adjustment': 0.05,
            'efficient_attention': True
        },
        'llama2': {
            # Llama2 é estável com configurações padrão
            'temperature_adjustment': 0.0,
            'top_p_adjustment': 0.0,
            'stable_mode': True
        },
        'llama3': {
            # Llama3 melhorado, mais eficiente
            'temperature_adjustment': -0.02,
            'top_p_adjustment': 0.02,
            'improved_reasoning': True
        }
    }
    
    # Combina configurações
    config = base_configs[performance_mode].copy()
    config.update(size_configs[model_size][performance_mode])
    
    # Aplica ajustes específicos do modelo
    if model_type in model_adjustments:
        adjustments = model_adjustments[model_type]
        
        # Ajusta temperatura
        if 'temperature_adjustment' in adjustments:
            config['temperature'] += adjustments['temperature_adjustment']
            config['temperature'] = max(0.01, min(1.0, config['temperature']))
        
        # Ajusta top_p
        if 'top_p_adjustment' in adjustments:
            config['top_p'] += adjustments['top_p_adjustment']
            config['top_p'] = max(0.1, min(1.0, config['top_p']))
        
        # Adiciona flags especiais
        for key, value in adjustments.items():
            if key not in ['temperature_adjustment', 'top_p_adjustment']:
                config[f'model_{key}'] = value
    
    return config

def get_available_models() -> dict:
    """Retorna lista de modelos suportados com suas características"""
    return {
        'codellama:7b': {
            'type': 'codellama',
            'size': 'medium',
            'description': '🔥 RECOMENDADO para código - CodeLlama 7B',
            'strengths': ['Geração de código', 'Debugging'],
            'best_for': 'Conversão Delphi→Java',
            'performance': '⚡ Rápido',
            'quality': '📊 Excelente para código'
        },
        'deepseek-r1:14b': {
            'type': 'deepseek-r1',
            'size': 'large',
            'description': '🧠 DeepSeek-R1 14B - Raciocínio avançado',
            'strengths': ['Raciocínio complexo', 'Análise detalhada'],
            'best_for': 'Análise complexa de sistemas',
            'performance': '🐢 Mais lento',
            'quality': '📊 Qualidade máxima'
        },
        'mistral:7b': {
            'type': 'mistral',
            'size': 'medium',
            'description': '⚡ Mistral 7B - Muito eficiente',
            'strengths': ['Eficiência', 'Velocidade'],
            'best_for': 'Análise rápida',
            'performance': '⚡ Muito rápido',
            'quality': '📊 Boa'
        },
        'llama3:8b': {
            'type': 'llama3',
            'size': 'medium',
            'description': '🚀 Llama3 8B - Equilibrado',
            'strengths': ['Versatilidade', 'Eficiência'],
            'best_for': 'Uso geral',
            'performance': '🏃 Rápido',
            'quality': '📊 Muito boa'
        }
    }

def get_model_system_prompt(model_name: str, task_type: str = 'conversion', performance_mode: str = 'fast') -> str:
    """Retorna prompt de sistema otimizado baseado no modelo e modo de performance"""
    
    model_type = detect_model_type(model_name)
    
    # Prompts base por tipo de modelo
    base_prompts = {
        'codellama': {
            'fast': "Expert Delphi→Java developer. Generate clean, functional Java Spring Boot code.",
            'balanced': "Expert software engineer specializing in Delphi to Java Spring Boot migration. Generate high-quality, well-structured code.",
            'quality': "Senior software architect with deep expertise in Delphi and Java Spring Boot. Generate production-ready, optimized code with best practices."
        },
        'deepseek-r1': {
            'fast': "Delphi→Java Spring Boot expert. Analyze and convert systematically.",
            'balanced': "Expert system architect specializing in legacy system modernization from Delphi to Java Spring Boot.",
            'quality': "Senior software architect with extensive experience in modernizing Delphi applications to Java Spring Boot. Use systematic reasoning and best practices."
        },
        'generic': {
            'fast': "Software developer expert in Delphi and Java. Convert code efficiently.",
            'balanced': "Experienced software engineer specializing in system modernization from Delphi to Java Spring Boot.",
            'quality': "Senior software engineer with expertise in legacy system modernization, specifically Delphi to Java Spring Boot migrations."
        }
    }
    
    # Prompts específicos por tarefa
    task_prompts = {
        'conversion': 'Generate functional Java Spring Boot code in JSON format.',
        'analysis': 'Analyze Delphi code structure and provide detailed insights.',
        'documentation': 'Generate clear, structured technical documentation.',
        'mermaid_diagram': 'Create valid Mermaid diagrams for system architecture.',
        'testing': 'Generate comprehensive JUnit test cases.'
    }
    
    # Seleciona prompt base
    if model_type in base_prompts:
        base_prompt = base_prompts[model_type][performance_mode]
    else:
        base_prompt = base_prompts['generic'][performance_mode]
    
    # Adiciona prompt específico da tarefa
    task_prompt = task_prompts.get(task_type, 'Complete the requested task efficiently.')
    
    return f"{base_prompt} {task_prompt}"

def combine_prompts_universal(base_prompt: str, task_type: str = 'conversion', model_name: str = 'codellama:7b', performance_mode: str = 'fast') -> str:
    """
    Combina prompts de forma otimizada para qualquer modelo
    
    Args:
        base_prompt: Prompt base do sistema
        task_type: Tipo de tarefa
        model_name: Nome do modelo
        performance_mode: 'fast', 'balanced', 'quality'
    """
    if not base_prompt or not base_prompt.strip():
        return get_model_system_prompt(model_name, task_type, performance_mode)
    
    model_type = detect_model_type(model_name)
    system_prompt = get_model_system_prompt(model_name, task_type, performance_mode)
    
    if performance_mode == 'fast':
        # ULTRA COMPACTO - Máxima velocidade
        return f"""TASK: {task_type.upper()}
{system_prompt}

INPUT: {base_prompt[:400]}...

OUTPUT: Direct response as requested."""
    
    elif performance_mode == 'balanced':
        # MODERADO - Equilíbrio velocidade/qualidade
        return f"""CONTEXT: {system_prompt}

TASK: {task_type}
{base_prompt[:1000]}...

INSTRUCTIONS:
- Structured response
- Focus on essentials
- Maintain technical quality

FORMAT: As specified in prompt."""
    
    else:  # quality mode
        # COMPLETO - Máxima qualidade
        model_instructions = {
            'codellama': "Use your code generation expertise to produce clean, efficient Java Spring Boot code.",
            'deepseek-r1': "Apply systematic reasoning and step-by-step analysis for optimal results.",
            'generic': "Apply best practices and thorough analysis for high-quality output."
        }
        
        instruction = model_instructions.get(model_type, model_instructions['generic'])
        
        return f"""SYSTEM CONTEXT:
{system_prompt}

SPECIALIZED PROMPT:
{base_prompt}

MODEL-SPECIFIC INSTRUCTIONS:
{instruction}

EXPECTED OUTPUT FORMAT:
- For code: Structured JSON with clean, functional code
- For analysis: Markdown with clear sections and insights
- For documentation: Professional technical format
"""

def get_enhanced_options_universal(model_name: str, task_type: str, performance_mode: str = 'fast') -> dict:
    """
    Retorna opções aprimoradas universais para qualquer modelo
    """
    base_options = get_universal_config(model_name, performance_mode)
    model_type = detect_model_type(model_name)
    
    # Ajustes específicos por tipo de tarefa e modelo
    task_adjustments = {
        'fast': {
            'conversion': {'temperature': 0.2, 'top_p': 0.6, 'top_k': 20},
            'analysis': {'temperature': 0.3, 'top_p': 0.7, 'top_k': 25},
            'documentation': {'temperature': 0.35, 'top_p': 0.75, 'top_k': 30},
            'mermaid_diagram': {'temperature': 0.1, 'top_p': 0.6, 'top_k': 20},
            'testing': {'temperature': 0.25, 'top_p': 0.65, 'top_k': 25}
        },
        'balanced': {
            'conversion': {'temperature': 0.15, 'top_p': 0.8, 'top_k': 35},
            'analysis': {'temperature': 0.2, 'top_p': 0.85, 'top_k': 40},
            'documentation': {'temperature': 0.25, 'top_p': 0.9, 'top_k': 45},
            'mermaid_diagram': {'temperature': 0.1, 'top_p': 0.8, 'top_k': 35},
            'testing': {'temperature': 0.15, 'top_p': 0.8, 'top_k': 35}
        },
        'quality': {
            'conversion': {'temperature': 0.05, 'top_p': 0.8, 'top_k': 50},
            'analysis': {'temperature': 0.1, 'top_p': 0.9, 'top_k': 50},
            'documentation': {'temperature': 0.15, 'top_p': 0.95, 'top_k': 50},
            'mermaid_diagram': {'temperature': 0.05, 'top_p': 0.85, 'top_k': 45},
            'testing': {'temperature': 0.1, 'top_p': 0.85, 'top_k': 45}
        }
    }
    
    # Aplica ajustes específicos
    if performance_mode in task_adjustments and task_type in task_adjustments[performance_mode]:
        base_options.update(task_adjustments[performance_mode][task_type])
    
    # Ajustes específicos do modelo
    if model_type == 'codellama':
        # CodeLlama funciona melhor com temperatura mais baixa para código
        if task_type == 'conversion':
            base_options['temperature'] = max(0.05, base_options['temperature'] - 0.05)
    elif model_type == 'mistral':
        # Mistral pode ser mais eficiente com top_k menor
        base_options['top_k'] = max(15, base_options['top_k'] - 5)
    
    return base_options

def get_performance_info_universal() -> dict:
    """Retorna informações sobre os modos de performance"""
    return {
        'performance_modes': {
            'fast': {
                'description': '🚀 VELOCIDADE MÁXIMA',
                'speed': '⚡ Muito Rápido',
                'memory': '💾 Baixo uso',
                'savings': 'CPU: ~60% menos | Memória: ~70% menos'
            },
            'balanced': {
                'description': '⚖️ EQUILIBRADO',
                'speed': '🏃 Rápido',
                'memory': '💾 Moderado', 
                'savings': 'CPU: ~30% menos | Memória: ~40% menos'
            },
            'quality': {
                'description': '🎯 QUALIDADE MÁXIMA',
                'speed': '🐢 Mais lento',
                'memory': '💾 Alto uso',
                'savings': 'Configurações completas'
            }
        }
    }

# Funções de compatibilidade com o sistema existente
def is_deepseek_r1_model(model_name: str) -> bool:
    """Compatibilidade com sistema existente"""
    return detect_model_type(model_name) == 'deepseek-r1'

def get_deepseek_r1_config(model_name: str, performance_mode: str = 'fast') -> dict:
    """Compatibilidade com sistema existente"""
    return get_universal_config(model_name, performance_mode)

def combine_prompts_with_deepseek(base_prompt: str, task_type: str = 'conversion', performance_mode: str = 'fast') -> str:
    """Compatibilidade com sistema existente"""
    return combine_prompts_universal(base_prompt, task_type, 'deepseek-r1:14b', performance_mode)

def get_deepseek_enhanced_options(model_name: str, task_type: str, performance_mode: str = 'fast') -> dict:
    """Compatibilidade com sistema existente"""
    return get_enhanced_options_universal(model_name, task_type, performance_mode)

def get_performance_info() -> dict:
    """Compatibilidade com sistema existente"""
    return get_performance_info_universal()['performance_modes']

def get_development_config(model_name: str = 'codellama:7b') -> dict:
    """
    Configuração ESPECÍFICA para desenvolvimento no VS Code
    OBJETIVO: Evitar travamentos e fornecer feedback rápido
    """
    
    return {
        # Configurações ultra-leves
        'ollama_model': model_name,
        'performance_mode': 'development',
        
        # Configurações LLM mínimas
        'temperature': 0.1,
        'top_p': 0.3,
        'top_k': 5,
        'num_predict': 150,
        'num_ctx': 512,
        'num_thread': 2,
        'num_gpu_layers': 0,
        
        # Timeouts agressivos
        'request_timeout': 10,
        'connect_timeout': 3,
        'read_timeout': 7,
        
        # Flags específicas
        'development_mode': True,
        'use_cache': True,
        'use_fallback': True,
        'debug_mode': False,
        'quick_response': True,
        
        # Para evitar travamentos
        'stream': False,
        'retry_count': 1,
        'low_vram': True
    }
