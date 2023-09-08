"""unit_plotting.py es un script con pruebas unitarias para cada función
    asociada al dibujo de figuras perteneciente al módulo plotting, usa datos
    simples para producir plots que pueden ser verificados manualmente
    """
import unittest
import sys
import os
from scipy import stats

# Obtener la ruta del directorio actual del archivo unit_simulation.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Agregar la ruta del directorio 'src' al path de Python
src_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from file_operations import read_cir_file
from plotting import plot_simulation_results, estimate_distribution, plot_distributions, plot_density

class TestPlottingFunctions(unittest.TestCase):

    def setUp(self):
        """Define los datos de prueba
        """
        # Configurar datos de prueba comunes
        self.simulation_results = {
            'sim1': {
                'time': [0, 1, 2, 3],
                'output1': [1, 2, 3, 4],
                'output2': [5, 6, 7, 8]
            },
            'sim2': {
                'time': [0, 1, 2, 3],
                'output1': [2, 4, 6, 8],
                'output2': [10, 12, 14, 16]
            }
        }
        self.num_timesteps = 100
        self.dist_type = 'normal'
        self.interpolation_method = 'linear'

    def test_plot_simulation_results(self):
        """Se debe verificar de forma manual el resultado de esta prueba.
        """
        # Prueba la función plot_simulation_results
        # Verificar si los gráficos se generan correctamente
        plot_simulation_results(self.simulation_results, output='output1', max_files=2)
        # Verificar que los gráficos se generen sin errores

    def test_estimate_distribution(self):
        """Se debe verificar de forma manual el resultado de esta prueba.
        """
        # Prueba la función estimate_distribution
        # Verificar si las distribuciones se estiman correctamente
        fitted_distributions = estimate_distribution(self.simulation_results, self.num_timesteps,
                                                     dist_type=self.dist_type,
                                                     interpolation_method=self.interpolation_method)
        # Verificar si la salida tiene el formato y los datos esperados

    def test_plot_distributions(self):
        """Se debe verificar de forma manual el resultado de esta prueba.
        """
        # Prueba la función plot_distributions
        # Verificar si los gráficos de las distribuciones se generan correctamente
        fitted_distributions = {
            0.0: stats.norm(0, 1),
            1.0: stats.norm(1, 1),
            2.0: stats.norm(2, 1)
        }
        plot_distributions(fitted_distributions, num_samples=100, n=2)
        # Verificar que los gráficos se generen sin errores

    def test_plot_density(self):
        """Se debe verificar de forma manual el resultado de esta prueba.
        """
        # Prueba la función plot_density
        # Verifica si los gráficos de densidad se generan correctamente
        plot_density(self.simulation_results, self.num_timesteps, num_bins=20, interpolation_method=self.interpolation_method)
        # Verificar que los gráficos se generen sin errores

if __name__ == '__main__':
    unittest.main()
