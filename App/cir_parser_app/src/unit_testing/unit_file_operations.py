"""unit_file_operations.py contiene las pruebas unitarias desarrolladas para
verificar las funciones pertenecientes al módulo.
    """

import sys
import os
import unittest

# Obtener la ruta del directorio actual del archivo unit_file_operations.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Agregar la ruta del directorio 'src' al path de Python
src_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))
sys.path.append(src_dir)

# Importar las funciones de file_operations.py
from file_operations import *


class TestFileOperations(unittest.TestCase):
    def test_read_cir_file(self):
        """Se lee un archivo cir y se compara con el diccionario esperado"""
        file_name = os.path.join(current_dir, 'LINEAL.cir')
        cir_dict = read_cir_file(file_name)

        expected_dict = {
            10: {'name': 'R2', 'value': 1000},
            11: {'name': 'L2', 'value': 0.001},
            12: {'name': 'R1', 'value': 1000},
            14: {'name': 'C1', 'value': 1e-06}
        }

        self.assertEqual(cir_dict, expected_dict)

    def test_create_new_cir_file(self):
        """Se crea un archivo y se compara con el archivo esperado"""
        input_file_name = os.path.join(current_dir, 'LINEAL.cir')
        output_file_name = os.path.join(current_dir, 'test_LINEAL.cir')
        cir_dict = {
            10: {'name': 'R2', 'value': 1},
            11: {'name': 'L2', 'value': 1},
            12: {'name': 'R1', 'value': 1},
            14: {'name': 'C1', 'value': 1}
        }

        create_new_cir_file(cir_dict, input_file_name, output_file_name)

        # Verificar que el nuevo archivo tenga los valores actualizados
        with open(output_file_name, 'r') as file:
            content = file.read()
        expected_content = """LINEAL (PSpice format)
.TEMP 27
.TRAN 20N 10U

.OPTIONS ABSTOL=1P ITL1=150 ITL2=20 ITL4=10 TRTOL=7 
.PROBE V(4,0)

VIN         3 0 DC 0 AC 1 0
+ PULSE ( 0 1 0  0  0  1e19 1e20 )
R2 1 0 1.0
L2 2 1 1.0 IC=0
R1 3 2 1.0
lin         4 3 1M IC=0 
C1 4 2 1.0

.END
"""
        self.assertEqual(content, expected_content)

        # Eliminar el archivo de prueba
        os.remove(output_file_name)

    def test_existe_carpeta(self):
        """Revisa la funcionalidad de la función que revisa la existencia
        de una carpeta, eliminando lo que contenga y generándola si no existe."""
        directory_name = os.path.join(current_dir, 'test_directory')
        os.makedirs(directory_name)

        # Verificar que la carpeta existe
        self.assertTrue(os.path.exists(directory_name))

        # Crear archivos de prueba en la carpeta
        file1_path = os.path.join(directory_name, 'file1.txt')
        file2_path = os.path.join(directory_name, 'file2.txt')
        with open(file1_path, 'w') as file1, open(file2_path, 'w') as file2:
            file1.write('File 1')
            file2.write('File 2')

        # Verificar que los archivos existen
        self.assertTrue(os.path.isfile(file1_path))
        self.assertTrue(os.path.isfile(file2_path))

        # Ejecutar la función para eliminar los archivos
        existe_carpeta(directory_name)

        # Verificar que los archivos han sido eliminados
        self.assertFalse(os.path.isfile(file1_path))
        self.assertFalse(os.path.isfile(file2_path))

        # Verificar que la carpeta está vacía
        self.assertEqual(os.listdir(directory_name), [])

        # Eliminar la carpeta de prueba
        os.rmdir(directory_name)


if __name__ == '__main__':
    unittest.main()
