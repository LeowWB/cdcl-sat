from util import ap_literal

class Graph:
	nodes = [] # index i will be the node corresponding to prop var i.
	order = [] # order in which prop vars were added. represented only by id.

	def __init__(self, size):
		self.nodes = [None] * (size + 10) #TODO to avoid off-by-one error for now

	def connect_clause(self, child, clause):
		for literal in clause.literals:
			parent = int(ap_literal(literal))
			self.nodes[child].add_parent(parent, clause.id)

	def create_node(self, index, truth):
		self.nodes[index] = Node(index, truth)
		self.order.append(index)

	def get_last_node(self):
		return self.nodes[self.order[-1]]

"""
	each node represents a single propositional variable.
	
	each element in parents is a list, whose first element is the parent node's id, and whose
	2nd element is the clause id through which the inference was made. 
"""
class Node:
	def __init__(self, id, truth):
		self.id = id
		self.truth = truth
		self.parents = []

	def add_parent(self, parent, edge):
		self.parents.append([parent, edge])