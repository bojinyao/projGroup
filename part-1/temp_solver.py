import networkx as nx
import os

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

def solve(graph, num_buses, size_bus, constraints):
    #TODO: Write this method as you like. We'd recommend changing the arguments here as well

    res = [[] for _ in range(num_buses)]
    nodes = list(graph.nodes)
    for i in range(len(nodes)):
        bus_index = i % num_buses
        res[bus_index].append(nodes[i])
    
    return res

def main():
    size_categories = ['small', 'medium', 'large']
    for size in size_categories:
        graph, num_buses, size_bus, constraints = parse_input(path_to_inputs + '/' + size)
        solution = solve(graph, num_buses, size_bus, constraints)
        output_file = open(path_to_outputs + "/" + size + ".out", "w")
        for lst in solution:
            output_file.write(str(lst))
            output_file.write("\n")

        output_file.close()


main()