import osmnx as ox
import networkx as nx
from heapq import *
import matplotlib.pyplot as plt
from collections import deque, defaultdict
import timeit

class Algorithms:
    def __init__(self, G, x, mode = "maximize"):
        self.G = G
        self.mode = mode
        self.x = x
        self.best = [[], 0.0, float('-inf'), 0.0] # Route, total distance, total gain only, total drop only
        self.start_node, self.end_node = None, None

    def create_elevation_profile(self):
        if len(self.best[0]) == 0 : return
        G = self.G
        
        elevation_profile_elenav = [G.node[route_node]['elevation'] for route_node in self.best[0]]
        # elevation_profile_short = [G.node[route_node]['elevation'] for route_node in self.shortest_route]
        plt.figure()
        plt.title("Elevation Profile")
        plt.ylabel("Elevation (m)")
        plt.plot(elevation_profile_elenav,color='black')
        # plt.plot(elevation_profile_short,color='blue')
        plt.savefig('./elenav/view/static/elevation_profile.png')
        return

    def verify_nodes(self):
        if not self.start_node or not self.end_node:
            return False
        return True

    def reconstruct_path(self, cameFrom, current):
        """
        Function to retrace the path from end node to start node. Returns in the format required by Mapbox API(for plotting)
        """
        if not cameFrom or not current : return
        total_path = [current]
        while current in cameFrom:
            current = cameFrom[current]
            total_path.append(current)
        self.best = [total_path[:], self.computeElevs(total_path, "normal"), self.computeElevs(total_path, "gain-only"), \
                                                                        self.computeElevs(total_path, "drop-only")]
        return

    def a_star(self):
        """
        Returns the route(list of nodes) that minimize change in elevation between start and end using the A* node, with the heuristic 
        being the distance from the end node. 
        Params:
            start_node: source node id
            end_node: target node id
            Returns:
            lat_longs: List of [lon,lat] in the route
        """
        
        if not self.verify_nodes() : return
        G, shortest = self.G, self.shortest_dist
        x, mode = self.x, self.mode
        start_node, end_node = self.start_node, self.end_node
        
        #The settotal_path of nodes already evaluated
        closedSet = set()
        # The set of currently discovered nodes that are not evaluated yet.
        # Initially, only the start node is known.        
        openSet = set()
        openSet.add(start_node)
        # For each node, which node it can most efficiently be reached from.
        # If a node can be reached from many nodes, cameFrom will eventually contain the
        # most efficient previous step.
        cameFrom = {}
        #For each node, the cost of getting from the start node to that node.
        gScore = {}
        for node in G.nodes():
            gScore[node] = float("inf")
        #The cost of going from start to start is zero.
        gScore[start_node] = 0 
        # For each node, the total cost of getting from the start node to the goal
        # by passing by that node. That value is partly known, partly heuristic.
        fScore = {}

        # For the first node, that value is completely heuristic.
        fScore[start_node] = 0#G.nodes[start_node]['dist_from_dest']

        while len(openSet):
            current = min([(node,fScore[node]) for node in openSet], key=lambda t: t[1])[0]            
            if current == end_node:
                self.reconstruct_path(cameFrom, current)
                return
            
            openSet.remove(current)
            closedSet.add(current)
            for nei in G.neighbors(current):
                if nei in closedSet:
                    continue # Ignore the neighbor which is already evaluated.
                #The distance from start to a neighbor
                tentative_gScore = gScore[current] + self.getCost(current, nei, "gain-only")
                if nei not in openSet:# Discover a new node
                    openSet.add(nei)
                else:
                    if tentative_gScore >= (1+x)*shortest :#Stop searching along this path if distance exceed 1.5 times shortest path
                        continue # This is not a better path.
                
                cameFrom[nei] = current
                gScore[nei] = tentative_gScore
                fScore[nei] = gScore[nei] # + G.nodes[neighbor]['dist_from_dest']
        


    def getCost(self, n1, n2, mode = "normal"):
        G = self.G
        if not n1 or not n2 : return
        
        if mode == "normal":
            try : return G.edges[n1, n2 ,0]["length"]
            except : return G.edges[n1, n2]["weight"]
        elif mode == "elevation-diff":
            return G.nodes[n2]["elevation"] - G.nodes[n1]["elevation"]
        elif mode == "gain-only":
            return max(0.0, G.nodes[n2]["elevation"] - G.nodes[n1]["elevation"])
        elif mode == "drop-only":
            return max(0.0, G.nodes[n1]["elevation"] - G.nodes[n2]["elevation"])
        else:
            return abs(G.nodes[n1]["elevation"] - G.nodes[n2]["elevation"])
        

    def dfs(self, start_node, end_node, currDist = 0.0, currElevDist = 0.0, path = [], descent = 0.0, visited = set()):
        """
        Returns the route(list of nodes) that maximizes absolute change in elevation between start and end using naive dfs
        Params:
            G : graph
            start_node: tuple (lat,long)
            end_node: tuple (lat,long)
            currDist : total distance travelled
            currElevDist : total change in elevation (not considering drops)
            path : path of nodes
            descent : total sum of drops for the given path
            Returns: None. All stats are recorded in best list
        """
        if not self.verify_nodes() : return
        
        if currDist > self.shortest_dist*(1.0+x):
            return
        
        if start_node == end_node:
            if self.mode == "maximize" and self.best[2] < currElevDist:
                self.best = [path[:], currDist, currElevDist, descent]
            elif self.mode == "minimize" and self.best[3] < descent:
                self.best = [path[:], currDist, currElevDist, descent]
            return
        
        visited.add(start_node)
        
        for nei in self.G.neighbors(start_node):
            if nei not in visited:
                distCost = currDist + self.getCost(start_node, nei), currElevDist
                gainCost = self.getCost(start_node, nei, "gain-only")
                dropCost = descent + min(self.getCost(start_node, nei, "elevation-diff"), 0.0)
                dfs(nei, end_node, distCost, elevCost, path + [nei], dropCost)
        
        visited.remove(start_node)
        return

    def computeElevs(self, route, mode = "both", piecewise = False):
        total = 0
        if piecewise : piecewiseElevs = []
        for i in range(len(route)-1):
            if mode == "both":
                diff = self.getCost(route[i],route[i+1],"elevation-diff")	
            elif mode == "gain-only":
                diff = self.getCost(route[i],route[i+1],"gain-only")
            elif mode == "drop-only":
                diff = self.getCost(route[i],route[i+1],"drop-only")
            elif mode == "normal":
                diff = self.getCost(route[i],route[i+1],"normal")
            total += diff
            if piecewise : piecewiseElevs.append(diff)
        if piecewise:
            return total, piecewiseElevs
        else:
            return total

    def getRoute(self, parent, dest):
        "returns the path given a parent mapping and the final dest"
        path = [dest]
        curr = parent[dest]
        while curr!=-1:
            path.append(curr)
            curr = parent[curr]
        return path[::-1]

    def dijkstra(self, weight):
        if not self.verify_nodes() : return
        G, x, shortest, mode = self.G, self.x, self.shortest_dist, self.mode
        start_node, end_node = self.start_node, self.end_node
        q, seen, mins = [(0.0, 0.0, start_node)], set(), {start_node: 0}
        
        parent = defaultdict(int)
        parent[start_node] = -1
        while q:
            currPriority, currDist, node = heappop(q)
            
            if node not in seen:
                seen.add(node)
                if node == end_node:
                    return currPriority, currDist, parent

                for nei in G.neighbors(node):
                    if nei in seen: continue
                    prev = mins.get(nei, None)
                    length = self.getCost(node, nei, "normal")
                    
                    if mode == "maximize":
                        if weight[0] == 1:
                            next = length - self.getCost(node, nei, "elevation-diff")
                        elif weight[0] == 2:
                            next = (length - self.getCost(node, nei, "elevation-diff"))*length
                        elif weight[0] == 3:
                            next = length + self.getCost(node, nei, "drop-only")
                    else:
                        if weight[0] == 1:
                            next = length + self.getCost(node, nei, "elevation-diff")
                        elif weight[0] == 2:
                            next = (length + self.getCost(node, nei, "elevation-diff"))*length 
                        else: 
                            next = length + self.getCost(node, nei, "gain-only")
                    if weight[1] : next += currPriority
                    nextDist = currDist + length
                    if nextDist <= shortest*(1.0+x) and (prev is None or next < prev):
                        parent[nei] = node
                        mins[nei] = next
                        heappush(q, (next, nextDist, nei))        
        
        return None, None, None

    def all_dijkstra(self):
        
        if not self.verify_nodes() : return
        start_node, end_node = self.start_node, self.end_node
        
        results = {}    
        for weight in [[1, True], [2, True], [3, True], [1, False], [2, False], [3, False]]:
	    temp = {}
            _, currDist, parent = self.dijkstra(weight)
            temp["distance"] = currDist
            if not currDist : continue
            
            route = self.getRoute(parent, end_node)
	    temp["route"] = parent
            elevDist, dropDist = self.computeElevs(route, "gain-only"), self.computeElevs(route, "drop-only")
	    temp["elev"] = elevDist
	    temp["drop"] = dropDist
	    results[str(weight)] = temp	            
            if self.mode == "maximize":
                if (elevDist > self.best[2]) or (elevDist == self.best[2] and currDist < self.best[1]):
                    self.best = [route[:], currDist, elevDist, dropDist]
            else:
                if (dropDist > self.best[3]) or (dropDist == self.best[3] and currDist < self.best[1]):
                    self.best = [route[:], currDist,  elevDist, dropDist]
        return results


    def shortest_path(self, start_location, end_location, x, algo = "dijkstra", mode = "maximize"):
        G = self.G
        self.x = x/100.0
        self.mode = mode
        self.start_node, self.end_node = None, None
                    #[path, totalDist, totalElevGain, totalElevDrop]
        self.best = [[], 0.0, float('-inf'), float('-inf')]        
        #get shortest path
        self.start_node, d1 = ox.get_nearest_node(G, point=start_location, return_dist = True)
        self.end_node, d2   = ox.get_nearest_node(G, point=end_location, return_dist = True)
        if d1 > 100 or d2 > 100:
            print("Nodes too far")
            return None,None

        self.shortest_route = nx.shortest_path(G, source=self.start_node, target=self.end_node, weight='length')
        self.shortest_dist  = sum(ox.get_route_edge_attributes(G, self.shortest_route, 'length'))
            
        
        if algo == "dfs":
            print("dfs")
            self.dfs(self.start_node, self.end_node)        
        elif algo == "astar":
            print("astar")
            self.a_star()        
        print("dijkstra")
        self.all_dijkstra()       
        shortest_route_latlong = [[G.node[route_node]['x'],G.node[route_node]['y']] for route_node in self.shortest_route] 
        shortestPathStats = [shortest_route_latlong, self.shortest_dist, \
                            self.computeElevs(self.shortest_route, "gain-only"), self.computeElevs(self.shortest_route, "drop-only")]
        
        if (self.mode == "maximize" and self.best[2] == float('-inf')) or (self.mode == "minimize" and self.best[3] == float('-inf')):            
            return shortestPathStats, [[], 0.0, 0, 0]
        
        self.create_elevation_profile()
        # print(self.best)
        self.best[0] = [[G.node[route_node]['x'],G.node[route_node]['y']] for route_node in self.best[0]] 
        # print("===>end", self.best[1:])
        return shortestPathStats, self.best
