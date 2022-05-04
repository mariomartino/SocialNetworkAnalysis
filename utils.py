import networkx as nx

def load_node(file_name, directed, sep = "\t"):
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
        
    with open(file_name) as file:
        edge = file.readline()
        while edge != "":
            nodes = edge.replace("\n", "").split(sep)
            G.add_edge(nodes[0], nodes[1])
            edge = file.readline()

    return G

def debug_info(G, DIRECTED):
    print("Numero di nodi:", G.number_of_nodes())
    print("Numero di archi:", G.number_of_edges())
    if not DIRECTED:
        print("Numero di componenti connesse:", nx.number_connected_components(G))
    else:
        print("Grafo fortemente connesso:", nx.is_strongly_connected(G))
    