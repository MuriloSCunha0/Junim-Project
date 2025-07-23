"""
Analisador de Projetos Java Spring Boot - Extrai estrutura e funcionalidades
Similar ao LegacyProjectAnalyzer, mas focado em projetos Java modernizados
"""

import logging
import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import zipfile
import tempfile

logger = logging.getLogger(__name__)

class JavaProjectAnalyzer:
    """
    Analisa projetos Java Spring Boot para extrair estrutura, funcionalidades
    e gerar documentação que pode ser comparada com o projeto Delphi original
    """
    
    def __init__(self):
        self.java_patterns = {
            'class_declaration': re.compile(r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?'),
            'interface_declaration': re.compile(r'(?:public|private|protected)?\s*interface\s+(\w+)(?:\s+extends\s+([^{]+))?'),
            'method_declaration': re.compile(r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:abstract)?\s*([^(]+?)\s+(\w+)\s*\(([^)]*)\)'),
            'annotation': re.compile(r'@(\w+)(?:\([^)]*\))?'),
            'field_declaration': re.compile(r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*([^;=]+?)\s+(\w+)'),
            'spring_mapping': re.compile(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\s*(?:\([^)]*\))?'),
            'jpa_annotation': re.compile(r'@(Entity|Table|Column|Id|GeneratedValue|ManyToOne|OneToMany|ManyToMany|OneToOne)')
        }
        
    def analyze_java_project(self, project_path: str) -> Dict[str, Any]:
        """
        Analisa projeto Java e extrai estrutura completa
        
        Args:
            project_path: Caminho para o projeto Java (pasta ou ZIP)
            
        Returns:
            Estrutura detalhada do projeto Java
        """
        logger.info(f"🔍 Iniciando análise do projeto Java: {project_path}")
        
        try:
            # Determina se é arquivo ZIP ou pasta
            if os.path.isfile(project_path) and project_path.endswith('.zip'):
                extracted_files = self._extract_and_collect_java_files(project_path)
            elif os.path.isdir(project_path):
                extracted_files = self._collect_java_files_from_directory(project_path)
            else:
                raise ValueError(f"Caminho inválido: {project_path}")
            
            if not extracted_files:
                raise ValueError("Nenhum arquivo Java encontrado no projeto")
            
            # Analisa cada arquivo Java
            analysis_results = {
                'metadata': self._generate_metadata(project_path, extracted_files),
                'project_structure': self._analyze_project_structure(extracted_files),
                'code_structure': self._analyze_code_structure(extracted_files),
                'spring_components': self._analyze_spring_components(extracted_files),
                'api_endpoints': self._extract_api_endpoints(extracted_files),
                'database_entities': self._analyze_jpa_entities(extracted_files),
                'dependencies': self._analyze_dependencies(extracted_files),
                'files_analyzed': {
                    'total_files': len(extracted_files),
                    'java_files': len([f for f in extracted_files if f['path'].endswith('.java')]),
                    'config_files': len([f for f in extracted_files if f['path'].endswith(('.properties', '.yml', '.yaml'))]),
                    'build_files': len([f for f in extracted_files if f['path'].endswith(('.pom.xml', 'build.gradle'))])
                },
                'architecture_analysis': self._analyze_architecture_patterns(extracted_files)
            }
            
            logger.info(f"✅ Análise Java concluída: {len(extracted_files)} arquivos processados")
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Erro na análise do projeto Java: {str(e)}")
            raise Exception(f"Falha na análise do projeto Java: {str(e)}")
    
    def _extract_and_collect_java_files(self, zip_path: str) -> List[Dict[str, Any]]:
        """Extrai ZIP e coleta todos os arquivos Java"""
        extracted_files = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Busca recursivamente por arquivos Java
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.java', '.properties', '.yml', '.yaml', '.xml', '.gradle')):
                            file_path = os.path.join(root, file)
                            relative_path = os.path.relpath(file_path, temp_dir)
                            
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                extracted_files.append({
                                    'path': relative_path,
                                    'filename': file,
                                    'content': content,
                                    'size': len(content),
                                    'type': self._determine_file_type(file)
                                })
                            except Exception as e:
                                logger.warning(f"Erro ao ler arquivo {file}: {str(e)}")
                
            except zipfile.BadZipFile:
                raise ValueError(f"Arquivo ZIP inválido: {zip_path}")
        
        return extracted_files
    
    def _collect_java_files_from_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Coleta arquivos Java de um diretório"""
        extracted_files = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(('.java', '.properties', '.yml', '.yaml', '.xml', '.gradle')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        extracted_files.append({
                            'path': relative_path,
                            'filename': file,
                            'content': content,
                            'size': len(content),
                            'type': self._determine_file_type(file)
                        })
                    except Exception as e:
                        logger.warning(f"Erro ao ler arquivo {file}: {str(e)}")
        
        return extracted_files
    
    def _determine_file_type(self, filename: str) -> str:
        """Determina o tipo do arquivo baseado na extensão"""
        if filename.endswith('.java'):
            return 'java_source'
        elif filename.endswith(('.properties', '.yml', '.yaml')):
            return 'configuration'
        elif filename.endswith('.xml'):
            return 'build_config' if filename in ['pom.xml'] else 'configuration'
        elif filename.endswith('.gradle'):
            return 'build_config'
        else:
            return 'other'
    
    def _generate_metadata(self, project_path: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera metadados do projeto"""
        project_name = os.path.basename(project_path).replace('.zip', '')
        
        # Tenta extrair nome do projeto dos arquivos de build
        for file in files:
            if file['filename'] == 'pom.xml':
                # Extrai nome do Maven POM
                artifactId_match = re.search(r'<artifactId>([^<]+)</artifactId>', file['content'])
                if artifactId_match:
                    project_name = artifactId_match.group(1)
                    break
            elif file['filename'] == 'build.gradle':
                # Extrai nome do Gradle
                name_match = re.search(r'rootProject\.name\s*=\s*[\'"]([^\'"]+)[\'"]', file['content'])
                if name_match:
                    project_name = name_match.group(1)
                    break
        
        return {
            'project_name': project_name,
            'analysis_date': datetime.now().isoformat(),
            'analyzer_version': '1.0.0',
            'project_type': 'Java Spring Boot',
            'source_path': project_path,
            'total_files': len(files),
            'total_size_chars': sum(f['size'] for f in files)
        }
    
    def _analyze_project_structure(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa a estrutura de pacotes do projeto"""
        packages = set()
        source_files = []
        
        for file in files:
            if file['type'] == 'java_source':
                # Extrai pacote do arquivo Java
                package_match = re.search(r'package\s+([\w.]+);', file['content'])
                if package_match:
                    packages.add(package_match.group(1))
                
                source_files.append({
                    'file': file['path'],
                    'package': package_match.group(1) if package_match else 'default',
                    'size': file['size']
                })
        
        return {
            'packages': sorted(list(packages)),
            'package_count': len(packages),
            'source_files': source_files,
            'main_package': self._determine_main_package(packages)
        }
    
    def _determine_main_package(self, packages: List[str]) -> str:
        """Determina o pacote principal do projeto"""
        if not packages:
            return 'default'
        
        # Encontra o pacote mais comum como base
        package_bases = {}
        for pkg in packages:
            parts = pkg.split('.')
            if len(parts) >= 2:
                base = '.'.join(parts[:2])
                package_bases[base] = package_bases.get(base, 0) + 1
        
        if package_bases:
            return max(package_bases.items(), key=lambda x: x[1])[0]
        
        return packages[0]
    
    def _analyze_code_structure(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa estrutura de código (classes, métodos, etc.)"""
        classes = []
        interfaces = []
        methods = []
        
        for file in files:
            if file['type'] == 'java_source':
                content = file['content']
                
                # Extrai classes
                class_matches = self.java_patterns['class_declaration'].finditer(content)
                for match in class_matches:
                    class_info = {
                        'name': match.group(1),
                        'file': file['path'],
                        'parent_class': match.group(2) if match.group(2) else None,
                        'implements': [i.strip() for i in match.group(3).split(',')] if match.group(3) else [],
                        'annotations': self._extract_annotations_before_declaration(content, match.start()),
                        'methods': self._extract_methods_from_class(content, match.start()),
                        'fields': self._extract_fields_from_class(content, match.start())
                    }
                    classes.append(class_info)
                
                # Extrai interfaces
                interface_matches = self.java_patterns['interface_declaration'].finditer(content)
                for match in interface_matches:
                    interface_info = {
                        'name': match.group(1),
                        'file': file['path'],
                        'extends': [i.strip() for i in match.group(2).split(',')] if match.group(2) else [],
                        'annotations': self._extract_annotations_before_declaration(content, match.start()),
                        'methods': self._extract_interface_methods(content, match.start())
                    }
                    interfaces.append(interface_info)
        
        return {
            'classes': classes,
            'interfaces': interfaces,
            'total_classes': len(classes),
            'total_interfaces': len(interfaces),
            'total_methods': sum(len(cls['methods']) for cls in classes),
            'class_distribution': self._analyze_class_distribution(classes)
        }
    
    def _extract_annotations_before_declaration(self, content: str, position: int) -> List[str]:
        """Extrai anotações antes de uma declaração"""
        lines_before = content[:position].split('\n')[-10:]  # Últimas 10 linhas antes
        annotations = []
        
        for line in reversed(lines_before):
            line = line.strip()
            if line.startswith('@'):
                annotation_match = self.java_patterns['annotation'].search(line)
                if annotation_match:
                    annotations.append(annotation_match.group(1))
            elif line and not line.startswith('//') and not line.startswith('/*'):
                break
        
        return list(reversed(annotations))
    
    def _extract_methods_from_class(self, content: str, class_start: int) -> List[Dict[str, Any]]:
        """Extrai métodos de uma classe"""
        methods = []
        
        # Encontra o conteúdo da classe (entre chaves)
        class_content = self._extract_class_body(content, class_start)
        if not class_content:
            return methods
        
        method_matches = self.java_patterns['method_declaration'].finditer(class_content)
        for match in method_matches:
            method_info = {
                'name': match.group(2),
                'return_type': match.group(1).strip(),
                'parameters': self._parse_parameters(match.group(3)),
                'annotations': self._extract_annotations_before_declaration(class_content, match.start())
            }
            methods.append(method_info)
        
        return methods
    
    def _extract_fields_from_class(self, content: str, class_start: int) -> List[Dict[str, Any]]:
        """Extrai campos/atributos de uma classe"""
        fields = []
        
        class_content = self._extract_class_body(content, class_start)
        if not class_content:
            return fields
        
        field_matches = self.java_patterns['field_declaration'].finditer(class_content)
        for match in field_matches:
            # Ignora métodos (que também podem ser capturados pelo regex)
            if '(' not in match.group(1):
                field_info = {
                    'name': match.group(2),
                    'type': match.group(1).strip(),
                    'annotations': self._extract_annotations_before_declaration(class_content, match.start())
                }
                fields.append(field_info)
        
        return fields
    
    def _extract_class_body(self, content: str, class_start: int) -> str:
        """Extrai o corpo de uma classe (conteúdo entre chaves)"""
        class_line_start = content.rfind('\n', 0, class_start)
        class_declaration_end = content.find('{', class_start)
        
        if class_declaration_end == -1:
            return ""
        
        # Encontra a chave de fechamento correspondente
        brace_count = 1
        pos = class_declaration_end + 1
        
        while pos < len(content) and brace_count > 0:
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
            pos += 1
        
        if brace_count == 0:
            return content[class_declaration_end + 1:pos - 1]
        
        return ""
    
    def _extract_interface_methods(self, content: str, interface_start: int) -> List[Dict[str, Any]]:
        """Extrai métodos de uma interface"""
        return self._extract_methods_from_class(content, interface_start)
    
    def _parse_parameters(self, params_str: str) -> List[Dict[str, str]]:
        """Analisa string de parâmetros de método"""
        if not params_str.strip():
            return []
        
        parameters = []
        param_parts = params_str.split(',')
        
        for param in param_parts:
            param = param.strip()
            if param:
                # Formato: @Annotation Type name ou Type name
                parts = param.split()
                if len(parts) >= 2:
                    param_type = parts[-2]
                    param_name = parts[-1]
                    parameters.append({
                        'name': param_name,
                        'type': param_type
                    })
        
        return parameters
    
    def _analyze_class_distribution(self, classes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa distribuição de tipos de classes"""
        distribution = {
            'controllers': 0,
            'services': 0,
            'entities': 0,
            'repositories': 0,
            'configurations': 0,
            'utilities': 0,
            'others': 0
        }
        
        for cls in classes:
            annotations = cls['annotations']
            class_name = cls['name'].lower()
            
            if 'Controller' in annotations or 'RestController' in annotations:
                distribution['controllers'] += 1
            elif 'Service' in annotations or 'service' in class_name:
                distribution['services'] += 1
            elif 'Entity' in annotations or 'entity' in class_name:
                distribution['entities'] += 1
            elif 'Repository' in annotations or 'repository' in class_name:
                distribution['repositories'] += 1
            elif 'Configuration' in annotations or 'config' in class_name:
                distribution['configurations'] += 1
            elif any(util in class_name for util in ['util', 'helper', 'tool']):
                distribution['utilities'] += 1
            else:
                distribution['others'] += 1
        
        return distribution
    
    def _analyze_spring_components(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa componentes específicos do Spring"""
        controllers = []
        services = []
        repositories = []
        entities = []
        
        for file in files:
            if file['type'] == 'java_source':
                content = file['content']
                
                # Busca por controllers
                if re.search(r'@(RestController|Controller)', content):
                    controller_info = self._extract_controller_info(content, file['path'])
                    if controller_info:
                        controllers.append(controller_info)
                
                # Busca por services
                if re.search(r'@Service', content):
                    service_info = self._extract_service_info(content, file['path'])
                    if service_info:
                        services.append(service_info)
                
                # Busca por repositories
                if re.search(r'@Repository', content):
                    repository_info = self._extract_repository_info(content, file['path'])
                    if repository_info:
                        repositories.append(repository_info)
                
                # Busca por entities
                if re.search(r'@Entity', content):
                    entity_info = self._extract_entity_info(content, file['path'])
                    if entity_info:
                        entities.append(entity_info)
        
        return {
            'controllers': controllers,
            'services': services,
            'repositories': repositories,
            'entities': entities,
            'component_summary': {
                'total_controllers': len(controllers),
                'total_services': len(services),
                'total_repositories': len(repositories),
                'total_entities': len(entities)
            }
        }
    
    def _extract_controller_info(self, content: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Extrai informações específicas de um controller"""
        class_match = self.java_patterns['class_declaration'].search(content)
        if not class_match:
            return None
        
        return {
            'name': class_match.group(1),
            'file': file_path,
            'endpoints': self._extract_endpoints_from_controller(content),
            'base_mapping': self._extract_request_mapping(content)
        }
    
    def _extract_service_info(self, content: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Extrai informações específicas de um service"""
        class_match = self.java_patterns['class_declaration'].search(content)
        if not class_match:
            return None
        
        return {
            'name': class_match.group(1),
            'file': file_path,
            'public_methods': self._extract_public_methods(content),
            'dependencies': self._extract_injected_dependencies(content)
        }
    
    def _extract_repository_info(self, content: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Extrai informações específicas de um repository"""
        class_match = self.java_patterns['class_declaration'].search(content)
        if not class_match:
            return None
        
        return {
            'name': class_match.group(1),
            'file': file_path,
            'entity_type': self._extract_repository_entity_type(content),
            'custom_queries': self._extract_custom_queries(content)
        }
    
    def _extract_entity_info(self, content: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Extrai informações específicas de uma entity"""
        class_match = self.java_patterns['class_declaration'].search(content)
        if not class_match:
            return None
        
        return {
            'name': class_match.group(1),
            'file': file_path,
            'table_name': self._extract_table_name(content),
            'fields': self._extract_entity_fields(content),
            'relationships': self._extract_entity_relationships(content)
        }
    
    def _extract_endpoints_from_controller(self, content: str) -> List[Dict[str, Any]]:
        """Extrai endpoints de um controller"""
        endpoints = []
        
        mapping_matches = self.java_patterns['spring_mapping'].finditer(content)
        for match in mapping_matches:
            # Encontra o método associado ao endpoint
            method_start = content.rfind('public', 0, match.start())
            if method_start != -1:
                method_line = content[method_start:content.find('\n', match.end())]
                method_name_match = re.search(r'(\w+)\s*\(', method_line)
                
                if method_name_match:
                    endpoints.append({
                        'http_method': match.group(1).replace('Mapping', '').upper(),
                        'method_name': method_name_match.group(1),
                        'annotation': match.group(0)
                    })
        
        return endpoints
    
    def _extract_request_mapping(self, content: str) -> Optional[str]:
        """Extrai base path do @RequestMapping da classe"""
        request_mapping_match = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']', content)
        if request_mapping_match:
            return request_mapping_match.group(1)
        return None
    
    def _extract_public_methods(self, content: str) -> List[str]:
        """Extrai métodos públicos de uma classe"""
        public_methods = []
        
        method_matches = re.finditer(r'public\s+[^(]+\s+(\w+)\s*\(', content)
        for match in method_matches:
            public_methods.append(match.group(1))
        
        return public_methods
    
    def _extract_injected_dependencies(self, content: str) -> List[str]:
        """Extrai dependências injetadas via @Autowired ou construtor"""
        dependencies = []
        
        # Busca por @Autowired
        autowired_matches = re.finditer(r'@Autowired[^;]+\s+(\w+)\s+(\w+);', content)
        for match in autowired_matches:
            dependencies.append(match.group(1))
        
        return dependencies
    
    def _extract_repository_entity_type(self, content: str) -> Optional[str]:
        """Extrai tipo de entidade de um repository"""
        # Busca por extends JpaRepository<Entity, ID>
        extends_match = re.search(r'extends\s+\w*Repository<(\w+),', content)
        if extends_match:
            return extends_match.group(1)
        return None
    
    def _extract_custom_queries(self, content: str) -> List[str]:
        """Extrai queries customizadas de um repository"""
        queries = []
        
        query_matches = re.finditer(r'@Query\s*\(\s*["\']([^"\']+)["\']', content)
        for match in query_matches:
            queries.append(match.group(1))
        
        return queries
    
    def _extract_table_name(self, content: str) -> Optional[str]:
        """Extrai nome da tabela de uma entity"""
        table_match = re.search(r'@Table\s*\(\s*name\s*=\s*["\']([^"\']+)["\']', content)
        if table_match:
            return table_match.group(1)
        return None
    
    def _extract_entity_fields(self, content: str) -> List[Dict[str, Any]]:
        """Extrai campos de uma entity JPA"""
        fields = []
        
        # Busca por campos com anotações JPA
        field_matches = re.finditer(r'@(Column|Id|GeneratedValue)[^;]+\s+(\w+)\s+(\w+);', content)
        for match in field_matches:
            fields.append({
                'name': match.group(3),
                'type': match.group(2),
                'annotation': match.group(1)
            })
        
        return fields
    
    def _extract_entity_relationships(self, content: str) -> List[Dict[str, Any]]:
        """Extrai relacionamentos JPA de uma entity"""
        relationships = []
        
        relationship_matches = re.finditer(r'@(OneToMany|ManyToOne|ManyToMany|OneToOne)[^;]+\s+(\w+)\s+(\w+);', content)
        for match in relationship_matches:
            relationships.append({
                'type': match.group(1),
                'target_entity': match.group(2),
                'field_name': match.group(3)
            })
        
        return relationships
    
    def _extract_api_endpoints(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrai todos os endpoints da API"""
        all_endpoints = []
        
        for file in files:
            if file['type'] == 'java_source':
                content = file['content']
                
                # Verifica se é um controller
                if re.search(r'@(RestController|Controller)', content):
                    base_mapping = self._extract_request_mapping(content)
                    endpoints = self._extract_endpoints_from_controller(content)
                    
                    for endpoint in endpoints:
                        endpoint['controller_file'] = file['path']
                        endpoint['base_path'] = base_mapping
                        all_endpoints.append(endpoint)
        
        return all_endpoints
    
    def _analyze_jpa_entities(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa entidades JPA do projeto"""
        entities = []
        
        for file in files:
            if file['type'] == 'java_source':
                content = file['content']
                
                if re.search(r'@Entity', content):
                    entity_info = self._extract_entity_info(content, file['path'])
                    if entity_info:
                        entities.append(entity_info)
        
        return {
            'entities': entities,
            'total_entities': len(entities),
            'tables': [e['table_name'] for e in entities if e['table_name']],
            'entity_relationships': self._map_entity_relationships(entities)
        }
    
    def _map_entity_relationships(self, entities: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Mapeia relacionamentos entre entidades"""
        relationships = {}
        
        for entity in entities:
            entity_name = entity['name']
            related_entities = []
            
            for rel in entity['relationships']:
                related_entities.append(rel['target_entity'])
            
            if related_entities:
                relationships[entity_name] = related_entities
        
        return relationships
    
    def _analyze_dependencies(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa dependências do projeto"""
        dependencies = {
            'maven_dependencies': [],
            'gradle_dependencies': [],
            'spring_boot_starters': [],
            'external_libraries': []
        }
        
        for file in files:
            if file['filename'] == 'pom.xml':
                dependencies['maven_dependencies'] = self._extract_maven_dependencies(file['content'])
                dependencies['spring_boot_starters'] = self._extract_spring_boot_starters(file['content'])
            elif file['filename'] == 'build.gradle':
                dependencies['gradle_dependencies'] = self._extract_gradle_dependencies(file['content'])
        
        return dependencies
    
    def _extract_maven_dependencies(self, pom_content: str) -> List[Dict[str, str]]:
        """Extrai dependências do Maven POM"""
        dependencies = []
        
        dependency_matches = re.finditer(
            r'<dependency>.*?<groupId>([^<]+)</groupId>.*?<artifactId>([^<]+)</artifactId>.*?(?:<version>([^<]+)</version>)?.*?</dependency>',
            pom_content, re.DOTALL
        )
        
        for match in dependency_matches:
            dependencies.append({
                'groupId': match.group(1),
                'artifactId': match.group(2),
                'version': match.group(3) if match.group(3) else 'managed'
            })
        
        return dependencies
    
    def _extract_spring_boot_starters(self, pom_content: str) -> List[str]:
        """Extrai Spring Boot starters do POM"""
        starters = []
        
        starter_matches = re.finditer(r'<artifactId>(spring-boot-starter[^<]+)</artifactId>', pom_content)
        for match in starter_matches:
            starters.append(match.group(1))
        
        return starters
    
    def _extract_gradle_dependencies(self, gradle_content: str) -> List[str]:
        """Extrai dependências do Gradle"""
        dependencies = []
        
        dependency_matches = re.finditer(r'implementation\s+["\']([^"\']+)["\']', gradle_content)
        for match in dependency_matches:
            dependencies.append(match.group(1))
        
        return dependencies
    
    def _analyze_architecture_patterns(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa padrões arquiteturais utilizados"""
        patterns = {
            'mvc_pattern': False,
            'repository_pattern': False,
            'service_layer': False,
            'dependency_injection': False,
            'rest_api': False,
            'jpa_orm': False,
            'configuration_classes': []
        }
        
        for file in files:
            if file['type'] == 'java_source':
                content = file['content']
                
                # Verifica padrões
                if re.search(r'@(RestController|Controller)', content):
                    patterns['mvc_pattern'] = True
                    patterns['rest_api'] = True
                
                if re.search(r'@Repository', content):
                    patterns['repository_pattern'] = True
                
                if re.search(r'@Service', content):
                    patterns['service_layer'] = True
                
                if re.search(r'@(Autowired|Inject)', content):
                    patterns['dependency_injection'] = True
                
                if re.search(r'@Entity', content):
                    patterns['jpa_orm'] = True
                
                if re.search(r'@Configuration', content):
                    class_match = self.java_patterns['class_declaration'].search(content)
                    if class_match:
                        patterns['configuration_classes'].append(class_match.group(1))
        
        return patterns
