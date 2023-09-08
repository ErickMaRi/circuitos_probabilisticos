"""unit_parameter_perturbator.py es un script que prueba la capacidad de parameter_perturbator
de producir archivos con perturbaciones en las magnitudes de sus elementos de circuito que son controlables,
usa la configuración default de la función y revisa si el resultado de la distribución uniforme sobrepasa
lo esperado para el parámetro de escala (0.03).
    """
import sys
import os
import unittest

# Obtener la ruta del directorio actual del archivo unit_simulation.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Agregar la ruta del directorio 'src' al path de Python
src_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from parameter_perturbation import parameter_perturbator
from file_operations import read_cir_file

class TestParameterPerturbator(unittest.TestCase):

    def test_parameter_perturbator(self):
        """Prueba a parameter perturbator y revisa si los valores de los elementos
        de los archivos creados tienen sentido para el parámetro de escala (0.03).
        """
        # Definir los valores de prueba
        cir_dict = {
            10: {'name': 'R2', 'value': 1000},
            11: {'name': 'L2', 'value': 0.001},
            12: {'name': 'R1', 'value': 1000},
            14: {'name': 'C1', 'value': 1e-06}
        }
        n_files = 5
        input_file_name = "App\\cir_parser_app\\src\\unit_testing\\LINEAL.cir"
        base_output_folder = "App\\cir_parser_app\\src\\unit_testing\\unit_new_cir\\"

        # Ejecutar la función de perturbación de parámetros
        parameter_perturbator(cir_dict, input_file_name, n_files=n_files, base_output_folder=base_output_folder)

        # Verificar los archivos generados
        for i in range(n_files):
            output_file_name = f"{base_output_folder}/new_cir_{i}.cir"
            self.assertTrue(os.path.exists(output_file_name))

            # Leer el archivo .cir generado y verificar los valores de los elementos
            new_cir_dict = read_cir_file(output_file_name)
            for element_id, element_data in new_cir_dict.items():
                value = element_data['value']
                self.assertTrue(0.97 * cir_dict[element_id]['value'] <= value <= 1.03 * cir_dict[element_id]['value'])

if __name__ == '__main__':
    unittest.main()
