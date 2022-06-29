import time
from utils import *
from task1_diam import parallel_diam

DIRECTED = False
DEBUG = False

if __name__ == "__main__":

    G = load_node("net_3", DIRECTED, sep = " ")

    if DEBUG:
        debug_info(G, DIRECTED)

    start_time = time.time()
    diam = parallel_diam(G, 6)
    print("La rete presenta un diametro pari a:", diam, "in ", start_time - time.time())
    