import networkx as nx
import matplotlib.pyplot as plt

graph_file_path = './inputs/small/graph.gml'
constraints_p = './inputs/small/parameters.txt'

k = 8
s = 7
N = 50
p_edge = 0.4

"""
Generates and writes graph to file
Returns the Graph object for use
"""
def generate_graph(k, s, N):
    G = nx.gnp_random_graph(N, 0.4)
    nx.write_gml(G, graph_file_path)
    return G


"""
Generates and writes constraints to file
Returns the list of lists for use
"""
def generate_constraints(G, k, s):
    
    return


"""
Perform sanity check on the generated outputs
"""
def sanity_check(N, G, constraints):
    return False


G = generate_graph(k, s, N)
constraints = generate_constraints(G, k, s)
if (not sanity_check(N, G, constraints)):
    print("Invalid stuff generated!")