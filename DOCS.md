# 📚 Documentación — Algoritmo de Dijkstra

Visualización interactiva del **Algoritmo de Dijkstra** sobre grafos viales reales obtenidos de OpenStreetMap. El sistema calcula la ruta más corta entre dos puntos y la presenta mediante mapas estáticos, HTML interactivo y un servidor web local.

---

## 🚀 Cómo ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/XeyKG/Algoritmo-Dijsktra.git
cd Algoritmo-Dijsktra
```

### 2. Crear un entorno virtual

Se recomienda usar un entorno virtual para aislar las dependencias del proyecto y evitar conflictos con otros paquetes del sistema.

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate

# En Linux / macOS:
source venv/bin/activate
```

### 3. Instalar las dependencias

Con el entorno virtual activo, instala todas las dependencias listadas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

> ⚠️ La instalación puede tardar unos minutos, especialmente `osmnx` y `scikit-learn`.

### 4. Ejecutar la aplicación

```bash
python main.py
```

El programa:
1. Descarga el grafo vial de la zona configurada desde OpenStreetMap.
2. Ejecuta el algoritmo de Dijkstra entre el origen y destino configurados.
3. Genera una imagen estática del resultado en `output/`.
4. Genera un mapa interactivo en HTML en `output/`.
5. Lanza un servidor web local en `http://localhost:5000` y abre el navegador automáticamente.

Para detener el servidor, presiona `Ctrl+C` en la terminal.

---

## 🛠️ Tecnologías utilizadas

| Librería | Versión mínima | ¿Para qué se usó? |
|---|---|---|
| `osmnx` | ≥ 1.9.0 | Descarga y construcción del grafo vial real desde OpenStreetMap |
| `networkx` | ≥ 3.0 | Representación y manipulación del grafo (nodos y aristas) |
| `matplotlib` | ≥ 3.8 | Generación de la imagen estática PNG con el camino resaltado |
| `numpy` | ≥ 1.26 | Operaciones numéricas auxiliares durante el procesamiento del grafo |
| `scikit-learn` | ≥ 1.4 | Cálculo de distancias y búsqueda de nodos más cercanos |
| `contextily` | ≥ 1.6 | Tiles de mapa base (fondo geográfico) para la visualización estática |
| `folium` | ≥ 0.15 | Generación del mapa interactivo en HTML con capas sobre OpenStreetMap |
| `flask` | ≥ 3.0 | Servidor web local que sirve el mapa interactivo en el navegador |

### ¿Por qué estas herramientas?

- **`osmnx` + `networkx`**: Permiten trabajar con grafos viales del mundo real sin construirlos manualmente. `osmnx` descarga la red de calles y la convierte directamente en un grafo compatible con `networkx`.
- **`folium` + `flask`**: Juntos ofrecen una experiencia interactiva en el navegador sin necesidad de un framework frontend. `folium` genera el HTML del mapa y `flask` lo sirve localmente.
- **`matplotlib` + `contextily`**: Para producir una visualización estática exportable como imagen, con un mapa base real como fondo.
- **`scikit-learn`**: Su módulo de vecinos más cercanos (`BallTree`) permite localizar eficientemente los nodos del grafo más cercanos a las coordenadas de origen y destino.
