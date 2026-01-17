import osmnx as ox
import networkx as nx
import itertools
import numpy as np
import os
from shapely.geometry import LineString

# --- CHANGE 1: Load Map (With Caching to fix timeout issues) ---
# We save the map to a file so we don't have to download it every time we restart
map_file = "bengaluru_drive.graphml"

if os.path.exists(map_file):
    print(f"Loading cached map data from {map_file}...")
    G = ox.load_graphml(map_file)
else:
    print("Downloading map data for Bengaluru... this may take a minute...")
    G = ox.graph_from_place("Bengaluru, Karnataka, India", network_type='drive')
    G = ox.add_edge_speeds(G)  # Adds speed limit data
    G = ox.add_edge_travel_times(G)  # Adds estimated travel time for edges
    # Save it for next time
    try:
        ox.save_graphml(G, map_file)
    except Exception as e:
        print(f"Warning: Could not save map cache: {e}")

# --- CHANGE 2: Warehouse Location (Bengaluru Central) ---
# Latitude, Longitude (Near MG Road/Cubbon Park)
warehouse_location = (12.9716, 77.5946)
print("Warehouse Location:", warehouse_location[1], warehouse_location[0])

# Find the nearest node on the map to our warehouse coordinates
warehouse_node = ox.distance.nearest_nodes(G, warehouse_location[1], warehouse_location[0])

def optimal_route(delivery_locations):
    # Convert delivery GPS (lat, lon) to nearest map nodes
    # Note: ox.nearest_nodes takes (G, X=Longitude, Y=Latitude)
    delivery_nodes = [ox.distance.nearest_nodes(G, lon, lat) for lat, lon in delivery_locations]
    
    # Combine warehouse + delivery nodes
    all_nodes = [warehouse_node] + delivery_nodes

    # Compute shortest paths between all locations
    distance_matrix = {}
    shortest_paths = {}
    
    for i in range(len(all_nodes)):
        for j in range(len(all_nodes)):
            if i != j:
                try:
                    # Calculate shortest path by length (distance)
                    path = nx.shortest_path(G, all_nodes[i], all_nodes[j], weight="length")
                    shortest_paths[(i, j)] = path
                    
                    # Calculate the actual length in meters
                    dist = nx.shortest_path_length(G, all_nodes[i], all_nodes[j], weight="length")
                    distance_matrix[(i, j)] = dist
                except nx.NetworkXNoPath:
                    # Fallback if a specific node is unreachable
                    distance_matrix[(i, j)] = float('inf')

    print("Distance Matrix Computed")

    # --- TSP ALGORITHM (Traveling Salesman Problem) ---
    def get_distance(u, v):
        return distance_matrix.get((u, v), float('inf'))

    def tsp(nodes):
        n = len(nodes)
        dp = {}
        parent = {}

        def dp_rec(mask, last):
            if mask == (1 << n) - 1:  # All nodes visited
                return get_distance(last, 0)  # Return to warehouse

            if (mask, last) in dp:
                return dp[(mask, last)]

            best_cost = float('inf')
            for i in range(n):
                if mask & (1 << i) == 0:  # If node i unvisited
                    new_mask = mask | (1 << i)
                    cost = get_distance(nodes[last], nodes[i]) + dp_rec(new_mask, i)
                    if cost < best_cost:
                        best_cost = cost
                        parent[(mask, last)] = i

            dp[(mask, last)] = best_cost
            return best_cost

        start_mask = 1  # Start with warehouse visited
        result = dp_rec(start_mask, 0)

        # Reconstruct path
        path = []
        mask = start_mask
        last = 0
        while (mask, last) in parent:
            next_node = parent[(mask, last)]
            path.append(nodes[next_node])
            mask |= (1 << next_node)
            last = next_node

        path.append(0)  # Return to warehouse
        return result, path

    # Prepare nodes for TSP
    nodes_indices = sorted(list(range(len(all_nodes))))
    
    # Run TSP
    shortest_distance, shortest_path_indices = tsp(nodes_indices)
    
    # Adjust path format
    if len(shortest_path_indices) > 1:
        # Ensure it starts at 0 (warehouse)
        if shortest_path_indices[0] != 0:
             shortest_path_indices = [0] + shortest_path_indices
    
    print("Shortest Distance (meters):", shortest_distance)
    print("Optimal Path Indices:", shortest_path_indices)

    # Convert indices back to map nodes
    optimized_route_nodes = [all_nodes[i] for i in shortest_path_indices]

    # --- Reconstruct Lat/Lon Path for Map Visualization ---
    full_route_latlon = []  

    for i in range(len(optimized_route_nodes) - 1):
        u_node = optimized_route_nodes[i]
        v_node = optimized_route_nodes[i+1]
        
        # Get indices in our local list to look up the cached path
        u_idx = all_nodes.index(u_node)
        v_idx = all_nodes.index(v_node)

        if (u_idx, v_idx) in shortest_paths:
            path_nodes = shortest_paths[(u_idx, v_idx)]
            
            # For every segment in this path, get the geometry
            for u, v in zip(path_nodes[:-1], path_nodes[1:]):
                if G.has_edge(u, v):
                    edge_data = G.get_edge_data(u, v)
                    # Handle multiple edges between nodes
                    if isinstance(edge_data, dict): 
                        # just take the first one (key=0 usually)
                        first_key = list(edge_data.keys())[0]
                        data = edge_data[first_key]
                    else:
                        data = edge_data

                    if "geometry" in data:
                        # Use actual curved road shape
                        line = data["geometry"]
                        road_points = list(zip(line.xy[1], line.xy[0])) # (lat, lon)
                        full_route_latlon.extend(road_points)
                    else:
                        # Straight line fallback
                        lat1, lon1 = G.nodes[u]['y'], G.nodes[u]['x']
                        lat2, lon2 = G.nodes[v]['y'], G.nodes[v]['x']
                        full_route_latlon.append((lat1, lon1))
                        full_route_latlon.append((lat2, lon2))
    
    # Add final point
    last_node = optimized_route_nodes[-1]
    full_route_latlon.append((G.nodes[last_node]['y'], G.nodes[last_node]['x']))

    # Compute breakdown distances
    route_distances = []
    current_dist = 0
    for i in range(len(shortest_path_indices) - 1):
        start = shortest_path_indices[i]
        end = shortest_path_indices[i + 1]
        dist = distance_matrix.get((start, end), 0)
        current_dist += dist
        
        # --- FIX: Force convert NumPy float to standard Python float ---
        standard_float_dist = float(round(current_dist / 1000, 2))
        route_distances.append(standard_float_dist)

    return full_route_latlon, shortest_path_indices, route_distances