"""
	implement cnf formula as array of clauses. implement clause as array of literals.

	TODO
	can probably combine exists_unit_clause with find_unit_clause and save the looping.
	use profiler to see where time wasted
	discard tautologies?
	remove pure literals?
	ctrl+F for other TODOs
	modify the input/output methods to make testing easier.
	write test script
	see if can reduce the amt of d8a stored in graph nodes (truth? diff edge for each parent?)
		truth - maybe can do this w a boolean list instead.
"""

from util import *
from debug import *
from graph import Graph

UNSAT = False
SAT = True

class Cdcl:
	def __init__(self, F, flat=True):
		self.F = copy.deepcopy(F)
		self.graph = Graph(len(ap_formula(F)))
		self.flat = flat

	def solve(self):
		F = copy.deepcopy(self.F)
		result = self.cdcl(F, [], 0)

		if self.flat:
			return (result[0], flatten(result[1]))
		else:
			return result

	def unit_prop(self, F):
		assert is_formula(F), "unit_prop assert formula" + str(F)
		propList = [] # vars assigned thru inference
		while (exists_unit_clause(F)):
			unitClause = find_unit_clause(F)
			l = unpack_unit_clause(unitClause)
			propList.append(l)
			F = self.resolve(l, F)
			self.update_graph(propList, unitClause)
		return (propList, F)


	def cdcl(self, F, decList, level):
		(propList, F) = self.unit_prop(F)
		decList.append(propList)
		if (contains_empty_clause(F)):
			return (UNSAT, None)
		if (is_empty_cnf(F)):
			return (SAT, decList)
		if (all_vars_assigned(F, decList)):
			return (SAT, decList)
		p = self.select_prop_var(F)
		l = self.select_literal(p, F)
		level += 1
		# result1 is the result of running cdcl over F ^ l
		#graphCopy = copy.deepcopy(self.graph)
		result1 = self.cdcl(land(F, l), copy.copy(decList), level)
		if result1[0] == SAT:
			return result1
		#self.graph = graphCopy
		return self.cdcl(land(F, lnot(l)), copy.copy(decList), level)

	# note that l is a literal, not prop var.
	def resolve(self, l, F):
		assert is_literal(l), "resolve assert literal" + str(l)
		assert is_formula(F), "resolve assert formula" + str(F)
		newF = []

		for clause in F:
			if l in clause.literals:
				continue
			elif lnot(l) in clause.literals:
				newClause = copy.deepcopy(clause)
				newClause.literals.remove(lnot(l))
				newF.append(newClause)
			else:
				newF.append(clause)
		
		return newF

	# TODO make this better
	def select_prop_var(self, F):
		assert is_formula(F), "select_prop_var assert" + str(F)
		return ap_literal(F[0].literals[0])

	# TODO make this better
	def select_literal(self, p, F):
		assert is_formula(F), "select_literal assert formula" + str(F)
		return p

	# this is called after unit propagation resolution. it updates the inference graph.
	def update_graph(self, propList, unitClause):
		literal = unpack_unit_clause(unitClause)
		propVar = ap_literal(literal)

		if len(propList) == 1:
			# unit clause was created as the result of a guess
			assert unitClause.id == -1
			self.graph.create_node(int(propVar), not is_neg_literal(literal))
		else:
			# unit clause was resolved from a clause that was present in the original F
			assert unitClause.id >= 0
			originalClause = copy.deepcopy(self.F[unitClause.id])
			originalClause.literals.remove(literal)
			self.graph.create_node(int(propVar), not is_neg_literal(literal))
			self.graph.connect_clause(int(propVar), originalClause)
