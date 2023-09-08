from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.NgSpice.Shared import NgSpiceShared

def run_simulations(cir_folder, debug=False):
    """Simula todos los archivos en una carpeta.

    Args:
        cir_folder (str): El path a la carpeta conteniendo los archivos cir.

    Returns:
        dict: Diccionario con keys como los archivos de origen y values como los valores.
    """

    #Revisamos el separador.
    if not cir_folder.endswith(os.path.sep):
        cir_folder += os.path.sep

    # Obtenemos una lista de archivos cir
    cir_files = [f for f in os.listdir(cir_folder) if f.endswith('.cir')]

    # Se inicia una instancia de la clase NgSpiceShared
    # Contiene muchas utilidades necesarias para correr la simulación
    ngspice = NgSpiceShared.new_instance()
    simulation_results = {} 
    #Recorremos los archivos
    for cir_file in cir_files:
        full_cir_path = cir_folder + cir_file
        # Cargamos los datos del archivo
        with open(full_cir_path, 'r', encoding="UTF-8") as file:
            content = file.read()
        # Corremos la simulación
        ngspice.load_circuit(content)
        ngspice.run()
        if debug:
            print("De hecho run funcionó")
        last_plot = ngspice.last_plot
        plot = ngspice.plot(simulation=ngspice, plot_name=last_plot)
        time_data = np.array(plot['time']._data)
        #Esto de aquí es un hack, sucede que las salidas pueden tener nombres arbitrarios
        #print(plot.keys())
        #print(list(plot.keys()))
        #print(str(list(plot.keys())[0]))
        #Nos estamos llevando la primer entrada en los keys
        #que no es time, no estamos manejando múltiple salida
        #correctamente, la solución se podrá obtener una vez
        #tengamos interfaz gráfica.
        for x in range(len(list(plot.keys()))):
            if str(list(plot.keys())[x]) != 'time':
                entrada = x
        voltage_data = np.array(plot[str(list(plot.keys())[entrada])]._data)
        #Armamos el diccionario
        simulation_results[cir_file] = {'time': time_data, str(list(plot.keys())[0]): voltage_data}

    return simulation_results