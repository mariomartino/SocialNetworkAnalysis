import networkx as nx
import math
import random
import itertools as it
from joblib import Parallel, delayed
import time
from utils import debug_info, load_node

# Optimal and Sampling. Funziona sia per grafi diretti che grafi non diretti.


def diameter(G, sample=None):
    nodes = G.nodes()
    n = len(nodes)
    diam = 0
    if sample is None:
        sample = nodes

    i = 0
    for u in sample:
        if i % 100 == 0:
            print("Iterazione:", i)
        udiam = 0
        clevel = [u]
        visited = set(u)
        old_visited = 1
        while len(visited) < n:
            nlevel = []
            old_visited = len(visited)
            while(len(clevel) > 0):
                c = clevel.pop()
                for v in G[c]:
                    if v not in visited:
                        visited.add(v)
                        nlevel.append(v)
            if old_visited == len(visited):
              break
            clevel = nlevel
            udiam += 1
        if udiam > diam:
            diam = udiam
        i += 1

    return diam


# Parallel Implementation. Funziona sia per grafi diretti che grafi non diretti.


def chunks(data, size):
    idata = iter(data)
    for i in range(0, len(data), size):
        yield {k: data[k] for k in it.islice(idata, size)}


def parallel_diam(G, j):
    diam = 0
    # Initialize the class Parallel with the number of available process
    with Parallel(n_jobs=j) as parallel:
        # Run in parallel diameter function on each processor by passing to each processor only the subset of nodes on which it works
        result = parallel(delayed(diameter)(G, X) for X in chunks(G.nodes(), math.ceil(len(G.nodes())/j)))
        # Aggregates the results
        for res in result:
            if res > diam:
                diam = res
    return diam


# Ad-Hoc Implementation. Vale solo per i grafi indiretti, valutare implementazione aggiuntiva.


def stream_diam(G):
    step = 0
    # At the beginning, R contains for each vertex v the number of nodes that can be reached from v in one step
    R = {v:  G.degree(v) for v in G.nodes()}
    done = False

    while not done:
        done = True
        for edge in G.edges():
            # At the i-th iteration, we want that R contains for each vertex v an approximation of the number of nodes that can be reached from v in i+1 steps
            # If there is edge (u,v), then v can reach in i+1 steps at least the number of nodes that u can reach in i steps
            if R[edge[0]] != R[edge[1]]:
                R[edge[0]] = max(R[edge[0]], R[edge[1]])
                R[edge[1]] = max(R[edge[0]], R[edge[1]])
                done = False
        step += 1

    return step

debug = True

DIRECTED = True
# file_name = "musae_facebook_edges.csv"
file_name = "Cit-HepTh.txt"
sep = "\t"
SAMPLE = 0.8
JOBS = 6

if __name__ == "__main__":
    G = load_node(file_name, DIRECTED, sep)
    if debug:
        debug_info(G, DIRECTED)
    start_time = time.time()
    print("Diametro ottimale: ", diameter(G.to_undirected()), "in", (time.time() - start_time), "s")
    start_time = time.time()
    nodes_sample = random.choices([*G.nodes()], k = int(SAMPLE * G.number_of_nodes()))
    print("Diametro con tasso di sampling", SAMPLE * 100, ":", diameter(G, nodes_sample), "in", (time.time() - start_time), "s")
    start_time = time.time()
    print("Diametro con implementazione parallela e", JOBS, "jobs:", parallel_diam(G, JOBS), "in", (time.time() - start_time), "s")
    if not DIRECTED:
        start_time = time.time()
        print("Diametro con implementazione ad-hoc:", stream_diam(G), "in", (time.time() - start_time), "s")


# L'algoritmo mi ha restituito 37 per la rete di citazioni, 15 per la rete di Facebook
