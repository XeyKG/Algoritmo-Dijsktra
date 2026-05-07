import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DijkstraResult:
    distances:         Dict[int, float]
    previous:         Dict[int, Optional[int]]
    exploration_order: List[int]
    path:             List[int]
    total_distance:   float


def run(G, source: int, target: int, weight: str = 'length') -> DijkstraResult:
    """Dijkstra completo — retorna resultado final."""
    dist = {n: float('inf') for n in G.nodes()}
    prev = {n: None         for n in G.nodes()}
    dist[source] = 0.0
    visited = set()
    exploration_order = []
    pq = [(0.0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        exploration_order.append(u)

        if u == target:
            break

        for v in G.successors(u):
            edge_data = G.get_edge_data(u, v)
            w = min(e.get(weight, 1) for e in edge_data.values())
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))

    path = _reconstruct_path(prev, source, target)

    print(f"[dijkstra] ✓ Ruta: {len(path)} nodos | "
          f"Distancia: {dist[target]:.0f} m | "
          f"Explorados: {len(exploration_order)}")

    return DijkstraResult(
        distances=dist,
        previous=prev,
        exploration_order=exploration_order,
        path=path,
        total_distance=dist[target]
    )


def run_stepwise(G, source: int, target: int, weight: str = 'length'):
    """
    Generador paso a paso para animación.
    Cada yield entrega el estado actual del algoritmo.
    """
    dist     = {n: float('inf') for n in G.nodes()}
    prev     = {n: None         for n in G.nodes()}
    dist[source] = 0.0
    visited  = set()
    frontier = set()
    frontier.add(source)
    pq = [(0.0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue

        visited.add(u)
        frontier.discard(u)

        partial_path = _reconstruct_path(prev, source, u)

        yield {
            "current":      u,
            "visited":      set(visited),
            "frontier":     set(frontier),
            "partial_path": partial_path,
            "dist":         dict(dist),
            "done":         u == target,
        }

        if u == target:
            break

        for v in G.successors(u):
            edge_data = G.get_edge_data(u, v)
            w = min(e.get(weight, 1) for e in edge_data.values())
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                frontier.add(v)
                heapq.heappush(pq, (new_dist, v))


def _reconstruct_path(prev: dict, source: int, target: int) -> List[int]:
    """Reconstruye el camino desde target hasta source siguiendo prev[]."""
    path = []
    cur  = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path if (path and path[0] == source) else []