import time
import networkx as nx
import random
from utils import affiliationG
from final_mockup import AdService

ctrs = dict()

def input_data():
    n = 20000
    G = affiliationG(n, 50, 0.5, 3, 0.35, 10) #This will be updated to the network model of net_x
    p = dict()
    for u in G.nodes():
        p[u] = dict()
    for u in G.nodes():
        for v in G[u]:
            if v not in p[u]:
                t=min(0.25, 2/max(G.degree(u), G.degree(v)))
                p[u][v] = p[v][u] = random.uniform(0, t)
    rev = dict()
    for i in range(5):
        rev[i] = random.randrange(10, 90, 5)/100
    B = 1400
    
    T = 5000
    #for the oracle
    for u in G.nodes():
        ctrs[u] = dict()
        for i in range(5):
            ctrs[u][i] = random.uniform(0.1, 0.6)
            
    return G, p, rev, B, T, ctrs

def oracle(u, i):
    r = random.random()
    if r <= ctrs[u][i]:
        return True
    return False

print("Upload Input")
G, p, rev, B, T, ctrs = input_data()
ads=AdService(G, p, rev, B)
revenue = 0
print("Start")
start = time.time()
for step in range(T):
    print(step)
    revenue += ads.run(step, oracle)

print("End")
print(time.time() - start)
print(revenue)
