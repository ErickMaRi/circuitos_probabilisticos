"""unit_ltspice_converter.py es un script que comprueba las funciones contenidas en
    el módulo ltspice_converter, a través de realizar distintas pruebas unitarias que
    comprueban sus dos funciones, dedicadas a convertir formatos para representar magnitudes
    de elementos de circuito.
    """
import sys
import os
import unittest
import math

# Obtiene la ruta del directorio actual del archivo unit_ltspice_converter.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Agrega la ruta del directorio 'src' al path de Python
src_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))
sys.path.append(src_dir)

# Importa las funciones de ltspice_converter.py
from ltspice_converter import *


class TestLTSpiceConverter(unittest.TestCase):
    def test_LTSpice_to_float(self):
        """Revisa la conversión de strings formateados a floats.
        """
        self.assertEqual(LTSpice_to_float("999"), 999.0)
        self.assertEqual(LTSpice_to_float("10K"), 10000.0)
        self.assertEqual(LTSpice_to_float("20N"), 2e-8)
        self.assertEqual(LTSpice_to_float("1U"), 1e-6)
        self.assertEqual(LTSpice_to_float("0.1U"), 1e-7)
        self.assertEqual(LTSpice_to_float("5M"), 5e-3)
        self.assertEqual(LTSpice_to_float("1G"), 1e9)
        self.assertEqual(LTSpice_to_float("2.5T"), 2.5e12)

    def test_float_to_LTSpice(self):
        """Revisa con márgenes de error (por los errores asociados a los floats)
        la cercanía entre las entradas en punto flotante y su resultado como string
        formateado.
        """
        self.assertTrue(math.isclose(LTSpice_to_float(float_to_LTSpice(0.0000001)), LTSpice_to_float("100N"), rel_tol=1e-9))
        self.assertEqual(float_to_LTSpice(1234.567), "1.234567K")
        self.assertTrue(math.isclose(LTSpice_to_float(float_to_LTSpice(1.5e-15)), LTSpice_to_float("1.5f"), rel_tol=1e-9))
        self.assertTrue(math.isclose(LTSpice_to_float(float_to_LTSpice(1000000000000)), LTSpice_to_float("1T"), rel_tol=1e-9))
        self.assertEqual(float_to_LTSpice(0.000000000001), "1.0p")


if __name__ == '__main__':
    unittest.main()
