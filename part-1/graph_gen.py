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

# G = nx.generators.random_graphs.dense_gnm_random_graph(30, 50)
G = nx.generators.random_graphs.gnm_random_graph(300, 100)
nx.draw(G, with_labels=True, font_weight='bold')
plt.show()