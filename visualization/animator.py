import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
import contextily as ctx
from matplotlib.lines import Line2D

from algorithm.dijkstra import run_stepwise, DijkstraResult
from config.settings import (
    OUTPUT_DIR, ANIMATION_FILENAME,
    ANIMATION_INTERVAL, ANIMATION_STEP,
    SHOW_LIVE, UNAB_LABEL, UIS_LABEL
)
from visualization.styles import *


def _build_frames(G, orig, dest):
    """Agrupa los pasos del generador en frames según ANIMATION_STEP."""
    frames = []
    buffer = None
    for i, state in enumerate(run_stepwise(G, orig, dest, weight='length')):
        buffer = state
        if i % ANIMATION_STEP == 0 or state["done"]:
            frames.append(state)
    # Asegurar que el frame final siempre esté incluido
    if buffer and (not frames or frames[-1] is not buffer):
        frames.append(buffer)
    return frames


def render_animation(G, result: DijkstraResult, orig: int, dest: int):
    """
    Genera animación estilo Waze:
      - Fondo de mapa real (contextily/OpenStreetMap tiles)
      - Nodos coloreados según estado: visitado / frontera / ruta / inicio / fin
      - Aristas de la ruta parcial actualizadas en tiempo real
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── Proyectar grafo a Web Mercator (EPSG:3857) para tiles de mapa ──
    import osmnx as ox
    G_proj = ox.project_graph(G, to_crs="EPSG:3857")
    pos_proj = {n: (G_proj.nodes[n]['x'], G_proj.nodes[n]['y'])
                for n in G_proj.nodes()}

    # ── Pre-calcular frames ─────────────────────────────────────────────
    print("[animator] Calculando frames...")
    frames = _build_frames(G, orig, dest)
    print(f"[animator] {len(frames)} frames generados")

    # ── Configurar figura ───────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 14), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_aspect('equal')
    ax.axis('off')

    # Límites del mapa
    xs = [pos_proj[n][0] for n in G_proj.nodes()]
    ys = [pos_proj[n][1] for n in G_proj.nodes()]
    pad_x = (max(xs) - min(xs)) * 0.04
    pad_y = (max(ys) - min(ys)) * 0.04
    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)

    # Añadir tiles de mapa base (OpenStreetMap)
    try:
        ctx.add_basemap(ax, crs="EPSG:3857",
                        source=ctx.providers.CartoDB.DarkMatter,
                        zoom=15, alpha=0.85)
        print("[animator] ✓ Mapa base cargado (CartoDB Dark Matter)")
    except Exception:
        try:
            ctx.add_basemap(ax, crs="EPSG:3857",
                            source=ctx.providers.OpenStreetMap.Mapnik,
                            zoom=15, alpha=0.75)
            print("[animator] ✓ Mapa base cargado (OpenStreetMap)")
        except Exception as e:
            print(f"[animator] Sin mapa base (sin internet): {e}")

    # ── Dibujar grafo estático (calles base tenues) ─────────────────────
    all_edges_x, all_edges_y = [], []
    for u, v in G_proj.edges():
        if u in pos_proj and v in pos_proj:
            x1, y1 = pos_proj[u]; x2, y2 = pos_proj[v]
            all_edges_x += [x1, x2, None]
            all_edges_y += [y1, y2, None]

    ax.plot(all_edges_x, all_edges_y,
            color='#334466', linewidth=0.4, alpha=0.5, zorder=2)

    # ── Capas dinámicas (se actualizan por frame) ───────────────────────
    # Aristas exploradas
    explored_lines, = ax.plot([], [], color=COLOR_EXPLORED,
                              linewidth=1.2, alpha=0.6, zorder=3)
    # Aristas frontera
    frontier_lines, = ax.plot([], [], color='#ff9900',
                              linewidth=1.5, alpha=0.8, zorder=4)
    # Ruta parcial
    route_lines, = ax.plot([], [], color=COLOR_PATH,
                           linewidth=3.5, alpha=0.95,
                           zorder=6, solid_capstyle='round')
    # Nodos explorados
    explored_scatter = ax.scatter([], [], c=COLOR_EXPLORED,
                                  s=18, alpha=0.7, zorder=5, edgecolors='none')
    # Nodos frontera
    frontier_scatter = ax.scatter([], [], c='#ff9900',
                                  s=30, alpha=0.9, zorder=6, edgecolors='none')
    # Nodo actual
    current_scatter = ax.scatter([], [], c='#ffffff',
                                 s=90, zorder=8, edgecolors='#ffdd00',
                                 linewidths=2)

    # Marcadores fijos UNAB y UIS
    if orig in pos_proj:
        ox_p, oy_p = pos_proj[orig]
        ax.scatter([ox_p], [oy_p], c=COLOR_ORIGIN, s=280,
                   zorder=10, edgecolors='white', linewidths=2)
        ax.annotate(f"  {UNAB_LABEL}", (ox_p, oy_p),
                    color='white', fontsize=11, fontweight='bold', zorder=11,
                    bbox=dict(boxstyle='round,pad=0.3', fc='#003322',
                              ec=COLOR_ORIGIN, alpha=0.85))

    if dest in pos_proj:
        dx_p, dy_p = pos_proj[dest]
        ax.scatter([dx_p], [dy_p], c=COLOR_DEST, s=280,
                   zorder=10, edgecolors='white', linewidths=2)
        ax.annotate(f"  {UIS_LABEL}", (dx_p, dy_p),
                    color='white', fontsize=11, fontweight='bold', zorder=11,
                    bbox=dict(boxstyle='round,pad=0.3', fc='#330011',
                              ec=COLOR_DEST, alpha=0.85))

    # ── HUD: título + info dinámica ─────────────────────────────────────
    ax.set_title('Dijkstra en tiempo real  —  UNAB → UIS  |  Bucaramanga',
                 color='white', fontsize=13, fontweight='bold', pad=12)

    info_text = ax.text(
        0.01, 0.01, '', transform=ax.transAxes,
        color='#ccddff', fontsize=9, va='bottom',
        bbox=dict(boxstyle='round', facecolor='#0d1117', alpha=0.85, edgecolor='#445')
    )

    legend_elements = [
        Line2D([0],[0], marker='o', color='w', markerfacecolor=COLOR_ORIGIN,
               markersize=10, label=f'Origen ({UNAB_LABEL})', linewidth=0),
        Line2D([0],[0], marker='o', color='w', markerfacecolor=COLOR_DEST,
               markersize=10, label=f'Destino ({UIS_LABEL})', linewidth=0),
        Line2D([0],[0], marker='o', color='w', markerfacecolor=COLOR_PATH,
               markersize=8,  label='Ruta parcial', linewidth=0),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='#ff9900',
               markersize=7,  label='Frontera (cola)', linewidth=0),
        Line2D([0],[0], marker='o', color='w', markerfacecolor=COLOR_EXPLORED,
               markersize=7,  label='Explorados', linewidth=0),
    ]
    ax.legend(handles=legend_elements, loc='upper right',
              facecolor='#1a1a2e', edgecolor='#445',
              labelcolor='white', fontsize=9)

    # ── Función de actualización por frame ──────────────────────────────
    def update(frame_idx):
        state = frames[frame_idx]
        visited  = state["visited"]
        frontier = state["frontier"]
        partial  = state["partial_path"]
        current  = state["current"]
        done     = state["done"]

        # Aristas exploradas
        ex, ey = [], []
        for u, v in G_proj.edges():
            if u in visited and v in visited:
                if u in pos_proj and v in pos_proj:
                    x1,y1=pos_proj[u]; x2,y2=pos_proj[v]
                    ex += [x1,x2,None]; ey += [y1,y2,None]
        explored_lines.set_data(ex, ey)

        # Aristas frontera (conectan visitados con frontera)
        fx, fy = [], []
        for u, v in G_proj.edges():
            if u in visited and v in frontier:
                if u in pos_proj and v in pos_proj:
                    x1,y1=pos_proj[u]; x2,y2=pos_proj[v]
                    fx += [x1,x2,None]; fy += [y1,y2,None]
        frontier_lines.set_data(fx, fy)

        # Ruta parcial
        if len(partial) > 1:
            rx = [pos_proj[n][0] for n in partial if n in pos_proj]
            ry = [pos_proj[n][1] for n in partial if n in pos_proj]
            route_lines.set_data(rx, ry)
        else:
            route_lines.set_data([], [])

        # Scatter nodos explorados
        exp_pts = np.array([pos_proj[n] for n in visited
                            if n in pos_proj and n not in (orig, dest)])
        if len(exp_pts):
            explored_scatter.set_offsets(exp_pts)
        else:
            explored_scatter.set_offsets(np.empty((0, 2)))

        # Scatter nodos frontera
        fro_pts = np.array([pos_proj[n] for n in frontier
                            if n in pos_proj])
        if len(fro_pts):
            frontier_scatter.set_offsets(fro_pts)
        else:
            frontier_scatter.set_offsets(np.empty((0, 2)))

        # Nodo actual
        if current in pos_proj and not done:
            current_scatter.set_offsets([pos_proj[current]])
        else:
            current_scatter.set_offsets(np.empty((0, 2)))

        # HUD info
        dist_m = state["dist"].get(current, 0)
        status = "✓ RUTA ENCONTRADA" if done else "Explorando..."
        info_text.set_text(
            f"Estado: {status}\n"
            f"Nodos explorados: {len(visited)}/{G.number_of_nodes()}\n"
            f"Dist. acumulada nodo actual: {dist_m:.0f} m\n"
            f"Frame: {frame_idx + 1}/{len(frames)}"
        )

        return (explored_lines, frontier_lines, route_lines,
                explored_scatter, frontier_scatter, current_scatter, info_text)

    # ── Crear animación ─────────────────────────────────────────────────
    ani = animation.FuncAnimation(
        fig, update,
        frames=len(frames),
        interval=ANIMATION_INTERVAL,
        blit=True,
        repeat=False
    )

    # Guardar GIF
    gif_path = os.path.join(OUTPUT_DIR, ANIMATION_FILENAME)
    print(f"[animator] Guardando GIF → {gif_path}  (puede tardar ~30s)...")
    ani.save(gif_path, writer='pillow', fps=25, dpi=100)
    print(f"[animator] ✓ GIF guardado")

    # Mostrar ventana interactiva
    if SHOW_LIVE:
        print("[animator] Mostrando animación en vivo (cierra la ventana para continuar)...")
        plt.show()

    plt.close()
    return ani