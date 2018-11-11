import networkx as nx
import random as r
import matplotlib.pyplot as plt

graph_file_path = './inputs/large/graph.gml'
constraints_path = './inputs/large/parameters.txt'

k = 33       # num of buses
s = 31       # capacity of each bus
N = 1000      # total num of students
p_edge = 0.6    # probability of creating an edge in random graph  
constraint_limit = 2000  # upper limit on number of constraints


"""
Writing k, s, and constraints to the parameters file.
"""
def write_constraints(constraints, path, k, s):
    f = open(path, "w+")
    f.write(str(k) + "\n")
    f.write(str(s) + "\n")
    for lst in constraints:
        f.write(str(lst))
        f.write("\n")
    f.close()

"""
Generates and writes graph to file
Returns the Graph object for use
"""
def generate_graph(N):
    G = nx.gnp_random_graph(N, p_edge)
    nx.write_gml(G, graph_file_path)
    return G


"""
Generates and writes constraints to file
Returns the list of lists for use
"""
def generate_constraints(G, k, s):
    constraints = []

    for _ in range(constraint_limit):
        rowdy_group_size = r.randint(2, s) # random number from 2 - capacity
        curr_group = []
        i = 0
        while(i < rowdy_group_size):
            curr_node = r.randint(0, N - 1)
            if (curr_node not in curr_group):
                curr_group.append(curr_node)
                i = i + 1
        constraints.append(curr_group)

    write_constraints(constraints, constraints_path, k, s)
    return constraints



"""
Perform sanity check on the generated outputs
"""
def sanity_check(N, G, constraints):
    total_capacity = k * s >= N
    if (not total_capacity):
        print("total capacity not enough")
    constraint_size = constraint_limit >= len(constraints)
    return total_capacity and constraint_size


G = generate_graph(N)
constraints = generate_constraints(G, k, s)
if (not sanity_check(N, G, constraints)):
    print("Invalid stuff generated!")