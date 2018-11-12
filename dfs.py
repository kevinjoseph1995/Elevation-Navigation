import networkx as nx 
import osmnx as ox 
import requests  
G = ox.graph_from_place('Piedmont, California, USA', network_type='drive')
G_proj = ox.project_graph(G)
origin = ox.get_nearest_node(G, (37.824044, -122.233651))
dest = ox.get_nearest_node(G, (37.826059, -122.240346))

r = nx.shortest_path(G_proj, source=origin, target=dest, weight='length')
shortest = sum(ox.get_route_edge_attributes(G_proj, r, 'length'))
G = ox.add_node_elevations(G, api_key=google_elevation_api_key)

def getCost(n1, n2, mode = "normal"):
    if mode == "normal":
        return G.edges[n1, n2 ,0]["length"]
    else:
        return abs(G.nodes[n1]["elevation"] - G.nodes[n2]["elevation"])

def dfs(src, currDist, currElevDist, path, target, best):
    
    if currDist > shortest*(1.0+x):
        return
    
    if src == target:
        if normal : 
            if best[0][1] > currDist:
                best[0] = [currElevDist, currDist]
                best[1] = path[:]
        
        else:
            if best[0][0] < currElevDist:
                best[0] = [currElevDist, currDist]
                best[1] = path[:]
        return
    
    visited.add(src)
    
    for nei in G.neighbors(src):
        if nei not in visited:
            dfs(nei, currDist + getCost(src, nei), currElevDist + getCost(src, nei, "elev"), path + [nei], target, best)
    
    visited.remove(src)
    return

normal = 0
visited = set()
x = 50.0/100
best = [[float("-inf"), float("inf")], []]
dfs(origin, 0.0, 0.0, [origin], dest, best)
print(best)