import ast
import os
import networkx as nx
import matplotlib.pyplot as plt


def extract_dependencies(tree):
    dependencies = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Call, ast.Attribute)):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    dependencies.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    dependencies.add(node.func.attr)
            elif isinstance(node, ast.Attribute):
                dependencies.add(node.attr)
    return list(dependencies)


def analyze_file(filename):
    with open(filename, 'r') as file:
        tree = ast.parse(file.read())

    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    dependencies = extract_dependencies(tree)

    return classes, functions, dependencies


def generate_graph():
    G = nx.DiGraph()

    all_functions = {}
    all_classes = {}

    for filename in os.listdir('App\cir_parser_app\src'):
        if filename.endswith('.py'):
            if filename not in ["análisis_estático.py"]:
                print(f'Archivo: {filename}')
                classes, functions, dependencies = analyze_file(f'App\cir_parser_app\src\{filename}')
                print(f'Clases: {classes}')
                print(f'Funciones: {functions}')

                all_functions[filename] = functions
                all_classes[filename] = classes

                # Add nodes to the graph
                for class_name in classes:
                    G.add_node(class_name, color='blue')

                for function_name in functions:
                    G.add_node(function_name, color='green')

    # Add edges to the graph based on the interdependencies
    for filename, functions in all_functions.items():
        _, _, dependencies = analyze_file(f'App\cir_parser_app\src\{filename}')
        for dependency in dependencies:
            if dependency in all_functions.get(filename, []) or dependency in all_classes.get(filename, []):
                for function in functions:
                    G.add_edge(function, dependency)
            else:
                for other_file, other_functions in all_functions.items():
                    if other_file != filename and dependency in other_functions:
                        for function in functions:
                            G.add_edge(function, dependency)

    # Draw the graph
    pos = nx.spring_layout(G, k=0.85, iterations=40)
    colors = [node[1]['color'] if 'color' in node[1] else 'red' for node in G.nodes(data=True)]
    nx.draw(G, pos, with_labels=True, font_weight='bold', node_color=colors)
    plt.show()


generate_graph()
