import networkx as nx
import os

# extra imports from solver.py
import metis
import math

###########################################
# Change this variable to the path to 
# the folder containing all three input
# size category folders
###########################################
path_to_inputs = "./inputs"

###########################################
# Change this variable if you want
# your outputs to be put in a 
# different folder
###########################################
path_to_outputs = "./outputs"

def parse_input(folder_name):
    '''
        Parses an input and returns the corresponding graph and parameters

        Inputs:
            folder_name - a string representing the path to the input folder

        Outputs:
            (graph, num_buses, size_bus, constraints)
            graph - the graph as a NetworkX object
            num_buses - an integer representing the number of buses you can allocate to
            size_buses - an integer representing the number of students that can fit on a bus
            constraints - a list where each element is a list vertices which represents a single rowdy group
    '''
    graph = nx.read_gml(folder_name + "/graph.gml")
    parameters = open(folder_name + "/parameters.txt")
    num_buses = int(parameters.readline())
    size_bus = int(parameters.readline())
    constraints = []
    
    for line in parameters:
        line = line[1: -2]
        curr_constraint = [num.replace("'", "") for num in line.split(", ")]
        constraints.append(curr_constraint)

    return graph, num_buses, size_bus, constraints


###########################################################
# IMPORTANT Algorithms we can use to help partition the graph
# Algorithm must return a set of nodes, and only require 
# graph as input nothing else
from networkx.algorithms import approximation

"""
Partition a graph using vertex cover algorithm
@param graph: graph itself
@param nodes: all nodes in the graph (optimization)
@return a list of lists (of nodes) as a partition of the graph
"""
def vertex_cover_partition(graph, nodes):
    prime_nodes = approximation.min_weighted_vertex_cover(graph)
    return ''


"""
Partition a graph using dominating set algorithm
@param graph: graph itself
@param nodes: all nodes in the graph (optimization)
@return a list of lists (of nodes) as a partition of the graph
"""
def dominating_set_partition(graph, nodes):
    prime_nodes = nx.dominating_set(graph)
    return ''

"""
Partition a graph based on nodes with degrees higher than average
A greedy approach to this problem itself
@param graph: graph itself
@param nodes: all nodes in the graph (optimization)
@return a list of lists (of nodes) as a partition of the graph
"""
def vertex_degree_partition(graph, nodes):
    return ''

##############
# Global Var #
algos = [vertex_cover_partition, dominating_set_partition]
##############


# if nx.is_connected(graph):
#         for algorithm in algos: # GLOBAL var used here
#             partitions = algorithm(graph, nodes)

#     else:
#         all_components = nx.connected_components(graph)
#         num_components = nx.is_connected(graph)
#         for component in all_components:
#             return 
def solve(graph, num_buses, size_bus, constraints):
    #TODO: Write this method as you like. We'd recommend changing the arguments here as well
    nodes = list(graph.nodes)
    if num_buses == 1:
        return [nodes]
    num_nodes = len(nodes)
    min_buses_needed = math.ceil(float(num_nodes) / float(size_bus))
    num_extra_buses = num_buses - min_buses_needed

    # Assign students to mininum number of buses needed to preserve friendships
    (unused_edgecuts, parts) = metis.part_graph(graph, min_buses_needed)
    partitions = [[] for _ in range(num_buses)]
    for i in range(num_nodes):
        partitions[parts[i]].append(nodes[i])

    # dealing with rowdy groups
    if num_extra_buses > 0:
        #do something

    else:
        #do something else

    return partitions




def main():
    size_categories = ['tiny']
    for size in size_categories:
        graph, num_buses, size_bus, constraints = parse_input(path_to_inputs + '/' + size)
        solution = solve(graph, num_buses, size_bus, constraints)
        output_file = open(path_to_outputs + "/" + size + ".out", "w")
        for lst in solution:
            output_file.write(str(lst))
            output_file.write("\n")

        output_file.close()


main()