import networkx as nx
import matplotlib.pyplot as plt

"""
To write gml file use -- nx.write_gml(G, path)   <-- path is string literal
To read gml file use -- H = nx.read_gml(path)

To Draw a graph:
ex. 
G = nx.generators.random_graphs.gnm_random_graph(300, 100)
nx.draw(G, with_labels=True, font_weight='bold')
plt.show()
"""

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
    graph = nx.read_gml(folder_name + "/test.gml")
    parameters = open(folder_name + "/test.txt")
    num_buses = int(parameters.readline())
    size_bus = int(parameters.readline())
    constraints = []
    
    for line in parameters:
        line = line[1: -2]
        curr_constraint = [num.replace("'", "") for num in line.split(", ")]
        constraints.append(curr_constraint)

    # return graph, num_buses, size_bus, constraints
    return num_buses, size_bus, constraints

# G = nx.generators.random_graphs.dense_gnm_random_graph(30, 50)
# G = nx.generators.random_graphs.gnm_random_graph(300, 100)

# G = nx.gnp_random_graph(50, 0.6)
# nx.draw(G, with_labels=True, font_weight='bold')
# plt.show()

import metis
# G = metis.example_networkx()
G = nx.gnp_random_graph(500, 0.6)
(edgecuts, parts) = metis.part_graph(G, 22)
# colors = ['red','blue','green']
# for i, p in enumerate(parts):
#     G.node[i]['color'] = colors[p]

partitions = [[] for _ in range(22)]

all_nodes = list(G.nodes)
for i in range(G.number_of_nodes()):
    partitions[parts[i]].append(all_nodes[i])

for i in range(22):
    print("part {}, length {}: {}".format(i, len(partitions[i]), partitions[i]))

# print(edgecuts)

# print(len(parts))
# print(max(parts))
# nx.draw(G, with_labels=True, font_weight='bold')
# plt.show()
