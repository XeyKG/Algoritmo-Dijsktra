import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

from algorithm.dijkstra import DijkstraResult
from config.settings import (
    OUTPUT_DIR, OUTPUT_FILENAME, FIGURE_DPI,
    UNAB_LABEL, UIS_LABEL
)
from visualization.styles import *


def _node_positions(G):
    return {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G.nodes()}


def _classify_nodes(G, result: DijkstraResult, orig, dest):
    path_set     = set(result.path)
    explored_set = set(result.exploration_order)
    colors, sizes = [], []
    for n in G.nodes():
        if n == orig:
            colors.append(COLOR_ORIGIN);    sizes.append(SIZE_ORIGIN)
        elif n == dest:
            colors.append(COLOR_DEST);      sizes.append(SIZE_DEST)
        elif n in path_set:
            colors.append(COLOR_PATH);      sizes.append(SIZE_PATH)
        elif n in explored_set:
            colors.append(COLOR_EXPLORED);  sizes.append(SIZE_EXPLORED)
        else:
            colors.append(COLOR_UNVISITED); sizes.append(SIZE_UNVISITED)
    return colors, sizes


def _classify_edges(G, result: DijkstraResult):
    path_edges = set(zip(result.path[:-1], result.path[1:]))
    explored   = set(result.exploration_order)
    colors, widths = [], []
    for u, v, _ in G.edges(keys=True):
        if (u, v) in path_edges:
            colors.append(COLOR_EDGE_PATH);     widths.append(WIDTH_PATH)
        elif u in explored or v in explored:
            colors.append(COLOR_EDGE_EXPLORED); widths.append(WIDTH_EXPLORED)
        else:
            colors.append(COLOR_EDGE_DEFAULT);  widths.append(WIDTH_DEFAULT)
    return colors, widths


def _legend():
    return [
        mpatches.Patch(color=COLOR_ORIGIN,    label=f'Origen ({UNAB_LABEL})'),
        mpatches.Patch(color=COLOR_DEST,      label=f'Destino ({UIS_LABEL})'),
        mpatches.Patch(color=COLOR_PATH,      label='Ruta óptima'),
        mpatches.Patch(color=COLOR_EXPLORED,  label='Explorados'),
        mpatches.Patch(color=COLOR_UNVISITED, label='No visitados'),
    ]


def _draw_full_graph(ax, G, pos, result, orig, dest):
    ax.set_facecolor(BG_COLOR)
    ax.set_title('Red vial + exploración Dijkstra',
                 color='white', fontsize=12, pad=10)

    node_colors, node_sizes = _classify_nodes(G, result, orig, dest)
    edge_colors, edge_widths = _classify_edges(G, result)

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors,
                           width=edge_widths, arrows=True, arrowsize=6,
                           alpha=0.8, connectionstyle='arc3,rad=0.05')
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax,
                            labels={orig: UNAB_LABEL, dest: UIS_LABEL},
                            font_size=9, font_color='white', font_weight='bold')
    ax.legend(handles=_legend(), loc='lower left',
              facecolor=PANEL_BG, edgecolor='#444', labelcolor='white', fontsize=9)


def _draw_route_detail(ax, G, pos, result, orig, dest):
    km = result.total_distance / 1000
    ax.set_facecolor(BG_COLOR)
    ax.set_title(f'Ruta óptima  —  {result.total_distance:.0f} m  ({km:.2f} km)',
                 color='white', fontsize=12, pad=10)

    subgraph = G.subgraph(set(result.exploration_order))
    sub_pos  = {n: pos[n] for n in subgraph.nodes()}
    path_edges = set(zip(result.path[:-1], result.path[1:]))

    edge_colors = [COLOR_EDGE_PATH if (u, v) in path_edges else '#223366'
                   for u, v, _ in subgraph.edges(keys=True)]
    edge_widths = [3.0 if c == COLOR_EDGE_PATH else 0.6 for c in edge_colors]

    nx.draw_networkx_edges(subgraph, sub_pos, ax=ax,
                           edge_color=edge_colors, width=edge_widths,
                           arrows=True, arrowsize=8, alpha=0.9,
                           connectionstyle='arc3,rad=0.05')

    node_colors, node_sizes = _classify_nodes(subgraph, result, orig, dest)
    nx.draw_networkx_nodes(subgraph, sub_pos, ax=ax,
                           node_color=node_colors, node_size=node_sizes, alpha=0.95)

    # Etiquetas con distancia acumulada en nodos del camino
    path_labels = {
        n: (f"{UNAB_LABEL}\n0 m" if n == orig
            else f"{UIS_LABEL}\n{result.total_distance:.0f} m" if n == dest
            else f"{result.distances[n]:.0f} m")
        for n in result.path
    }
    nx.draw_networkx_labels(subgraph, sub_pos, labels=path_labels, ax=ax,
                            font_size=7, font_color='white', verticalalignment='bottom')

    # Distancia por segmento sobre cada arista del camino
    for u, v in path_edges:
        if u in pos and v in pos:
            x1, y1 = pos[u]; x2, y2 = pos[v]
            seg = G[u][v][0].get('length', 0)
            ax.annotate(f"{seg:.0f}m", xy=((x1+x2)/2, (y1+y2)/2),
                        fontsize=6.5, color=COLOR_EDGE_LABEL, ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.1', fc=BG_COLOR, ec='none', alpha=0.7))

    ax.legend(handles=_legend(), loc='lower left',
              facecolor=PANEL_BG, edgecolor='#444', labelcolor='white', fontsize=9)


def render(G, result: DijkstraResult, orig: int, dest: int):
    """Genera y guarda la visualización completa (2 paneles)."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pos = _node_positions(G)

    fig, axes = plt.subplots(1, 2, figsize=(20, 14), facecolor=BG_COLOR)
    fig.suptitle(
        f'Algoritmo Dijkstra — Ruta más corta\n{UNAB_LABEL} → {UIS_LABEL}  |  Bucaramanga, Colombia',
        fontsize=16, fontweight='bold', color='white', y=0.98
    )

    _draw_full_graph(axes[0],  G, pos, result, orig, dest)
    _draw_route_detail(axes[1], G, pos, result, orig, dest)

    fig.text(0.5, 0.01,
             f"Distancia: {result.total_distance:.0f} m  ({result.total_distance/1000:.2f} km)  |  "
             f"Nodos en ruta: {len(result.path)}  |  "
             f"Explorados: {len(result.exploration_order)}  |  "
             f"Total grafo: {G.number_of_nodes()}",
             ha='center', fontsize=10, color='#aaaacc',
             bbox=dict(boxstyle='round', facecolor=PANEL_BG, alpha=0.8, edgecolor='#555'))

    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    out_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    plt.savefig(out_path, dpi=FIGURE_DPI, bbox_inches='tight', facecolor=BG_COLOR)
    plt.close()
    print(f"[plotter] ✓ Imagen guardada → {out_path}")