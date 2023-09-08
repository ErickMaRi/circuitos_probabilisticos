import re
import os
import numpy as np
from scipy import interpolate
from scipy import stats

def parameter_perturbator(cir_dict, dist='uniform', scale=0.03, n_files=10, input_file_name="cir_parse\cir.cir", base_output_folder="new_cir_files", new_filename= "new_cir", retornar_lista_dicts=False):
    """Genera n_files archivos .cir que contienen 
    valores para sus parámetros perturbados con distribuciones probabilísticas.

    Args:
        cir_dict (dict): Diccionario que contiene entradas con la línea en la que
        se encuentra el elemento, conteniendo entradas con el nombre del mismo y su valor.
        dist (str, optional): Distribución elegida ('uniform', 'normal',
        etc.). La distribución 'uniform' es la default.
        scale (float, optional): Parámetro de escala. Su default es 0.03, un +-3% de variación en una distribución uniforme.
        n_files (int, optional): Número de archivos a escribir, su default es 10.
        input_file_name (str, optional): Camino del archivo original al cual perturbar.
        parámetros, su valor default es "cir_parse\cir.cir".
        base_output_folder (str, optional): Carpeta que contendrá los archivos generados, su default es "new_cir_files".
    """
    existe_carpeta(base_output_folder) # Revisamos si existe la carpeta
    out_dicts = []
    # Realizamos n_files loops
    for i in range(n_files):
        # Iniciamos un diccionario vacío
        new_cir_dict = {}
        for key, item in cir_dict.items():
            #Agarramos el valor actual
            value = item['value']
            # Ese valor es perturbado probabilísticamente.
            if dist == 'uniform':
                min_val = value * (1 - scale)
                max_val = value * (1 + scale)
                new_val = np.random.uniform(min_val, max_val)
            elif dist == 'normal':
                std_dev = value * scale
                new_val = np.random.normal(value, std_dev)
            else:
                raise ValueError('Unsupported distribution')

            # Atajamos los valores negativos
            while new_val < 0:
                if dist == 'uniform':
                    new_val = np.random.uniform(min_val, max_val)
                elif dist == 'normal':
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
        output_file_name = os.path.join(base_output_folder, f"{new_filename}_{i}.cir")
        # Con el nuevo dict creamos otro .cir
        create_new_cir_file(new_cir_dict, input_file_name, output_file_name) 
        # Queremos la lista?
        if retornar_lista_dicts & (i == n_files) : 
            return out_dicts