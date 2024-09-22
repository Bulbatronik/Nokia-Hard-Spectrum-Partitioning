from math import ceil

def occupy_spectrum(G, path, first_slot, num_slots):
    """This function occupies the spectrum of the links in the path."""
    # For each link ('node' and 'next node' pair) in the path
    for link in zip(path, path[1:]):
        # For each channel in the spectrum
        for slot_shift in range(num_slots):
            # Mark the channel as occupied
            G.edges[link]['spectrum_slots'][first_slot + slot_shift] = 1
            
def spectrum_occupation(G):
    """This function returns the number of occupied slots in the network."""
    num_slots_occupied = 0
    # Get the edges of the network
    E = list(G.edges())
    # For each link in the network
    for link in E:
        # Sum the number of occupied slots
        num_slots_occupied += sum(G.edges[link]['spectrum_slots'])
    return num_slots_occupied 

def clear_spectrum(G, num_slots):
    """This function clears the spectrum of all links in the network."""
    for link in G.edges:
        G.edges[link]['spectrum_slots'] = [0] * num_slots


def choose_MF(path_length, traffic, partitioning):
    """This function chooses the modulation format for a given path length and traffic."""
    # {traffic_request_Gbit/s: [(maximum_reach, number_of_slots)]}
    MF_option = {200: (900, 2), 400: (600, 3)}
    
    # Initialize variables
    min_slots = int(1e6)
    num_reg_min = 0
    max_slots = int(1e6)
    num_reg_max = 0
    traffic_G = 200*ceil(traffic/200)
    
    # Choose option with lowest number of slots 
    # with a sufficient reachability w.r.t. path length
    max_reach, num_slots = MF_option[traffic_G]
    # Can reach and enough slots -> No regeneration
    if path_length <= max_reach and num_slots < min_slots:
        min_slots = num_slots
    # Can't reach and enough slots -> Regeneration
    elif path_length > max_reach and num_slots < min_slots: 
        min_slots = ceil(path_length/max_reach)
        num_reg_min = ceil(path_length/max_reach)-1
    
    # Soft spectrum partitioning
    if partitioning == 'Soft': 
         # Last two outputs are not used for soft partitioning
        return min_slots, num_reg_min, None, None
    
    # Hard spectrum partitioning 
    elif partitioning == 'Hard':
        # Traffic request is 400 Gbps
        if traffic_G == 400:
            # Check if 200 Gbps is possible
            max_reach, num_slots = MF_option[traffic_G/2]
            # Can reach and enough slots -> No regeneration
            if path_length <= max_reach and 2*num_slots < max_slots:
                max_slots = 2*num_slots
            # Can't reach and enough slots -> Regeneration
            elif path_length > max_reach and num_slots < max_slots:
                max_slots = 2*ceil(path_length/max_reach)
                num_reg_max = 2*(ceil(path_length/max_reach)-1)
        # Return the number of slots and the number of regenerations
        # for the minimum and maximum modulation format
        return min_slots, num_reg_min, max_slots, num_reg_max