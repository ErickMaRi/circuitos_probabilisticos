import ast
import os
import subprocess
import logging
from typing import Dict, List, Set, Tuple
import networkx as nx
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_and_install_tool(command, install_command=None):
    try:
        subprocess.run(command, capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        if install_command:
            logging.info(f"Installing {command[0]}...")
            subprocess.run(install_command, check=True)
        else:
            logging.warning(f"{command[0]} not found and no install command provided.")

def install_missing_tools():
    check_and_install_tool(['plantuml', '-version'], ['sudo', 'apt-get', 'install', '-y', 'plantuml'])
    check_and_install_tool(['coverage', '--version'], ['pip', 'install', 'coverage'])
    check_and_install_tool(['radon', '--version'], ['pip', 'install', 'radon'])
    check_and_install_tool(['black', '--version'], ['pip', 'install', 'black'])
    check_and_install_tool(['python3', '-c', 'import seaborn'], ['pip', 'install', 'seaborn'])

install_missing_tools()

import seaborn as sns  # Import after ensuring installation

class DependencyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.dependencies = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.dependencies.add(alias.name.split('.')[0])

    def visit_ImportFrom(self, node):
        if node.module:
            self.dependencies.add(node.module.split('.')[0])

def extract_dependencies(tree: ast.AST) -> Set[str]:
    visitor = DependencyVisitor()
    visitor.visit(tree)
    return visitor.dependencies

def analyze_file(filename: str) -> Tuple[Dict[str, List[str]], List[str], Set[str]]:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read())
        classes = {node.name: [n.name for n in node.body if isinstance(n, ast.FunctionDef)] 
                   for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree))]
        dependencies = extract_dependencies(tree)
        return classes, functions, dependencies
    except Exception as e:
        logging.error(f"Error analyzing file {filename}: {str(e)}")
        return {}, [], set()

def generate_dependency_graph(directory: str) -> nx.DiGraph:
    G = nx.DiGraph()
    all_dependencies: Dict[str, Set[str]] = {}

    for filename in os.listdir(directory):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            filepath = os.path.join(directory, filename)
            logging.info(f'Analyzing: {filename}')
            _, _, dependencies = analyze_file(filepath)
            all_dependencies[filename] = dependencies

            G.add_node(filename, size=3000, color='lightblue', style='filled')

    for filename, dependencies in all_dependencies.items():
        for dep in dependencies:
            if dep + '.py' in all_dependencies:
                G.add_edge(filename, dep + '.py')
            else:
                G.add_node(dep, size=1000, color='lightgreen', style='filled', shape='box')
                G.add_edge(filename, dep)

    return G

def visualize_dependency_graph(G: nx.DiGraph, output_file: str):
    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G, k=0.9, iterations=50)
    
    sns.set_style("whitegrid")
    
    sizes = [G.nodes[node]['size'] for node in G.nodes]
    colors = [G.nodes[node]['color'] for node in G.nodes]
    
    nx.draw(G, pos, with_labels=True, node_size=sizes, node_color=colors, 
            font_size=10, font_weight='bold', edge_color='gray')
    
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    plt.title("Project Dependency Graph", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, format="png", dpi=300, bbox_inches='tight')
    plt.close()
    logging.info(f"Dependency graph saved as '{output_file}'")

def generate_plantuml(filename: str, classes: Dict[str, List[str]], functions: List[str]) -> str:
    plantuml = "@startuml\n"
    plantuml += f"package {filename} {{\n"
    
    if classes:
        for cls, methods in classes.items():
            plantuml += f"  class {cls} {{\n"
            for method in methods:
                plantuml += f"    {method}()\n"
            plantuml += "  }\n"
    
    if functions:
        for func in functions:
            plantuml += f"  object {func}()\n"
    
    plantuml += "}\n"
    plantuml += "@enduml"
    
    return plantuml

def save_plantuml(plantuml: str, output_file: str):
    try:
        result = subprocess.run(['plantuml', '-pipe'], input=plantuml.encode(), capture_output=True)
        with open(output_file, 'wb') as f:
            f.write(result.stdout)
        logging.info(f"PlantUML diagram saved as '{output_file}'")
    except Exception as e:
        logging.error(f"Error generating PlantUML diagram: {str(e)}")

def analyze_code_quality(filename: str) -> Dict[str, int]:
    try:
        result = subprocess.run(['pylint', filename, '--output-format=json'], capture_output=True, text=True)
        import json
        data = json.loads(result.stdout)
        return {
            'convention': sum(1 for msg in data if msg['type'] == 'convention'),
            'refactor': sum(1 for msg in data if msg['type'] == 'refactor'),
            'warning': sum(1 for msg in data if msg['type'] == 'warning'),
            'error': sum(1 for msg in data if msg['type'] == 'error')
        }
    except Exception as e:
        logging.error(f"Error analyzing code quality of {filename}: {str(e)}")
        return {}

def find_todos(filename: str) -> List[str]:
    todos = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for i, line in enumerate(file, 1):
                if 'TODO' in line:
                    todos.append(f"Line {i}: {line.strip()}")
                elif 'FIXME' in line:
                    todos.append(f"Line {i}: {line.strip()}")
    except Exception as e:
        logging.error(f"Error finding TODOs in {filename}: {str(e)}")
    return todos

def analyze_test_coverage(directory: str) -> Dict[str, float]:
    try:
        result = subprocess.run(['coverage', 'run', '-m', 'pytest', directory], capture_output=True, text=True)
        coverage_result = subprocess.run(['coverage', 'report', '-m'], capture_output=True, text=True)
        
        coverage_data = {}
        for line in coverage_result.stdout.splitlines()[2:-2]:  # Skip header and footer
            parts = line.split()
            if len(parts) >= 5:
                filename = parts[0]
                coverage = float(parts[-1].rstrip('%'))
                coverage_data[filename] = coverage
        
        return coverage_data
    except Exception as e:
        logging.error(f"Error analyzing test coverage: {str(e)}")
        return {}

def analyze_complexity(filename: str) -> Dict[str, int]:
    try:
        result = subprocess.run(['radon', 'cc', filename, '-s', '-j'], capture_output=True, text=True)
        import json
        data = json.loads(result.stdout)
        return data
    except Exception as e:
        logging.error(f"Error analyzing complexity of {filename}: {str(e)}")
        return {}

def count_lines_of_code(filename: str) -> int:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return sum(1 for _ in file)
    except Exception as e:
        logging.error(f"Error counting lines of code in {filename}: {str(e)}")
        return 0

def check_formatting(filename: str) -> bool:
    try:
        result = subprocess.run(['black', '--check', filename], capture_output=True, text=True)
        return "would reformat" not in result.stdout
    except Exception as e:
        logging.error(f"Error checking formatting of {filename}: {str(e)}")
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    graphs_dir = os.path.join(script_dir, 'graphs')
    os.makedirs(graphs_dir, exist_ok=True)
    
    logging.info(f"Analyzing project structure in {script_dir}")
    G = generate_dependency_graph(script_dir)

    logging.info("Generating dependency graph visualization...")
    visualize_dependency_graph(G, os.path.join(graphs_dir, 'dependency_graph.png'))

    logging.info("Generating PlantUML diagrams...")
    for filename in os.listdir(script_dir):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            filepath = os.path.join(script_dir, filename)
            classes, functions, _ = analyze_file(filepath)
            plantuml = generate_plantuml(filename, classes, functions)
            plantuml_output_file = os.path.join(graphs_dir, f'{filename[:-3]}_structure.png')
            try:
                save_plantuml(plantuml, plantuml_output_file)
            except FileNotFoundError:
                logging.error(f"PlantUML not found. Please install PlantUML to generate diagrams.")

    logging.info("Analyzing code quality...")
    for filename in os.listdir(script_dir):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            filepath = os.path.join(script_dir, filename)
            quality_metrics = analyze_code_quality(filepath)
            logging.info(f"{filename} code quality metrics: {quality_metrics}")

    logging.info("Finding TODOs and FIXMEs...")
    for filename in os.listdir(script_dir):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            filepath = os.path.join(script_dir, filename)
            todos = find_todos(filepath)
            if todos:
                logging.info(f"TODOs in {filename}:")
                for todo in todos:
                    logging.info(todo)

    logging.info("Analyzing test coverage...")
    coverage_data = analyze_test_coverage(script_dir)
    for filename, coverage in coverage_data.items():
        logging.info(f"{filename}: {coverage}% test coverage")

    logging.info("Analyzing code complexity...")
    for filename in os.listdir(script_dir):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            complexity = analyze_complexity(filename)
            logging.info(f"{filename} code complexity metrics: {complexity}")

    logging.info("Counting lines of code...")
    for filename in os.listdir(script_dir):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            loc = count_lines_of_code(filename)
            logging.info(f"{filename} lines of code: {loc}")

    logging.info("Checking code formatting...")
    for filename in os.listdir(script_dir):
        if filename.endswith('.py') and filename != os.path.basename(__file__):
            is_formatted = check_formatting(filename)
            logging.info(f"{filename} formatting: {'correct' if is_formatted else 'needs reformatting'}")

if __name__ == "__main__":
    main()
