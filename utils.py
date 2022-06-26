import networkx as nx

def load_node(file_name, directed, sep = "\t"):
    """The function read graph informations from file and generate a networkx Graph

    Args:
        file_name (string): The name of the file for the informations loading
        directed (bool): True if the graph is directed, else False
        sep (str, optional): Separator between nodes in the file. Defaults to "\t".

    Returns:
        networkx.Graph: The generated graph
    """
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
    """Function printing the informations of the graph to show the correctness of graph loading

    Args:
        G (network.Graph): The graph we compute informations on
        DIRECTED (bool): True if G is directed, else False
    """
    print("Numero di nodi:", G.number_of_nodes())
    print("Numero di archi:", G.number_of_edges())
    if not DIRECTED:
        print("Numero di componenti connesse:", nx.number_connected_components(G))
    else:
        print("Grafo fortemente connesso:", nx.is_strongly_connected(G))
    