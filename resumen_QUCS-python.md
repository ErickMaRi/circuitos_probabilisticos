## Información relevante para lidiar con el uso de QUCS y python

```python
import subprocess

# Definir los componentes del circuito
R = 1e3  # Resistencia de 1 kOhm
C = 1e-6  # Condensador de 1 uF

# Generar el netlist
netlist = f"""
* Circuito RC simple
R1 in out {R}
C1 out 0 {C}
Vin in 0 AC 1V
.tran 0.1ms 10ms
.end
"""

# Escribir el netlist en un archivo
with open('rc.cir', 'w') as f:
    f.write(netlist)

# Ejecutar la simulación en QUCS
subprocess.run(['qucsator', '-i', 'rc.cir', '-o', 'rc.dat'])

# Extraer los resultados de la simulación
with open('rc.dat', 'r') as f:
    for line in f:
        if line.startswith('V(out)'):
            _, _, _, vout = line.split()
            print(f"Vout = {vout} V")
```

Este script define un circuito RC con una resistencia de 1 kOhm y un condensador de 1 uF, y genera un netlist para el circuito. Luego, escribe el netlist en un archivo, ejecuta una simulación en QUCS utilizando la herramienta de línea de comandos `qucsator` y extrae la tensión de salida del circuito.
Referencias:
- [QUCS - Quite Universal Circuit Simulator](https://qucs.sourceforge.io/)
- [QUCSATOR](https://github.com/Qucs/qucsator)

## PYTHON-QUCS
Existe una librería llamada python-qucs que debería servir como una interfaz con la cual extraer información, pero parece ser despreciada:
- [PYTHON-QUCS](https://github.com/zonca/python-qucs)
