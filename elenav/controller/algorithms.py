import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

def create_elevation_profile(G,total_path):
    elevation_profile = [G.node[route_node]['elevation'] for route_node in total_path]
    plt.figure()
    plt.title("Elevation Profile")
    plt.ylabel("Elevation (m)")
    plt.plot(elevation_profile,color='black')
    plt.savefig('./elenav/view/static/elevation_profile.png')
    ascent=0.0
    descent=0.0
    if len(total_path)>1:
        for i in range(1,len(total_path)):
            if G.node[total_path[i]]['elevation']-G.node[total_path[i-1]]['elevation'] >= 0:
                ascent += G.node[total_path[i]]['elevation']-G.node[total_path[i-1]]['elevation']
            else:
                descent += -(G.node[total_path[i]]['elevation']-G.node[total_path[i-1]]['elevation'])

    return ascent,descent


def sample_algorithm_format(G, start_location, end_location):
    # Should return (route(list of [(longs,lats)]), elevation gain,elevation drop
    pass

def get_shortest_path(G, start_location, end_location):
    source = ox.get_nearest_node(G, point=start_location)
    target = ox.get_nearest_node(G, point=end_location)
    shortest_route = nx.shortest_path(G, source = source, target = target, weight='length')
    shortest_dist = sum(ox.get_route_edge_attributes(G, shortest_route, 'length'))
    return shortest_dist

def a_star(G,start_location,end_location, shortestDist, x = 0.0, reconstruct = True):
    """
    Returns the route(list of nodes) that minimize change in elevation between start and end using the A* node, with the heuristic 
    being the distance from the end node. 
    Params:
        start_location: tuple (lat,long)
        end_location: tuple (lat,long)
        Returns:
        lat_longs: List of [lon,lat] in the route
    """
    
    start_node = ox.get_nearest_node(G, point=start_location)
    end_node = ox.get_nearest_node(G, point=end_location)
    # start_node=start_location
    # end_node=end_location

    def reconstruct_path(cameFrom, current):
        """
        Function to retrace the path from end node to start node. Returns in the format required by Mapbox API(for plotting)
        """
        total_path = [current]
        while current in cameFrom:
            current = cameFrom[current]
            total_path.append(current)
        ele_latlong=[[G.node[route_node]['x'],G.node[route_node]['y']] for route_node in total_path ] 
        ascent,descent=create_elevation_profile(G,total_path)
        return ele_latlong,ascent,descent    
        
    
    #The settotal_path of nodes already evaluated
    closedSet=set()
    # The set of currently discovered nodes that are not evaluated yet.
    # Initially, only the start node is known.        
    openSet=set()
    openSet.add(start_node)
    # For each node, which node it can most efficiently be reached from.
    # If a node can be reached from many nodes, cameFrom will eventually contain the
    # most efficient previous step.
    cameFrom={}
    #For each node, the cost of getting from the start node to that node.
    gScore={}
    for node in G.nodes():
        gScore[node]=float("inf")
    #The cost of going from start to start is zero.
    gScore[start_node] = 0 
    # For each node, the total cost of getting from the start node to the goal
    # by passing by that node. That value is partly known, partly heuristic.
    fScore={}

    # For the first node, that value is completely heuristic.
    fScore[start_node] = 0#G.nodes[start_node]['dist_from_dest']

    

    while openSet!={}:
        current= min([(node,fScore[node]) for node in openSet],key=lambda t: t[1]) [0]            
        if current==end_node:
            return reconstruct_path(cameFrom, current)
        openSet.remove(current)
        closedSet.add(current)

        for neighbor in G.neighbors(current):
            if neighbor in closedSet:
                continue # Ignore the neighbor which is already evaluated.
            #The distance from start to a neighbor
            tentative_gScore= gScore[current]+abs(G.nodes[current]['elevation'] - G.nodes[neighbor]['elevation'])
            if neighbor not in openSet:# Discover a new node
                openSet.add(neighbor)
            else:
                if tentative_gScore>=gScore[neighbor] :#Stop searching along this path if distance exceed 1.5 times shortest path
                    continue# This is not a better path.
            cameFrom[neighbor]=current
            gScore[neighbor]=tentative_gScore
            fScore[neighbor]=gScore[neighbor]# + G.nodes[neighbor]['dist_from_dest']

def getCost(G, n1, n2, mode = "normal"):
    if mode == "normal":
        try : return G.edges[n1, n2 ,0]["length"]
        except : return G.edges[n1, n2]["weight"]
    elif mode == "elevation-diff":
	    return G.nodes[n2]["elevation"] - G.nodes[n1]["elevation"]
    elif mode == "gain-only":
	    return max(0,G.nodes[n2]["elevation"] - G.nodes[n1]["elevation"])
    elif mode == "drop-only":
	    return max(0,G.nodes[n1]["elevation"] - G.nodes[n2]["elevation"])
    else:
        return abs(G.nodes[n1]["elevation"] - G.nodes[n2]["elevation"])
    
    #assert iisintace float, Create a graph and confirm edge length is what is expected.

def dfs(G, start_location, end_location, best, shortest, currDist = 0.0, currElevDist = 0.0, path = [], descent = 0.0, x = 0.0, visited = set()):
    """
    Returns the route(list of nodes) that maximizes absolute change in elevation between start and end using naive dfs
    Params:
        G : graph
        start_location: tuple (lat,long)
        end_location: tuple (lat,long)
        currDist : total distance travelled
        currElevDist : total change in elevation (not considering drops)
        path : path of nodes
        descent : total sum of drops for the given path
        best : list to keep track of best seen so far
        x : threshold for distance
        Returns:
        lat_longs: [path, currDist, currElevDist , descent]
    """
    if currDist > shortest*(1.0+x):
        return
    
    if start_location == end_location:
        if best[2] < currElevDist:
            best[0], best[1], best[2], best[3] = path[:], currDist, currElevDist, descent
        return
    
    visited.add(start_location)
    
    for nei in G.neighbors(start_location):
        if nei not in visited:
            dfs(G, nei, end_location, best, shortest, currDist + getCost(G, start_location, nei), \
            currElevDist + getCost(G, start_location, nei, "gain-only"), \
            path + [nei], descent + min(getCost(G, start_location, nei, "elevation-diff"), 0.0), x, visited)
    
    visited.remove(start_location)
    return