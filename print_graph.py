import networkx as nx
import matplotlib.pyplot as plt
import sys

args = sys.argv
if len(args) == 1:
    exit(404)
path = args[1]
H = nx.read_gml(path)
nx.draw(H, with_labels=True, font_weight='bold')
plt.show()
