import networkx as nx


def page_rank(G):
  num_nodes = G.number_of_nodes()
  rank = 1/num_nodes
  nnode = [
    (n, {"weight": rank}) for n in G.nodes()
    ]

  G.update(nodes = nnode)
  
  for i in range(0,4):
    for u in G.nodes():
      out_edge = G.out_edge(u)
      d = u["weight"]/len(out_edge)
      n_out_edge = [
        (u, v, {"weight" : d})
        for v in G[u]
      ]
      G.update(edges = n_out_edge)
    
    for u in G.nodes():
      in_edge = G.in_edges(u)
      u["weight"] = sum(in_edge)
      

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
