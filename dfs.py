from collections import deque, defaultdict
from heapq import *
import networkx as nx 
import osmnx as ox 
import requests  
# G = ox.graph_from_place('Piedmont, California, USA', network_type='walk')
org, dst = (37.826003, -122.23309), (37.817440, -122.250660)
G = ox.graph_from_point(org, distance=2000)
bbox = ox.bbox_from_point(org, distance=2000)


G = ox.add_node_elevations(G, api_key=google_elevation_api_key)
G = ox.add_edge_grades(G)

G_proj = ox.project_graph(G)
origin = ox.get_nearest_node(G, org, return_dist = True)
dest = ox.get_nearest_node(G, dst, return_dist = True)
if origin[1] > 100 or dest[1] > 100:
    raise ValueError("Nodes found are inaccurate!!")

r = nx.shortest_path(G_proj, source=origin[0], target=dest[0], weight='length')
shortest = sum(ox.get_route_edge_attributes(G_proj, r, 'length'))

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

#https://gist.github.com/kachayev/5990802
def dijkstra(src, target):
    q, seen, mins = [(0,src,[])], set(), {src: 0}
    while q:
        cost, node, path = heappop(q)
        if node not in seen:
            seen.add(node)
            path.append(node)
            if node == target: return cost

            for nei in G.neighbors(node):
                if nei in seen: continue
                prev = mins.get(nei, None)
                next = cost + getCost(node, nei)
                if prev is None or next < prev:
                    mins[nei] = next
                    heappush(q, (next, nei, path))

    return float("inf")

#need to see which one is faster
#https://codereview.stackexchange.com/questions/79025/dijkstras-algorithm-in-python
def dijkstra_2(src, target):
    dist = {}
    queue = [(0, src)]
    while queue:
        cost, node = heappop(queue)
        if node == target:
            return dist
        if node not in dist: # v is unvisited
            dist[node] = cost
            for nei in G.neighbors(node):
                if nei not in dist:
                    heappush(queue, (cost + getCost(node, nei), nei))

    # to give same result as original, assign zero distance to unreachable vertices             
    return float('inf')
    # return [0 if x is None else x for x in A]

normal = 0
visited = set()
x = 10.0/100
best = [[float("-inf"), float("inf")], []]
dfs(origin[0], 0.0, 0.0, [origin[0]], dest[0], best)
bfs(origin[0], dest[0], best)
dijkstra(origin[0], dest[0])
print(best)