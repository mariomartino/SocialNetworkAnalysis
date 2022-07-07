import time, matplotlib.pyplot as plt, math
from collections import Counter
from task1_triangles import parallel_triangles
from utils import *
from task1_diam import parallel_diam
from task2_centrality import degree
from task1_clustering import spectral, two_means

DIRECTED = False
DEBUG = False

if __name__ == "__main__":

    G = load_node("net_3", DIRECTED, sep = " ")

    if DEBUG:
        debug_info(G, DIRECTED)

    start_time = time.time()
    diam = parallel_diam(G, 6)
    print("La rete presenta un diametro pari a:", diam, "in ", time.time() - start_time)

    # OUTPUT:  
    # a) La rete presenta un diametro pari a: 3 in  11411.527503490448

    start_time = time.time()
    triangles = parallel_triangles(G, 6)
    print("La rete presenta un numero di triangoli pari a:", triangles, "in", time.time() - start_time)

    # OUTPUT:
    # a) La rete presenta un numero di triangoli pari a: 513929287 in 3045.270566701889

    # DEGREE Computation 
    
    deg = degree(G)
    degrees = list(deg.values())
    hist = Counter(degrees)
    plt.scatter(np.log(list(hist.keys())),np.log(list(hist.values())))
    plt.show()
    plt.scatter(list(hist.keys()),list(hist.values()))
    plt.show()

    # OUTPUT: 
    # a) PNG file
    
    # Lower and Upper Bound diameter
    eigenvalues = nx.laplacian_spectrum(G)
    eigenvalue = eigenvalues[1]
    max_degree = max(list(deg.keys()))
    lower_bound = 4/(G.number_of_nodes()*eigenvalue)
    upper_bound = 2*math.sqrt(2*max_degree/eigenvalue)*math.log2(G.number_of_nodes())
    print("Lower bound:", lower_bound)
    print("Upper bound:", upper_bound)

    # OUTPUT:
    # a) Lower bound: 1.1294527970616156e-06
    # b) Upper bound: 53773.234311672306

    # Mining Clustering

    n_clusters, aver_clustering = spectral(G, False)
    print("Il numero di clusters, dividendo fino ad arrivare a clusters formati da meno di 1000 elementi è:", n_clusters)
    print("L'average clustering coefficient di 5 clusters è:", aver_clustering)

    # OUTPUT:
    # a) Il numero di clusters, dividendo fino ad arrivare a clusters formati da meno di 100 elementi è: 42
    # b) L'average clustering coefficient di 5 clusters è: [0.22117517107138338, 0.22728621738461366, 0.22329175648319702, 0.22245495750721841, 0.22160608992808825]
