"""simulation.py contiene el código relacionado a la simulación de los archivos, contiene:
        run_simulations(cir_folder, debug=False, output=None, prog=True, compat=None):
        Que ejecuta una simulación a través de PySpice en NgSpice, construye un diccionario
        que contiene los archivos de origen de la simulación y en los values los resultados
        de simular.
    """
from PySpice.Spice.NgSpice.Shared import NgSpiceShared
import numpy as np
import os

def run_simulations(cir_folder, debug=False, output=None, prog=True, compat=None):
    """Simula todos los archivos en una carpeta.

    Args:
        cir_folder (str): El path a la carpeta conteniendo los archivos cir.

    Returns:
        dict: Diccionario con keys como los archivos de origen y values como los valores.
    """

    # Revisamos el separador.
    if not cir_folder.endswith(os.path.sep):
        cir_folder += os.path.sep

    # Obtenemos una lista de archivos cir
    cir_files = [f for f in os.listdir(cir_folder) if f.endswith('.cir')]

    # Se inicia una instancia de la clase NgSpiceShared
    # Contiene muchas utilidades necesarias para correr la simulación
    ngspice = NgSpiceShared.new_instance()
    simulation_results = {}
    # Recorremos los archivos
    for cir_file in cir_files:
        full_cir_path = cir_folder + cir_file
        # Cargamos los datos del archivo
        with open(full_cir_path, 'r', encoding="UTF-8") as file:
            content = file.read()
        if compat == "lt":
            ngspice.exec_command("set ngbehavior=lt")
        elif compat == "ps":
            ngspice.exec_command("set ngbehavior=ps")
        # Corremos la simulación
        ngspice.load_circuit(content)
        ngspice.run()
        if prog:
            print(f"Se simuló con éxito el archivo: {str(cir_file)}")
        last_plot = ngspice.last_plot
        plot = ngspice.plot(simulation=ngspice, plot_name=last_plot)
        if debug:
            print(
                f'Los vectores obtenidos al simular son: {str(list(plot.keys()))}.')
        time_data = np.array(plot['time']._data)
        # Esto de aquí es un hack, sucede que las salidas pueden tener nombres arbitrarios
        # print(plot.keys())
        # print(list(plot.keys()))
        # print(str(list(plot.keys())[0]))
        # Nos estamos llevando la primer entrada en los keys
        # que no es time, no estamos manejando múltiple salida
        # correctamente, la solución se podrá obtener una vez
        # tengamos interfaz gráfica.
        entrada = 0
        if output:
            # Si el usuario conoce una salida y la selecciona:
            try:
                for x in range(len(list(plot.keys()))):
                    if str(list(plot.keys())[x]) == str(output):
                        entrada = x
                voltage_data = np.array(
                    plot[str(list(plot.keys())[entrada])]._data)
                simulation_results[cir_file] = {
                    'time': time_data, str(output): voltage_data}
            except:
                print("Hubo un error al procesar la salida seleccionada.")
                print("La lista de los keys en el plot perteneciente a los ")
                print(f"resultados pertenecientes a la simulación son: \n {str(list(plot.keys()))}")
                print("Se usará el primer key que no sea el tiempo...")
                for x in range(len(list(plot.keys()))):
                    if str(list(plot.keys())[x]) != 'time':
                        entrada = x
                voltage_data = np.array(
                    plot[str(list(plot.keys())[entrada])]._data)
                simulation_results[cir_file] = {
                    'time': time_data, str(list(plot.keys())[entrada]): voltage_data}
        else:
            # Si el usuario no selecciona una salida
            for x in range(len(list(plot.keys()))):
                if str(list(plot.keys())[x]) != 'time':
                    entrada = x
            voltage_data = np.array(
                plot[str(list(plot.keys())[entrada])]._data)
            simulation_results[cir_file] = {
                'time': time_data, str(list(plot.keys())[entrada]): voltage_data}

    return simulation_results
