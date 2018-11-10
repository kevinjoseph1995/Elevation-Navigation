import osmnx as ox
import networkx as nx
import numpy as np

class Router:
    def __init__(self):
        print("Initialized")

    def get_bounding_box(self,start_location,end_location,distance=2000):
        """
        Returns the bounding box (N,S,E,W) given the start and end coordinates.

        Params:
            start_location: tuple (lat,long)
            end_location: tuple (lat,long)
            distance: Additional width given to the bbox at the corners(in metres)
        Returns:
            bbox: tuple (n,s,e,w)
        """
        bbox1=ox.bbox_from_point(start_location, distance)
        bbox2=ox.bbox_from_point(end_location, distance)
        bbox=(max(bbox1[0],bbox2[0]),min(bbox1[1],bbox2[1]),max(bbox1[2],bbox2[2]),min(bbox1[3],bbox2[3]))
        
        return bbox

    def get_shortest_path(self,start_location,end_location):
        """
        INCOMPOLETE
        """
        bbox=self.get_bounding_box(start_location,end_location)
        G = ox.graph_from_bbox(bbox[0],bbox[1],bbox[2],bbox[3],network_type='drive')
        start_node=ox.get_nearest_node(G, point=start_location)
        end_node=ox.get_nearest_node(G, point=end_location)
        route = nx.shortest_path(G, start_node, end_node)
        lat_longs = ";".join(["{0},{1}".format(G.node[route_node]['x'], G.node[route_node]['y']) for route_node in route])
        
        return lat_longs


# r=Router()
# r.get_shortest_path((42.377041, -72.519681),(42.350070, -72.528798))
