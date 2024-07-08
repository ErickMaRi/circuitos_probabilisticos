"""simulation.py contiene el código relacionado a la simulación de los archivos, contiene:
        run_simulations(cir_folder, debug=False, output=None, prog=True, compat=None):
        Que ejecuta una simulación a través de PySpice en NgSpice, construye un diccionario
        que contiene los archivos de origen de la simulación y en los values los resultados
        de simular.
    """
from PySpice.Spice.NgSpice.Shared import NgSpiceShared
import numpy as np
import os

def run_simulations(cir_folder, debug=True, prog=False, compat=None, update_callback=None):
    """_    Ejecuta las simulaciones de todos los archivos .cir en el cir_folder
    que los contenga._

    Args:
        cir_folder (_str_): _Dirección del folder contenedor de los archivos .cir_
        debug (bool, optional): _Controla salidas a consola útiles para el desarrollador_.
            Defaults to True.
        prog (bool, optional): _Muestra en la consola el progreso de las simulaciones_.
            Defaults to False.
        compat (_str_, optional): _Controla la el modo de compatibilidad de PySpice con
            LtSpice y PSpice (lt o ps)_. Defaults to None.
        update_callback (_callable_, optional): _Función de callback para actualizar el progreso. 
            Toma un argumento entero que representa el número de simulaciones completadas._
            Defaults to None.


    Returns:
    tuple: Un tuple conteniendo dos elementos:
            - dict: Diccionario con los resultados de la simulación.
            - list: Lista de salidas disponibles.
    """

    # Si el folder no termina con el separador del sistema operativo
    if not cir_folder.endswith(os.path.sep):
        # Lo añadimos
        cir_folder += os.path.sep
    
    # Entonces recorremos todos los archivos cir en el folder
    cir_files = [f for f in os.listdir(cir_folder) if f.endswith('.cir')]

    # Declaramos una instancia de NgSpice para la simulación
    ngspice = NgSpiceShared.new_instance()

    # Contenedor para los resultados
    simulation_results = {}

    # Conjunto vacío contenedor de los nombres de las salidas
    available_outputs = set()
    
    # Recorremos la carpeta simulando todos los archivos cir
    for i, cir_file in enumerate(cir_files, 1):

        # Establecemos el camino al archivo que queremos simular
        full_cir_path = cir_folder + cir_file

        # Abrimos el archivo, ojo al encoding
        with open(full_cir_path, 'r', encoding="UTF-8") as file:
            content = file.read()
        
        # Seleccionamos el modo de compatibilidad, si es necesario
        if compat == "lt":
            ngspice.exec_command("set ngbehavior=lt")
        elif compat == "ps":
            ngspice.exec_command("set ngbehavior=ps")
        
        # Cargamos el contenido del .cir en el ambiente de ngspice
        ngspice.load_circuit(content)
        ngspice.run() # Simulamos
        
        # Talvez producimos salidas sobre el progreso de la simulación
        if prog:
            print(f"Se simuló con éxito el archivo: {str(cir_file)}")
        
        # Sostenemos la última salida
        last_plot = ngspice.last_plot

        # Construímos un objeto plot del ambiente PySpice
        plot = ngspice.plot(simulation=ngspice, plot_name=last_plot)
        
        # Salida para el desarrollador
        if debug:
            print(f'Los vectores obtenidos al simular son: {str(list(plot.keys()))}.')
        
        # Extraemos los datos del objeto plot:
        time_data = np.array(plot['time']._data) # El tiempo
        results = {'time': time_data} # Comenzamos a llenar los resultados
        
        # No sabemos que salidas existen ni cuantas hay
        for key in plot.keys():
            if key != 'time': # Pero sabemos que ya recogimos el tiempo

                # Extraemos las salidas por como se les nombró en el netlist
                results[key] = np.array(plot[key]._data)
                available_outputs.add(key)
        
        simulation_results[cir_file] = results
        
        # Finalmente el callback comunica a la UI que logramos simular
        if update_callback:
            update_callback(i)
    
    #Fin
    return simulation_results, list(available_outputs)