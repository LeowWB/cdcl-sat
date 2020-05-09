from copy import deepcopy

class Clause:
	def __init__(self, id, literals):
		self.id = id
		self._literals = dict()	# keeps track of the ORIGINAL literals in the clause, as well as wehn they were "removed"
		self._lit_set = set(literals)
		self.length = len(literals)
		for lit in literals:
			self._literals[lit] = -1

	def __len__(self):
		return self.length

	def remove_literal(self, lit, level):
		assert lit in self._literals.keys()
		self._literals[lit] = level
		self._lit_set.remove(lit)
		self.length -= 1

	def get_unit_literal(self):
		assert self.length == 1
		return list(self._lit_set)[0]
	
	def all_literals(self):
		return self._lit_set

	def reset_to_level(self, level):
		for lit in self._literals.keys():
			if self._literals[lit] > level:
				self._literals[lit] = -1
				self._lit_set.add(lit)
				self.length += 1
	
	def __str__(self):
		return str(self._literals.keys())
	
	def __repr__(self):
		return str(self._literals.keys())