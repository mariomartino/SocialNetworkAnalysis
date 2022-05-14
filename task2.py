import networkx as nx
import utils

def page_rank(G):
  graph = G.copy()
  num_nodes = graph.number_of_nodes()
  rank = 1/num_nodes
  nnode = [
    (n, {"weight": rank}) for n in graph.nodes()
    ]

  graph.update(nodes = nnode)
  
  for i in range(0, 2):
    for u in graph.nodes(data="weight"):
      out_edge = graph.out_edges(u)
      if u[1] != 0 and len(out_edge) != 0:
        d = u[1]/len(out_edge)
      else: 
        d = 0
      n_out_edge = [
        (u[0], v, {"weight" : d})
        for v in graph[u[0]]
      ]
      graph.update(edges = n_out_edge)
    
    unode = []
    for u in graph.nodes(data="weight"):
      in_edge = graph.in_edges(u[0], data="weight")
      unode.append(
        (u[0], {"weight": sum(v[2] for v in in_edge)})
      )

    graph.update(nodes = unode)
  
  pagerank = dict( {u[0]: u[1] for u in graph.nodes(data="weight")} )
  return pagerank

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

def betweenness(G):
    edge_btw={frozenset(e):0 for e in G.edges()}
    node_btw={i:0 for i in G.nodes()}

    for s in G.nodes():
        tree=[] 
        spnum={i:0 for i in G.nodes()} 
        parents={i:[] for i in G.nodes()} 
        distance={i:-1 for i in G.nodes()} 
        eflow={frozenset(e):0 for e in G.edges()} 
        vflow={i:1 for i in G.nodes()} 

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

def btw(G):
    return betweenness(G)[1]

def hits(G):
  hubs = dict( {v: 1 for v in G.nodes()} )
  auth = dict( {v: 1 for v in G.nodes()} )

  for i in range(0,100):
    new_hubs=dict({v: 0 for v in G.nodes()})
    new_auth=dict({v: 0 for v in G.nodes()})
    tot_hubs = 0
    tot_auth = 0

    for u in G.nodes():
      out = G.out_edges(u)
      inn = G.in_edges(u)

      for o in out:
        if o[1] != u:
          new_hubs[u] += hubs[o[1]]
      
      for j in inn:
        if j[0] != u:
          new_auth[u] += auth[j[0]]

    
    tot_hubs += sum(new_hubs.values())
    tot_auth += sum(new_auth.values())
    
    for h in new_hubs:
      new_hubs[h] /= tot_hubs

    for a in new_auth:
      new_auth[a] /= tot_auth

    hubs = new_hubs
    auth = new_auth
  return hubs, auth

###########################################################################
## Main test ##
G = utils.load_node("email-Eu-core.txt", True, " ")

cen = degree(G)
clo = closeness(G)
bet = btw(G)
pr = page_rank(G)
h, a = hits(G)

###########################################################################

cen_sort = list(cen.items())
cen_sort.sort(key= lambda tup:tup[1], reverse=True)

# Stampa di tutti i nodi con la loro degree
#for key, value in cen.items():
#  print(str(key) + ": " + str(value))

#Stampa dei nodi ordinati decrescente
#for k in cen_sort:
#  print(k)

clo_sort = list(clo.items())
clo_sort.sort(key= lambda tup:tup[1], reverse=True)

# Stampa di tutti i nodi con la loro closeness
#for key, value in clo.items():
#  print(str(key) + ": " + str(value))

#Stampa dei nodi ordinati decrescente
#for k in clo_sort:
#  print(k)

bet_sort = list(bet.items())
bet_sort.sort(key= lambda tup:tup[1], reverse=True)

# Stampa di tutti i nodi con la loro betweeness
#for key, value in bet.items():
#  print(str(key) + ": " + str(value))

#Stampa dei nodi ordinati decrescente
#for k in bet_sort:
#  print(k)

results = list(pr.items())
results.sort(key=lambda tup:tup[1], reverse=True)

#Stampa del page rank in ordine decrescente
#for u in results:
#  print(u)

hubs = list(h.items())
hubs.sort(key=lambda tup:tup[1], reverse=True)

#Stampa del hubs in ordine decrescente
#for u in hubs:
#  print(u)

auth = list(a.items())
auth.sort(key=lambda tup:tup[1], reverse=True)

#Stampa del hubs in ordine decrescente
#for u in auth:
#  print(u)

print("Degree: "+str(cen_sort[0]))
print("Closeness: "+str(clo_sort[0]))
print("Betweenness: "+str(bet_sort[0]))
print("Page Rank: "+str(results[0]))
print("Hubs: "+str(hubs[0]))
print("Authority: "+str(auth[0]))



