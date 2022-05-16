import networkx as nx
import math
import random
import itertools as it
from joblib import Parallel, delayed
import time
from utils import debug_info, load_node
from priorityq import PriorityQueue
import random
from scipy.sparse import linalg

# Bottom-Up Approach. It works for undirected. It seems it must be tested on directed graph. A termination condition is not present.

def hierarchical(G):
    # Create a priority queue with each pair of nodes indexed by distance
    pq = PriorityQueue()
    for u in G.nodes():
        for v in G.nodes():
            if u != v:
                if (u, v) in G.edges() or (v, u) in G.edges():
                    pq.add(frozenset([frozenset([u]), frozenset([v])]), 0)
                else:
                    pq.add(frozenset([frozenset([u]), frozenset([v])]), 1)

    # Start with a cluster for each node
    
    for u in G.nodes():
        clusters = set(frozenset([u]) for u in G.nodes())

    done = False
    while not done:
        # Merge closest clusters
        s = list(pq.pop())
        clusters.remove(s[0])
        clusters.remove(s[1])

        # Update the distance of other clusters from the merged cluster
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
    n=G.number_of_nodes()
    # Choose two clusters represented by vertices that are not neighbors
    u = random.choice(list(G.nodes()))
    v = random.choice(list(nx.non_neighbors(G, u)))
    results = []
    cluster0 = {u}
    cluster1 = {v}
    added = 2

    while added < n:
        # Choose a node that is not yet in a cluster and add it to the closest cluster
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
    edge_btw={frozenset(e):0 for e in G.edges()}
    node_btw={i:0 for i in G.nodes()}

    for s in G.nodes():
        # Compute the number of shortest paths from s to every other node
        tree=[] #it lists the nodes in the order in which they are visited
        spnum={i:0 for i in G.nodes()} #it saves the number of shortest paths from s to i
        parents={i:[] for i in G.nodes()} #it saves the parents of i in each of the shortest paths from s to i
        distance={i:-1 for i in G.nodes()} #the number of shortest paths starting from s that use the edge e
        eflow={frozenset(e):0 for e in G.edges()} #the number of shortest paths starting from s that use the edge e
        vflow={i:1 for i in G.nodes()} #the number of shortest paths starting from s that use the vertex i. It is initialized to 1 because the shortest path from s to i is assumed to uses that vertex once.

        #BFS
        queue=[s]
        spnum[s]=1
        distance[s]=0
        while queue != []:
            c=queue.pop(0)
            tree.append(c)
            for i in G[c]:
                if distance[i] == -1: #if vertex i has not been visited
                    queue.append(i)
                    distance[i]=distance[c]+1
                if distance[i] == distance[c]+1: #if we have just found another shortest path from s to i
                    spnum[i]+=spnum[c]
                    parents[i].append(c)

        # BOTTOM-UP PHASE
        while tree != []:
            c=tree.pop()
            for i in parents[c]:
                eflow[frozenset({c,i})]+=vflow[c] * (spnum[i]/spnum[c]) #the number of shortest paths using vertex c is split among the edges towards its parents proportionally to the number of shortest paths that the parents contributes
                vflow[i]+=eflow[frozenset({c,i})] #each shortest path that use an edge (i,c) where i is closest to s than c must use also vertex i
                edge_btw[frozenset({c,i})]+=eflow[frozenset({c,i})] #betweenness of an edge is the sum over all s of the number of shortest paths from s to other nodes using that edge
            if c != s:
                node_btw[c]+=vflow[c] #betweenness of a vertex is the sum over all s of the number of shortest paths from s to other nodes using that vertex

    return edge_btw,node_btw

# Girman-Newman Algorithm.

def girman_newman(G):
    # Clusters are computed by iteratively removing edges of largest betweenness
    graph=G.copy() #We make a copy of the graph. In this way we will modify the copy, but not the original graph
    done = False
    while not done:
        # After each edge removal we will recompute betweenness:
        # indeed, edges with lower betweenness may have increased their importance,
        # since shortest path that previously went through on deleted edges, now may be routed on this new edge;
        # similarly, edges with high betweenness may have decreased their importance,
        # since most of the shortest paths previously going through them disappeared because the graph has been disconnected.
        # However, complexity arising from recomputing betweenness at each iteration is huge.
        # An optimization in this case would be to compute betweenness only once
        # and to remove edges in decreasing order of computed betweenness.
        eb, nb = betweenness(graph)
        #Finding the edge with highest betweenness
        edge = None
        bet = -1
        for i in eb.keys():
            if eb[i] > bet:
                edge=i
                bet = eb[i]
        graph.remove_edge(*list(edge))
        #Deciding whether to stop the clustering procedure
        #To automatize this decision, we can use some measure of performance of the clustering.
        #An example of this measure is the function nx.algorithms.community.partition_quality(G, list(nx.connected_components(graph))).
        #See networx documentation for more details.
        #Given one such measure, one may continue iteration of the algorithm as long as the newly achieved clustering
        #has performance that are not worse than the previous clustering or above a given threshold.
        print(list(nx.connected_components(graph)))
        a = input("Do you want to continue? (y/n) ")
        if a == "n":
            done = True

    return list(nx.connected_components(graph))

# Spectral Algorithm working on Laplacian. It works for both directed and undirected graph

def spectral(G):
    n=G.number_of_nodes()
    nodes=sorted(G.nodes())

    L = nx.laplacian_matrix(G, nodes).asfptype()

    w, v = linalg.eigsh(L,n-1)

    c1= set()
    c2=set()
    for i in range(n):
        if v[i,0] < 0:
            c1.add(nodes[i])
        else:
            c2.add(nodes[i])
    return (c1, c2)


debug = True

DIRECTED = True
# file_name = "musae_facebook_edges.csv"
file_name = "email-Eu-core.txt"
# file_name = "Cit-HepTh.txt"
sep = " "
SAMPLE = 0.8
JOBS = 6

if __name__ == "__main__":
    G = load_node(file_name, DIRECTED, sep)
    if debug:
        debug_info(G, DIRECTED)
    # start_time = time.time()
    # print("Clustering gerarchico: ", hierarchical(G), "in", (time.time() - start_time), "s")
    start_time = time.time()
    print("Clustering two means:", two_means(G.to_undirected()), "in", (time.time() - start_time), "s")
    """start_time = time.time()
    print("Diametro con implementazione parallela e", JOBS, "jobs:", parallel_diam(G, JOBS), "in", (time.time() - start_time), "s")
    if not DIRECTED:
        start_time = time.time()
        print("Diametro con implementazione ad-hoc:", stream_diam(G), "in", (time.time() - start_time), "s")"""