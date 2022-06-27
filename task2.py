import networkx as nx
import numpy as np
from joblib import Parallel, delayed
import math
import utils

def page_rank(G):
  """A PageRank implementation that iterates on nodes and edges.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute the Pagerank value

  Returns:
      networkx.Graph: The modified graph including the Pagerank value
  """
  num_nodes = G.number_of_nodes()
  rank = 1/num_nodes
  nnode = [
    (n, {"page_rank": rank}) for n in G.nodes()
    ]

  G.update(nodes = nnode)
  
  for i in range(0, 2):
    for u in G.nodes(data="page_rank"):
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
        (u[0], {"page_rank": sum(v[2] for v in in_edge)})
      )

    G.update(nodes = unode)
  
  return G

def page_rank2(G):
  """A PageRank implementation that exploit matrices formulas.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute the Pagerank value

  Returns:
      dict: A dictionary containing the Pagerank values. Format:("node":"value")
  """
  n = G.number_of_nodes()
  i = 0
  nodes = dict()
  for node in G.nodes():
    nodes[node] = i
    i += 1
  transition = np.zeros((n,n))
  rank = np.array([[1/n] for i in range(n)])

  for edge in G.edges():
    transition[nodes[edge[1]]][nodes[edge[0]]] = 1/G.out_degree(edge[0])

  for i in range(2):
    rank = np.dot(transition, rank)

  result_dict = dict() 
  for node in G.nodes():
    result_dict[node] = rank[nodes[node]][0]
  return result_dict

def degree(G):
  """Method that returns the centrality of the nodes by returning their own degrees.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute the centrality measure

  Returns:
      dict: A dictionary containing the Degree value. Format: ("node":"value")
  """
  cen=dict()
  for i in G.nodes():
      cen[i]=G.degree(i)
  return cen

def closeness(G):
  """Method that returns the centrality of the nodes by returning their closenesses.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute the centrality measure

  Returns:
      dict: A dictionary containing the Closeness value. Format: ("node":"value")
  """
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
  """Method that returns the centrality of the nodes by returning their Betweenness value.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute the centrality measure

  Returns:
      dict, dict: Dictionaries containing the Betweenness value. Respectively the former represents the edge betweenness 
      while the latter represents the node betweenness. Format: ("node":"value")
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
  """Method that returns the centrality of the nodes by returning their betweenness.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute the centrality measure

  Returns:
      dict: A dictionary containing the Node Betweenness value. Format: ("node":"value")
  """
  return betweenness(G)[1]

###########################################################################
# Hits Implementation.

def hits(G):
  """A Hits implementation that iterates on nodes and edges.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute the Hits values

  Returns:
      networkx.Graph: The modified graph including the Hits values
  """
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
          new_hubs[u] += auth[o[1]]
      
      for j in inn:
        if j[0] != u:
          new_auth[u] += hubs[j[0]]

    
    tot_hubs += sum(new_hubs.values())
    tot_auth += sum(new_auth.values())
    
    for h in new_hubs:
      new_hubs[h] /= tot_hubs

    for a in new_auth:
      new_auth[a] /= tot_auth

    hubs = new_hubs
    auth = new_auth
  return hubs, auth

def hits2(G):
  """A Hits implementation that exploit matrices formulas.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute the Hits values

  Returns:
      dict: A dictionary containing the Hits values. Format:("node":"value")
  """
  n = G.number_of_nodes()
  transition = np.zeros((n,n))
  hubs = np.array([[1] for i in range(n)])
  auth = np.array([[1] for i in range(n)])
  
  i = 0
  nodes = dict()
  for node in G.nodes():
    nodes[node] = i
    i += 1

  for edge in G.edges():
    transition[nodes[edge[0]]][nodes[edge[1]]] = 1

  for i in range(100):
    newhubs = np.dot(transition, auth)
    newhubs = newhubs/(sum(newhubs))
    newauth = np.dot(transition.transpose(), hubs)
    newauth = newauth/(sum(newauth))
    hubs = newhubs
    auth = newauth
  
  hubs_dict = dict()
  auth_dict = dict()
  for node in G.nodes():
    hubs_dict[node] = hubs[nodes[node]][0]
    auth_dict[node] = auth[nodes[node]][0]

  return hubs_dict, auth_dict

def hits_hubs(G, hubs):
  """A function that, taken graph and a dictionary representing the hubbiness values, insert the Hits values as node properties in the graph.

  Args:
      G (networkx.Graph): The graph on which the Hubbiness Values have been computed
      hubs (dict): A dictionary containing the Hits values. Format:("node":"value")

  Returns:
      networkx.Graph: The graph updated with the Hubbiness Values.
  """
  nnode = [
    (n, {"hubs": hubs[n]}) for n in G.nodes()
    ]
  
  G.update(nodes = nnode)
  return G

def hits_authority(G, authority):
  """A function that, taken graph and a dictionary representing the authority values, insert the Hits values as node properties in the graph.

  Args:
      G (networkx.Graph): The graph on which the Authority Values have been computed
      authority (dict): A dictionary containing the Hits values. Format:("node":"value")

  Returns:
      networkx.Graph: The graph updated with the Authority Values.
  """
  nnode = [
    (n, {"authority": authority[n]}) for n in G.nodes()
    ]
  
  G.update(nodes = nnode)
  return G

def hits_average(G, hubs, authority):
  """A function that, taken graph and two dictionary representing the Hits values, insert the Average Hits values as node properties in the graph.

  Args:
      G (networkx.Graph): The graph on which the Average Hits Values have been computed
      hubs (dict): A dictionary containing the Hits values. Format:("node":"value")
      authority (dict): A dictionary containing the Hits values. Format:("node":"value")

  Returns:
      networkx.Graph: The graph updated with the Average Hits Values.
  """
  nnode = [
    (n, {"average": (authority[n]+hubs[n])/2}) for n in G.nodes()
    ]
  
  G.update(nodes = nnode)
  return G

###########################################################################
# Hits Parallel Implementation. Map Reduce.
# I must compute the sum for every row before to sum the column value (e.g same-i-sum before of same-j-sum).

def matrix_division(matrix, array, k):
  """A function that divides a matrix in blocks (K*K) and a vector in blocks (1*K).

  Args:
      matrix (np.array): The matrix the function must split
      array (np.array): The array the function must split
      k (int): size of the blocks

  Yields:
      int, np.array, np.array: The integer of the starting index of the blocks/array, then respectively the sub-matrix and the sub-array
  """
  
  for i in range(0, matrix.shape[0], k):
    for j in range(0, matrix.shape[1], k):
      yield i, matrix[i:min(i+k,matrix.shape[0]), j:min(j+k,matrix.shape[1])], array[j:min(j+k,matrix.shape[1])]

def parallel_multiply(j, matrix, array):
  """A function that multiplicates the matrix and the array in input

  Args:
      j (int): The starting index of the matrix, it saves a split information to pass it to a reducer
      matrix (np.array): The matrix to multiply
      array (np.array): The array to multiply

  Returns:
      int, np.array: The 'j' value and the results of the multiplication
  """
  return j, np.dot(matrix,array)

def pagerank_parallel(G, jobs):
  """A Pagerank implementation that exploits multi-process programming.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute Pagerank values.
      jobs (int): The number of processes the funcion must create

  Returns:
      dict: A dictionary containing the Pagerank values. Format: ("node":"value")
  """
  n = G.number_of_nodes()
  pagerank = np.array(n*[1/n])
  transition = np.zeros((n,n))
  i = 0
  nodes = dict()
  for node in G.nodes():
    nodes[node] = i
    i += 1
  for edge in G.edges():
    transition[nodes[edge[1]]][nodes[edge[0]]] = 1/G.out_degree(edge[0])
  with Parallel(n_jobs=jobs) as parallel:
    for _ in range(0, 2):
      results = np.zeros((n,))
      # MAP PART
      result = parallel(delayed(parallel_multiply)(j, matrix, array) for j, matrix, array in matrix_division(transition, pagerank, math.ceil(n/jobs)))
      # REDUCE PART
      for res in result:
        end_point = min(res[0] + math.ceil(n/jobs), n)
        results[res[0]:end_point,] += res[1]
      pagerank = results[:]
  result_dict = dict() 
  for node in G.nodes():
    result_dict[node] = pagerank[nodes[node]]
  return result_dict

def hits_parallel(G, jobs):
  """A Hits implementation that exploits multi-process programming.

  Args:
      G (networkx.Graph): The graph on which the algorithm must compute Hits values.
      jobs (int): The number of processes the funcion must create

  Returns:
      dict: A dictionary containing the Pagerank values. Format: ("node":"value")
  """
  n = G.number_of_nodes()
  hubs = np.array(n*[1])
  auth = np.array(n*[1])
  transition = np.zeros((n,n))
  i = 0
  nodes = dict()
  for node in G.nodes():
    nodes[node] = i
    i += 1
  for edge in G.edges():
    transition[nodes[edge[0]]][nodes[edge[1]]] = 1
  with Parallel(n_jobs=jobs) as parallel:
    for _ in range(0, 100):
      newhubs = np.zeros((n,))
      newauth = np.zeros((n,))
      # MAP PART
      result_hubs = parallel(delayed(parallel_multiply)(j, matrix, array) for j, matrix, array in matrix_division(transition, auth, math.ceil(n/jobs)))
      result_auth = parallel(delayed(parallel_multiply)(j, matrix, array) for j, matrix, array in matrix_division(transition.transpose(), hubs, math.ceil(n/jobs)))
      # REDUCE PART
      for res in result_hubs:
        end_point = min(res[0] + math.ceil(n/jobs), n)
        newhubs[res[0]:end_point,] += res[1]
      for res in result_auth:
        end_point = min(res[0] + math.ceil(n/jobs), n)
        newauth[res[0]:end_point,] += res[1]
      hubs = newhubs[:]/(sum(newhubs))
      auth = newauth[:]/(sum(newauth))
  hubs_dict = dict()
  auth_dict = dict() 
  for node in G.nodes():
    hubs_dict[node] = hubs[nodes[node]]
    auth_dict[node] = auth[nodes[node]]
  return hubs_dict, auth_dict

###########################################################################
## Main test ##
G = utils.load_node("email-Eu-core.txt", True, " ")

# cen = degree(G)
# clo = closeness(G)
# bet = btw(G)
# page_rank(G)
# h, a = hits(G)
# pagerank2 = page_rank2(G)
res = pagerank_parallel(G, 6)
hub, auth = hits2(G)
hub_parallel, auth_parallel = hits_parallel(G, 6)

print("PARALLEL: ", hub_parallel)
print("NORMAL: ", hub)

exit(0)
hits_hubs(G,hub)
hits_authority(G,auth)
hits_average(G,hub, auth)


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

results = list(G.nodes(data="page_rank"))
results.sort(key=lambda tup:tup[1], reverse=True)

#Stampa del page rank in ordine decrescente
#for u in results:
#  print(u)

hubs = list(G.nodes(data="hubs"))
hubs.sort(key=lambda tup:tup[1], reverse=True)

#Stampa del hubs in ordine decrescente
#for u in hubs:
#  print(u)

auth = list(G.nodes(data="authority"))
auth.sort(key=lambda tup:tup[1], reverse=True)

#Stampa del authority in ordine decrescente
#for u in auth:
#  print(u)

av = list(G.nodes(data="average"))
av.sort(key=lambda tup:tup[1], reverse=True)

#Stampa del average in ordine decrescente
#for u in av:
#  print(u)

res = [(k, v) for k, v in res.items()]
res.sort(key=lambda tup:tup[1], reverse=True)

#Stampa del pagerank calcolato in maniera parallela
#for u in res:
#  print(u)

pagerank2 = [(k, v) for k, v in pagerank2.items()]
pagerank2.sort(key=lambda tup:tup[1], reverse=True)

#Stampa del pagerank calcolato in forma matriciale
#for u in pagerank2:
#  print(u)

print("Degree: "+str(cen_sort[0]))
print("Closeness: "+str(clo_sort[0]))
print("Betweenness: "+str(bet_sort[0]))
print("Page Rank: "+ str(results[0:10]))
print("Page Rank parallelo:"+ str(res[0]))
print("Page Rank matriciale:" + str(pagerank2[0]))
print("Hubs: "+str(hubs[0]))
print("Authority: "+str(auth[0]))
print("Average: "+str(av[0]))
