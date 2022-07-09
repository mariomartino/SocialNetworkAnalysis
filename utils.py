import random
import networkx as nx
import numpy as np

def load_node(file_name, directed, sep = "\t"):
    """The function read graph informations from file and generate a networkx Graph

    Args:
        file_name (string): The name of the file for the informations loading
        directed (bool): True if the graph is directed, else False
        sep (str, optional): Separator between nodes in the file. Defaults to "\t".

    Returns:
        networkx.Graph: The generated graph
    """

    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
        
    with open(file_name) as file:
        edge = file.readline()
        while edge != "":
            nodes = edge.replace("\n", "").split(sep)
            G.add_edge(nodes[0], nodes[1])
            edge = file.readline()

    return G

def debug_info(G, DIRECTED):

    """Function printing the informations of the graph to show the correctness of graph loading

    Args:
        G (network.Graph): The graph we compute informations on
        DIRECTED (bool): True if G is directed, else False
    """
    
    print("Numero di nodi:", G.number_of_nodes())
    print("Numero di archi:", G.number_of_edges())
    if not DIRECTED:
        print("Numero di componenti connesse:", nx.number_connected_components(G))
    else:
        print("Grafo fortemente connesso:", nx.is_strongly_connected(G))
    
## TASK 2 UTILS

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

## FINAL PROJECT TASK 2 UTILS

def affiliationG(n, m, q, c, p, s):
    G = nx.Graph()
    community=dict() #It keeps for each community the nodes that it contains
    for i in range(m):
        community[i]=set()
    comm_inv=dict() #It keeps for each node the communities to which is affiliated
    for i in range(n):
        comm_inv[i]=set()
    # Keeps each node as many times as the number of communities in which is contained
    # It serves for the preferential affiliation to communities (view below)
    communities=[]
    #Keeps each node as many times as its degree
    #It serves for the preferential attachment of weak ties (view below)
    nodes=[]

    for i in range(n):
        # Preferential Affiliation to communities
        r=random.random()
        # Preferential Affiliation is done only with probability q.
        # Preferential affiliation works as follows:
        # a node is chosen proportionally to the number of communities in which it is contained
        # and is copied (i.e., i is affilated to the same communities containing the chosen node).
        # Observe that the probability that i is affilated to a given community increases when the number of nodes in that community is large,
        # since the probability of selecting a node from a large community is larger than from a small community
        if r <= q and len(communities) > 0:
            prot=random.choice(communities) #Choose a prototype to copy
            for comm in comm_inv[prot]:
                community[comm].add(i)
                if comm not in comm_inv[i]:
                    comm_inv[i].add(comm)
                    communities.append(i)
        # With remaining probability (or if i is the first node to be processed and thus preferential attachment is not possible),
        # i is affiliated to at most c randomly chosen communities
        else:
            num_com=random.randint(1,c)  #number of communities is chosen at random among 1 and c
            for k in range(num_com):
                comm=random.choice([x for x in range(m)])
                community[comm].add(i)
                if comm not in comm_inv[i]:
                    comm_inv[i].add(comm)
                    communities.append(i)

        # Strong ties (edge within communities)
        # For each community and each node within that community we add an edge with probability p
        for comm in comm_inv[i]:
            for j in community[comm]:
                if j != i and not G.has_edge(i, j):
                    r2=random.random()
                    if r2 <= p:
                        G.add_edge(i,j)
                        nodes.append(i)
                        nodes.append(j)

        # Preferential Attachment of weak ties
        # We choose s nodes with a probability that is proportional to their degree and we add an edge to these nodes
        if len(nodes) == 0: #if i is the first node to be processed (and thus preferential attachment is impossible), then the s neighbors are selected at random
            for k in range(s):
                v = random.choice([x for x in range(n) if x != i])
                if not G.has_edge(i,v):
                    G.add_edge(i, v)
                    nodes.append(i)
                    nodes.append(v)
        else:
            for k in range(s):
                v = random.choice(nodes)
                if not G.has_edge(i,v):
                    G.add_edge(i, v)
                    nodes.append(i)
                    nodes.append(v)



    return G