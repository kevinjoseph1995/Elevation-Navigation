a = Algorithms(G,0.5)
a.start_node,d1 = ox.get_nearest_node(G, point=(37.7792,-122.4991), return_dist = True)
a.end_node,d2 = ox.get_nearest_node(G, point=(37.756,-122.3889), return_dist = True)
a.shortest_route = nx.shortest_path(G, source=a.start_node, target=a.end_node, weight='length')
a.shortest_dist = sum(ox.get_route_edge_attributes(G, a.shortest_route, 'length'))
nxelev = a.computeElevs(a.shortest_route,"gain-only")
nxdrop = a.computeElevs(a.shortest_route,"drop-only")
RESULTS['Location5']['nx']['route'] = a.shortest_route
RESULTS['Location5']['nx']['distance'] = a.shortest_dist
RESULTS['Location5']['nx']['elev'] = nxelev
RESULTS['Location5']['nx']['drop'] = nxdrop
dres = a.all_dijkstra()
RESULTS['Location5']['max']['dijkstra'] = dres

%timeit a.dijkstra([1, True])
%timeit a.dijkstra([2, True])
%timeit a.dijkstra([3, True])
%timeit a.dijkstra([1, False])
%timeit a.dijkstra([2, False])
%timeit a.dijkstra([3, False])


========================================

a = Algorithms(G,0.5,"minimize")
a.start_node,d1 = ox.get_nearest_node(G, point=(37.7792,-122.4991), return_dist = True)
a.end_node,d2 = ox.get_nearest_node(G, point=(37.756,-122.3889), return_dist = True)
a.shortest_route = nx.shortest_path(G, source=a.start_node, target=a.end_node, weight='length')
a.shortest_dist = sum(ox.get_route_edge_attributes(G, a.shortest_route, 'length'))
nxelev = a.computeElevs(a.shortest_route,"gain-only")
nxdrop = a.computeElevs(a.shortest_route,"drop-only")
dresmin = a.all_dijkstra()
RESULTS['Location5']['min']['dijkstra'] = dresmin
RESULTS['Location5']['min']['astar'] = {}
RESULTS['Location5']['min']['astar']['route'] = a.best[0]
RESULTS['Location5']['min']['astar']['distance'] = a.best[1]
RESULTS['Location5']['min']['astar']['elev'] = a.best[2]
RESULTS['Location5']['min']['astar']['drop'] = a.best[3]

%timeit a.dijkstra([1, True])
%timeit a.dijkstra([2, True])
%timeit a.dijkstra([3, True])
%timeit a.dijkstra([1, False])
%timeit a.dijkstra([2, False])
%timeit a.dijkstra([3, False])
%timeit a.a_star()

