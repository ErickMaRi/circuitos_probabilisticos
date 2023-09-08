"""#plotting.py contiene:
        plot_simulation_results(simulation_results, output=None, max_files=None):
        dibuja una max_files cantidad de plots para los resultados de las simulaciones.
        
        estimate_distributions(simulation_results, num_timesteps, dist_type='normal', interpolation_method='linear'):
        estima una lista de distribuciones probabilísticas basadas en los resultados no uniformes en el tiempo de la
        simulación, interpolándolos a datos uniformes en el tiempo, para luego estimar un diccionario de distribuciones
        que contienen el instante en el tiempo, con la distribución probabilística (asumida normal por defecto).
        
        plot_distributions(fitted_distributions, num_samples=1000, n=10): Grafica las distribuciones estimadas.
        
        plot_density(simulation_results, num_timesteps, num_bins=200, interpolation_method='linear'): Usa los resultados
        de las simulaciones para graficar la densidad de los resultados interpolados a uniformes en el tiempo, con
        resolución configurable (coloreado logarítmicamente)."""
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import LogNorm
import seaborn as sns
import numpy as np
from scipy import interpolate, stats

def plot_simulation_results(simulation_results, output=None, max_files=None):
    """Grafica las simulaciones contenidas en el diccionario.

    Args:
        simulation_results (dict): Diccionario que contien
         los resultados de la simulación.
    """
    files_counter = 0
    for file_name, plot in simulation_results.items():
        if files_counter >= max_files:
            break
        files_counter = files_counter + 1
        # Extraemos el vector de tiempo y voltaje
        time_vector = np.array(plot['time'])
        # print(str(list(plot.keys())))
        if output:
            voltage_vector = np.array(plot[str(output)])
            dependiente = output
        else:
            dependiente = str(list(plot.keys())[1])
            voltage_vector = np.array(plot[dependiente])
        # Creamos el plot
        plt.figure(figsize=(10, 5))
        plt.plot(time_vector, voltage_vector)

        plt.title(f"Resultados de la simulación de: {file_name}")
        plt.xlabel('Time (s)')
        plt.ylabel(dependiente)

        # Show
        plt.show()

def estimate_distribution(simulation_results, num_timesteps, dist_type='normal', interpolation_method='linear'):
    # Inicializamos el diccionario vacío
    # lo vamos a llenar con distribuciones
    fitted_distributions = {}

    # El tiempo mínimo entre los mínimos y el máximo de los máximos
    min_time = min(min(result['time'])
                   for result in simulation_results.values())
    max_time = max(max(result['time'])
                   for result in simulation_results.values())

    # Preparamos un espacio en el cual llenar los datos que vamos a interpolar
    uniform_time_grid = np.linspace(min_time, max_time, num_timesteps)
    all_interpolated_results = []

    # Iteramos por sobre los resultados de la simulación
    for circuit_name, circuit_results in simulation_results.items():
        # Extraemos el tiempo
        times = circuit_results['time']

        # Extraemos el key que no se llama "time"
        value_key = [key for key in circuit_results.keys() if key != 'time'][0]
        values = circuit_results[value_key]

        # Interpolamos los valores a unos distribuídos de forma uniforme
        f = interpolate.interp1d(
            times, values, kind=interpolation_method, fill_value='extrapolate')
        interpolated_values = f(uniform_time_grid)

        # Guardamos los datos interpolados
        all_interpolated_results.append(interpolated_values)

    all_interpolated_results = np.array(all_interpolated_results)

    # Usamos una de dos distribuciones
    if dist_type == 'normal':
        dist = stats.norm
    elif dist_type == 'uniform':
        dist = stats.uniform
    else:
        raise ValueError(f"Tipo desconocido de distribución: {dist_type}")

    # Ahora para cada timestep vamos aproximando la distribución
    for i in range(num_timesteps):
        timestep_data = all_interpolated_results[:, i]

        # Fit
        distribution = dist(*dist.fit(timestep_data))

        # Vamos guardando los datos.
        fitted_distributions[uniform_time_grid[i]] = distribution

    return fitted_distributions

def plot_distributions(fitted_distributions, num_samples=1000, n=20):
    data = []
    for time, distribution in fitted_distributions.items():
        # Muestreamos la distribución
        samples = distribution.rvs(size=num_samples)
        data.append(samples)

    plt.figure(figsize=(10, 6))

    # Creamos un gráfico de violines
    sns.violinplot(data=data)

    # Obtenemos las claves del diccionario como una lista y la convertimos a un array de numpy
    label_times = np.array(list(fitted_distributions.keys()))

    # Se elige cada n etiquetas
    x_ticks = np.arange(len(fitted_distributions))[::n]
    x_labels = [f'{time:.2e}' for time in label_times][::n]

    # Se formatea el gráfico en notación científica
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-2, 2))

    plt.xticks(x_ticks, labels=x_labels)
    plt.ylabel("Magnitud")
    plt.gca().xaxis.set_major_formatter(formatter)

    # Show
    plt.show()

def plot_density(simulation_results, num_timesteps, num_bins=200, interpolation_method='linear'):
    # Mínimos y máximos en tiempo
    min_time = min(min(result['time'])
                   for result in simulation_results.values())
    max_time = max(max(result['time'])
                   for result in simulation_results.values())
    uniform_time_grid = np.linspace(min_time, max_time, num_timesteps)

    all_interpolated_results = []
    # Recorremos los resultados para interpolar
    for circuit_name, circuit_results in simulation_results.items():
        times = circuit_results['time']
        value_key = [key for key in circuit_results.keys() if key != 'time'][0]
        values = circuit_results[value_key]

        f = interpolate.interp1d(
            times, values, kind=interpolation_method, fill_value='extrapolate')
        interpolated_values = f(uniform_time_grid)

        all_interpolated_results.append(interpolated_values)

    # Hacemos las columnas los timestep
    data = np.transpose(all_interpolated_results)

    plt.figure(figsize=(10, 6))

    # Construimos un arreglo con los datos en cada timestep
    flattened_data = data.flatten()
    time_data = np.repeat(uniform_time_grid, data.shape[1])

    # Creamos un histograma en 2d con colores logarítmicos
    plt.hist2d(time_data, flattened_data, bins=num_bins,
               density=True, cmap='plasma', norm=LogNorm())
    plt.xlabel('Time')
    plt.ylabel(f'Valor: {str(value_key)}')

    # Añadimos una barra con la leyenda
    plt.colorbar(label='Density')

    # Show
    plt.show()
