
<h1 align="center">
  <h1 align="center">Hard Spectrum Partitioning</h1>
  <img src="https://www.vanillaplus.com/wp-content/uploads/2023/02/NOKIA-new-logo.png" alt="Nokia Logo">
</h1>

*The project was developed with Ignazio Maria Castrignano in collaboration with [**Nokia BELL LABs Vimercate**](https://www.bell-labs.com) under the supervision of <ins>Annalisa Morea</ins>.*

## Overview

The problem formulation and the assistance for the project was provided by **Nokia BELL LABs Vimercate** within the initiative *Adopt a course* between the companies and Politecnico di Milano.

The goal of the project is to assess overall spectral efficiency in a network with multiple channel widths, where the fiber spectrum is hardly divided into 2 sections: 50GHz and 75GHz. For each service, the tool must decide if it is better to route it using modulation formats at 50GHz or 75GHz bandwidth; and the optical channel is routed only in the spectrum part associated with its width. A more illustrative description of the `Routing and Spectrum Allocation (RSA)` problem is provided in [this file](materials/CND_Lab3_2023.pdf).

The objective is to implement the behavior described above, computing spectrum occupation as a function of increasing traffic. Compare these results with another scenario where the channel width is an input, and it is possible to allocate a 75GHz channel in a 50GHz spectrum region (or vice versa) without restriction `(Soft Partitioning)`.

The results are simulated over a `continental` and `national` optical networks. Objective-wise, we try to minimize the `blocking probability` of the routed traffic and the `overall cost` of the network (OEO devices for add/drop and regeneration). 



## Approach
### 1. Traffic Generation 
In order to simulate the demands between the nodes, we start by creating a graph representing the topology. In order to see the specifications and constraints of each topology, refer to the tables in [Projects Nokia_Short.pdf](materials/Final%20Presentation%20Project%208.pdf). Each demand is stored inside a dictionary, where a tuple `(s, d)` represents the source and destination nodes, and the corresponding key is a `list of traffic demands` to be routed between the pair of nodes. 


### 2. Algorithms
First, our approach was to solve the problem directly using the `optimization` techniques provided in [this paper](materials/Designing_Operating_and_Reoptimizing_Elastic_Optical_Networks.pdf) and adapted to include the cost of regenerations. The solution was feasible for a network with 10 links and 100 demands in a considerable amount of time, which was infeasible for a larger network/traffic due to the computation constraints. After the unsuccessful attempt, we decided to use `heuristic methods`, as they are, generally, faster and more scalable. 

#### 2.1 Mixed Integer Linear Problem (MILP)

We start by formulating the problem for `soft spectrum partitioning` as a `MILP`. Our goal is to minimize the sum of the total blocked traffic plus the cost of the regenerations. In order to solve the optimization problem, we used [`Gurobipy`](https://support.gurobi.com/hc/en-us). By setting up the constraints and a set of variables, we have not been able to solve the problem due to its large scale even without the constraints on the hard partitioning.  

#### 2.2 First Fit Approach
The first heuristic we applied was the `First Fit method`. The basic idea behind it is to compute *k* shortest paths between a pair of nodes. Then for each demand between the nodes, we try to route it using the first available shortest path. This approach is suboptimal, particularly for a small number of *k*, but it is extremely fast in comparison to the other algorithms.

#### 2.3 Genetic Algorithm
The metaheuristic algorithm is inspired by the process of natural selection that belongs to the larger class of **evolutionary algorithms (EA)**. One candidate solution in `Genetic Algorithm` is called **Chromosome**. One value of the Chromosome is called **Gene**. All the calculated Chromosomes are 
called Population. Taking the best candidate populations as **Parents**, then taking the best offsprings and make them **Parents**, and so one until the best solution is found.

In our case, we use [`jMetalPy`](https://github.com/jMetal/jMetalPy) library due to its simplicity and support of a large variety of metaheuristic algorithms. Our goal is to optimize thee total spectrum allocation while using as a binary variable if a specific demand was routed successfully or not while satisfying the constraints.


### 3. Simulation 
We perform the simulation over each topology for both algorithms using both partitioning. To analyze the `hard spectrum partitioning` we define a hyperparameter, which controls the percentage of spectrum allocated to 75GHz channels. We continuously increase the number of demands by 50 until the blocking probability exceeds 1%. Since the traffic for each number of demands is random, we perform multiple `Monte Carlo simulations` and record the mean value of the cost and blocking probability with confidence intervals. 

### 4. Results
The final results are presented [this file](materials/Final%20Presentation%20Project%208.pdf). The presentation was held at the office of Nokia and received the maximum grade for the project. 


## Miscellaneous
The folder `miscellaneous` includes the homework/lab assignments during the course `Communication Network Design` done using [`Net2Plan`](https://www.net2plan.com/) software *with Esat Ince*.
