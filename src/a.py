import matplotlib.pyplot as plt
import networkx as nx

a = nx.DiGraph()
a.add_node(1)
a.add_node(2)
a.add_edge(2,1)
a.nodes[2]["hello"] = 1000
nx.draw_networkx(a, node_color="#ffdddd")
plt.show()
