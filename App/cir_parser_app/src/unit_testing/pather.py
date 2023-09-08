import os

def print_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            print(file_path)

# Ruta de la carpeta que quieres explorar
directory_path = r'C:\Users\ACER\Documents\Proyecto_viejo_abstractas\reponuevo\proyecto-circuitos-perturbados-con-qucs'

# Llama a la función para imprimir los archivos
print_files_in_directory(directory_path)
