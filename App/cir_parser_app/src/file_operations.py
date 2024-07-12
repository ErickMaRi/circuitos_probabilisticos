import ltspice_converter as spceconvrt
import os
import regex as re

def read_cir_file(file_name):
    """
    Lee un archivo .cir que define un circuito y construye un netlist.

    Esta función toma como entrada la dirección de un netlist formateado en .cir,
    extrae los parámetros a un diccionario que contiene la línea en la que se encuentran,
    su nombre, valor, y ahora también el tipo de distribución y su escala.

    Args:
        file_name (str): Ruta del archivo .cir a leer.

    Returns:
        dict: Diccionario que contiene:
              - Clave: Número de línea en el archivo original.
              - Valor: Diccionario con 'name' (nombre del componente), 'value' (valor del componente),
                       'dist' (tipo de distribución), y 'scale' (escala de la distribución).

    Notas:
        - La función usa la línea que contiene '.TEMP' como marcador del comienzo del circuito principal.
        - Solo se extraen componentes resistivos (R), capacitivos (C) o inductivos (L).
        - Se manejan casos especiales como componentes con condiciones iniciales (IC).
        - La función utiliza codificación UTF-8 para leer el archivo.
        - Ahora se extraen los datos de distribución si están presentes en el comentario.

    Raises:
        FileNotFoundError: Si el archivo especificado no existe.
        UnicodeDecodeError: Si hay problemas al decodificar el archivo con UTF-8.
    """
    with open(file_name, 'r', encoding="UTF-8") as file:
        content = file.read()

    lines = content.split('\n')
    cir_dict = {}
    temp_flag = False
    line_counter = 0

    for line in lines:
        line_counter += 1
        component_match = re.match(
            r'([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+(.*?)(?=(\s+[A-Za-z0-9]+\s+|$))', line)
        if ".TEMP" in line:
            temp_flag = True
        if component_match and temp_flag:
            component_name = component_match.group(1)
            component_value = component_match.group(4)
            if component_name[0] in ['R', 'C', 'L']:
                value = component_value.split()[0]
                dist_info = re.search(r'\*DIST:\s*(\w+)\s*([\d.]+)*', line)
                
                if dist_info:
                    dist_type = dist_info.group(1).lower()
                    dist_scale = float(dist_info.group(2)) if dist_info.group(2) else 0.00
                else:
                    dist_type = 'uniform'
                    dist_scale = 0.00

                cir_dict[line_counter] = {
                    'value': spceconvrt.LTSpice_to_float(value),
                    'name': component_name,
                    'dist': dist_type,
                    'scale': dist_scale
                }

                if 'IC' in component_value:
                    cir_dict[line_counter]['IC'] = component_value.split('IC=')[1]

    return cir_dict

def create_new_cir_file(cir_dict, input_file_name, output_file_name):
    """
    Escribe un nuevo documento netlist con los valores dictados por un diccionario,
    manteniendo los comentarios de distribución si están presentes.

    Args:
        cir_dict (dict): Diccionario que contiene:
                         - Clave: Número de línea en el archivo original.
                         - Valor: Diccionario con 'name' (nombre del componente),
                                  'value' (nuevo valor del componente),
                                  'dist' (tipo de distribución),
                                  'scale' (escala de la distribución).
        input_file_name (str): Ruta del archivo .cir de entrada.
        output_file_name (str): Ruta donde se guardará el nuevo archivo .cir.

    Returns:
        None
    """
    with open(input_file_name, 'r', encoding="UTF-8") as in_file:
        with open(output_file_name, 'w', encoding="UTF-8") as out_file:
            line_counter = 0
            for line in in_file:
                line_counter += 1
                if line_counter in cir_dict:
                    parts = line.split(';')
                    component_part = parts[0].strip()
                    comment_part = ';'.join(parts[1:]).strip() if len(parts) > 1 else ""

                    component_match = re.match(
                        r'([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+(.*?)(?=(\s+[A-Za-z0-9]+\s+|$))', component_part)
                    if component_match:
                        component_parts = component_part.split()
                        new_value = spceconvrt.float_to_LTSpice(cir_dict[line_counter]['value'])
                        
                        if "IC=" in component_parts[-1]:
                            ic_part = component_parts[-1]
                            component_parts[-2] = new_value
                            component_parts[-1] = ic_part
                        else:
                            component_parts[-1] = new_value

                        component_part = ' '.join(component_parts)

                    if comment_part:
                        new_line = f"{component_part} ; {comment_part}\n"
                    else:
                        new_line = f"{component_part}\n"

                    out_file.write(new_line)
                else:
                    out_file.write(line)

def existe_carpeta(directory_name):
    """
    Crea una carpeta si no existe y elimina todos los archivos en ella si ya existe.

    Esta función verifica la existencia de una carpeta. Si no existe, la crea.
    Si existe, elimina todos los archivos contenidos en ella.

    Args:
        directory_name (str): Nombre o ruta del directorio a verificar/crear.

    Returns:
        None

    Notas:
        - Esta función es útil para preparar un directorio limpio para nuevos archivos.
        - Solo elimina archivos, no subcarpetas.

    Raises:
        OSError: Si hay problemas al crear el directorio o eliminar archivos.

    Advertencia:
        Esta función elimina archivos sin confirmación. Úsese con precaución.
    """
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    else:
        files = os.listdir(directory_name)
        for file in files:
            file_path = os.path.join(directory_name, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
