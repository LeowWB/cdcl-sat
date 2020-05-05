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

	def solve(self):
		F = copy.deepcopy(self.F)
		result = self.cdcl(F, [], 0, self.G.copy())

		if self.flat:
			return (result[0], flatten(result[1]))
		else:
			return result

	def unit_prop(self, F, level, G):
		assert is_formula(F), "unit_prop assert formula" + str(F)
		propList = [] # vars assigned thru inference
		agenda = [] #stack. purpose of this is so we explore in a more DFS-like manner
		debug_clauseswegotridof = []
		while (exists_unit_clause(F) and not contains_empty_clause(F)):
			if (len(agenda) == 0):
				unitClause = find_unit_clause(F)
				if unitClause.id == -1:
					deb = unpack_unit_clause(unitClause)
					deb = ap_literal(deb)
					deb = int(deb)
					assert not (deb in set(G.nodes)), "why's it inside 2"
			else:
				unitClause = agenda.pop()
				if not len(unitClause.literals) == 1:
					continue
			l = unpack_unit_clause(unitClause)
			propList.append(l)
			debug_clauseswegotridof.append(unitClause.id)
			# print('before resolution')
			# print_formula(F)
			# print(propList, unitClause.literals, unitClause.id)
			F = self.resolve(l, F, agenda)
			# print("my F for the original clause below after resolution: ", end='')
			# print_formula(F)
			G = self.update_graph(G, propList, unitClause, level)
		#debug_noneg1 = True
		#for id in debug_clauseswegotridof:
		#	if id == -1:
		#		debug_noneg1 = False
		#if debug_noneg1 and level > 0:
		#	set_trace()
		#debug_allreason = True
		#for prop in propList:
		#	ind = int(ap_literal(prop))
		#	if not "reason" in G.nodes[ind]:
		#		debug_allreason = False
		#if debug_allreason and level > 0:
		#	set_trace()

		return (propList, F, G)


	def cdcl(self, F, decList, level, G, fit_in = False):
		#if not cryptosolve(self.F)[0]:
		#	set_trace()

		assert set(map(lambda x: int(ap_literal(x)), flatten(decList))) == set(G.nodes), "why not same"
		deb_numneg1 = 0
		for clause in F:
			if clause.id==-1:
				deb_numneg1 += 1
		
		assert deb_numneg1 < 2, "why more than 1 neg1"
		(propList, F, G) = self.unit_prop(F, level, G)
		if not fit_in:
			decList.append(propList)
		else:
			decList[-1] = decList[-1] + propList
		#print(f'level {level} decList {decList}')
		if (contains_empty_clause(F)):
			
			if level==0:
				return (UNSAT, None, 0)

			empty_clause = find_empty_clause(F)
			#print(f'level {level} emptyclauseid {empty_clause.id} emptyclause {self.F[empty_clause.id].literals}')
			# print('empty_clause: ', empty_clause.id, empty_clause.literals, decList)
			newLemma = self.diagnose_alt(G, decList, empty_clause.id, F)
			#set_trace()
			# print('newLemma: ', newLemma.literals)
			newLemma.id = len(self.F)
			#print(f'newlemma {newLemma.literals}')

			lemma_is_trivial = False
			for lit in newLemma.literals:
				if lnot(lit) in newLemma.literals:
					lemma_is_trivial = True
					break
				
			if not lemma_is_trivial:
				self.F.append(newLemma)
			else:
				assert False, "WHY TRIVIAL"

			#decide where to backtrack to. TODO this can be abstracted out. 
			# we can have multiple "algorithms" for
			# deciding where to backtrack to. can say in report which is best.
			#this one takes 2nd biggest number among the levels of the vars in the clause
			if len(newLemma.literals)==1:
				thislevel=1
				#print(f'backtrack to this level: {thislevel}')
				return (UNSAT, None, thislevel)

			biggest = [0,0]
			for clauseVar in ap_clause(newLemma):
				curVarLevel = G.nodes[int(clauseVar)]["l"]
				if curVarLevel > biggest[0]:
					biggest[1] = biggest[0]
					biggest[0] = curVarLevel
				elif curVarLevel > biggest[1]:
					biggest[1] = curVarLevel
			#print(f'backtrack to this level: {biggest[1]}')
			return (UNSAT, None, biggest[1])
		if (is_empty_cnf(F)):
			return (SAT, decList)
		if (all_vars_assigned(F, decList)):
			return (SAT, decList)
		p = self.select_prop_var(F)
		l = self.select_literal(p, F)
		level += 1

		#assert not (p in set(map(ap_literal, flatten(decList)))), "why you still make this decision"

		#for clause in F:
		#	assert clause.id > -1, "WHY HERE GOT ID NEGATIVE"

		# result1 is the result of running cdcl over F ^ l
		# print('land operation result: ', print_formula(land(F,l)), print_formula(F))	
		result1 = self.cdcl(land(F, l), copy.copy(decList), level, G.copy())
		# print('result1 ', result1)
		if result1[0] == SAT:
			return result1

		backtrackLevel = result1[2]

		if level > backtrackLevel and backtrackLevel > 0:
			return result1
		
		F = self.apply_decisions(decList)
		return self.cdcl(F, copy.copy(decList), level-1, G.copy(), True) # TODO probably dunnid copy G agn

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
		#if (ap_literal(l) in ap_formula(newF)):
		#	set_trace()#, "why isn't it gone?"
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
	def diagnose_alt(self, G, decList, emptyClauseId, formula):
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
		#if not (len(predecessor_set) == len(learnedClauseLits)):
		#	set_trace()
		#if not (len(set(learnedClauseLits)) == len(learnedClauseLits)):
		#	set_trace()

		learnedClause = Clause(-2, learnedClauseLits)
		learnedClause.deb_circumstances = (G.copy(), copy.deepcopy(decList), emptyClauseId, deepcopy(formula))
		return learnedClause

	def diagnose(self, G, decList, emptyClauseId, formula):
		learnedClause = copy.deepcopy(self.F[emptyClauseId])
		curLevelVars = list(map(ap_literal, decList[-1]))	# all vars assigned in current level
		debug_iterno = 0

		while len(ap_clause(learnedClause) & set(curLevelVars)) > 1:
			debug_iterno += 1
			nextNodeToResolve = int(curLevelVars.pop())
			if "reason" not in G.nodes[nextNodeToResolve]: # we got nothing to resolve with if the value was an arbitrary assignment
				continue
			nextClauseToResolve = G.nodes[nextNodeToResolve]["reason"]
			nextClauseToResolve = self.F[nextClauseToResolve]
			learnedClause = self.diagnose_resolve(learnedClause, nextClauseToResolve)
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
		print("NO")
		return c1

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

	def show_graph(self, G):
		draw_networkx(G, node_color="#ffdddd")
		plt.show()