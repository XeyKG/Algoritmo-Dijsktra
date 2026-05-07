# Coordenadas geográficas reales
UNAB_COORD = (7.1169, -73.1053)
UIS_COORD  = (7.138786, -73.12047)
UNAB_LABEL = "UNAB"
UIS_LABEL  = "UIS"

# Parámetros OSM
GRAPH_RADIUS_M = 1600
NETWORK_TYPE   = "drive"
OSM_TIMEOUT    = 180
OSM_ENDPOINT   = "https://overpass-api.de/api/interpreter"

# Parámetros visualización estática
OUTPUT_DIR      = "output"
OUTPUT_FILENAME = "dijkstra_UNAB_UIS.png"
FIGURE_DPI      = 150

# Parámetros animación
ANIMATION_FILENAME  = "dijkstra_animacion.gif"   # gif exportable
ANIMATION_INTERVAL  = 40      # ms entre frames (menor = más rápido)
ANIMATION_STEP      = 8       # nodos explorados por frame
SHOW_LIVE           = True    # mostrar ventana en tiempo real