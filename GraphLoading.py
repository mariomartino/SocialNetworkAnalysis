import networkx as nx

G = nx.Graph()

with open("Cit-HepTh.txt") as file:
    edge = file.readline()
    while edge != "":
        nodes = edge.replace("\n", "").split("\t")
        G.add_edge(nodes[0], nodes[1])
        edge = file.readline()

print(G.number_of_edges())

