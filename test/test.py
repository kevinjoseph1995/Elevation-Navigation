import sys
# sys.path.insert(0, '..')
import osmnx as ox
import networkx as nx
from src.controller.algorithms import *
from src.controller.server import create_geojson, create_data
from src.model.graph_model import *

#get_bounding_box
def test_get_bounding_box():
    model = Model()
    bbox = model.get_bounding_box()
    assert len(bbox) == 4
    assert all(isinstance(coord, float) for coord in bbox)

#get_graph
def test_get_graph():
    model = Model()
    G = model.get_graph()
    assert isinstance(G, nx.classes.multidigraph.MultiDiGraph)


def test_shortest_path():
    #shortest_path
    shortest_path = Algorithms.shortest_path()
    assert (len(shortest_path) == 4)
    path, distCost, ascent, descent = shortest_path()
    assert isinstance(path, list)
    assert isinstance(distCost, float)
    assert isinstance(ascent, float)
    assert isinstance(descent, float)

def test_create_geojson():
    json = create_geojson([123.1, 123.1])
    assert isinstance(json, dict)
    assert all(k in ["properties", "type", "geometry"] for k in json.keys())

def test_create_data():
    d = create_data(72.1, -128.1)
    assert isinstance(d, dict)

if __name__ == "__main__":
    print("Testing get_bounding_box")
    test_get_bounding_box()
    print("Testing get_graph")
    test_get_graph()
    print("Testing get_shortest_path")
    test_shortest_path()
    print("Testing create_geojson")
    test_create_geojson()
    print("Testing create_data")
    test_create_data()