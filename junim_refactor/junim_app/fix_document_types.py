"""
Script para adicionar o tipo de documento de modernização detalhada ao DocumentationGenerator
"""

import sys
from pathlib import Path

# Lê o arquivo atual
doc_gen_file = Path("core/documentation_generator.py")

try:
    with open(doc_gen_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procura pela seção onde precisamos adicionar o novo tipo
    modernization_strategy_line = "'modernization_strategy': {"
    
    if modernization_strategy_line in content:
        # Encontra o final da definição de modernization_strategy
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            if "'modernization_strategy': {" in line:
                # Procura pelo fechamento desta seção
                j = i + 1
                brace_count = 1
                while j < len(lines) and brace_count > 0:
                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')
                    j += 1
                
                # Agora j aponta para a linha após o fechamento de modernization_strategy
                # Vamos inserir o novo documento antes da linha que contém apenas '}'
                insert_position = j - 1
                
                # Verifica se o novo documento já existe
                if 'detailed_modernization' not in content:
                    new_doc_lines = [
                        "            },",
                        "            'detailed_modernization': {",
                        "                'name': '🔧 Plano Detalhado de Modernização',",
                        "                'prompt_type': 'detailed_modernization',",
                        "                'filename': 'detailed_modernization_plan.md',",
                        "                'priority': 5,",
                        "                'use_modernization_engine': True",
                    ]
                    
                    # Remove o } da linha anterior e adiciona as novas linhas
                    if lines[insert_position-1].strip() == '}':
                        lines[insert_position-1] = lines[insert_position-1].replace('}', '')
                    
                    # Insere as novas linhas
                    for idx, new_line in enumerate(new_doc_lines):
                        lines.insert(insert_position + idx, new_line)
                    
                    # Adiciona o } de fechamento de volta
                    lines.insert(insert_position + len(new_doc_lines), "            }")
                    
                    # Escreve o arquivo modificado
                    new_content = '\n'.join(lines)
                    
                    with open(doc_gen_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print("✅ Tipo de documento 'detailed_modernization' adicionado com sucesso!")
                    break
                else:
                    print("ℹ️ Tipo de documento 'detailed_modernization' já existe.")
                    break
        else:
            print("❌ Não foi possível encontrar a seção modernization_strategy no arquivo.")
    else:
        print("❌ Seção modernization_strategy não encontrada no arquivo.")

except Exception as e:
    print(f"❌ Erro ao modificar o arquivo: {str(e)}")
