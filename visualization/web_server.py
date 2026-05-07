import json
import time
import threading
import webbrowser
import heapq

from flask import Flask, Response, render_template

from config.settings import UNAB_COORD, UIS_COORD, UNAB_LABEL, UIS_LABEL
from algorithm.dijkstra import DijkstraResult

app = Flask(__name__, template_folder='../templates')

# Estado global compartido entre hilos
_graph_data = {}


def init_server(G, orig: int, dest: int, result: DijkstraResult):
    """Registra el grafo y resultado para que el servidor los use."""
    _graph_data['G']      = G
    _graph_data['orig']   = orig
    _graph_data['dest']   = dest
    _graph_data['result'] = result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stream')
def stream():
    """Server-Sent Events: transmite el proceso de Dijkstra paso a paso."""
    def generate():
        G    = _graph_data['G']
        orig = _graph_data['orig']
        dest = _graph_data['dest']

        # ── Evento init: grafo completo ───────────────────────────────
        edges = []
        for u, v in G.edges():
            edges.append([
                G.nodes[u]['y'], G.nodes[u]['x'],
                G.nodes[v]['y'], G.nodes[v]['x']
            ])

        init_payload = {
            'type':        'init',
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
            'orig_node':   orig,
            'dest_node':   dest,
            'unab_lat':    UNAB_COORD[0],
            'unab_lon':    UNAB_COORD[1],
            'uis_lat':     UIS_COORD[0],
            'uis_lon':     UIS_COORD[1],
            'edges':       edges,
        }
        yield f"data: {json.dumps(init_payload)}\n\n"
        time.sleep(0.3)

        # ── Dijkstra paso a paso ──────────────────────────────────────
        dist     = {n: float('inf') for n in G.nodes()}
        prev     = {n: None         for n in G.nodes()}
        dist[orig] = 0.0
        visited  = set()
        frontier = {}      # node_id → dist tentativa
        pq       = [(0.0, orig)]
        frontier[orig] = 0.0
        exploration_order = []

        STEP = 6   # nodos por frame (ajusta velocidad)

        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue

            visited.add(u)
            frontier.pop(u, None)
            exploration_order.append(u)

            # Reconstruir ruta parcial
            partial = []
            cur = u
            while cur is not None:
                partial.append([G.nodes[cur]['y'], G.nodes[cur]['x']])
                cur = prev[cur]
            partial.reverse()

            # Nuevos vecinos que entran a la frontera
            new_frontier = []
            for v in G.successors(u):
                edge_data = G.get_edge_data(u, v)
                w = min(e.get('length', 1) for e in edge_data.values())
                nd = dist[u] + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    if v not in visited:
                        frontier[v] = nd
                        heapq.heappush(pq, (nd, v))
                        new_frontier.append([
                            G.nodes[v]['y'], G.nodes[v]['x'], v, nd
                        ])

            step_payload = {
                'type':         'step',
                'node':         u,
                'lat':          G.nodes[u]['y'],
                'lon':          G.nodes[u]['x'],
                'dist_m':       dist[u],
                'partial_path': partial,
                'new_frontier': new_frontier,
            }
            yield f"data: {json.dumps(step_payload)}\n\n"

            if u == dest:
                break

            # Control de velocidad
            if len(exploration_order) % STEP == 0:
                time.sleep(0.05)

        # ── Evento result: ruta final ─────────────────────────────────
        path = []
        cur  = dest
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()

        path_coords = [
            [G.nodes[n]['y'], G.nodes[n]['x']]
            for n in path if n in G.nodes
        ]

        result_payload = {
            'type':           'result',
            'path_coords':    path_coords,
            'path_nodes':     len(path),
            'total_dist':     dist[dest],
            'explored_nodes': len(exploration_order),
        }
        yield f"data: {json.dumps(result_payload)}\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache',
                             'X-Accel-Buffering': 'no'})


def run(G, orig: int, dest: int, result: DijkstraResult, port: int = 5000):
    """Inicia el servidor y abre el navegador automáticamente."""
    init_server(G, orig, dest, result)

    url = f"http://127.0.0.1:{port}"
    print(f"[web_server] ✓ Servidor corriendo en {url}")
    print(f"[web_server] Abriendo navegador...")

    # Abrir el navegador después de 1 segundo (esperar que Flask arranque)
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    app.run(port=port, debug=False, threaded=True)