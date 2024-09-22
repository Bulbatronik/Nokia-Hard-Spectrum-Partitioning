
from spectrum import choose_MF, occupy_spectrum

def First_Fit(G, path, min_slots, max_slots, last_slot_75, partitioning):
    """First Fit spectrum assignment"""

    # Find the number of slots avalilable along the path (minimum)
    slots_in_band = min([len(G.edges[(a, b)]['spectrum_slots']) 
                         for a, b in zip(path, path[1:])])
    
    ######################## Soft spectrum partitioning
    if partitioning == 'Soft':
        # Find the first slot that can accommodate the demand
        for first_slot in range(slots_in_band - min_slots + 1):
            spectrum_is_free = True
            # For every link in the path
            for link in zip(path, path[1:]):
                # Check if the slots are free
                if sum(G.edges[link]['spectrum_slots'][first_slot : first_slot + min_slots]) != 0:
                    spectrum_is_free = False
                    break
            # If the spectrum is free, return the first and flag of optimal partitioning
            if spectrum_is_free:
                # We can always use the efficient partitioning for soft case 
                return first_slot, 0 
        # No spectrum available
        return None, None
    
    ######################## Hard spectrum partitioning
    elif partitioning == 'Hard':
        # If the number of slots is even, we can use the min_slots as 50 GHz
        if min_slots%2 == 0:
            slots_50 = min_slots
            slots_75 = max_slots
        # If the number of slots is odd, we can use the max_slots as 50 GHz
        else:
            slots_50 = max_slots
            slots_75 = min_slots
        
        # Find the first slot that can accommodate the demand within 50 GHz region (after last_slot_75)
        for first_slot in range(last_slot_75, slots_in_band - slots_50 + 1):
            spectrum_is_free = True
            # For every link in the path
            for link in zip(path, path[1:]):
                # Check if the slots are free
                if sum(G.edges[link]['spectrum_slots'][first_slot : first_slot + slots_50]) != 0:
                    spectrum_is_free = False
                    break
            # If the spectrum is free, return the first and flag of optimal partitioning
            if spectrum_is_free:
                return first_slot, 0
        
        # Find the first slot that can accommodate the demand within 75 GHz region (before last_slot_75)
        for first_slot in range(last_slot_75 - slots_75 + 1):
            spectrum_is_free = True
            # For every link in the path
            for link in zip(path, path[1:]):
                # Check if the slots are free
                if sum(G.edges[link]['spectrum_slots'][first_slot : first_slot + slots_75]) != 0:
                    spectrum_is_free = False
                    break
            # If the spectrum is free, return the first and flag of suboptimal partitioning
            if spectrum_is_free:
                return first_slot, 1
        # No spectrum available (both partitioningS)    
        return None, None


def k_SP_FF_RSA(G, k, k_SP_dict, path_lengths, traffic_dict, last_slot_75, partitioning): 
    """A function that computes the RSA for the k shortest paths between 
    each pair of nodes in the network (First Fit approach)"""
    # Initialize the list of chosen paths, number of regenerators and lost traffic
    chosen_paths = [] 
    num_reg = 0
    lost_traffic = 0
    
    # For each pair of nodes and their traffic between them
    for (src_id, dst_id), traffic_G_list in traffic_dict.items():
        for traffic_G in traffic_G_list:
            chosen_paths.append(-1)
            # For each shortest path between the nodes
            for path_ind, path in enumerate(k_SP_dict[(src_id, dst_id)]):
                # Choose MF that provisions traffic with lowest spectrum occupation
                path_length = path_lengths[((src_id, dst_id))][path_ind]
                min_slots, num_reg_min, max_slots, num_reg_max = choose_MF(path_length, traffic_G, partitioning) 
                
                # Select the first available spectrum channel
                first_slot, method = First_Fit(G, path, min_slots, max_slots, last_slot_75, partitioning)
                
                # Soft partitioning
                if partitioning == 'Soft':
                    # Always efficient
                    num_slots = min_slots
                    num_reg += num_reg_min
                # Hard partitioning
                elif partitioning == 'Hard':
                    # Efficient way
                    if method == 0:
                        num_slots = min_slots
                        num_reg += num_reg_min
                    # Inefficient way
                    else: 
                        num_slots = max_slots
                        num_reg += num_reg_max
                
                # If the spectrum is available, occupy it
                if first_slot != None:
                    occupy_spectrum(G, path, first_slot, num_slots)
                    chosen_paths[-1] = path_ind
                    break
                else:
                    # If the spectrum is not available, drop the traffic
                    lost_traffic+=traffic_G
    # Return the number of regenerators and lost traffic
    return num_reg, lost_traffic

