import networkx as nx
import math
import random
import itertools as it
from joblib import Parallel, delayed
import time

from utils import load_node, debug_info

# Optimal algorithm. There are two implementations for both directed and undirected graph.

def undirected_triangles(G, sample=None):
    triangles = 0
    parallel = True

    if sample is None:
        parallel = False
        sample = G.nodes()

    for u in sample:
        for v in G[u]:
            for w in G[u]:
                if w in G[v]:
                    triangles += 1
    if not parallel:
        triangles = int(triangles / 6)
    return triangles

def directed_triangles(G, sample=None):
    triangles = 0
    parallel = True

    if sample is None:
        parallel = False
        sample = G.nodes()

    for u in sample:
        for v in G[u]:
            for w in G[v]:
                if u in G[w] and u != w and v != u and w != v:
                    triangles += 1

    if not parallel:
        triangles = int(triangles / 3)
    return triangles

# Parallel Algorithm. There are two implementations for both directed and undirected graph.

def chunks(data, size):
    idata = iter(data)
    for i in range(0, len(data), size):
        yield {k: data[k] for k in it.islice(idata, size)}

def parallel_undirected_triangles(G, j):
    triangles = 0
    with Parallel(n_jobs=j) as parallel:
        result = parallel(delayed(undirected_triangles)(G, X) for X in chunks(G.nodes(), math.ceil(len(G.nodes())/j)))
        for res in result:
            triangles += res
    return int(triangles / 6)

def parallel_directed_triangles(G, j):
    triangles = 0
    with Parallel(n_jobs=j) as parallel:
        result = parallel(delayed(directed_triangles)(G, X) for X in chunks(G.nodes(), math.ceil(len(G.nodes())/j)))
        for res in result:
            triangles += res
    return int(triangles / 3)

# Optimized algorithm. It works only for undirected graphs.

def less(G, edge):
    if G.degree(edge[0]) < G.degree(edge[1]):
        return 0
    if G.degree(edge[0]) == G.degree(edge[1]) and edge[0] < edge[1]:
        return 0
    return 1

def num_triangles(G):
    num_triangles = 0
    m = nx.number_of_edges(G)

    heavy_hitters = set()
    for u in G.nodes():
        if G.degree(u) >= math.sqrt(m):
            heavy_hitters.add(u)

    for triple in it.combinations(heavy_hitters,3):
        if G.has_edge(triple[0], triple[1]) and G.has_edge(triple[0], triple[2]) and G.has_edge(triple[2], triple[1]):
            num_triangles += 1

    for edge in G.edges():  
        if edge[0] != edge[1]:
            sel = less(G, edge)
            if edge[sel] not in heavy_hitters: 
                for i in G[edge[sel]]:  
                    if less(G, [i, edge[1-sel]]) and G.has_edge(i, edge[1-sel]) and i != edge[sel] and i != edge[1-sel]:  
                        num_triangles += 1

    return num_triangles

debug = False

DIRECTED = False
file_name = "musae_facebook_edges.csv"
# file_name = 'ca-sandi_auths.mtx'
# file_name = 'email-Eu-core.txt'
sep = " "
JOBS = 6

if __name__ == "__main__":
    G = load_node(file_name, DIRECTED, sep)
    if debug:
        debug_info(G, DIRECTED)
    start_time = time.time()
    if not DIRECTED:
        print("Numero di triangoli con algoritmo ottimale: ", undirected_triangles(G), "in", (time.time() - start_time), "s")
        start_time = time.time()
        print("Numero di triangoli con algoritmo parallelo: ", parallel_undirected_triangles(G, JOBS), "in", (time.time() - start_time), "s")
        start_time = time.time()
        print("Numero di triangoli con algoritmo ottimizzato: ", num_triangles(G), "in", (time.time() - start_time), "s")
    else:
        print("Numero di triangoli con algoritmo ottimale: ", directed_triangles(G), "in", (time.time() - start_time), "s")
        start_time = time.time()
        print("Numero di triangoli con algoritmo parallelo: ", parallel_directed_triangles(G, JOBS), "in", (time.time() - start_time), "s")

