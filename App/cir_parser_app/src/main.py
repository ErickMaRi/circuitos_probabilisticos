#main.py
from file_operations import *
from ltspice_converter import *
from parameter_perturbation import *
from simulation import *
from plotting import *

if __name__ == '__main__':
    import pprint
    file_name = './App/cir_parser_app/archivos_cir/LINEAL.cir'
    cir_dict = read_cir_file(file_name)
    formatted_dict = pprint.pformat(cir_dict)
    print(formatted_dict)
    print(cir_dict)
    parameter_perturbator(cir_dict, n_files=20, debug=True, input_file_name=file_name,dist = {key: 'uniform' for key in cir_dict.keys()}, scale = {key: 0.1 for key in cir_dict.keys()})
    simulation_results = run_simulations("new_cir_files", debug=True, compat="ps", output='V(3)')
    #estimated_distributions = estimate_distribution(simulation_results, num_timesteps=2000)
    #plot_simulation_results(simulation_results, output='V(4)', max_files= 1)
    plot_density(simulation_results, num_timesteps = 10000, num_bins = 1000)
