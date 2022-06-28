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
