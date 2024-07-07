"""simulation.py contiene el código relacionado a la simulación de los archivos, contiene:
        run_simulations(cir_folder, debug=False, output=None, prog=True, compat=None):
        Que ejecuta una simulación a través de PySpice en NgSpice, construye un diccionario
        que contiene los archivos de origen de la simulación y en los values los resultados
        de simular.
    """
from PySpice.Spice.NgSpice.Shared import NgSpiceShared
import numpy as np
import os

def run_simulations(cir_folder, debug=True, prog=True, compat=None):
    if not cir_folder.endswith(os.path.sep):
        cir_folder += os.path.sep

    cir_files = [f for f in os.listdir(cir_folder) if f.endswith('.cir')]
    ngspice = NgSpiceShared.new_instance()
    simulation_results = {}
    available_outputs = set()

    for cir_file in cir_files:
        full_cir_path = cir_folder + cir_file
        with open(full_cir_path, 'r', encoding="UTF-8") as file:
            content = file.read()
        if compat == "lt":
            ngspice.exec_command("set ngbehavior=lt")
        elif compat == "ps":
            ngspice.exec_command("set ngbehavior=ps")
        ngspice.load_circuit(content)
        ngspice.run()
        if prog:
            print(f"Se simuló con éxito el archivo: {str(cir_file)}")
        last_plot = ngspice.last_plot
        plot = ngspice.plot(simulation=ngspice, plot_name=last_plot)
        if debug:
            print(f'Los vectores obtenidos al simular son: {str(list(plot.keys()))}.')
        time_data = np.array(plot['time']._data)

        results = {'time': time_data}
        for key in plot.keys():
            if key != 'time':
                results[key] = np.array(plot[key]._data)
                available_outputs.add(key)
        simulation_results[cir_file] = results

    return simulation_results, list(available_outputs)
