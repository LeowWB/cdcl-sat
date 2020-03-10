from copy import deepcopy

class Clause:
	def __init__(self, id, literals):
		self.id = id
		self.literals = literals

	def clone(self):
		return Clause(self.id, deepcopy(self.literals))