import networkx as nx
import math
import random
import itertools as it
from joblib import Parallel, delayed
import time
from utils import debug_info, load_node

# Optimal and Sampling. Funziona sia per grafi diretti che grafi non diretti.


def diameter(G, sample=None):
    """This function computes the grah diameter by launching a BFS on nodes in parameter 'sample'. If 'sample' is None
    the BFS is computed starting from all nodes in graph.

    Args:
        G (networkx.Graph): The graph of which the function must compute the diameter
        sample (list, optional): The list of nodes from which the BFS starts. Defaults to None.

    Returns:
        int: The diameter of the graph
    """
    diam = 0
    if sample is None:
        sample = G.nodes()

    connected_components = nx.strongly_connected_components(G) if nx.is_directed(G) else nx.connected_components(G)
    connected_components = list(connected_components)
    connected_components.sort(key=len, reverse=True)

    for comp in connected_components:
        n = len(comp)
        if n < diam:
            continue
        for u in comp.intersection(sample):
            udiam = 0
            clevel = [u]
            visited = set([u])
            while len(visited)  < n:
                nlevel = []
                while(len(clevel) > 0):
                    c = clevel.pop()
                    for v in G[c]:
                        if v not in visited and v in comp:
                            visited.add(v)
                            nlevel.append(v)
                clevel = nlevel
                udiam += 1
            if udiam > diam:
                diam = udiam
    
    return diam


# Parallel Implementation. Funziona sia per grafi diretti che grafi non diretti.


def chunks(data, size):
    """Splits the iterable 'data' parameter in blocks of 'size' elements.

    Args:
        data (iterable): The set the function must split
        size (int): The size of returned blocks

    Yields:
        dict: Dictionary containing a single block
    """
    idata = iter(data)
    for i in range(0, len(data), size):
        yield {k: data[k] for k in it.islice(idata, size)}


def parallel_diam(G, j):
    """Computes diameter by operating on different cores in parallel

    Args:
        G (networkx.Graph): The graph on which we must compute diameter
        j (int): The number of processes the function creates

    Returns:
        int: The diameter of the graph
    """
    diam = 0
    with Parallel(n_jobs=j) as parallel:
        result = parallel(delayed(diameter)(G, X) for X in chunks(G.nodes(), math.ceil(len(G.nodes())/j)))
        for res in result:
            if res > diam:
                diam = res
    return diam


# Ad-Hoc Implementation. Vale solo per i grafi indiretti, valutare implementazione aggiuntiva.


def stream_diam(G):
    """A function approximating the diameter computation

    Args:
        G (networkx.Graph): The graph on which we must compute diameter

    Returns:
        int: The approximated diameter of the graph
    """
    step = 0
    R = {v:  G.degree(v) for v in G.nodes()}
    done = False

    while not done:
        done = True
        for edge in G.edges():
            if R[edge[0]] != R[edge[1]]:
                R[edge[0]] = max(R[edge[0]], R[edge[1]])
                R[edge[1]] = max(R[edge[0]], R[edge[1]])
                done = False
        step += 1

    return step

# Ad Hoc Implementation that executes BFS on only nodes in biggest connected components (strongly if directed). The implementation is valid for both directed and undirected graphs.

def optimized_diameter(G, percentage=0.2, directed=False):
    """Diameter computation by sampling nodes that are in biggest connected components.

    Args:
        G (networkx.Graph): The graph on which we must compute diameter
        percentage (float, optional): The percentage of nodes included in sampling. Defaults to 0.2.
        directed (bool, optional): The graph is directed or not. Defaults to False.

    Returns:
        int: The diameter of the graph
    """
    if directed:
        components = list(nx.strongly_connected_components(G))
    else:
        components = list(nx.connected_components(G))
    components.sort(key=len, reverse=True)
    Gset = []
    current = 0
    while len(Gset) < int(percentage*G.number_of_nodes()):
        Gset.extend(list(components[current]))
        current += 1
    
    diam = diameter(G, sample = Gset)

    return diam


debug = True

DIRECTED = True
# file_name = "musae_facebook_edges.csv"
file_name = "Cit-HepTh.txt"
# file_name = "ca-sandi_auths.mtx"
sep = "\t"
SAMPLE = 0.8
JOBS = 6

if __name__ == "__main__":
    G = load_node(file_name, DIRECTED, sep)
    if debug:
        debug_info(G, DIRECTED)
    start_time = time.time()
    print("Diametro ottimale: ", diameter(G), "in", (time.time() - start_time), "s")
    start_time = time.time()
    nodes_sample = random.choices([*G.nodes()], k = int(SAMPLE * G.number_of_nodes()))
    print("Diametro con tasso di sampling", SAMPLE * 100, ":", diameter(G, nodes_sample), "in", (time.time() - start_time), "s")
    start_time = time.time()
    print("Diametro con implementazione parallela e", JOBS, "jobs:", parallel_diam(G, JOBS), "in", (time.time() - start_time), "s")
    start_time = time.time()
    print("Diametro con nuova implementazione ad-hoc:", optimized_diameter(G, directed=DIRECTED), "in", (time.time() - start_time), "s")
    if not DIRECTED:
        start_time = time.time()
        print("Diametro con implementazione ad-hoc:", stream_diam(G), "in", (time.time() - start_time), "s")
