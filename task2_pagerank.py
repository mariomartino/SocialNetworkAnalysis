import numpy as np
from joblib import Parallel, delayed
import math
from utils import *

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

def page_rank_matrices(G):
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

if __name__ == "__main__":

    G = load_node("email-Eu-core.txt", True, " ")

    pagerank_iter = page_rank(G)
    page_rank_matrix = page_rank_matrices(G)
    pagerank_parall = pagerank_parallel(G, 6)