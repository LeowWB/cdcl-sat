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
from form import Form

UNSAT = False
SAT = True

class Cdcl:
	def __init__(self, F, flat=True):
		self.F = F
		self.MAX_ID = len(F)
		self.flat = flat	# whether we'll flatten output
		self.L = []			# lemmas that we've learnt
		self.decisions = [] # decisions we've made that aren't in declist.
		self.num_vars = len(ap_formula(F))
		self.pure_lit_timer = 0 # every so often, we will eradicate all pure literals

	def solve(self):
		F = copy.deepcopy(self.F)
		result = self.cdcl(F, [], 0, DiGraph())
		if self.flat:
			return (result[0], flatten(result[1]) + self.decisions)
		elif result[0]:
			return (result[0], result[1] + self.decisions)
		else:
			return result

	# lit_list is a list of literals that we want to unit-propagate. they will be treated with highest priority.
	def unit_prop(self, F, level, G, lit_list = None):
		assert is_formula(F), "unit_prop assert formula" + str(F)
		propList = [] # vars assigned thru inference
		agenda = [] #stack. purpose of this is so we explore in a more DFS-like manner

		while (lit_list or (exists_unit_clause(F) and not contains_empty_clause(F))):
			if lit_list:
				unitClause = make_singleton_clause(lit_list.pop())
			elif (len(agenda) == 0):
				unitClause = find_unit_clause(F)
			else:
				unitClause = agenda.pop()
				if not len(unitClause) == 1:
					continue
			l = unpack_unit_clause(unitClause)
			propList.append(l)
			F = self.resolve(l, F, agenda, level)
			G = self.update_graph(G, propList, unitClause, level)
		return (propList, F, G)

	# fit_in - true if this cdcl iter continues another level (rather than starting a new lvl). affects how propList is added to decList.
	# next_prop is a list of literals we want to unit prop the next cycle.
	def cdcl(self, F, decList, level, G, fit_in = False, next_prop = None):
		(propList, F, G) = self.unit_prop(F, level, G, lit_list = next_prop)
		# if level is 0, we can't backtrack any further. so any inferences we make, we can apply to the actual self.F.
		if level == 0:
			self.F = copy.deepcopy(F)
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
			self.F.add_clause(copy.deepcopy(newLemma))

			# updates the newLemma to the current state of decisions
			F.add_clause(newLemma)
			for i in range(len(decList)):
				sublist = decList[i]
				for sublit in sublist:
					if lnot(sublit) in newLemma.all_literals():
						newLemma.remove_literal(lnot(sublit), i)

			# if the new clause is a unit clause, backtrack all the way to the start
			if len(newLemma)==1:
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
		l = self.select_literal(F)
		result1 = self.cdcl(F, decList, level+1, G, next_prop = [l])
		
		if result1[0] == SAT:
			return result1

		# since the above if-statement didn't get called, we assume the result was UNSAT.
		# so we undo the effects of the previous guess, from both G and decList
		G.remove_nodes_from([int(ap_literal(x)) for x in decList.pop()])
		
		# this if-block handles backjumping. if the conflict diagnosis told us to backjump further
		# back than this level, then we just do so by returning.
		if level+1 > result1[2] > 0:
			return result1
			
		F.reset_to_level(level)

		pure_lits = []

		self.pure_lit_timer += 1
		if self.pure_lit_timer == 6:
			self.pure_lit_timer = 0
			F, pure_lits = self.eradicate_pure_lits(F)

		return self.cdcl(F, decList, level, G, True, pure_lits)

	# note that l is a literal, not prop var.
	def resolve(self, l, F, agenda, level):
		assert is_literal(l), "resolve assert literal" + str(l)
		assert is_formula(F), "resolve assert formula" + str(F)
		for clause in F.all_clauses():
			if l in clause.all_literals():
				F.remove_clause_id(clause.id, level)
			elif lnot(l) in clause.all_literals():
				clause.remove_literal(lnot(l), level)
				if len(clause) == 1:
					agenda.append(clause)
		return F

	# TODO make this better
	def select_literal(self, F):
		assert is_formula(F), "select_literal assert formula" + str(F)
		occurrences = dict() # occurrences in 2-clauses
		for clause in F.all_clauses():
			if len(clause) > 2:
				continue
			for lit in clause.all_literals():
				if lit in occurrences.keys():
					occurrences[lit] += 1
				else:
					occurrences[lit] = 1
		max_lit = F.last_lit()
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
			G.add_node(int(propVar))
			G.nodes[int(propVar)]["v"] = not is_neg_literal(literal)
			G.nodes[int(propVar)]["l"] = level
			G.nodes[int(propVar)]["reason"] = unitClause.id

			# loop thru the literals of the original clause, other than the one that became part of the unit clause
			for original_clause_lit in self.F._clauses[unitClause.id].all_literals():
				if original_clause_lit == literal:
					continue
				parent_node_id = int(ap_literal(original_clause_lit))
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
		predecessor_set = predecessor_set.union(set(map(ap_literal, self.F._clauses[emptyClauseId].all_literals())))
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

	# identifies pure lits and appends them to the formula as unit clauses, to be removed in the next unitProp
	def eradicate_pure_lits(self, F):
		lit_counts = []
		lit_occurrences = dict()

		for i in range(self.num_vars):
			lit_counts.append([0,0])

		# count the lits
		for clause in F.all_clauses():
			for lit in clause.all_literals():
				lit_index = int(ap_literal(lit))-1
				lit_counts[lit_index][int(is_neg_literal(lit))] += 1
				if lit in lit_occurrences.keys():
					lit_occurrences[lit].add(clause.id)
				else:
					lit_occurrences[lit] = set([clause.id])

		pure_lit_decisions = []

		# identify the pure lits
		for i in range(self.num_vars):
			if lit_counts[i][0] == 0 and lit_counts[i][1] > 0:
				pure_lit_decisions.append(lnot(str(i+1)))
			elif lit_counts[i][0] > 0 and lit_counts[i][1] == 0:
				pure_lit_decisions.append(str(i+1))
		
		return F, pure_lit_decisions

# TODO re3move this
def deb_print(x):
	return;print(str(x))