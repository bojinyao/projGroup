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


def transfer_node_w_index(partitions, node, from_bus_index, to_bus_index):
    """[Custom] Transfer node from_bus_index to_bus_index
    returns None
    """
    partitions[from_bus_index].remove(node)
    partitions[to_bus_index].add(node)

def transfer_node(node, from_bus, to_bus):
    """[Custom] node from_bus to_bus, no indices needed
    returns None
    """
    from_bus.remove(node)
    to_bus.add(node)

def rowdy_group_presence(nodes, rowdy_groups):
    """[Custom] Calculate number of groups each node belongs to
    Returns a dictionary with key=node, val=count
    """
    presence_counts = {n : 0 for n in nodes}
    for group in rowdy_groups:
        for n in group:
            presence_counts[n] += 1
    return presence_counts

# Temporary Global Vars
DISPLAYCOUNT = False
SHOWBUSINFO = False

def solve(input_name, graph, num_buses, size_bus, constraints):
    #TODO: Write this method as you like. We'd recommend changing the arguments here as well
    nodes = list(graph.nodes)
    if num_buses == 1: # special case for one group...
        return [nodes]
    num_nodes = len(nodes)
    # PARTITIONING: 
    # Assign students to mininum number of buses needed to preserve friendships
    (unused_edgecuts, parts) = metis.part_graph(graph, num_buses)
    partitions = [set() for _ in range(num_buses)] # Buses are actually represented as sets, only printed as lists
    for i in range(num_nodes):
        partitions[parts[i]].add(nodes[i])


    node_degrees = {n : graph.degree[n] for n in nodes}
    rowdy_groups = [set(group) for group in constraints]
    presence_counts = rowdy_group_presence(nodes, rowdy_groups)

    # Making sure every bus has the right number of nodes
    extra_buses = [i for i in range(num_buses) if len(partitions[i]) == 0]
    num_extra_buses = len(extra_buses)
    buses_used = num_buses - num_extra_buses
    bus_overflows = [[] for _ in range(num_buses)]
    for bus_index in range(num_buses):
        curr_bus = partitions[bus_index]
        if len(curr_bus) > size_bus:
            num_over = len(curr_bus) - size_bus
            cutoff_nodes = sorted(list(curr_bus), key=lambda n: presence_counts[n], reverse=True)[0:num_over]
            for n in cutoff_nodes:
                curr_bus.remove(n)
            bus_overflows[bus_index].extend(cutoff_nodes)
    
    cur_bus_sizes = [len(partitions[i]) for i in range(num_buses)]
    # Greedily distribute the cutoff nodes starting from buses of smallest sizes (least like to create rowdy group)

    # TAKING CARE OF ROWDY GROUPS
    # old insert ->
    for bus_index in range(num_buses):
        curr_bus = partitions[bus_index]
        for group_index in range(len(rowdy_groups)):
            curr_group = rowdy_groups[group_index]
            if curr_group.issubset(curr_bus):
                # if rowdy group present, switch the one with min edges
                # with min edge one from previous bus (mod)
                transfer = min(curr_group, key=lambda n: node_degrees[n])
                prev_bus_index = bus_index - 1
                transfer_node_w_index(partitions, transfer, bus_index, prev_bus_index)

                back_transfer = min(partitions[prev_bus_index], key=lambda n: node_degrees[n])
                transfer_node_w_index(partitions, back_transfer, prev_bus_index, bus_index)
                
                # print(f"In {input_name}, {transfer} <-> {back_transfer} switched bus: {bus_index}, {prev_bus_index}")
    

    # RESULT CHECK
    if SHOWBUSINFO:
        for i in range(num_buses):
            l = len(partitions[i])
            if l == 0:
                print(f"{input_name} line {i} is an empty bus")
            if l > size_bus:
                print(f"{input_name} line {i} has too many nodes")
    return partitions
    
    # old <-
    # extra_buses = [i for i in range(num_buses) if len(partitions[i]) == 0]
    # num_extra_buses = len(extra_buses)
    # buses_used = num_buses - num_extra_buses
    # if num_extra_buses > 0:     
    #     bus_select = 0
    #     for bus in partitions:
    #         for group in rowdy_groups:
    #             if group.issubset(bus):
    #                 # if rowdy group present, send one with most rowdy group presence to an empty bus
    #                 # fill up empty buses first this way
    #                 transfer = max(group, key=lambda n: presence_counts[n])
    #                 dest_bus = partitions[extra_buses[bus_select % num_extra_buses]]
    #                 transfer_node(transfer, bus, dest_bus)
    #                 bus_select += 1
    #                 # print(f"In {input_name} Transferred {transfer} to {dest_bus}")
    # else:

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
                output_file.write(str(list(lst)))
                output_file.write("\n")

            output_file.close()

            # Print stuff start > uncomment when actually running the algorithm
            count += 1 
            if DISPLAYCOUNT:
                print(f"Finished {count}/{file_counts[size]}", end="\r")
        print(f"Done with {size}.")
        # Print stuff end <

if __name__ == '__main__':
    main()


