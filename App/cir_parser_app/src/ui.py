"""ui.py contiene las clases asociadas a la interfaz gráfica principal de la aplicación,
la clase asociada a un cuadro de diálogo y una función que maneja la línea a la que pertenece
el elemento de circuito:
        get_line_from_name(name, dict): Busca en un diccionario formateado para contener la línea,
        magnitud y nombre de cada elemento, la línea a la que pertenece uno buscado por su nombre.

        ElementDialog(simpledialog.Dialog): Cuadro de diálogo utilizado para actualizar los valores
        de la tabla, cuando el usuario de da doble click a una entrada de la tabla.

        UI: Clase que contiene la interfaz gráfica principal, los botones para cargar un archivo cir,
        generar archivos según los parámetros, simular los archivos generados y producir los plots.
        También contiene la tabla con los elementos (resistencias, capacitores e inductores), las 
        propiedades de la forma en la que se perturban los valores de los elementos (tipo de
        distribución, escala de la distribución) es controlable al darle doble click a una entrada
        de la tabla. Además contiene la capacidad de controlar parámetros universales de la simulación.
"""
from file_operations import *
from ltspice_converter import *
from parameter_perturbation import *
from simulation import *
from plotting import *

import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import messagebox
from tkinter import ttk
import threading


def get_line_from_name(name, dict):
    """Función que toma como entrada el nombre de un elemento y toma un diccionario
    en el formato que produce cir_parser, retorna la línea a la que pertenece el 
    elemento.

    Args:
        name (_str_): _String que contiene el elemento de circuito, por su nombre._
        dict (_dict_): _Diccionario en el formato generado por cir_parser, contiene
        la magnitud y nombre de cada elemento, por línea en la que lo encontró parser._

    Returns:
        línea _int_: _Línea en la que se encontraba el elemento que estábamos buscando_
    """
    for line, element in dict.items():
        if element['name'] == name:
            return line
    return None  # Return None if the name wasn't found


class ElementDialog(simpledialog.Dialog):
    """_Ventana que contiene un diálogo y los parámetros a configurar en la
    línea de la tabla seleccionada, se instancia con ElementDialog(self.root,
    self, element, dist, scale, line), para ingresar desde la ventana en la que se abre,
    las variables de la clase que le contiene, los atributos de la interfáz gráfica,
    el elemento al que se le dió click (nombre, distribución, escala y línea de la que
    proviene)._

    Args:
        simpledialog (_type_): _description_
    """

    def __init__(self, master, ui, element, dist, scale, line):
        # Se inicializan los elementos que conforman el mensaje del cuadro de texto,
        # su uso es en el código que captura el evento de darle click a una fila de
        # la tabla de la interfaz.
        self.element = element
        self.dist = dist
        self.scale = scale
        self.ui = ui
        self.line = line
        super().__init__(master)

    def body(self, master):
        """El cuerpo del cuadro de texto.

        Args:
            master: _Parámetro que especifíca la ventana de
            la que proviene este cuadro de diálogo_
        """

        # El nombre del elemento:
        tk.Label(master, text="Element:").grid(row=0)  # El texto
        tk.Label(master, text=self.element).grid(row=0, column=1)  # El valor

        # El combobox para seleccionar la distribución:
        tk.Label(master, text="Distribution:").grid(row=1)
        self.dist_entry = ttk.Combobox(master, values=["uniform", "normal"])
        self.dist_entry.set(self.dist)
        self.dist_entry.grid(row=1, column=1)

        # El cuadro de texto con el cual definir la escala.
        tk.Label(master, text="Scale:").grid(row=2)
        self.scale_entry = tk.Entry(master)
        self.scale_entry.insert(tk.END, str(self.scale))
        self.scale_entry.grid(row=2, column=1)

        return self.dist_entry  # initial focus

    def apply(self):
        """Actualiza los valores de la clase del cuadro de texto,
        según los ingresados por el usuario.
        """
        self.dist = self.dist_entry.get()
        self.scale = float(self.scale_entry.get())
        self.ui.dist[self.line] = self.dist
        self.ui.scale[self.line] = self.scale


class UI:

    def __init__(self):
        """_Clase contenedora de la interfaz gráfica y las funciones necesarias para operar
    las librerías, contiene:
        1-El archivo a procesar actualmente
        2-La cantidad de archivos a producir
        3-La cantidad de contenedores para el gráfico de densidad
        4-Booleano sobre el estado de la simulación, ¿Corren simulaciones?
        5-Booleano sobre el estado de la simulación, ¿Se están generando archivos?
        6-Booleano sobre el estado de la simulación, ¿Hay resultados?
        7-Diccionario con el contenido del circuito
        8-Diccionario con las distribuciones seleccionadas
        9-Diccionario con las escalas para las distribuciones seleccionadas
        10-Variable raiz, asistente con el manejo de los widgets de TkInter
        _
        """
        self.current_file = ""
        self.num_files = 10
        self.num_timesteps = 200
        self.num_bins = 200
        self.running_simulation = False
        self.generating_files = False
        self.simulation_results = None
        self.cir_dict = {}
        self.dist = {}
        self.scale = {}
        self.root = None

    def on_table_click(self, event):
        """Al darle click a una entrada de la tabla se usan las entradas en la
        misma para construir un cuadro de diálogo que asiste para actualizar los
        valores de los diccionario.

        Args:
            event (_type_): _description_
        """
        # Los valores de la tabla en este instante en esa entrada.
        item = self.table.focus()
        element = self.table.item(item)['values'][0]
        dist = self.table.item(item)['values'][2]
        scale = self.table.item(item)['values'][3]

        print(
            f'El elemento {str(element)}, pasa de tener una distribución {str(dist)}, a escala {str(scale)}.')

        # Construimos el cuadro de diálogo, que va a terminar conteniendo los valores que vamos a ingresar.
        line = get_line_from_name(element, self.cir_dict)
        dialog = ElementDialog(self.root, self, element, dist, scale, line)
        # Ya el usuario cerró la ventana, actualizamos los valores en UI
        self.dist[line] = dialog.dist
        self.scale[line] = dialog.scale
        print(
            f'A una distribución {str(self.dist[line])}, a escala {str(self.scale[line])}.')
        # Actualizamos la tabla
        self.table.delete(item)  # Eliminamos los contenidos actuales

        # Insert a new item with the updated data
        self.table.insert('', 'end', values=(
            element, self.cir_dict[line]['value'], self.dist[line], self.scale[line]))

    def load_file(self):
        """Función dedicada a cargar un archivo .cir y leerlo,
        read_cir_file crea un nuevo diccionario que sirve para
        poblar las entradas de la tabla.
        """
        # Setup las ventanas para buscar un archivo:
        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename()
        # Si hay archivo
        if filename:
            self.current_file = filename
            print(f"Archivo cargado: {self.current_file}")
            self.cir_dict = read_cir_file(
                self.current_file)  # Poblamos cir_dict

            # Inicializamos valores por defecto para las distribuciones y las escalas
            self.dist = {key: 'uniform' for key in self.cir_dict.keys()}
            self.scale = {key: 0.03 for key in self.cir_dict.keys()}

            # Limpiamos los contenidos de la tabla
            for row in self.table.get_children():
                self.table.delete(row)

            # Para poblarla con lo que nos dictan los diccionarios.
            for key in self.cir_dict:
                element = self.cir_dict[key]['name']
                magnitude = self.cir_dict[key]['value']
                distribution = self.dist[key]
                scale = self.scale[key]
                self.table.insert('', 'end', values=(
                    element, magnitude, distribution, scale))

    def generate_files(self):
        """Genera una cantidad definida por la UI, de archivos .cir
        que tienen sus parámetros alterados probabilísticamente segun lo
        configurado en la interfaz gráfica.
        """
        if not self.current_file:
            messagebox.showwarning(
                "Advertencia", "Por favor, carga un archivo .cir primero.")
            return
        if self.generating_files:
            messagebox.showwarning(
                "Advertencia", "La generación de archivos ya está en progreso.")
            return

        def generate():
            """Genera una cantidad de archivos pasando los argumentos de la
            clase UI para ejecutar read_cir_files.
            """
            self.generating_files = True
            cir_dict = read_cir_file(self.current_file)
            parameter_perturbator(
                cir_dict,
                dist=self.dist,
                scale=self.scale,
                n_files=self.num_files,
                input_file_name=self.current_file,
                debug=False
            )
            self.generating_files = False

        thread = threading.Thread(target=generate)
        thread.start()

    def run_simulations(self):
        """Ejecuta las simulaciones de todos los archivos contenidos en
        new_cir_files, para construir los resultados de las simulaciones.
        """
        if self.running_simulation:
            messagebox.showwarning(
                "Advertencia", "La simulación ya está en progreso.")
            return

        def run_simulation():
            self.running_simulation = True
            self.simulation_results = run_simulations(
                "new_cir_files", prog=True)
            self.running_simulation = False

        thread = threading.Thread(target=run_simulation)
        thread.start()

    def plot_distributions(self):
        """Genera el plot de distribuciones probabilísticas asociadas a los resultados de
        las simulaciones.
        """
        if not self.simulation_results:
            messagebox.showwarning(
                "Advertencia", "No se han ejecutado las simulaciones.")
            return

        fitted_distributions = estimate_distribution(
            self.simulation_results, num_timesteps=self.num_timesteps)
        plot_distributions(fitted_distributions)

    def plot_density(self):
        """Genera el plot de densidades en escala logarítmica, asociadas a los resultados de
        las simulaciones.
        """
        if not self.simulation_results:
            messagebox.showwarning(
                "Advertencia", "No se han ejecutado las simulaciones.")
            return

        plot_density(self.simulation_results,
                     num_timesteps=self.num_timesteps, num_bins=self.num_bins)

    def create_ui(self):
        """Dibuja la interfaz gráfica.
        """
        # Ahora habrá root
        root = tk.Tk()
        root.title("CIR Parser UI")

        # Desde el root se define que la interfaz tiene frame
        frame = tk.Frame(root)
        frame.pack(pady=20)

        # TABLA:
        # Creamos un frame para la tabla
        table_frame = tk.Frame(root)
        table_frame.pack(pady=20)

        # Creamos la tabla contenedora de los elementos, sus magnitudes y perturbaciones.
        self.table = ttk.Treeview(table_frame, columns=(
            "Elemento", "Magnitud", "Distribución", "Escala"), show="headings")
        self.table.heading("Elemento", text="Elemento")
        self.table.heading("Magnitud", text="Magnitud")
        self.table.heading("Distribución", text="Distribución")
        self.table.heading("Escala", text="Escala")
        self.table.pack()

        # Si le damos doble click 1 a una entrada de la tabla...
        self.table.bind('<Double-1>', self.on_table_click)
        # Actualizamos los valores de la tabla


        # BOTONES:
        # Dibujamos los botones.
        load_button = tk.Button(
            frame, text="Cargar Archivo", command=self.load_file)
        load_button.pack(side=tk.LEFT, padx=10)

        generate_button = tk.Button(
            frame, text="Generar Archivos", command=self.generate_files)
        generate_button.pack(side=tk.LEFT, padx=10)

        simulate_button = tk.Button(
            frame, text="Simular", command=self.run_simulations)
        simulate_button.pack(side=tk.LEFT, padx=10)

        plot_distributions_button = tk.Button(
            frame, text="Gráfico de Distribuciones", command=self.plot_distributions)
        plot_distributions_button.pack(side=tk.LEFT, padx=10)

        plot_density_button = tk.Button(
            frame, text="Gráfico de Densidad", command=self.plot_density)
        plot_density_button.pack(side=tk.LEFT, padx=10)

        options_frame = tk.LabelFrame(root, text="Opciones")
        options_frame.pack(pady=20)

        # OPCIONES:
        # Dibujamos las opciones universales como cantidad de archivos, timesteps, bins.
        num_files_label = tk.Label(options_frame, text="Cantidad de Archivos:")
        num_files_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        num_files_entry = tk.Entry(options_frame, width=10)
        num_files_entry.insert(tk.END, "10")
        num_files_entry.grid(row=0, column=1, padx=10, pady=5)
        num_files_description = tk.Label(
            options_frame, text="Número de archivos a generar.")
        num_files_description.grid(
            row=0, column=2, padx=10, pady=5, sticky=tk.W)

        num_timesteps_label = tk.Label(
            options_frame, text="Número de Timesteps:")
        num_timesteps_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        num_timesteps_entry = tk.Entry(options_frame, width=10)
        num_timesteps_entry.insert(tk.END, "200")
        num_timesteps_entry.grid(row=3, column=1, padx=10, pady=5)
        num_timesteps_description = tk.Label(
            options_frame, text="Número de pasos de tiempo para interpolar y estimar las distribuciones.")
        num_timesteps_description.grid(
            row=3, column=2, padx=10, pady=5, sticky=tk.W)

        num_bins_label = tk.Label(options_frame, text="Número de Bins:")
        num_bins_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.E)
        num_bins_entry = tk.Entry(options_frame, width=10)
        num_bins_entry.insert(tk.END, "200")
        num_bins_entry.grid(row=4, column=1, padx=10, pady=5)
        num_bins_description = tk.Label(
            options_frame, text="Número de contenedores (bins) para la representación de la densidad.")
        num_bins_description.grid(
            row=4, column=2, padx=10, pady=5, sticky=tk.W)

        # Definimos funciones que asisten a actualizar los parámetros universales
        # en el main loop.

        def update_num_files():
            self.num_files = int(num_files_entry.get())

        def update_num_timesteps():
            self.num_timesteps = int(num_timesteps_entry.get())

        def update_num_bins():
            self.num_bins = int(num_bins_entry.get())

        num_files_entry.bind("<FocusOut>", lambda e: update_num_files())
        num_timesteps_entry.bind(
            "<FocusOut>", lambda e: update_num_timesteps())
        num_bins_entry.bind("<FocusOut>", lambda e: update_num_bins())

        # Corre el backend de Tk
        root.mainloop()


    def run(self):
        #Corre el código para configurar y de hecho dibujar la interfaz gráfica.
        self.create_ui()

if __name__ == "__main__":
    ui = UI()
    ui.run()