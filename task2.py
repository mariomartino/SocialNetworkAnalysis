import networkx as nx
import utils

def page_rank(G):
  num_nodes = G.number_of_nodes()
  rank = 1/num_nodes
  nnode = [
    (n, {"weight": rank}) for n in G.nodes()
    ]

  G.update(nodes = nnode)
  
  for i in range(0, 2):
    for u in G.nodes(data="weight"):
      out_edge = G.out_edges(u)
      if u[1] != 0 and len(out_edge) != 0:
        d = u[1]/len(out_edge)
      else: 
        d = 0
      n_out_edge = [
        (u[0], v, {"weight" : d})
        for v in G[u[0]]
      ]
      G.update(edges = n_out_edge)
    
    unode = []
    for u in G.nodes(data="weight"):
      in_edge = G.in_edges(u[0], data="weight")
      unode.append(
        (u[0], {"weight": sum(v[2] for v in in_edge)})
      )

    G.update(nodes = unode)
  
  return G

def degree(G):
    cen=dict()
    for i in G.nodes():
        cen[i]=G.degree(i)
    return cen

def closeness(G):
    cen=dict()

    for u in G.nodes():
        visited=set()
        visited.add(u)
        queue=[u]
        dist=dict()
        dist[u] = 0

        while len(queue) > 0:
            v = queue.pop(0)
            for w in G[v]:
                if w not in visited:
                    queue.append(w)
                    visited.add(w)
                    dist[w]=dist[v]+1

        cen[u]=sum(dist.values())

    return cen

G = utils.load_node("email-Eu-core.txt", True, " ")
page_rank(G)
for u in G.nodes(data="weight"):
  print(u)

#Fare il sort per vedere il nodo più popolare