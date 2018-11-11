import networkx as nx
import matplotlib.pyplot as plt
import sys

args = sys.argv
path = args[1]

if not path:
    exit(404)
H = nx.read_gml(path)
nx.draw(H, with_labels=True, font_weight='bold')
plt.show()
