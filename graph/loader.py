import osmnx as ox
import pyproj
from config.settings import (
    UNAB_COORD, UIS_COORD,
    GRAPH_RADIUS_M, NETWORK_TYPE,
    OSM_TIMEOUT, OSM_ENDPOINT
)


def configure_osmnx():
    ox.settings.timeout = OSM_TIMEOUT
    ox.settings.overpass_endpoint = OSM_ENDPOINT


def download_graph():
    """Descarga el grafo vial real desde OSM centrado entre UNAB y UIS."""
    configure_osmnx()
    center_lat = (UNAB_COORD[0] + UIS_COORD[0]) / 2
    center_lon = (UNAB_COORD[1] + UIS_COORD[1]) / 2

    print(f"[loader] Descargando grafo OSM (radio={GRAPH_RADIUS_M}m)...")

    # Forzar CRS UTM zona 18N (cubre Bucaramanga exactamente)
    # EPSG:32618 = WGS 84 / UTM zone 18N
    ox.settings.default_crs = "EPSG:4326"

    G = ox.graph_from_point(
        (center_lat, center_lon),
        dist=GRAPH_RADIUS_M,
        dist_type='bbox',        # ← usar bbox en lugar de buffer circular
        network_type=NETWORK_TYPE,
        simplify=True
    )

    print(f"[loader] ✓ {G.number_of_nodes()} nodos | {G.number_of_edges()} aristas")
    return G


def get_nearest_nodes(G):
    """Retorna los nodos OSM más cercanos a UNAB y UIS."""
    orig = ox.distance.nearest_nodes(G, UNAB_COORD[1], UNAB_COORD[0])
    dest = ox.distance.nearest_nodes(G, UIS_COORD[1],  UIS_COORD[0])
    print(f"[loader] Nodo UNAB: {orig} | Nodo UIS: {dest}")
    return orig, dest