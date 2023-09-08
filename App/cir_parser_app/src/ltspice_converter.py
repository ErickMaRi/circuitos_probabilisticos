"""ltspice_converter.py contiene funciones relacionadas al manejo de strings,
en el contexto de convertir de float al formato de string utilizado en LTSpice:
        LTSpice_to_float(string): Convierte de strings formateadas en el estilo
        utilizado en los netlist de LTSpice a floats.
        float_to_LTSpice(flo): Convierte de floats a strings en el estilo
        utilizado en los netlist de LTSpice.
    """
import regex as re

def LTSpice_to_float(string):
    """Pasa de la notación usada para representar magnitudes en un netlist a un float.

    Args:
        string : En la forma 999, 10K, 20N etc.

    Returns:
        float: Valor en punto flotante extraido de la notación.
    """
    try:
        return float(string)
    except:
        # Vamos a hacer letra minúscula cualquier entrada
        multiplier = None
        string = string.lower()

        # Luego detectar la magnitud del valor
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
    """Converts float to LtSpice notation
    Example:
        27000 -> '27K'
        0.0000001 -> '100N'
        1234.567 -> '1.235K'
    Args:
        flo (float): float number to convert

    Returns:
        str: string representation of flo in LtSpice notation
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
