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
k = 3
s = 5

params = open('./test.txt', "w+")
params.write(str(k) + "\n")
params.write(str(s) + "\n")
for lst in [range(3) for _ in range(5)]:
    params.write(str(list(lst)))
    params.write('\n')

params.close()

print(parse_input('./'))
