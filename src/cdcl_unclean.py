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
	see if can reduce the amt of d8a stored in graph nodes
		truth - maybe can do this w a boolean list instead.
		may not need to store 1 edge per parent - 1 edge for whole node is fine
"""

from util import *
from debug import *
from graph import Graph
from copy import deepcopy

UNSAT = False
SAT = True

class Cdcl:
	def __init__(self, F, flat=True):
		self.F = copy.deepcopy(F)
		self.MAX_ID = len(F)
		self.graph = Graph(len(ap_formula(F)))
		self.flat = flat	# whether we'll flatten output
		self.L = []			# lemmas that we've learnt

	def solve(self):
		F = copy.deepcopy(self.F)
		result = self.cdcl(F, [], 0)

		if self.flat:
			return (result[0], flatten(result[1]))
		else:
			return result

	def unit_prop(self, F, level):
		assert is_formula(F), "unit_prop assert formula" + str(F)
		propList = [] # vars assigned thru inference
		agenda = [] #stack. purpose of this is so we explore in a more DFS-like manner
		while (exists_unit_clause(F) and not contains_empty_clause(F)):
			if (len(agenda) == 0):
				unitClause = find_unit_clause(F)
			else:
				unitClause = agenda.pop()
				if not len(unitClause.literals) == 1:
					continue
			l = unpack_unit_clause(unitClause)
			propList.append(l)
			# print('before resolution')
			# print_formula(F)
			# print(propList, unitClause.literals, unitClause.id)
			F = self.resolve(l, F, agenda)
			# print("my F for the original clause below after resolution: ", end='')
			# print_formula(F)
			self.update_graph(propList, unitClause, level)
		return (propList, F)


	def cdcl(self, F, decList, level):
		(propList, F) = self.unit_prop(F, level)
		decList.append(propList)
		if (contains_empty_clause(F)):
			empty_clause = find_empty_clause(F)
			# print('empty_clause: ', empty_clause.id, empty_clause.literals, decList)
			newLemma = self.diagnose(decList, empty_clause.id, F)
			# print('newLemma: ', newLemma.literals)
			self.L.append(newLemma)

			#decide where to backtrack to. TODO this can be abstracted out. 
			# we can have multiple "algorithms" for
			# deciding where to backtrack to. can say in report which is best.
			#this one takes 2nd biggest number among the levels of the vars in the clause
			biggest = [0,0]
			for clauseVar in ap_clause(newLemma):
				curVarLevel = self.graph.nodes[int(clauseVar)].level
				if curVarLevel > biggest[0]:
					biggest[1] = biggest[0]
					biggest[0] = curVarLevel
				elif curVarLevel > biggest[1]:
					biggest[1] = curVarLevel

			return (UNSAT, None, biggest[1])
		if (is_empty_cnf(F)):
			return (SAT, decList)
		if (all_vars_assigned(F, decList)):
			return (SAT, decList)
		p = self.select_prop_var(F)
		l = self.select_literal(p, F)
		level += 1
		# result1 is the result of running cdcl over F ^ l
		graphCopy = copy.deepcopy(self.graph)
		# print('land operation result: ', print_formula(land(F,l)), print_formula(F))	
		result1 = self.cdcl(land(F, l), copy.copy(decList), level)
		# print('result1 ', result1)
		if result1[0] == SAT:
			return result1

		backtrackLevel = result1[2]

		if level > backtrackLevel:
			return result1
		
		F = self.apply_decisions(decList, F)
		# print('after apply_decisions: ', print_formula(F))
		self.graph = graphCopy
		return self.cdcl(land(F, lnot(l)), copy.copy(decList), level)

	# note that l is a literal, not prop var.
	def resolve(self, l, F, agenda):
		assert is_literal(l), "resolve assert literal" + str(l)
		assert is_formula(F), "resolve assert formula" + str(F)
		newF = []
		# print('current literal: ', l)
		for clause in F:
			# print('l and clauses:', l, clause.literals)
			if l in clause.literals:
				# print('l already in clause: ', l, clause.literals)
				continue
			elif lnot(l) in clause.literals:
				newClause = copy.deepcopy(clause)
				newClause.literals.remove(lnot(l))
				newF.append(newClause)
				if len(newClause.literals) == 1:
					agenda.append(newClause)
					# print('appending new clause to agenda: ', newClause.literals)
			else:
				newF.append(clause)
		# print('this is the newF: ', print_formula(newF))
		return newF

	# TODO make this better
	def select_prop_var(self, F):
		assert is_formula(F), "select_prop_var assert" + str(F)
		return ap_literal(F[-1].literals[-1])

	# TODO make this better
	def select_literal(self, p, F):
		assert is_formula(F), "select_literal assert formula" + str(F)
		return p

	# this is called after unit propagation resolution. it updates the inference graph.
	def update_graph(self, propList, unitClause, level):
		literal = unpack_unit_clause(unitClause)
		propVar = ap_literal(literal)
		if len(propList) == 1:
			# unit clause was created as the result of a guess
			assert unitClause.id == -1
			# print('proplength = 1, original clause from unitClause.id: ', unitClause.literals)
			self.graph.create_node(int(propVar), not is_neg_literal(literal), level)
		else:
			# unit clause was resolved from a clause that was present in the original F
			assert unitClause.id >= 0
			# originalClause = copy.deepcopy(self.F[unitClause.id])
			originalClause = copy.deepcopy(self.F[unitClause.id])
			# print('original clause from unitClause id: ', originalClause.id, originalClause.literals)
			# print('inside update graph: ', literal, originalClause.literals)
			# print_formula(self.F)
			# print('F ', self.F[unitClause.id].literals)
			# print('literal to be removed: ', literal, 'from ', originalClause.literals)
			# print('number of literals found about to be removed: ', originalClause.literals.count(literal))
			originalClause.literals.remove(literal)
			self.graph.create_node(int(propVar), not is_neg_literal(literal), level)
			self.graph.connect_clause(int(propVar), originalClause)

	def diagnose(self, decList, emptyClauseId, formula):
		curLevelLits = decList[-1]						# all lits assigned in current level
		curLevelVars = map(ap_literal, curLevelLits)	# all vars assigned in current level
		lastIndex = -1
		learnedClauseInd = emptyClauseId				# partial learned clause
		learnedClause = self.F[learnedClauseInd]
		learnedClauseCopy = copy.deepcopy(learnedClause)
		item = None
		for item in curLevelVars:
			pass
		# conflictNodeId = int(curLevelVars.values())
		# print('conflictNodeID: ', item)
		# print('current level lits: ', decList)
		varsWhoseClausesWeveResolved = set()
		while len(ap_clause(learnedClause) & set(curLevelVars)) > 1:
			try:
				nextNodeInd = self.graph.order[lastIndex]

				if (not (nextNodeInd in self.graph.nodes[conflictNodeId].ancestors)):
					lastIndex -= 1
					continue

				nextNode = self.graph.nodes[nextNodeInd]
				varsWhoseClausesWeveResolved.add(nextNode.id)

				# this if-block is an ugly shortcut
				if len(nextNode.parents) == 0:
					break

				nextClauseInd = nextNode.parents[0][1]
				nextClause = self.F[nextClauseInd]
				lastIndex -= 1
				learnedClause = self.diagnose_resolve(learnedClause, nextClause)
			except Exception as e:
				print(e)
		# print('did something happen here? ', learnedClause.id, learnedClause.literals)
		return learnedClause

	# resolution in the context of conflict diagnosis
	def diagnose_resolve(self, c1, c2):
		for lit in c1.literals:
			if lnot(lit) in c2.literals:
				newClauseLits = c1.literals + c2.literals
				newClauseLits = list(set(newClauseLits))
				newClauseLits.remove(lit)
				newClauseLits.remove(lnot(lit))
				return Clause(-2, newClauseLits)
		# ideally we never reach this line at all. but something's wrong with the code.
		# so this is an ugly (but still not incorrect) soln
		return c1

	# call this after backtracking. applies all the decisions we've made so far to the formula
	# *AND LEMMAS*
	def apply_decisions(self, decList, F):
		flatList = flatten(decList)
		newL = []
		for clause in self.L:
			intersectionSize = len(set(flatList).intersection(set(clause.literals)))
			# print('intersection size ', intersectionSize, flatList, clause.literals)
			if intersectionSize != 0:
				continue	# remove clauses that are already satisfied.
			
			newClause = copy.deepcopy(clause)
			for lit in newClause.literals:
				if lnot(lit) in flatList:
					newClause.literals.remove(lit)
			# print('clause and newclause id: ', clause.id, newClause.id)
			# newClause.id = len(F) + len(newL)	# this line is the funky line.
			# newClause.id = self.MAX_ID + len(newL)
			# self.MAX_ID += 1
			newL.append(newClause)
			# print('new clause stuff: ', newClause.id, newClause.literals)
			# print(print_formula(newL))
		return copy.deepcopy(F) + newL