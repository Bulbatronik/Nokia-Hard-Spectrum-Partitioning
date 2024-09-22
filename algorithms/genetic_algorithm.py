import copy

# Import the necessary classes and functions from jmetal
from jmetal.core.solution import IntegerSolution
from jmetal.core.problem import IntegerProblem
import jmetal.algorithm.singleobjective.genetic_algorithm
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.operator.mutation import IntegerPolynomialMutation
from jmetal.operator.crossover import IntegerSBXCrossover
from jmetal.operator.selection import RouletteWheelSelection
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.util.constraint_handling import overall_constraint_violation_degree

from algorithms.first_fit import First_Fit
from spectrum import choose_MF, occupy_spectrum, spectrum_occupation, clear_spectrum


def _fixed_replacement(self, population, offspring_population):
    population.extend(offspring_population)
    population.sort(key=lambda s: (-overall_constraint_violation_degree(s), s.objectives[0]))
    return population[: self.population_size]

jmetal.algorithm.singleobjective.genetic_algorithm.GeneticAlgorithm.replacement = _fixed_replacement


def GenAlg(G, k, paths_dict, len_p, D, last_slot_75, partitioning):
    """A function that computes the RSA for the k shortest paths using a Genetic Algorithm."""
    algorithm = GeneticAlgorithm(
                                problem = RoutingProblem(k, G, paths_dict,len_p, D, last_slot_75, partitioning),
                                population_size = 250,
                                offspring_population_size = 250,
                                mutation = IntegerPolynomialMutation(probability= 0.01),
                                crossover = IntegerSBXCrossover(probability=0.8),
                                selection = RouletteWheelSelection(),
                                termination_criterion = StoppingByEvaluations(max_evaluations=5000)
                                )
        
    algorithm.run()
    result = algorithm.result()
    return result.attributes['num_reg'], result.attributes['lost_traff']


class RoutingProblem(IntegerProblem):
    """ Class representing the Routing and Spectrum Allocation (RSA) problem."""
    def __init__(self, k, G, k_SP_dict, path_lengths, traffic_dict, last_slot_75, partitioning):
        super(RoutingProblem, self).__init__()
        
        # save shortest paths, traffic and graph
        self.k = k
        self.G = copy.deepcopy(G)
        self.last_slot_75 = last_slot_75
        self.partitioning = partitioning
        self.k_SP_dict = copy.deepcopy(k_SP_dict)
        self.traffic_dict = copy.deepcopy(traffic_dict)
        self.path_lengths = copy.deepcopy(path_lengths)
        self.src_dst_pair_list = list(self.traffic_dict.keys())
        
        # Spectrum allocationc optimization problem
        self._number_of_objectives = 1
        
        # One variable and one constraint for each demand
        demands = sum([len(traffic_dict[key]) for key in traffic_dict.keys()])
        self._number_of_variables = demands
        self._number_of_constraints = demands
        
        # Bounds for the variables
        self.lower_bound = [0] * self._number_of_variables
        self.upper_bound = [self.k - 1] * self._number_of_variables
        
    def evaluate(self, solution: IntegerSolution) -> IntegerSolution:
        # Clear the spectrum
        clear_spectrum(self.G, 176)
        
        # Initialize number of regenerators and lost traffic
        lost_traff = 0
        num_reg = 0
        
        # For each request
        for request_index, path_index in enumerate(solution.variables):
            # Try to allocate the spectrum
            solution.constraints[request_index], reg, lost = self.allocate_spectrum(request_index, path_index)
            # Update the number of regenerators and lost traffic
            lost_traff += lost
            num_reg += reg

        # Update the objectives    
        solution.objectives[0] = spectrum_occupation(self.G)
        # Update the attributes
        solution.attributes['lost_traff'] = lost_traff
        solution.attributes['num_reg'] = num_reg
        return solution
    
    def allocate_spectrum(self, request_index, path_index):
        # Initialize the variables for the request and path
        value = 0
        ri = 0
        
        # Find the source and destination pair
        for key in self.traffic_dict.keys():
            ri=0
            for _ in range(len(self.traffic_dict[key][0])):
                if value == request_index:
                    break
                ri+=1
                value += 1# BREAK FROM BOTH LOOPS
            if value == request_index:
                break
        
        src_dst_pair = key

        # Find the path, traffic and path length        
        path = self.k_SP_dict[src_dst_pair][path_index]
        traffic_G = self.traffic_dict[src_dst_pair]
        path_length = self.path_lengths[src_dst_pair][path_index]
        
        # Choose MF that provisions traffic with lowest spectrum occupation
        min_slots, num_reg_min, max_slots, num_reg_max = choose_MF(path_length, traffic_G[0][ri-1], self.partitioning) 
        
        # Select the first available spectrum channel
        first_slot, method = First_Fit(self.G, path, min_slots, max_slots, self.last_slot_75, self.partitioning)

        # Soft partitioning
        if self.partitioning == 'Soft':
            # Always efficient
            num_slots = min_slots
            num_reg = num_reg_min
        # Hard partitioning
        elif self.partitioning == 'Hard':
            # Efficient way
            if method == 0:# efficient way (for soft always efficient)
                num_slots = min_slots
                num_reg = num_reg_min
            # Inefficient way
            else:
                num_slots = max_slots
                num_reg = num_reg_max
            
        # If the spectrum is available, occupy it
        if first_slot != None:
            occupy_spectrum(self.G, path, first_slot, num_slots)
            return 1, 0, num_reg
        else:
            # If the spectrum is not available, drop the traffic
            lost_traffic = traffic_G[0][ri-1]
            return -1, num_reg, lost_traffic

    # Required methods for the class 
    def name(self):
        return 'Routing'
    
    def number_of_constraints(self):
        return self._number_of_constraints
    
    def number_of_objectives(self):
        return self._number_of_objectives
    
    def number_of_variables(self):
        return self._number_of_variables
    