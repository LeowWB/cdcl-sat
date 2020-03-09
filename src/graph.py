class Graph:
	nodes = []
	order = []
	
	def __init__(self, size):
		nodes = [None] * (size + 10) #TODO to avoid off-by-one error for now

	def connect(self, child, parent, edge):
		child_node = nodes[child]
		child_node.add_parent(parent, edge)
	
	def create_node(self, index, truth):
		nodes[index] = Node(index, truth)
		order.append(index)


class Node:
	def __init__(self, id, truth):
		self.id = id
		self.truth = truth
		self.parents = []

	def add_parent(self, parent, edge):
		self.parents.append([parent, edge])