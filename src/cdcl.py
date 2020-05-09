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
from networkx import DiGraph, draw_networkx, ancestors, descendants, shortest_path_length, all_simple_paths
import matplotlib.pyplot as plt
from pdb import set_trace
from form import Form
from collections import deque

UNSAT = False
SAT = True

class Cdcl:
	def __init__(self, F, flat=True):
		self.F = F
		self.MAX_ID = len(F)
		self.flat = flat	# whether we'll flatten output
		self.L = []			# lemmas that we've learnt
		self.decisions = [] # decisions we've made that aren't in dec_list.
		self.num_vars = len(ap_formula(F))
		self.pure_lit_timer = 0 # every so often, we will eradicate all pure literals
		self.forget_timer = 0
		self.branch_count = 0 # calls to select_literal
		self.lemma_count = 0

	def solve(self):
		F = copy.deepcopy(self.F)
		result = self.cdcl(F, [], 0, DiGraph())
		if self.flat:
			return (result[0], flatten(result[1]) + self.decisions, self.branch_count)
		elif result[0]:
			return (result[0], result[1] + self.decisions, self.branch_count)
		else:
			return (result[0], result[1], self.branch_count)

	# lit_list is a list of literals that we want to unit-propagate. they will be treated with highest priority.
	def unit_prop(self, F, level, G, lit_list = None):
		assert is_formula(F), "unit_prop assert formula" + str(F)
		prop_list = [] # vars assigned thru inference
		agenda = [] #stack. purpose of this is so we explore in a more DFS-like manner

		while (lit_list or (exists_unit_clause(F) and not contains_empty_clause(F))):
			if lit_list:
				unit_clause = make_singleton_clause(lit_list.pop())
			elif (len(agenda) == 0):
				unit_clause = find_unit_clause(F)
			else:
				unit_clause = agenda.pop()
				if not len(unit_clause) == 1:
					continue
			l = unpack_unit_clause(unit_clause)
			prop_list.append(l)
			F = self.resolve(l, F, agenda, level)
			G = self.update_graph(G, prop_list, unit_clause, level)
		return (prop_list, F, G)

	# fit_in - true if this cdcl iter continues another level (rather than starting a new lvl). affects how prop_list is added to dec_list.
	# next_prop is a list of literals we want to unit prop the next cycle.
	def cdcl(self, F, dec_list, level, G, fit_in = False, next_prop = None):
		(prop_list, F, G) = self.unit_prop(F, level, G, lit_list = next_prop)
		# if level is 0, we can't backtrack any further. so any inferences we make, we can apply to the actual self.F.
		if level == 0:
			self.forget_timer += 1
			if self.forget_timer >= 2:
				F.permanently_forget_clauses(self.MAX_ID, self.lemma_count)
				self.forget_timer = 0
			self.F = copy.deepcopy(F)
			self.decisions += prop_list
			prop_list = []

		if not fit_in:
			dec_list.append(prop_list)
		else:
			dec_list[-1] = dec_list[-1] + prop_list

		if contains_empty_clause(F):
			if level==0:
				return (UNSAT, None, 0) # empty clause at level 0 implies we've derived two directly contradictory clauses thru resolution

			empty_clause = find_empty_clause(F)
			new_lemma = self.diagnose(G, dec_list, empty_clause.id, F, level)
			self.lemma_count += 1
			nl_copy = copy.deepcopy(new_lemma)
			self.F.add_clause(nl_copy)

			# updates the new_lemma to the current state of decisions
			F.add_clause(new_lemma)
			self.update_clause(new_lemma, dec_list)
			return (UNSAT, None, self.decide_backjump_level(nl_copy, G))
		if (is_empty_cnf(F)):
			return (SAT, dec_list)
		l = self.select_literal(F)
		result1 = self.cdcl(F, dec_list, level+1, G, next_prop = [l])
		
		if result1[0] == SAT:
			return result1

		# since the above if-statement didn't get called, we assume the result was UNSAT.
		# so we undo the effects of the previous guess, from both G and dec_list
		G.remove_nodes_from([int(ap_literal(x)) for x in dec_list.pop()])
		
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

		return self.cdcl(F, dec_list, level, G, True, pure_lits)

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
	# pick branching literal
	def select_literal(self, F):
		assert is_formula(F), "select_literal assert formula" + str(F)
		self.branch_count += 1
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
	def update_graph(self, G, prop_list, unit_clause, level):
		if level == 0:
			return G
		literal = unpack_unit_clause(unit_clause) # the literal that we just decided
		propVar = ap_literal(literal)	# the propvar whose value we have just decided
		if unit_clause.id == -1:
			# unit clause was created as the result of a guess
			assert not (int(propVar) in set(G.nodes)), "why's it inside"
			G.add_node(int(propVar))
			G.nodes[int(propVar)]["v"] = not is_neg_literal(literal)
			G.nodes[int(propVar)]["l"] = level
		else:
			# unit clause was resolved from a clause that was present in the original F
			assert unit_clause.id >= 0
			G.add_node(int(propVar))
			G.nodes[int(propVar)]["v"] = not is_neg_literal(literal)
			G.nodes[int(propVar)]["l"] = level
			G.nodes[int(propVar)]["reason"] = unit_clause.id

			# loop thru the literals of the original clause, other than the one that became part of the unit clause
			for original_clause_lit in self.F._clauses[unit_clause.id].all_literals():
				if original_clause_lit == literal or original_clause_lit in self.decisions:
					continue
				parent_node_id = int(ap_literal(original_clause_lit))
				child_node_id = int(propVar)
				G.add_edge(parent_node_id, child_node_id)
		return G

	
	# to avoid confusion all vars are stored as strings (just like in the clauses), unless in the graph.
	def diagnose(self, G, dec_list, emptyClauseId, formula, level):
		curLevelVars = list(map(ap_literal, dec_list[-1]))	# all vars assigned in current level
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

	# forcefully updates a clause to the current state of affairs (according to dec_list)
	def update_clause(self, clause, dec_list):
		for i in range(len(dec_list)):
			sublist = dec_list[i]
			for sublit in sublist:
				if lnot(sublit) in clause.all_literals():
					clause.remove_literal(lnot(sublit), i)

	def decide_backjump_level(self, new_lemma, G):
		# if the new clause is a unit clause, backtrack all the way to the start
		if len(new_lemma)==1:
			return 1 #(UNSAT, None, 1)
		# else, we map each var in the new clause to the level it was assigned, and go to the second-most recent of those levels
		# rationale: at that point, all but one of the vars will have been assigned. we can then infer the last var.
		biggest = [0,0]
		for clause_var in ap_clause(new_lemma):
			cur_var_level = G.nodes[int(clause_var)]["l"]
			if cur_var_level > biggest[0]:
				biggest[1] = biggest[0]
				biggest[0] = cur_var_level
			elif cur_var_level > biggest[1]:
				biggest[1] = cur_var_level
		return biggest[1]

# TODO re3move this
def deb_print(x):
	return;print(str(x))