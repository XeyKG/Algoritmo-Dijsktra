# Dijkstra UNAB → UIS — Bucaramanga

Visualización interactiva del algoritmo de Dijkstra sobre la red vial real
de Bucaramanga, desde la **UNAB** (Av. 42 #48-11) hasta la **UIS** (Cra. 27 Calle 9),
usando datos reales de **OpenStreetMap** y un servidor web en tiempo real.

---

## Estructura del proyecto
dijkstra_unab_uis/
│
├── main.py # Punto de entrada
├── requirements.txt # Dependencias
├── README.md
│
├── config/
│ ├── _init_.py
│ └── settings.py # Coordenadas, parámetros globales
│
├── graph/
│ ├── _init_.py
│ ├── loader.py # Descarga el grafo desde OSM
│ └── validator.py # Valida conectividad y aristas
│
├── algorithm/
│ ├── _init_.py
│ └── dijkstra.py # Dijkstra manual + generador paso a paso
│
├── visualization/
│ ├── _init_.py
│ ├── styles.py # Colores y tamaños
│ ├── plotter.py # Imagen estática PNG (matplotlib)
│ ├── animator.py # Animación GIF paso a paso
│ ├── map_html.py # Mapa estático HTML con Folium
│ └── web_server.py # Servidor Flask + SSE en tiempo real
│
├── templates/
│ └── index.html # Interfaz web interactiva (Leaflet.js)
│
└── output/ # Archivos generados (auto-creada)
├── dijkstra_UNAB_UIS.png
├── dijkstra_animacion.gif
└── ruta_unab_uis.html

---

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd dijkstra_unab_uis
```

### 2. Crear entorno virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Uso

```bash
python main.py
```

El programa ejecuta los siguientes pasos en orden:

| Paso | Descripción | Salida |
|------|-------------|--------|
| 1 | Descarga la red vial real desde OpenStreetMap | En memoria |
| 2 | Localiza los nodos más cercanos a UNAB y UIS | Log en consola |
| 3 | Ejecuta Dijkstra con trazabilidad completa | En memoria |
| 4 | Genera imagen estática de dos paneles | `output/dijkstra_UNAB_UIS.png` |
| 5 | Genera mapa HTML con Folium | `output/ruta_unab_uis.html` |
| 6 | Inicia servidor web y abre el navegador | `http://127.0.0.1:5000` |

Para detener el servidor: `Ctrl + C`

---

## Interfaz web (`http://127.0.0.1:5000`)

Presiona **▶ Ejecutar Dijkstra** para ver el algoritmo en tiempo real sobre
el mapa de Bucaramanga.

### Leyenda de colores

| Color | Significado |
|-------|-------------|
| 🟢 Verde | Origen — UNAB |
| 🔴 Rojo | Destino — UIS |
| 🔵 Azul | Nodos explorados (ya procesados) |
| 🟠 Naranja | Frontera — cola de prioridad activa |
| ⚪ Blanco | Nodo que se está procesando ahora |
| 🟡 Amarillo | Ruta óptima (parcial → final) |

### Panel lateral

- **Distancia total** en metros
- **Nodos en la ruta** final
- **Nodos explorados** en tiempo real
- **Barra de progreso** de exploración
- **Log** con timestamps de cada evento

---

## Algoritmo — Dijkstra
Entrada: G (DiGraph OSM), origen (UNAB), destino (UIS), peso = 'length'
Salida: camino óptimo, distancias, orden de exploración

dist[todos] = ∞
dist[UNAB] = 0
cola_prioridad = [(0, UNAB)]

mientras cola no vacía:
(d, u) = extraer mínimo
si u ya visitado → continuar
marcar u como visitado
si u == UIS → detener ✓

para cada vecino v de u (respetando dirección de la calle):
nueva_dist = dist[u] + longitud(u → v)
si nueva_dist < dist[v]:
dist[v] = nueva_dist
prev[v] = u
insertar (nueva_dist, v) en cola

reconstruir camino siguiendo prev[] desde UIS → UNAB

La complejidad con cola de prioridad (heap) es **O((V + E) log V)**.

---

## Datos geográficos

| Campo | Valor |
|-------|-------|
| Fuente | OpenStreetMap vía Overpass API |
| Tipo de red | `drive` — solo calles vehiculares |
| Radio de descarga | 1600 m desde el punto central |
| Sentidos de calles | Respetados (grafo **dirigido**) |
| Peso de aristas | `length` — distancia real en metros |
| Coordenada UNAB | `7.12565, -73.11358` |
| Coordenada UIS | `7.13858, -73.12424` |

---

## Dependencias
osmnx>=1.9.0
networkx>=3.0
matplotlib>=3.8
numpy>=1.26
scikit-learn>=1.4
contextily>=1.6
folium>=0.15
flask>=3.0

---
