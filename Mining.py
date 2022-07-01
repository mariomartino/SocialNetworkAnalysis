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

    # start_time = time.time()
    # diam = parallel_diam(G, 6)
    # print("La rete presenta un diametro pari a:", diam, "in ", time.time() - start_time)

    # OUTPUT:  
    # a) La rete presenta un diametro pari a: 3 in  -11411.527503490448

    # start_time = time.time()
    # triangles = parallel_triangles(G, 6)
    # print("La rete presenta un numero di triangoli pari a:", triangles, "in ", time.time() - start_time)

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
    # eigenvalues = nx.laplacian_spectrum(G)
    # eigenvalue = eigenvalues[1]
    # max_degree = max(list(deg.keys()))
    # print(eigenvalues[:10], eigenvalues[-10:])
    # print(eigenvalue, max_degree)
    # lower_bound = 4/(G.number_of_nodes()*eigenvalue) # 1.1294527970616156e-06
    # upper_bound = 2*math.sqrt(2*max_degree/eigenvalue)*math.log2(G.number_of_nodes()) # 53773.234311672306

    # Mining Clustering

    spectral(G)
    two_means(G)

    