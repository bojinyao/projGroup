import networkx as nx
import os

import metis
import math
import output_scorer as scorer
import sys
import time

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


def second_smallest(numbers):
    """Find the second smallest number in an iterable
    From StackOverFlow: 
    https://stackoverflow.com/questions/26779618/python-find-second-smallest-number
    """
    m1, m2 = float('inf'), float('inf')
    for x in numbers:
        if x <= m1:
            m1, m2 = x, m1
        elif x < m2:
            m2 = x
    return m2

def transfer_node_w_index(partitions, node, from_bus_index, to_bus_index):
    """[Custom] Transfer node from_bus_index to_bus_index
    returns None
    """
    partitions[from_bus_index].remove(node)
    partitions[to_bus_index].add(node)

def transfer_node(node, from_set, to_set):
    """[Custom] node from_bus to_bus, no indices needed
    returns None
    """
    from_set.remove(node)
    to_set.add(node)

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
DisplayCount = True
DoSanityCheck = False

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
    empty_buses_indices = [i for i in range(num_buses) if len(partitions[i]) == 0]
    num_empty_buses = len(empty_buses_indices)
    buses_used = num_buses - num_empty_buses
    # bus_overflows = [[] for _ in range(num_buses)] #unused keep around for future use 
    all_overflows = []
    num_overflows = 0
    for bus_index in range(num_buses):
        curr_bus = partitions[bus_index]
        if len(curr_bus) > size_bus:
            num_over = len(curr_bus) - size_bus
            cutoff_nodes = sorted(list(curr_bus), key=lambda n: presence_counts[n], reverse=True)[0:num_over]
            for n in cutoff_nodes:
                # make sure no bus has too many nodes
                curr_bus.remove(n)
            # bus_overflows[bus_index].extend(cutoff_nodes) #unused keep around for future use 
            all_overflows.extend(cutoff_nodes)
    num_overflows = len(all_overflows)
    all_overflows.sort(key=lambda n: node_degrees[n], reverse=True) # nodes with least degrees get popped first
    # Greedily distribute the cutoff nodes starting from buses of smallest sizes (least likely to create rowdy group)
    # An unlikely special case
    if num_empty_buses > 0 and num_overflows < num_empty_buses: # unlikely to happen
        # exhaust overflows first
        empty_buses_select = 0
        while empty_buses_select < num_overflows:
            to_bus = partitions[empty_buses_indices[empty_buses_select]]
            to_bus.add(all_overflows.pop())
            empty_buses_select += 1
        # fill up rest of the empty buses
        counter = 0
        while empty_buses_select < num_empty_buses:
            curr_bus = partitions[counter % num_buses]
            if len(curr_bus) > 1:
                transfer = min(curr_bus, key=lambda n: node_degrees[n])
                transfer_node_w_index(partitions, transfer, counter % num_buses, empty_buses_indices[empty_buses_select])
                empty_buses_select += 1
            counter += 1
    else: 
        if num_empty_buses > 0: 
            # much more likely to happen
            # fill up all empty buses first
            empty_buses_select = 0
            while empty_buses_select < num_empty_buses:
                to_bus = partitions[empty_buses_indices[empty_buses_select]]
                to_bus.add(all_overflows.pop())
                empty_buses_select += 1

        #BUG did not consider the case when all_overflows is empty while there are empty buses
        #BUG when all_over_flow is empty, need to fill up empty buses with stuff from other buses
        # For all remaining extra nodes, fill up remaining buses from the lowest
        # evenly up.
        curr_bus_sizes = {len(partitions[i]) for i in range(num_buses)}
        bar = second_smallest(curr_bus_sizes)
        while len(all_overflows) > 0:
            for bus_index in range(num_buses):
                curr_bus = partitions[bus_index]
                if len(curr_bus) < bar and len(all_overflows) > 0:
                    curr_bus.add(all_overflows.pop())
            curr_bus_sizes = {len(partitions[i]) for i in range(num_buses)}
            bar = second_smallest(curr_bus_sizes)
    
    # TAKING CARE OF ROWDY GROUPS
    # Fill up remaining empty buses
    curr_bus_sizes = {len(partitions[i]) for i in range(num_buses)}
    bar = min(second_smallest(curr_bus_sizes), size_bus) # upper limit on number of nodes placed in empty buses

    empty_buses_indices = [i for i in range(num_buses) if len(partitions[i]) == 0]
    num_empty_buses = len(empty_buses_indices)
    if num_empty_buses > 0:
        num_nodes_delegated = 0
        empty_buses_select = 0

        for bus_index in range(num_buses):
            curr_bus = partitions[bus_index]
            for group_index in range(len(rowdy_groups)):
                curr_group = rowdy_groups[group_index]
                if curr_group.issubset(curr_bus) \
                and (float(num_nodes_delegated) / float(num_empty_buses)) <= bar:
                    transfer = max(curr_group, key=lambda n: presence_counts[n])
                    dest_bus_index = empty_buses_indices[empty_buses_select % num_empty_buses]
                    transfer_node_w_index(partitions, transfer, bus_index, dest_bus_index)
                    num_nodes_delegated += 1
                    empty_buses_select += 1

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
    
    # All remaining empty buses can be filled with nodes with min edges
    empty_buses_indices = [i for i in range(num_buses) if len(partitions[i]) == 0]
    num_empty_buses = len(empty_buses_indices)
    if num_empty_buses > 0:
        empty_buses_select = 0
        while empty_buses_select < num_empty_buses:
            for bus_index in range(num_buses):
                curr_bus = partitions[bus_index]
                if len(curr_bus) > 1 and empty_buses_select < num_empty_buses:
                    transfer = min(curr_bus, key=lambda n: node_degrees[n])
                    transfer_node_w_index(partitions, transfer, bus_index, empty_buses_indices[empty_buses_select])
                    empty_buses_select += 1

    # RESULT CHECK
    if DoSanityCheck:
        for i in range(num_buses):
            l = len(partitions[i])
            if l == 0:
                print(f"{input_name} line {i} is an empty bus")
            if l > size_bus:
                print(f"{input_name} line {i} has too many nodes")
        all_node_counts = {n : 0 for n in nodes}
        for bus in partitions:
            for node in bus:
                all_node_counts[node] += 1
        for node, count in all_node_counts.items():
            if count != 1:
                print(f"{input_name} node: {node} occured {count} times")
    return partitions

def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        The student should modify `solve` to return their solution and modify
        the portion which writes it to a file to make sure their output is
        formatted correctly.
    '''
    # size_categories = ["small", "medium", "large"]
    size_categories = ["small", "medium", "large"]
    file_counts = {"small": 331, "medium": 331, "large": 100}
    total_percentage = 0.0
    total_num_files = sum([file_counts[size] for size in size_categories])
    if not os.path.isdir(path_to_outputs):
        os.mkdir(path_to_outputs)

    for size in size_categories:
        # Print stuff start >
        print(f"Directory: {size}, Files: {file_counts[size]}")
        count = 0
        start_time = time.time()
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
            score, msg = scorer.score_output(category_path + "/" + input_name, output_category_path + "/" + input_name + ".out")
            if score == -1:
                print(f"File {input_name}: {msg}")
            total_percentage += score
            # Print stuff start > uncomment when actually running the algorithm
            count += 1 
            if DisplayCount:
                print(f"Finished {count}/{file_counts[size]}", end="\r")
        end_time = time.time()
        print(f"Done with {size}. Took {end_time - start_time} seconds.")
        # Print stuff end <

    print(f"Done with all sizes, avg percentage is: {total_percentage/total_num_files}")
if __name__ == '__main__':
    main()


