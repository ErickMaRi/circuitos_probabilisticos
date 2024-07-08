"""ltspice_converter.py contiene funciones relacionadas al manejo de strings,
en el contexto de convertir de float al formato de string utilizado en LTSpice:
        LTSpice_to_float(string): Convierte de strings formateadas en el estilo
        utilizado en los netlist de LTSpice a floats.
        float_to_LTSpice(flo): Convierte de floats a strings en el estilo
        utilizado en los netlist de LTSpice.
    """
import regex as re

def LTSpice_to_float(string):
    """
    Convierte una cadena en notación LTSpice a un número de punto flotante.

    Esta función toma una cadena que representa una magnitud en el formato utilizado
    en los netlists de LTSpice y la convierte a un número de punto flotante.

    Args:
        string (str): Cadena en formato LTSpice. Puede ser de la forma '999', '10K', '20N', etc.

    Returns:
        float: Valor en punto flotante extraído de la notación LTSpice.

    Raises:
        ValueError: Si la cadena no puede ser convertida a un número válido.

    Ejemplos:
        >>> LTSpice_to_float('10K')
        10000.0
        >>> LTSpice_to_float('20N')
        2e-8
        >>> LTSpice_to_float('1.5Meg')
        1500000.0
    """
    try:
        return float(string)
    except:
        # Vamos a hacer letra minúscula cualquier entrada
        multiplier = None
        string = string.lower()
      
        # Luego detectar la magnitud del valor #Código horrible
        if "f" in string:
            multiplier = pow(10, -15)
        elif "p" in string:
            multiplier = pow(10, -12)
        elif "n" in string:
            multiplier = pow(10, -9)
        elif "u" in string:
            multiplier = pow(10, -6)
        elif "m" in string:
            multiplier = pow(10, -3)
        elif "k" in string:
            multiplier = pow(10, 3)
        elif "meg" in string:
            multiplier = pow(10, 6)
        elif "g" in string:
            multiplier = pow(10, 9)
        elif "t" in string:
            multiplier = pow(10, 12)
        elif "e" in string:
            #Algunos netlist vienen formateados en la forma 12E-3
            split = string.split("e")
            string = float(float(split[0])*pow(10, int(split[1])))

        if multiplier:

            string = re.sub(r'[^\d\.]', '', string)
            string.rstrip("0")
            if '.' in string:
                parte_entera, parte_decimal = string.split('.')
                string = (int(parte_entera) * multiplier) + (int(parte_decimal) * pow(10, -len(parte_decimal))) * multiplier
            else:
                string = int(string) * multiplier
        return string

def float_to_LTSpice(flo):
    """
    Convierte un número de punto flotante a notación LTSpice.

    Esta función toma un número de punto flotante y lo convierte a una cadena
    en el formato utilizado en los netlists de LTSpice.

    Args:
        flo (float): Número de punto flotante a convertir.

    Returns:
        str: Representación en cadena del número en notación LTSpice.

    Ejemplos:
        >>> float_to_LTSpice(27000)
        '27K'
        >>> float_to_LTSpice(0.0000001)
        '100N'
        >>> float_to_LTSpice(1234.567)
        '1.235K'

    Notas:
        - La función utiliza una lista de unidades y sufijos para determinar
          la representación más apropiada.
        - Si el número es muy grande (>1e12), la función intenta usar el sufijo
          más grande disponible ('T' para tera).
    """
    units = [
        {"limit": 1e-15, "suffix": "f"},
        {"limit": 1e-12, "suffix": "p"},
        {"limit": 1e-9, "suffix": "n"},
        {"limit": 1e-6, "suffix": "u"},
        {"limit": 1e-3, "suffix": "m"},
        {"limit": 1, "suffix": ""},
        {"limit": 1e3, "suffix": "K"},
        {"limit": 1e6, "suffix": "Meg"},
        {"limit": 1e9, "suffix": "G"},
        {"limit": 1e12, "suffix": "T"},
    ]

    for unit in units: # Por cada diccionario en units
        if flo < unit["limit"]: #Si la entrada es menor al límite
            value = flo / prev_unit["limit"] # Retornamos el float en el límite anterior
            return f"{value}{prev_unit['suffix']}" #Con el sufijo anterior
        prev_unit = unit #Actualizamos la nueva unidad

    return f"{flo*pow(10, -12)}T"  # Si el valor es enorme intentamos usar el sufijo mayor
