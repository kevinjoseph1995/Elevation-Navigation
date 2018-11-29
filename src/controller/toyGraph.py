import networkx as nx
import algorithms

#graph 1
G = nx.Graph()
[G.add_node(i, elev = 0.0) for i in range(7)]
edgeList = [(0,1,2.0), (1,2,2.0), (0,3,2.0), (3,4,1.0), (4,2,2.0), (0,5,3.0), (5,2,3.0), (0,6,4.0), (6,2,4.0)]
G.add_weighted_edges_from(edgeList)
elev = [0, 0, 0, 2, 2, 3, 4]

for i, e in enumerate(elev):
    G.node[i]["elevation"] = e

def getSum(G, route, attribute):

    attribute_values = []
    for u, v in zip(route[:-1], route[1:]):
        data = G.get_edge_data(u, v)[attribute]
        attribute_values.append(data)
    return sum(attribute_values)

source = 0
target = 2
shortestDist = 4.0
highElev = 4.0
highElevDist = 8.0
x = 100 #in percentage

assert getSum(G, nx.shortest_path(G, 0, 2, "weight") , "weight") == 4
algos=algorithms.Algorithms()
print(algos.a_star(G,0,2))
assert getSum(G, algos.a_star(G,0,2) , "weight") == 4