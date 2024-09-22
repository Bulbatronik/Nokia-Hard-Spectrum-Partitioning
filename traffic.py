import random
import numpy as np

class DemandList(dict):
    """A dictionary that maps keys to lists."""
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(DemandList, self).__setitem__(key, [])
        self[key].append(value)
        
def generate_traffic(demands, nodes):
    """Generate a list of demands for a network with a given number of nodes."""
    D = DemandList()
    for _ in range(demands):
        # Generate random source and destination nodes
        s_d = random.sample(range(0, nodes), 2)
        # Append the demand to the list of demands for the source-destination pair
        D[(s_d[0], s_d[1])] = np.random.choice([100,150,200,250,300,350,400]).tolist()
    return D