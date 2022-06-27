import numpy as np
from joblib import Parallel, delayed
import math
from utils import *

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

def hits_matrices(G):
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