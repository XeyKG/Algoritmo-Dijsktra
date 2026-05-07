from graph.loader      import download_graph, get_nearest_nodes
from graph.validator   import ensure_edge_lengths, check_path_exists
from algorithm         import dijkstra
from visualization     import plotter
from visualization     import map_html
from visualization.web_server import run as run_server


def main():
    # 1. Cargar grafo real desde OSM
    G = download_graph()
    G = ensure_edge_lengths(G)

    # 2. Localizar nodos
    orig, dest = get_nearest_nodes(G)
    check_path_exists(G, orig, dest)

    # 3. Dijkstra completo (para imagen y HTML estático)
    result = dijkstra.run(G, orig, dest, weight='length')

    # 4. Imagen estática PNG
    plotter.render(G, result, orig, dest)

    # 5. HTML estático con folium
    map_html.render_html(G, result)

    # 6. Servidor web interactivo (abre el navegador automáticamente)
    #    ↓ Este bloquea hasta que cierres el servidor con Ctrl+C
    run_server(G, orig, dest, result, port=5000)


if __name__ == "__main__":
    main()