"""
	TODO
	use profiler to see where time wasted
	discard tautologies? <- if randomly generated formula, can preprocess.
	ctrl+F for other TODOs
"""

from util import *
from debug import *
from graph import Graph
from copy import deepcopy
from networkx import DiGraph, draw_networkx
import matplotlib.pyplot as plt
from pdb import set_trace

UNSAT = False
SAT = True

class Cdcl:
	def __init__(self, F, flat=True):
		self.F = copy.deepcopy(F)
		self.MAX_ID = len(F)
		self.G = DiGraph()
		self.flat = flat	# whether we'll flatten output
		self.L = []			# lemmas that we've learnt
		self.decisions = [] # decisions we've made that aren't in declist.
		self.num_vars = len(ap_formula(F))
		self.pure_lit_timer = 0 # every so often, we will eradicate all pure literals

	def solve(self):
		F = copy.deepcopy(self.F)
		result = self.cdcl(F, [], 0, self.G.copy())
		if self.flat:
			return (result[0], flatten(result[1]) + self.decisions)
		elif result[0]:
			return (result[0], result[1] + self.decisions)
		else:
			return result

	def unit_prop(self, F, level, G):
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
			F = self.resolve(l, F, agenda)
			G = self.update_graph(G, propList, unitClause, level)
		return (propList, F, G)

	# fit_in - true if this cdcl iter continues another level (rather than starting a new lvl). affects how propList is added to decList.
	def cdcl(self, F, decList, level, G, fit_in = False):
		(propList, F, G) = self.unit_prop(F, level, G)

		# if level is 0, we can't backtrack any further. so any inferences we make, we can apply to the actual self.F, so we don't have to keep running apply_decisions
		if level == 0:
			self.F = F
			for i in range(len(self.F)):
				self.F[i].id = i
			self.decisions += propList
			propList = []

		if not fit_in:
			decList.append(propList)
		else:
			decList[-1] = decList[-1] + propList

		if contains_empty_clause(F):
			if level==0:
				return (UNSAT, None, 0) # empty clause at level 0 implies we've derived two directly contradictory clauses thru resolution

			empty_clause = find_empty_clause(F)
			newLemma = self.diagnose(G, decList, empty_clause.id, F)
			newLemma.id = len(self.F)
			self.F.append(newLemma)

			# if the new clause is a unit clause, backtrack all the way to the start
			if len(newLemma.literals)==1:
				return (UNSAT, None, 1)

			# else, we map each var in the new clause to the level it was assigned, and go to the second-most recent of those levels
			# rationale: at that point, all but one of the vars will have been assigned. we can then infer the last var.
			biggest = [0,0]
			for clauseVar in ap_clause(newLemma):
				curVarLevel = G.nodes[int(clauseVar)]["l"]
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
		l = self.select_literal(F)

		result1 = self.cdcl(land(F, l), decList, level+1, G.copy())
		
		# first operand: whether the recursive cdcl call has been successful. if successful, can return
		# second operand: handles backtracking. if our current level is still too high, just return back to prev level.
		if result1[0] == SAT:
			return result1

		decList.pop()
		
		if level+1 > result1[2] > 0:
			return result1
		
		F = self.apply_decisions(decList)

		self.pure_lit_timer += 1
		if self.pure_lit_timer == 6:
			self.pure_lit_timer = 0
			F = self.eradicate_pure_lits(F)

		return self.cdcl(F, decList, level, G, True)

	# note that l is a literal, not prop var.
	def resolve(self, l, F, agenda):
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
				if len(newClause.literals) == 1:
					agenda.append(newClause)
			else:
				newF.append(copy.deepcopy(clause))
		return newF

	# TODO make this better
	def select_literal(self, F):
		assert is_formula(F), "select_literal assert formula" + str(F)
		occurrences = dict() # occurrences in 2-clauses
		for clause in F:
			if len(clause.literals) > 2:
				continue
			for lit in clause.literals:
				if lit in occurrences.keys():
					occurrences[lit] += 1
				else:
					occurrences[lit] = 1
		max_lit = F[0].literals[0] # default return value
		max_occ = 0
		for lit in occurrences.keys():
			if occurrences[lit] > max_occ:
				max_occ = occurrences[lit]
				max_lit = lit

		return max_lit

	# this is called after unit propagation resolution. it updates the inference graph.
	def update_graph(self, G, propList, unitClause, level):
		literal = unpack_unit_clause(unitClause) # the literal that we just decided
		propVar = ap_literal(literal)	# the propvar whose value we have just decided
		if unitClause.id == -1:
			# unit clause was created as the result of a guess
			assert not (int(propVar) in set(G.nodes)), "why's it inside"
			G.add_node(int(propVar))
			G.nodes[int(propVar)]["v"] = not is_neg_literal(literal)
			G.nodes[int(propVar)]["l"] = level
		else:
			# unit clause was resolved from a clause that was present in the original F
			assert unitClause.id >= 0
			originalClause = copy.deepcopy(self.F[unitClause.id])
			originalClause.literals.remove(literal)
			G.add_node(int(propVar))
			G.nodes[int(propVar)]["v"] = not is_neg_literal(literal)
			G.nodes[int(propVar)]["l"] = level
			G.nodes[int(propVar)]["reason"] = unitClause.id
			for literal in originalClause.literals:
				parent_node_id = int(ap_literal(literal))
				child_node_id = int(propVar)
				G.add_edge(parent_node_id, child_node_id)
		return G

	# to avoid confusion all vars are stored as strings (just like in the clauses), unless in the graph.
	def diagnose(self, G, decList, emptyClauseId, formula):
		curLevelVars = list(map(ap_literal, decList[-1]))	# all vars assigned in current level
		theRandomlyAssignedVar = None # in the current lvl, the ONE var that was randomly assigned (can we just assume to be first in curLevelVars?) TODO
		for v in curLevelVars:
			v = int(v)
			if not "reason" in G.nodes[v]:
				theRandomlyAssignedVar = str(v)
				break
		#if theRandomlyAssignedVar == None:
		#	set_trace()
		curLevelVars.remove(theRandomlyAssignedVar) # the rest were inferred - don't worry about them.
		predecessor_set = set()

		for v in curLevelVars:
			v = int(v)
			predecessors_of_v = set(G.predecessors(v))
			predecessor_set = predecessor_set.union(predecessors_of_v)

		predecessor_set = set(map(str, predecessor_set))
		predecessor_set = predecessor_set.union(set(map(ap_literal, self.F[emptyClauseId].literals)))
		predecessor_set = predecessor_set - set(curLevelVars)
		predecessor_set.add(str(theRandomlyAssignedVar))

		learnedClauseLits = []
		for v in predecessor_set:
			if G.nodes[int(v)]["v"]:
				learnedClauseLits.append("-" + str(v))
			else:
				learnedClauseLits.append(str(v))

		learnedClause = Clause(-2, learnedClauseLits)
		return learnedClause

	# call this after backtracking. applies all the decisions we've made so far to the formula
	# *AND LEMMAS*
	def apply_decisions(self, decList):
		assignments_so_far = flatten(decList)
		new_F = []

		for clause in self.F:
			if len(set(assignments_so_far).intersection(set(clause.literals))) > 0:
				continue # remove clauses that are already satisfied
			
			newClause = copy.deepcopy(clause)
			for lit in clause.literals:
				if lnot(lit) in assignments_so_far:
					newClause.literals.remove(lit)
			new_F.append(newClause)
		
		return new_F

	# identifies pure lits and appends them to the formula as unit clauses, to be removed in the next unitProp
	def eradicate_pure_lits(self, F):
		lit_counts = []
		lit_occurrences = dict()

		for i in range(self.num_vars):
			lit_counts.append([0,0])

		# count the lits
		for clause in F:
			for lit in clause.literals:
				lit_index = int(ap_literal(lit))-1
				lit_counts[lit_index][int(is_neg_literal(lit))] += 1
				if lit in lit_occurrences.keys():
					lit_occurrences[lit].add(clause.id)
				else:
					lit_occurrences[lit] = set([clause.id])

		# identify the pure lits
		for i in range(self.num_vars):
			if lit_counts[i][0] == 0 and lit_counts[i][1] > 0:
				F = land(F, lnot(str(i+1)))
			elif lit_counts[i][0] > 0 and lit_counts[i][1] == 0:
				F = land(F, str(i+1))
		
		return F