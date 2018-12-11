import osmnx as ox
import networkx as nx
import numpy as np
import pickle as p
import os
from elenav.model.config import API

class Model:
    def __init__(self):
        print("Model Initialized")        
        self.GOOGLEAPIKEY=API["googleapikey"]        
        if os.path.exists("./graph.p"):
            self.G = p.load( open( "graph.p", "rb" ) )
            self.init = True
            print("Loaded Graph")
        else:
            self.init = False

    def get_graph_with_elevation(self, G):
        """
        Returns networkx graph G with eleveation data appended to each node and rise/fall grade to each edge.

        Params:
            bbox:tuple (n,s,e,w)
        Returns:
            G: networkx graph
        """
        G = ox.add_node_elevations(G, api_key=self.GOOGLEAPIKEY)        
        return G

    def distance_between_locs(self,lat1,lon1,lat2,lon2):
        """
        Return the distance between two locations given the lat/long's.
        """
        R=6371008.8 #radius of the earth
        
        lat1 = np.radians(lat1)
        lon1 = np.radians(lon1)
        lat2 = np.radians(lat2)
        lon2 = np.radians(lon2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        distance = R * c
        return distance

    def add_dist_from_dest(self,G,end_location):
        """
        Adds distance from destination location to all the nodes in the graph
        Args:
        G : networkx multidigraph
        Returns
        G : networkx multidigraph
        """
        end_node=G.nodes[ox.get_nearest_node(G, point=end_location)]
        lat1=end_node["y"]
        lon1=end_node["x"]
        
        for node,data in G.nodes(data=True):
            lat2=G.nodes[node]['y']
            lon2=G.nodes[node]['x']
            distance=self.distance_between_locs(lat1,lon1,lat2,lon2)            
            data['dist_from_dest'] = distance
            
        return G

    
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
        bbox1 = ox.bbox_from_point(start_location, distance)
        bbox2 = ox.bbox_from_point(end_location, distance)
        bbox = (max(bbox1[0],bbox2[0]),min(bbox1[1],bbox2[1]),max(bbox1[2],bbox2[2]),min(bbox1[3],bbox2[3]))

        return bbox

    def get_graph(self, start_location, end_location):
        """
        Return networkx graph with the elevation data added to the nodes. (If theis class had already been called before it will load the cached
        graph to save time. 
        """


        if not self.init:
            print("Loading Graph")
            # bbox=self.get_bounding_box(start_location,end_location)
            # self.G = ox.graph_from_bbox(bbox[0],bbox[1],bbox[2],bbox[3],network_type='walk', simplify=False)
            self.G = ox.graph_from_point(start_location, distance=20000, network_type='walk')
            self.G = self.get_graph_with_elevation(self. G)                         
            p.dump( self.G, open( "graph.p", "wb" ) )
            self.init = True
            print("Saved Graph")
        self.G = self.add_dist_from_dest(self. G,end_location)
        return self.G

    
    
