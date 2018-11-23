import networkx as nx
import os

import metis
import math
import output_scorer as scorer

###########################################
# Change this variable to the path to 
# the folder containing all three input
# size category folders
###########################################
path_to_inputs = "./all_inputs"

###########################################
# Change this variable if you want
# your outputs to be put in a 
# different folder
###########################################
path_to_outputs = "./all_outputs"

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

def solve(input_name, graph, num_buses, size_bus, constraints):
    #TODO: Write this method as you like. We'd recommend changing the arguments here as well
    
    nodes = list(graph.nodes)
    if num_buses == 1: # special case for one group...
        return [nodes]
    num_nodes = len(nodes)

    # PARTITIONING: 
    # Assign students to mininum number of buses needed to preserve friendships
    (unused_edgecuts, parts) = metis.part_graph(graph, num_buses)

    # TAKING CARE OF ROWDY GROUPS
    buses_used = max(parts) + 1
    num_extra_buses = num_buses - buses_used

    partitions = [[] for _ in range(num_buses)]
    for i in range(num_nodes):
        partitions[parts[i]].append(nodes[i])
    

    # RESULT CHECK
    for i in range(num_buses):
        l = len(partitions[i])
        if l == 0:
            print(f"{input_name} line {i} is an empty bus")
        if l > size_bus:
            print(f"{input_name} line {i} has too many nodes")
    return partitions
    

def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        The student should modify `solve` to return their solution and modify
        the portion which writes it to a file to make sure their output is
        formatted correctly.
    '''
    # size_categories = ["small", "medium", "large"]
    size_categories = ["small"]
    file_counts = {"small": 331, "medium": 331, "large": 100}
    if not os.path.isdir(path_to_outputs):
        os.mkdir(path_to_outputs)

    for size in size_categories:
        # Print stuff start >
        print(f"Directory: {size}, Files: {file_counts[size]}")
        count = 0
        # Print stuff end <

        category_path = path_to_inputs + "/" + size
        output_category_path = path_to_outputs + "/" + size
        category_dir = os.fsencode(category_path)
        
        if not os.path.isdir(output_category_path):
            os.mkdir(output_category_path)

        for input_folder in os.listdir(category_dir):
            input_name = os.fsdecode(input_folder) 
            graph, num_buses, size_bus, constraints = parse_input(category_path + "/" + input_name)
            # print("Working on {}".format(input_name))
            solution = solve(input_name, graph, num_buses, size_bus, constraints)
            output_file = open(output_category_path + "/" + input_name + ".out", "w")

            #TODO: modify this to write your solution to your 
            #      file properly as it might not be correct to 
            #      just write the variable solution to a file
            # output_file.write(solution)
            for lst in solution:
                output_file.write(str(lst))
                output_file.write("\n")

            output_file.close()

            # Print stuff start > uncomment when actually running the algorithm
            count += 1 
            print(f"Finished {count}/{file_counts[size]}", end="\r")
        print(f"Done with {size}.")
        # Print stuff end <

if __name__ == '__main__':
    main()


