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

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import threading

class ElementDialog(simpledialog.Dialog):
    def __init__(self, master, ui, element, dist, scale, line):
        self.element = element
        self.dist = dist
        self.scale = scale
        self.ui = ui
        self.line = line
        super().__init__(master)

    def body(self, master):
        ttk.Label(master, text="Element:").grid(row=0)
        ttk.Label(master, text=self.element).grid(row=0, column=1)

        ttk.Label(master, text="Distribution:").grid(row=1)
        self.dist_entry = ttk.Combobox(master, values=["uniform", "normal"])
        self.dist_entry.set(self.dist)
        self.dist_entry.grid(row=1, column=1)

        ttk.Label(master, text="Scale:").grid(row=2)
        self.scale_entry = ttk.Entry(master)
        self.scale_entry.insert(tk.END, str(self.scale))
        self.scale_entry.grid(row=2, column=1)

        return self.dist_entry

    def apply(self):
        self.dist = self.dist_entry.get()
        self.scale = float(self.scale_entry.get())
        self.ui.dist[self.line] = self.dist
        self.ui.scale[self.line] = self.scale


class UI:
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
        item = self.table.focus()
        element = self.table.item(item)['values'][0]
        dist = self.table.item(item)['values'][2]
        scale = self.table.item(item)['values'][3]

        line = self.get_line_from_name(element)
        dialog = ElementDialog(self.root, self, element, dist, scale, line)
        self.dist[line] = dialog.dist
        self.scale[line] = dialog.scale

        self.table.delete(item)
        self.table.insert('', 'end', values=(
            element, self.cir_dict[line]['value'], self.dist[line], self.scale[line]))

    def get_line_from_name(self, name):
        for line, element in self.cir_dict.items():
            if element['name'] == name:
                return line
        return None

    def load_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.current_file = filename
            self.cir_dict = read_cir_file(self.current_file)
            self.dist = {key: 'uniform' for key in self.cir_dict.keys()}
            self.scale = {key: 0.03 for key in self.cir_dict.keys()}
            self.populate_table()

    def populate_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
        for key in self.cir_dict:
            element = self.cir_dict[key]['name']
            magnitude = self.cir_dict[key]['value']
            distribution = self.dist[key]
            scale = self.scale[key]
            self.table.insert('', 'end', values=(
                element, magnitude, distribution, scale))

    def generate_files(self):
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
        self.simulation_counter_label.config(text=f"Simulaciones ejecutadas: {count}")

    def run_simulations(self):
        if self.running_simulation:
            messagebox.showwarning("Advertencia", "La simulación ya está en progreso.")
            return

        def run_simulation():
            self.running_simulation = True
            self.simulation_results, self.available_outputs = run_simulations("new_cir_files", prog=True)
            self.running_simulation = False
            self.update_simulation_counter(len(self.simulation_results))
            self.output_selection['values'] = self.available_outputs

        thread = threading.Thread(target=run_simulation)
        thread.start()

    def plot_distributions(self):
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

    def update_num_files(self, value):
        self.num_files = int(value)

    def update_num_timesteps(self, value):
        self.num_timesteps = int(value)

    def update_num_bins(self, value):
        self.num_bins = int(value)

    def run(self):
        self.create_ui()


if __name__ == "__main__":
    ui = UI()
    ui.run()
