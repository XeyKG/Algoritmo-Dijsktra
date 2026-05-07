import networkx as nx


def ensure_edge_lengths(G):
    """Garantiza que todas las aristas tengan el atributo 'length'."""
    import numpy as np
    for u, v, k, data in G.edges(keys=True, data=True):
        if 'length' not in data:
            lat1, lon1 = G.nodes[u]['y'], G.nodes[u]['x']
            lat2, lon2 = G.nodes[v]['y'], G.nodes[v]['x']
            R = 6371000
            a = (np.sin(np.radians((lat2 - lat1) / 2)) ** 2 +
                 np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) *
                 np.sin(np.radians((lon2 - lon1) / 2)) ** 2)
            G[u][v][k]['length'] = round(2 * R * np.arcsin(np.sqrt(a)), 1)
    return G


def check_path_exists(G, orig, dest):
    """Lanza excepción si no hay camino entre origen y destino."""
    if not nx.has_path(G, orig, dest):
        raise ValueError(
            f"[validator] No existe camino entre {orig} y {dest}. "
            "Verifica que los nodos estén en el mismo componente conexo."
        )
    print("[validator] ✓ Camino existe entre UNAB y UIS")