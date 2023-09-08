from file_operations import *
from ltspice_converter import *
from parameter_perturbation import *
from simulation import *
from plotting import *

if __name__ == '__main__':
    import pprint
    file_name = 'cir_parse\cir.cir'
    cir_dict = read_cir_file(file_name)
    formatted_dict = pprint.pformat(cir_dict)
    print(formatted_dict)
    parameter_perturbator(cir_dict, n_files=1000, scale=0.5)
    simulation_results = run_simulations("new_cir_files", debug=True)
    estimated_distributions = estimate_distribution(simulation_results, num_timesteps=200)
    print(estimated_distributions)
    plot_distributions(estimated_distributions)
    plot_density(simulation_results, num_timesteps=200)