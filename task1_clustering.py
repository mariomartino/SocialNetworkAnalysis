import networkx as nx
import random
import time

import numpy as np
from utils import debug_info, load_node
from priorityq import PriorityQueue
import random
from scipy.sparse import linalg

# Bottom-Up Approach. It works for undirected. It seems it must be tested on directed graph. A termination condition is not present.

def hierarchical(G):
    """Computes two clusters by following a bottom up approach.

    Args:
        G (networkx.Graph): The graph the algorithm must compute the clusters of
    """
    pq = PriorityQueue()
    for u in G.nodes():
        for v in G.nodes():
            if u != v:
                if (u, v) in G.edges() or (v, u) in G.edges():
                    pq.add(frozenset([frozenset([u]), frozenset([v])]), 0)
                else:
                    pq.add(frozenset([frozenset([u]), frozenset([v])]), 1)

    
    for u in G.nodes():
        clusters = set(frozenset([u]) for u in G.nodes())

    done = False
    while not done:
        s = list(pq.pop())
        clusters.remove(s[0])
        clusters.remove(s[1])

        for w in clusters:
            e1 = pq.remove(frozenset([s[0], w]))
            e2 = pq.remove(frozenset([s[1], w]))
            if e1 == 0 or e2 == 0:
                pq.add(frozenset([s[0] | s[1], w]), 0)
            else:
                pq.add(frozenset([s[0] | s[1], w]), 1)

        clusters.add(s[0] | s[1])

        print(clusters)
        a = input("Do you want to continue? (y/n) ")
        if a == "n":
            done = True


# Two Means Algorithm. It should work on both directed and undirected graphs.
# The algorithm has been changed in order to manage not connected graphs.

def two_means(G):
    """The algorithm computes the clusters in the graph by applying a distance rules. Randomly select a neighbours of
    nodes yet in solution and adds it to the cluster.

    Args:
        G (networkx.Graph): The graph the algorithm must compute the clusters of
    """
    n=G.number_of_nodes()
    u = random.choice(list(G.nodes()))
    v = random.choice(list(nx.non_neighbors(G, u)))
    results = []
    cluster0 = {u}
    cluster1 = {v}
    added = 2

    while added < n:
        list_possible = [el for el in G.nodes() if el not in cluster0|cluster1 and (len( 
            set(G.neighbors(el)).intersection(cluster0)) != 0 or len(set(G.neighbors(el)).intersection(cluster1)) != 0)]
        if len(list_possible) == 0:
            results.append(cluster0)
            results.append(cluster1)
            u = random.choice(list(el for el in G.nodes() if el not in list(results[i] for i in range(len(results)))))
            v = random.choice(list(nx.non_neighbors(G, u)))
            cluster0 = {u}
            cluster1 = {v}
            added += 2
            continue
        x = random.choice(list_possible)
        if len(set(G.neighbors(x)).intersection(cluster0)) != 0:
            cluster0.add(x)
            added+=1
        elif len(set(G.neighbors(x)).intersection(cluster1)) != 0:
            cluster1.add(x)
            added+=1

    results.extend([cluster0, cluster1])
    
    print(results)
    for i in range(len(results)):
        print(len(results[i]))


# Betweenness Algorithm. 

def betweenness(G):
    """The algorithm computes the betweenness of the nodes by computing BFS starting from all nodes.

    Args:
        G (networkx.Graph): The graph the algorithm must compute the clusters of

    Returns:
        dict, dict: Dictionary containing the edge betweenness and the node betweenness respectively
    """
    edge_btw={frozenset(e):0 for e in G.edges()}
    node_btw={i:0 for i in G.nodes()}

    for s in G.nodes():
        tree=[]
        spnum={i:0 for i in G.nodes()} 
        parents={i:[] for i in G.nodes()} 
        distance={i:-1 for i in G.nodes()} 
        eflow={frozenset(e):0 for e in G.edges()} 
        vflow={i:1 for i in G.nodes()} 

        #BFS
        queue=[s]
        spnum[s]=1
        distance[s]=0
        while queue != []:
            c=queue.pop(0)
            tree.append(c)
            for i in G[c]:
                if distance[i] == -1: 
                    queue.append(i)
                    distance[i]=distance[c]+1
                if distance[i] == distance[c]+1: 
                    spnum[i]+=spnum[c]
                    parents[i].append(c)

        while tree != []:
            c=tree.pop()
            for i in parents[c]:
                eflow[frozenset({c,i})]+=vflow[c] * (spnum[i]/spnum[c]) 
                vflow[i]+=eflow[frozenset({c,i})]
                edge_btw[frozenset({c,i})]+=eflow[frozenset({c,i})] 
            if c != s:
                node_btw[c]+=vflow[c] 

    return edge_btw,node_btw

# Girman-Newman Algorithm. A termination condition is not present. It works but the betweenness computation require an huge amount of time.

def girman_newman(G):
    """Computes the clusters of the graph passed as parameter by using the Girman-Newman algorithm.

    Args:
        G (networkx.Graph): The graph the algorithm must compute the clusters of

    Returns:
        list: List of connected components of modified graph
    """
    graph=G.copy() 
    done = False
    while not done:
        eb, nb = betweenness(graph)
        edge = None
        bet = -1
        for i in eb.keys():
            if eb[i] > bet:
                edge=i
                bet = eb[i]
        graph.remove_edge(*list(edge))
        print(list(nx.connected_components(graph)))
        a = input("Do you want to continue? (y/n) ")
        if a == "n":
            done = True

    return list(nx.connected_components(graph))

# Spectral Algorithm working on Laplacian. It works for both directed and undirected graph. It's the only method that exploit direction information.

def spectral(G, directed):
    """The function computes the clusters by working on Laplacian Matrix.

    Args:
        G (networkx.Graph): The graph we must compute the clusters of
        directed (bool): True if G is directed, else False.

    Returns:
        tuple: Tuple containing the two clusters computed by the algorithm.
    """
    MIN_NUMBER_ELEMENTS = 1000
    nodes=sorted(G.nodes())

    if not directed:
        L = nx.laplacian_matrix(G, nodes).asfptype()
    else:
        L = nx.directed_laplacian_matrix(G, nodes)

    w, eigenvectors = linalg.eigsh(L, 15, which="SM")

    active_clusters = []
    solution = []
    iterazione = 1
    
    active_clusters.append(set(nodes))
    
    while (len(active_clusters) > 0 and iterazione < 15):
        new_active_clusters = []
        for c in active_clusters:
            c1 = set()
            c2 = set()
            for node in c:
                if eigenvectors[int(node),iterazione] > 0:
                    c1.add(node)
                else:
                    c2.add(node)
            if len(c1) < MIN_NUMBER_ELEMENTS and len(c1) > 0:
                solution.append(c1)
            elif len(c1) != 0:
                new_active_clusters.append(c1)
            if len(c2) < MIN_NUMBER_ELEMENTS and len(c2) > 0:
                solution.append(c2)
            elif len(c2) != 0:
                new_active_clusters.append(c2)
        active_clusters = new_active_clusters
        iterazione += 1

    solution.extend(active_clusters)
    return len(solution), [nx.average_clustering(G, nodes=solution[i]) for i in range(5)]

debug = False

file_name, sep, DIRECTED = "musae_facebook_edges.csv", ",", False
file_name, sep, DIRECTED = "ca-sandi_auths.mtx", " ", False
file_name, sep, DIRECTED = "email-Eu-core.txt", " ", True
file_name, sep, DIRECTED = "Cit-HepTh.txt", "/t", True

if __name__ == "__main__":
    G = load_node(file_name, DIRECTED, sep)
    if debug:
        debug_info(G, DIRECTED)
    start_time = time.time()
    print("Clustering gerarchico: ", hierarchical(G), "in", (time.time() - start_time), "s")
    start_time = time.time()
    print("Clustering two means:", two_means(G.to_undirected()), "in", (time.time() - start_time), "s")
    start_time = time.time()
    print("Clustering con Girman-Newman", girman_newman(G.to_undirected()), "in", (time.time() - start_time), "s")
    start_time = time.time()
    print("Clustering con matrice Laplaciana", spectral(G, DIRECTED), "in", (time.time() - start_time), "s")