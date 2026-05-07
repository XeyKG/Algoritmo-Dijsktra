import os
import folium
from config.settings import (
    UNAB_COORD, UIS_COORD, UNAB_LABEL, UIS_LABEL, OUTPUT_DIR
)
from algorithm.dijkstra import DijkstraResult


HTML_FILENAME = "ruta_unab_uis.html"


def render_html(G, result: DijkstraResult):
    """Genera mapa interactivo HTML estilo Waze con Folium."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    center = [
        (UNAB_COORD[0] + UIS_COORD[0]) / 2,
        (UNAB_COORD[1] + UIS_COORD[1]) / 2
    ]

    mapa = folium.Map(location=center, zoom_start=15,
                      tiles='CartoDB dark_matter')

    # ── Todas las calles del grafo (tenues) ──────────────────────────
    for u, v in G.edges():
        x1, y1 = G.nodes[u]['x'], G.nodes[u]['y']
        x2, y2 = G.nodes[v]['x'], G.nodes[v]['y']
        folium.PolyLine(
            [(y1, x1), (y2, x2)],
            color='#334466', weight=1, opacity=0.4
        ).add_to(mapa)

    # ── Ruta óptima resaltada ─────────────────────────────────────────
    route_coords = [
        (G.nodes[n]['y'], G.nodes[n]['x'])
        for n in result.path
    ]
    folium.PolyLine(
        route_coords,
        color='#ffdd00', weight=6, opacity=0.95,
        tooltip=f"Ruta óptima: {result.total_distance:.0f} m"
    ).add_to(mapa)

    # ── Nodos explorados (círculos pequeños azules) ───────────────────
    path_set = set(result.path)
    for node in result.exploration_order:
        if node not in path_set:
            lat = G.nodes[node]['y']
            lon = G.nodes[node]['x']
            folium.CircleMarker(
                location=(lat, lon),
                radius=3,
                color='#4488ff',
                fill=True,
                fill_opacity=0.6,
                tooltip=f"Explorado | dist: {result.distances[node]:.0f} m"
            ).add_to(mapa)

    # ── Nodos de la ruta (círculos amarillos) ─────────────────────────
    for node in result.path:
        if node not in (result.path[0], result.path[-1]):
            lat = G.nodes[node]['y']
            lon = G.nodes[node]['x']
            folium.CircleMarker(
                location=(lat, lon),
                radius=5,
                color='#ffdd00',
                fill=True,
                fill_opacity=0.9,
                tooltip=f"Ruta | dist acum: {result.distances[node]:.0f} m"
            ).add_to(mapa)

    # ── Marcador UNAB ─────────────────────────────────────────────────
    folium.Marker(
        UNAB_COORD,
        popup=folium.Popup(
            f"<b>{UNAB_LABEL}</b><br>Av. 42 #48-11<br>"
            f"<span style='color:green'>Origen</span>", max_width=200
        ),
        icon=folium.Icon(color='green', icon='university', prefix='fa')
    ).add_to(mapa)

    # ── Marcador UIS ──────────────────────────────────────────────────
    folium.Marker(
        UIS_COORD,
        popup=folium.Popup(
            f"<b>{UIS_LABEL}</b><br>Cra. 27 Calle 9<br>"
            f"<span style='color:red'>Destino</span><br>"
            f"Distancia: <b>{result.total_distance:.0f} m "
            f"({result.total_distance/1000:.2f} km)</b>", max_width=200
        ),
        icon=folium.Icon(color='red', icon='flag', prefix='fa')
    ).add_to(mapa)

    # ── Info box flotante ─────────────────────────────────────────────
    info_html = f"""
    <div style="position:fixed; bottom:30px; left:30px; z-index:9999;
                background:#1a1a2e; color:white; padding:12px 16px;
                border-radius:8px; border:1px solid #445;
                font-family:monospace; font-size:13px;">
        <b>Dijkstra — {UNAB_LABEL} → {UIS_LABEL}</b><br>
        Distancia: {result.total_distance:.0f} m
                  ({result.total_distance/1000:.2f} km)<br>
        Nodos en ruta: {len(result.path)}<br>
        Nodos explorados: {len(result.exploration_order)}<br>
        Total grafo: {G.number_of_nodes()}
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(info_html))

    out_path = os.path.join(OUTPUT_DIR, HTML_FILENAME)
    mapa.save(out_path)
    print(f"[map_html] ✓ Mapa HTML guardado → {out_path}")