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

        
        #Graph initialization
        # bbox = self.get_bounding_box(start_location, end_location)

        if not self.init:
            print("Loading Graph")
            # bbox=self.get_bounding_box(start_location,end_location)
            # self.G = ox.graph_from_bbox(bbox[0],bbox[1],bbox[2],bbox[3],network_type='walk', simplify=False)
            self.G = ox.graph_from_point(start_location, distance=10000, simplify = True, network_type='walk')
            self.G = self.get_graph_with_elevation(self. G)            
            p.dump( self.G, open( "graph.p", "wb" ) )
            self.init = True
            print("Saved Graph")

        return self.G

    
    
