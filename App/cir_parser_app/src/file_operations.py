"""file_operations.py contiene:
        read_cir_file(file_name): Lee un archivo .cir que define un circuito y
        construye un netlist que representa los elementos resistivos, inductivos
        o capacitivos, con la línea en la que se encuentran, su nombre y su magnitud.

        create_new_cir_file(cir_dict, input_file_name, output_file_name): Escribe un
        nuevo netlist con los valores definidos por un diccionario, es usado en
        parameter_perturbator.

        existe_carpeta(directory_name): Revisa si una carpeta existe, si no existe
        la crea, si existe elimina todos los archivos que contenga.
    """
import ltspice_converter as spceconvrt
import os
import regex as re

def read_cir_file(file_name):
    """
    Lee un archivo .cir que define un circuito y construye un netlist.

    Esta función toma como entrada la dirección de un netlist formateado en .cir,
    extrae los parámetros a un diccionario que contiene la línea en la que se encuentran,
    su nombre y valor.

    Args:
        file_name (str): Ruta del archivo .cir a leer.

    Returns:
        dict: Diccionario que contiene:
              - Clave: Número de línea en el archivo original.
              - Valor: Diccionario con 'name' (nombre del componente) y 'value' (valor del componente).

    Notas:
        - La función usa la línea que contiene '.TEMP' como marcador del comienzo del circuito principal.
        - Solo se extraen componentes resistivos (R), capacitivos (C) o inductivos (L).
        - Se manejan casos especiales como componentes con condiciones iniciales (IC).
        - La función utiliza codificación UTF-8 para leer el archivo.

    Raises:
        FileNotFoundError: Si el archivo especificado no existe.
        UnicodeDecodeError: Si hay problemas al decodificar el archivo con UTF-8.
    """
    # Abrimos el archivo inicial en formato de lectura, es sensible a
    # fallar si el valor de encoding no es el correcto para el archivo
    # .cir, LTSpice utiliza UTF-8 para codificar y por esa razon se tiene
    # por determinado, aunque raro debería poder ser posible editar esto
    # desde la UI entendiendo que puedan haber errores.
    with open(file_name, 'r', encoding="UTF-8") as file:
        # Vertimos el contenido en content
        content = file.read()

    # Lo separamos en una lista, línea por línea
    lines = content.split('\n')
    # Inicializamos un diccionario vacío.
    cir_dict = {}
    temp_flag = False
    line_counter = 0
    # Recorremos las líneas
    for line in lines:
        line_counter += 1
        # Con regex extraemos grupos de caracteres separados por barra espaciadora.
        component_match = re.match(
            r'([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+(.*?)(?=(\s+[A-Za-z0-9]+\s+|$))', line)
        if ".TEMP" in line:
            temp_flag = True
        # Separamos los componentes
        if component_match and temp_flag:
            component_name = component_match.group(1)
            component_value = component_match.group(4)
            # Sólo nos llevamos resistencias, capacitores o inductores.
            if component_name[0] in ['R', 'C', 'L']:
                # Si el grupo cuarto es separable por barra espaciadora
                if len(component_value.split()) != 1:
                    # Y el elemento contiene las condiciones iniciales
                    if component_value.split()[1].split("=")[0] == "IC":
                        # Con cuidado evitamos añadir al diccionario las condiciones iniciales
                        cir_dict[line_counter] = {
                            'value': spceconvrt.LTSpice_to_float(component_value.split()[0]),
                            'name': component_name,
                        }
                else:
                    cir_dict[line_counter] = {
                        'value': spceconvrt.LTSpice_to_float(component_value),
                        'name': component_name,
                    }
            continue

    return cir_dict

def create_new_cir_file(cir_dict, input_file_name, output_file_name):
    """
    Escribe un nuevo documento netlist con los valores dictados por un diccionario.

    Esta función lee un archivo .cir existente y crea uno nuevo, reemplazando los valores
    de los componentes especificados en el diccionario proporcionado.

    Args:
        cir_dict (dict): Diccionario que contiene:
                         - Clave: Número de línea en el archivo original.
                         - Valor: Diccionario con 'name' (nombre del componente) y 'value' (nuevo valor del componente).
        input_file_name (str): Ruta del archivo .cir de entrada.
        output_file_name (str): Ruta donde se guardará el nuevo archivo .cir.

    Returns:
        None

    Notas:
        - La función mantiene el formato original del archivo, solo cambiando los valores especificados.
        - Se manejan casos especiales como componentes con condiciones iniciales (IC).
        - La función utiliza codificación UTF-8 para leer el archivo de entrada.

    Raises:
        FileNotFoundError: Si el archivo de entrada no existe.
        UnicodeDecodeError: Si hay problemas al decodificar el archivo de entrada con UTF-8.
        IOError: Si hay problemas al escribir el archivo de salida.
    """
    # Abrimos el .cir
    with open(input_file_name, 'r', encoding="UTF-8") as in_file:
        # Abrimos el archivo en el que guardaremos el nuevo netlist.
        with open(output_file_name, 'w') as out_file:
            line_counter = 0
            # Leemos línea por línea
            for line in in_file:
                line_counter += 1
                # Si la línea es una de nuestro diccionario
                if line_counter in cir_dict:
                    # Y el regex comprueba tiene la forma que esperamos
                    component_match = re.match(
                        r'([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+(.*?)(?=(\s+[A-Za-z0-9]+\s+|$))', line)
                    if component_match:
                        # Separamos la línea en las barras espaciadoras
                        component_parts = line.split()
                        # Si el último grupo son las condiciones iniciales
                        if component_parts[-1].split("=")[0] == "IC":
                            # Tenemos el cuidado de reescribir en el lugar correcto
                            component_parts[-2] = spceconvrt.float_to_LTSpice(
                                cir_dict[line_counter]['value'])
                        else:
                            # De otra forma sin miedo en el último grupo va el valor
                            component_parts[-1] = spceconvrt.float_to_LTSpice(
                                cir_dict[line_counter]['value'])
                        # Con el regex que usamos armamos de nuevo la línea
                        line = ' '.join(component_parts) + '\n'
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
