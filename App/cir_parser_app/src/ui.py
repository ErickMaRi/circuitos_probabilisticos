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
import os
from file_operations import read_cir_file
from parameter_perturbation import parameter_perturbator
from simulation import run_simulations
from plotting import estimate_distribution, plot_distributions, plot_density
from ltspice_converter import LTSpice_to_float, float_to_LTSpice

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import threading
import re

class ElementDialog(simpledialog.Dialog):

    """
    Cuadro de diálogo utilizado para actualizar los valores de la tabla.

    Este diálogo se muestra cuando el usuario da doble click a una entrada de la tabla.
    Permite modificar la distribución y la escala de perturbación para un elemento específico.

    Attributes:
        element (str): Nombre del elemento seleccionado.
        dist (str): Tipo de distribución actual.
        scale (float): Escala de la distribución actual.
        ui (UI): Referencia a la instancia principal de la interfaz de usuario.
        line (int): Número de línea del elemento en el archivo original.
    """

    def __init__(self, master, ui, element, dist, scale, line):
        self.element = element
        self.dist = dist
        self.scale = scale
        self.ui = ui
        self.line = line
        super().__init__(master)

    def body(self, master):

        """
        Crea y dispone los widgets del cuerpo del diálogo.

        Args:
            master (tk.Widget): Widget padre para los elementos del diálogo.

        Returns:
            tk.Widget: Widget que debe tener el foco inicial.
        """

        ttk.Label(master, text="Element:").grid(row=0)
        ttk.Label(master, text=self.element).grid(row=0, column=1)

        ttk.Label(master, text="Distribution:").grid(row=1)
        self.dist_entry = ttk.Combobox(master, values=["uniform", "normal"])
        self.dist_entry.set(self.dist)
        self.dist_entry.grid(row=1, column=1)

        ttk.Label(master, text="Scale:").grid(row=2)
        self.scale_entry = ttk.Entry(master)
        self.scale_entry.insert(tk.END, f"{self.scale:.2%}")
        self.scale_entry.grid(row=2, column=1)

        return self.dist_entry

    def apply(self):

        """
        Aplica los cambios realizados en el diálogo.

        Este método se llama cuando el usuario confirma los cambios.
        Actualiza los valores de distribución y escala en la instancia de UI.
        """

        self.dist = self.dist_entry.get()
        self.scale = float(self.scale_entry.get().strip('%')) / 100
        self.ui.cir_dict[self.line]['dist'] = self.dist
        self.ui.cir_dict[self.line]['scale'] = self.scale


class UI:

    """
    Clase que contiene la interfaz gráfica principal de la aplicación.

    Esta clase maneja la carga de archivos .cir, la generación de archivos perturbados,
    la simulación de circuitos y la visualización de resultados.

    Attributes:
        current_file (str): Ruta del archivo .cir actualmente cargado.
        num_files (int): Número de archivos a generar en la perturbación.
        num_timesteps (int): Número de pasos de tiempo para la simulación.
        num_bins (int): Número de bins para los gráficos de densidad.
        running_simulation (bool): Indica si una simulación está en progreso.
        generating_files (bool): Indica si se están generando archivos.
        simulation_results (dict): Resultados de la simulación.
        cir_dict (dict): Diccionario con la información del archivo .cir.
        dist (dict): Diccionario con las distribuciones de perturbación por línea.
        scale (dict): Diccionario con las escalas de perturbación por línea.
        simulation_counter (int): Contador de simulaciones ejecutadas.
        root (tk.Tk): Ventana principal de la aplicación.
        selected_output (str): Salida seleccionada para visualización.
        available_outputs (list): Lista de salidas disponibles para visualización.
    """

    def __init__(self):
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
        self.simulation_counter = 0
        self.root = None
        self.selected_output = ""  # Attribute to store selected output
        self.available_outputs = []  # Attribute to store available outputs

    def on_table_click(self, event):
        """
        Maneja el evento de doble click en un elemento de la tabla.

        Abre un diálogo para editar las propiedades de perturbación del elemento seleccionado.

        Args:
            event (tk.Event): Evento de doble click.
        """

        item = self.table.focus()
        element = self.table.item(item)['values'][0]
        dist = self.table.item(item)['values'][2]
        scale = float(self.table.item(item)['values'][3].strip('%')) / 100

        line = self.get_line_from_name(element)
        dialog = ElementDialog(self.root, self, element, dist, scale, line)
        self.cir_dict[line]['dist'] = dialog.dist
        self.cir_dict[line]['scale'] = dialog.scale

        self.table.delete(item)
        self.table.insert('', 'end', values=(
            element, self.cir_dict[line]['value'], self.cir_dict[line]['dist'], f"{self.cir_dict[line]['scale']:.2%}"))


    def get_line_from_name(self, name):

        """
        Obtiene el número de línea de un elemento a partir de su nombre.

        Args:
            name (str): Nombre del elemento.

        Returns:
            int or None: Número de línea del elemento si se encuentra, None si no se encuentra.
        """

        for line, element in self.cir_dict.items():
            if element['name'] == name:
                return line
        return None

    def load_file(self):

        """
        Carga un archivo .cir seleccionado por el usuario.

        Actualiza el diccionario de circuito y la tabla de elementos.
        """

        filename = filedialog.askopenfilename()
        if filename:
            self.current_file = filename
            self.cir_dict = read_cir_file(self.current_file)
            self.dist = {key: self.cir_dict[key]['dist'] for key in self.cir_dict.keys()}
            self.scale = {key: self.cir_dict[key]['scale'] for key in self.cir_dict.keys()}
            self.populate_table()

    def populate_table(self):

        """
        Llena la tabla con los elementos del circuito cargado.

        Muestra el nombre, magnitud, distribución y escala de cada elemento.
        """

        for row in self.table.get_children():
            self.table.delete(row)
        for key in self.cir_dict:
            element = self.cir_dict[key]['name']
            magnitude = self.cir_dict[key]['value']
            distribution = self.cir_dict[key]['dist']
            scale = self.cir_dict[key]['scale']
            self.table.insert('', 'end', values=(
                element, magnitude, distribution, f"{scale:.2%}"))

    def generate_files(self):

        """
        Genera archivos perturbados basados en el archivo .cir cargado.

        Utiliza un hilo separado para no bloquear la interfaz de usuario.
        """

        if not self.current_file:
            messagebox.showwarning("Advertencia", "Por favor, carga un archivo .cir primero.")
            return
        if self.generating_files:
            messagebox.showwarning("Advertencia", "La generación de archivos ya está en progreso.")
            return

        def generate():
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
            messagebox.showinfo("Info", "Archivos generados con éxito.")

        thread = threading.Thread(target=generate)
        thread.start()

    def update_simulation_counter(self, count):

        """
        Actualiza el contador de simulaciones en la interfaz.

        Args:
            count (int): Número actual de simulaciones completadas.
        """

        self.root.after(0, lambda: self.simulation_counter_label.config(text=f"Simulaciones ejecutadas: {count}"))

    def run_simulations(self):

        """
        Ejecuta las simulaciones de los archivos generados.

        Utiliza un hilo separado para no bloquear la interfaz de usuario.
        Actualiza la lista de salidas disponibles al finalizar.
        """

        if self.running_simulation:
            messagebox.showwarning("Advertencia", "La simulación ya está en progreso.")
            return

        def run_simulation():            
            self.running_simulation = True
            self.simulation_results, self.available_outputs = run_simulations(
                "new_cir_files", 
                prog=True, 
                update_callback=self.update_simulation_counter
            )
            self.running_simulation = False
            self.output_selection['values'] = self.available_outputs

        thread = threading.Thread(target=run_simulation)
        thread.start()

    def plot_distributions(self):

        """
        Genera y muestra gráficos de distribución para la salida seleccionada.

        Utiliza los resultados de la simulación para crear los gráficos.
        """

        if not self.simulation_results:
            messagebox.showwarning("Advertencia", "No se han ejecutado las simulaciones.")
            return

        selected_output = self.output_selection.get()
        if not selected_output:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una salida para plotear.")
            return

        filtered_results = {file: {'time': data['time'], selected_output: data[selected_output]}
                            for file, data in self.simulation_results.items() if selected_output in data}

        fitted_distributions = estimate_distribution(filtered_results, num_timesteps=self.num_timesteps)
        plot_distributions(fitted_distributions)

    def plot_density(self):

        """
        Genera y muestra gráficos de densidad para la salida seleccionada.

        Utiliza los resultados de la simulación para crear los gráficos.
        """

        if not self.simulation_results:
            messagebox.showwarning("Advertencia", "No se han ejecutado las simulaciones.")
            return

        selected_output = self.output_selection.get()
        if not selected_output:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una salida para plotear.")
            return

        filtered_results = {file: {'time': data['time'], selected_output: data[selected_output]}
                            for file, data in self.simulation_results.items() if selected_output in data}

        plot_density(filtered_results, num_timesteps=self.num_timesteps, num_bins=self.num_bins)

    def create_ui(self):

        """
        Crea y configura la interfaz gráfica principal.

        Inicializa todos los widgets y frames de la aplicación.
        """

        self.root = tk.Tk()
        self.root.title("CIR Parser UI")

        # Ensure the icon file is in the correct path
        icon_path = os.path.join(os.path.dirname(__file__), "icon/icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)  # Set your icon path here
            except Exception as e:
                print(f"Error setting icon: {e}")
        else:
            print(f"Icon file not found: {icon_path}")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        load_button = ttk.Button(top_frame, text="Cargar Archivo", command=self.load_file)
        load_button.pack(side=tk.LEFT, padx=5)

        info_button = ttk.Button(top_frame, text="Info Netlist", command=self.show_netlist_info)
        info_button.pack(side=tk.LEFT, padx=5)

        generate_button = ttk.Button(top_frame, text="Generar Archivos", command=self.generate_files)
        generate_button.pack(side=tk.LEFT, padx=5)
        simulate_button = ttk.Button(top_frame, text="Simular", command=self.run_simulations)
        simulate_button.pack(side=tk.LEFT, padx=5)

        output_selection_label = ttk.Label(top_frame, text="Seleccionar Salida para Plotear:")
        output_selection_label.pack(side=tk.LEFT, padx=5)
        self.output_selection = ttk.Combobox(top_frame)
        self.output_selection.pack(side=tk.LEFT, padx=5)

        plot_distributions_button = ttk.Button(top_frame, text="Gráfico de Distribuciones", command=self.plot_distributions)
        plot_distributions_button.pack(side=tk.LEFT, padx=5)
        plot_density_button = ttk.Button(top_frame, text="Gráfico de Densidad", command=self.plot_density)
        plot_density_button.pack(side=tk.LEFT, padx=5)

        self.simulation_counter_label = ttk.Label(main_frame, text="Simulaciones ejecutadas: 0")
        self.simulation_counter_label.pack(side=tk.TOP, pady=5)

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.table = ttk.Treeview(table_frame, columns=("Elemento", "Magnitud", "Distribución", "Escala"), show="headings")
        self.table.heading("Elemento", text="Elemento")
        self.table.heading("Magnitud", text="Magnitud")
        self.table.heading("Distribución", text="Distribución")
        self.table.heading("Escala", text="Escala")
        self.table.pack(fill=tk.BOTH, expand=True)
        self.table.bind('<Double-1>', self.on_table_click)

        options_frame = ttk.LabelFrame(main_frame, text="Opciones")
        options_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        self.create_options_frame(options_frame)

        self.root.mainloop()

    def create_options_frame(self, frame):

        """
        Crea y configura el frame de opciones en la interfaz.

        Args:
            frame (ttk.Frame): Frame donde se colocarán las opciones.
        """

        num_files_label = ttk.Label(frame, text="Cantidad de Archivos:")
        num_files_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        num_files_entry = ttk.Entry(frame, width=10)
        num_files_entry.insert(tk.END, "10")
        num_files_entry.grid(row=0, column=1, padx=10, pady=5)
        num_files_entry.bind("<FocusOut>", lambda e: self.update_num_files(num_files_entry.get()))

        num_timesteps_label = ttk.Label(frame, text="Número de Timesteps:")
        num_timesteps_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        num_timesteps_entry = ttk.Entry(frame, width=10)
        num_timesteps_entry.insert(tk.END, "200")
        num_timesteps_entry.grid(row=1, column=1, padx=10, pady=5)
        num_timesteps_entry.bind("<FocusOut>", lambda e: self.update_num_timesteps(num_timesteps_entry.get()))

        num_bins_label = ttk.Label(frame, text="Número de Bins:")
        num_bins_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        num_bins_entry = ttk.Entry(frame, width=10)
        num_bins_entry.insert(tk.END, "200")
        num_bins_entry.grid(row=2, column=1, padx=10, pady=5)
        num_bins_entry.bind("<FocusOut>", lambda e: self.update_num_bins(num_bins_entry.get()))


    def show_netlist_info(self):
        """
        Muestra una ventana emergente con información detallada sobre el netlist cargado.
        
        Esta función analiza el contenido del archivo .cir cargado y extrae información
        relevante como el nombre del netlist, subcircuitos, cantidad de elementos,
        temperatura, timestep y tiempo de simulación.
        """
        if not self.current_file:
            messagebox.showwarning("Advertencia", "Por favor, carga un archivo .cir primero.")
            return

        # Crear una nueva ventana emergente
        info_window = tk.Toplevel(self.root)
        info_window.title("Información del Netlist")
        info_window.geometry("400x300")

        # Crear un widget de texto para mostrar la información
        info_text = tk.Text(info_window, wrap=tk.WORD, padx=10, pady=10)
        info_text.pack(fill=tk.BOTH, expand=True)

        # Analizar el archivo .cir
        with open(self.current_file, 'r', encoding="UTF-8") as file:
            content = file.read()

        # Extraer información
        netlist_name = self.current_file.split('/')[-1].split('\\')[-1]  # Obtener el nombre del archivo
        subcircuits = len(re.findall(r'\.SUBCKT', content))
        elements = len(re.findall(r'^[RCLVIX]', content, re.MULTILINE))
        temp_match = re.search(r'\.TEMP\s+(\d+)', content)
        temp = temp_match.group(1) if temp_match else "No especificada"
        tran_match = re.search(r'\.TRAN\s+([\d.]+\w*)\s+([\d.]+\w*)', content)
        timestep, sim_time = (tran_match.groups() if tran_match else ("No especificado", "No especificado"))

        # Formatear y mostrar la información
        info = f"""Nombre del Netlist: {netlist_name}
Subcircuitos: {subcircuits}
Cantidad de Elementos: {elements}
Temperatura: {temp}
Timestep: {timestep}
Tiempo de Simulación: {sim_time}
Timesteps mínimos recomendados: {str(round(LTSpice_to_float(sim_time)/LTSpice_to_float(timestep)))}
"""
        info_text.insert(tk.END, info)
        info_text.config(state=tk.DISABLED)  # Hacer el texto de solo lectura


    def update_num_files(self, value):

        """
        Actualiza el número de archivos a generar.

        Args:
            value (str): Nuevo valor para num_files.
        """

        self.num_files = int(value)

    def update_num_timesteps(self, value):

        """
        Actualiza el número de pasos de tiempo para la simulación.

        Args:
            value (str): Nuevo valor para num_timesteps.
        """

        self.num_timesteps = int(value)

    def update_num_bins(self, value):

        """
        Actualiza el número de bins para los gráficos de densidad.

        Args:
            value (str): Nuevo valor para num_bins.
        """

        self.num_bins = int(value)

    def run(self):

        """
        Inicia la ejecución de la interfaz gráfica.

        Este método debe ser llamado para mostrar y ejecutar la aplicación.
        """

        self.create_ui()


if __name__ == "__main__":
    ui = UI()
    ui.run()
