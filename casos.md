## Casos de Uso

### 1. Cargar archivo de netlist del circuito
- Descripción: Permite al usuario cargar un archivo de netlist que contiene la descripción del circuito.
- Actores: Usuario
- Flujo principal:
  1. El usuario selecciona la opción de cargar archivo de netlist en la interfaz de usuario.
  2. El sistema muestra un cuadro de diálogo para seleccionar el archivo.
  3. El usuario selecciona el archivo de netlist y lo carga en el software.
  4. El sistema verifica la validez del archivo y lo procesa para obtener los parámetros del circuito.

### 2. Ajustar parámetros del circuito
- Descripción: Permite al usuario ajustar los parámetros de los elementos del circuito para realizar simulaciones con diferentes valores.
- Actores: Usuario
- Flujo principal:
  1. El usuario accede a la opción de ajustar parámetros en la interfaz de usuario.
  2. El sistema muestra una lista de elementos del circuito y sus valores actuales.
  3. El usuario selecciona un elemento y modifica su valor según sus necesidades.
  4. El sistema actualiza los parámetros del circuito con los valores modificados.

### 3. Ejecutar simulaciones del circuito
- Descripción: Permite al usuario realizar múltiples simulaciones del circuito con pequeñas perturbaciones en los valores de los parámetros.
- Actores: Usuario
- Flujo principal:
  1. El usuario solicita al software ejecutar las simulaciones del circuito.
  2. El sistema genera pequeñas perturbaciones en los valores de los parámetros del circuito según una distribución probabilística uniforme.
  3. Para cada simulación, el sistema utiliza los parámetros perturbados y ejecuta la simulación.
  4. El sistema recopila los resultados de cada simulación y los almacena para su posterior análisis.

### 4. Mostrar resultados y distribuciones probabilísticas
- Descripción: Permite al usuario visualizar los resultados de las simulaciones realizadas y las distribuciones probabilísticas asociadas a los parámetros del circuito.
- Actores: Usuario
- Flujo principal:
  1. El usuario solicita al software mostrar los resultados de las simulaciones.
  2. El sistema presenta los resultados de cada simulación en forma de gráficos, tablas u otros elementos visuales.
  3. El usuario puede explorar los resultados y obtener información sobre el comportamiento del circuito con las perturbaciones en los parámetros.
  4. El sistema también muestra las distribuciones probabilísticas asociadas a los parámetros perturbados.

### 5. Guardar configuración del circuito
- Descripción: Permite al usuario guardar la configuración actual del circuito, incluyendo los parámetros ajustados y las perturbaciones aplicadas.
- Actores: Usuario
- Flujo principal:
  1. El usuario selecciona la opción de guardar configuración en la interfaz de usuario.
  2. El sistema guarda la configuración actual del circuito en un archivo o base de datos.
  3. El usuario proporciona un nombre y ubicación para guardar el archivo.
  4. El sistema confirma que la configuración se ha guardado correctamente.

### 6. Cargar configuración previa del circuito
- Descripción: Permite al usuario cargar una configuración previamente guardada del circuito para retomar simulaciones anteriores.
- Actores: Usuario
- Flujo principal:
  1. El usuario selecciona la opción de cargar configuración en la interfaz de usuario.
  2. El sistema muestra una lista de archivos o registros de configuraciones previas.
  3. El usuario selecciona el archivo o registro deseado y carga la configuración en el software.
  4. El sistema restaura la configuración del circuito, incluyendo los parámetros y perturbaciones guardadas.

### 7. Exportar resultados de simulaciones
- Descripción: Permite al usuario exportar los resultados de las simulaciones realizadas en un formato específico, como CSV o Excel.
- Actores: Usuario
- Flujo principal:
  1. El usuario solicita al software exportar los resultados de las simulaciones.
  2. El sistema genera un archivo en el formato especificado, que incluye los datos de las simulaciones y las distribuciones probabilísticas asociadas.
  3. El usuario selecciona una ubicación y proporciona un nombre para guardar el archivo exportado.
  4. El sistema confirma que el archivo se ha exportado correctamente.

### 8. Visualizar circuito en formato gráfico
- Descripción: Permite al usuario visualizar el circuito cargado en un formato gráfico para facilitar su comprensión y análisis.
- Actores: Usuario
- Flujo principal:
  1. El usuario selecciona la opción de visualizar circuito en formato gráfico.
  2. El sistema muestra una representación gráfica del circuito, incluyendo los elementos y conexiones.
  3. El usuario puede hacer zoom, moverse por el circuito y obtener información detallada sobre los componentes.
  4. El sistema proporciona herramientas de análisis visual, como mediciones de voltaje o corriente en diferentes puntos del circuito
