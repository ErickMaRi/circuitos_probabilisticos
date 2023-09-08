import os
from PySpice.Spice.Netlist import Circuit

def read_cir_file(file_name):

    """_Toma como entrada la dirección de un netlist formateado en .cir,
    extrae los parámetros a un diccionario que contiene, la línea en la
    que se encuentran, su nombre y valor_

    Returns:
        _dict_: _Diccionario que contiene: la línea de la que fue
        extraído en los keys, en los valores un diccionario que contiene el nombre y el valor_
    """
    #Abrimos el archivo inicial en formato de lectura, es sensible a
    #fallar si el valor de encoding no es el correcto para el archivo
    #.cir, LTSpice utiliza UTF-8 para codificar y por esa razon se tiene
    #por determinado, aunque raro debería poder ser posible editar esto
    # desde la UI entendiendo que puedan haber errores.
    with open(file_name, 'r', encoding="UTF-8") as file:
        #Vertimos el contenido en content
        content = file.read()

    #Lo separamos en una lista, línea por línea
    lines = content.split('\n')
    #Inicializamos un diccionario vacío.
    cir_dict = {}

    line_counter = 0
    #Recorremos las líneas
    for line in lines:
        line_counter += 1
        #Con regex extraemos grupos de caracteres separados por barra espaciadora.
        component_match = re.match(r'([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+(.*?)(?=(\s+[A-Za-z0-9]+\s+|$))', line)
        
        #Separamos los componentes
        if component_match:
            component_name = component_match.group(1)
            component_value = component_match.group(4)
            #Sólo nos llevamos resistencias, capacitores o inductores.
            if component_name[0] in ['R', 'C', 'L']:
                #Si el grupo cuarto es separable por barra espaciadora
                if len(component_value.split()) != 1:
                    #Y el elemento contiene las condiciones iniciales
                    if component_value.split()[1].split("=")[0] == "IC":
                        #Con cuidado evitamos añadir al diccionario las condiciones iniciales
                        cir_dict[line_counter] = {
                            'value': LTSpice_to_float(component_value.split()[0]),
                            'name': component_name,
                        }
                else:
                    cir_dict[line_counter] = {
                        'value': LTSpice_to_float(component_value),
                        'name': component_name,
                    }
            continue

    return cir_dict

def create_new_cir_file(cir_dict, input_file_name, output_file_name):
    """Escribe un nuevo documento netlist, que contiene los valores dictados por un diccionario

    Args:
        cir_dict (_dict_): _Diccionario que contiene en los keys la línea
        en la que se encuentra el elemento, en sus valores un diccionario
        que contiene el nombre y el valor del elemento_
        input_file_name (_type_): _description_
        output_file_name (_type_): _description_
    """
    #Abrimos cir.cir
    with open(input_file_name, 'r', encoding="UTF-8") as in_file:
        #Abrimos el archivo en el que guardaremos el nuevo netlist.
        with open(output_file_name, 'w') as out_file:
            line_counter = 0
            #Leemos línea por línea
            for line in in_file:
                line_counter += 1
                #Si la línea es una de nuestro diccionario
                if line_counter in cir_dict:
                    #Y el regex comprueba tiene la forma que esperamos
                    component_match = re.match(r'([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+(.*?)(?=(\s+[A-Za-z0-9]+\s+|$))', line)
                    if component_match:
                        #Separamos la línea en las barras espaciadoras
                        component_parts = line.split()
                        #Si el último grupo son las condiciones iniciales
                        if component_parts[-1].split("=")[0] == "IC":
                            #Tenemos el cuidado de reescribir en el lugar correcto
                            component_parts[-2] = float_to_LTSpice(cir_dict[line_counter]['value'])
                        else:
                            #De otra forma sin miedo en el último grupo va el valor
                            component_parts[-1] = float_to_LTSpice(cir_dict[line_counter]['value'])
                        #Con el regex que usamos armamos de nuevo la línea
                        line = ' '.join(component_parts) + '\n'
                out_file.write(line)

def existe_carpeta(directory_name):
    """Creamos una carpeta si esta no existe.

    Args:
        directory_name (str): Nombre del directorio.
    """
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    else:
        pass
