from itertools import islice
import networkx as nx

def k_shortest_paths(G, N, k):
    """A function that computes the k shortest paths between 
    each pair of nodes in the network (Brute-force approach)"""
    # Paths and their lengths
    paths_dict, len_p = {}, {}
    # For each pair of nodes
    for src_id in N:
        for dst_id in N:
            # Skip the same node
            if src_id == dst_id:
                continue        
            # Compute the k shortest paths between the nodes
            paths_dict[(src_id, dst_id)] = list(islice(nx.shortest_simple_paths(G, src_id, dst_id, weight='weight'), k)) 
            # Compute the lengths of the paths
            paths_list = paths_dict[(src_id, dst_id)]
            len_p[(src_id, dst_id)] = [nx.path_weight(G, path, weight="weight") for path in paths_list]
    return paths_dict, len_p