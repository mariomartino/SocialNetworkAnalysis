from utils import *

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


if __name__ == "__main__":

    # G = load_node("email-Eu-core.txt", True, " ")
    G = load_node("net_3", False, sep = " ")
    cen = degree(G)  # Really Fast
    clo = closeness(G)  # Overtime
    edge_btw, node_btw = betweenness(G)
