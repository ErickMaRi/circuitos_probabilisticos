"""parameter_perturbation.py contiene:
        parameter_perturbator(cir_dict, input_file_name, dist=None, scale=None, n_files=10,
        base_output_folder="new_cir_files", new_filename="new_cir", retornar_lista_dicts=False, debug=False):
        Una función encargada de poblar un directorio con una cantidad n_files de archivos cir, estos contienen
        el netlist que describe un circuito original, pero con el valor de las magnitudes de sus elementos
        perturbados según el diccionario en dist y el diccionario en scale."""
import os
import numpy as np
import file_operations as fileopr

def parameter_perturbator(cir_dict, input_file_name, dist=None, scale=None, n_files=10, base_output_folder="new_cir_files", new_filename="new_cir", retornar_lista_dicts=False, debug=False):
    """Genera n_files archivos .cir que contienen 
    valores para sus parámetros perturbados con distribuciones probabilísticas.

    Args:
        cir_dict (dict): Diccionario que contiene entradas con la línea en la que
        se encuentra el elemento, conteniendo entradas con el nombre del mismo y su valor.
        dist (dict, optional): Diccionario que mapea cada elemento a su distribución ('uniform', 'normal',
        etc.). Si no se proporciona, se usa 'uniform' para todos los elementos.
        scale (dict, optional): Diccionario que mapea cada elemento a su parámetro de escala. Si no se proporciona,
        se usa 0.03 para todos los elementos.
        n_files (int, optional): Número de archivos a escribir, su default es 10.
        input_file_name (str, optional): Camino del archivo original al cual perturbar.
        parámetros, su valor default es "./archivos_cir/LINEAL.cir".
        base_output_folder (str, optional): Carpeta que contendrá los archivos generados, su default es "new_cir_files".
    """
    if dist is None:
        dist = {key: 'uniform' for key in cir_dict.keys()}
    if scale is None:
        scale = {key: 0.03 for key in cir_dict.keys()}
    if debug:
        print(dist)
        print(scale)
    # Revisamos si existe la carpeta
    fileopr.existe_carpeta(base_output_folder)
    out_dicts = []
    # Realizamos n_files loops
    for i in range(n_files):
        # Iniciamos un diccionario vacío
        new_cir_dict = {}
        for key, item in cir_dict.items():
            # Agarramos el valor actual
            value = item['value']
            # Ese valor es perturbado probabilísticamente.
            element_dist = dist[key]
            element_scale = scale[key]
            if element_dist == 'uniform':
                min_val = value * (1 - element_scale)
                max_val = value * (1 + element_scale)
                new_val = np.random.uniform(min_val, max_val)
            elif element_dist == 'normal':
                std_dev = value * element_scale
                new_val = np.random.normal(value, std_dev)
            else:
                raise ValueError('Unsupported distribution')

            # Atajamos los valores negativos
            while new_val < 0:
                if element_dist == 'uniform':
                    new_val = np.random.uniform(min_val, max_val)
                elif element_dist == 'normal':
                    new_val = np.random.normal(value, std_dev)
            # Vamos armando el diccionario vacío
            new_cir_dict[key] = {
                'value': new_val,
                'name': item['name'],
            }
            # Talvez vamos a ocupar esta lista de diccionarios
            if retornar_lista_dicts:
                out_dicts.append(new_cir_dict)
        # Usamos el marco de referencia
        output_file_name = os.path.join(
            base_output_folder, f"{new_filename}_{i}.cir")
        # Con el nuevo dict creamos otro .cir
        fileopr.create_new_cir_file(
            new_cir_dict, input_file_name, output_file_name)
        # Queremos la lista?
        if retornar_lista_dicts & (i == n_files):
            return out_dicts
