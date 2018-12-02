import sys
# sys.path.insert(0, '..')
import osmnx as ox
import networkx as nx
from elenav.controller.settings import *
from elenav.controller.algorithms import *
from elenav.controller.server import create_geojson, create_data
from elenav.model.graph_model import *

def return_on_failure(value = ""):
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                f(*args,**kwargs)
                print("====>Passed " + u"\u2713\n")
            except Exception as e:
                print(e)
                print("====>Failed " + u"\u2717\n")
        return applicator
    return decorate

#get_bounding_box
@return_on_failure("")
def test_get_bounding_box(start, end):
    model = Model()
    bbox = model.get_bounding_box(start, end)
    assert len(bbox) == 4
    assert all(isinstance(coord, float) for coord in bbox)

#get_graph
@return_on_failure("")
def test_get_graph(start, end):
    model = Model()
    G = model.get_graph(start, end)
    assert isinstance(G, nx.classes.multidigraph.MultiDiGraph)

@return_on_failure("")
def test_shortest_path():
    
    #TESTING ALGO CORRECTNESS
    G = nx.Graph()
    [G.add_node(i, elevation = 0.0) for i in range(7)]
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
    # shortest_path = a_star(G, source, target, reconstruct = False)
    # assert getSum(G, nx.shortest_path(G, 0, 2, "weight") , "weight") == 4
    # assert getSum(G, shortest_path , "weight") == 4

    # assert (len(shortest_path) == 4)
    # path, distCost, ascent, descent = shortest_path()
    # assert isinstance(path, list)
    # assert isinstance(distCost, float)
    # assert isinstance(ascent, float)
    # assert isinstance(descent, float)
    shortest_path = [[], 0.0, float('-inf'), 0.0]
    dfs(G, source, target, shortest_path , 4, x = 1)
    assert shortest_path[1] == highElevDist
    assert shortest_path[2] == highElev

@return_on_failure("")
def test_create_geojson(location):
    json = create_geojson(location)
    assert isinstance(json, dict)
    assert all(k in ["properties", "type", "geometry"] for k in json.keys())

@return_on_failure("")
def test_create_data(start, end):
    d = create_data(start, end)
    assert isinstance(d, dict)

if __name__ == "__main__":
    start, end = (42.373222, -72.519852), (42.375544, -72.524210)
    print("====>Testing get_bounding_box")
    
    test_get_bounding_box(start, end)
    
    print("====>Testing get_graph")
    test_get_graph(start, end)
    print("====>Testing get_shortest_path")
    test_shortest_path()
    print("====>Testing create_geojson")
    test_create_geojson(start)
    print("====>Testing create_data")
    test_create_data(start, end)