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
"""

from io import *
from util import *
import copy

UNSAT = False
SAT = True

def main():
	F = read_input()
	print("Input:")
	print(F)
	print("\nOutput:")
	print(dpll(F, [], 0))

def unitProp(F):
	assert is_formula(F), "unitProp assert formula" + str(F)
	propList = [] # vars assigned thru inference
	while (exists_unit_clause(F)):
		l = unpack_singleton_clause(find_unit_clause(F))
		propList.append(l)
		F = resolve(l, F)
	return (propList, F)


def dpll(F, decList, level):
	(propList, F) = unitProp(F)
	if (contains_empty_clause(F)):
		return (UNSAT, None)
	if (is_empty_cnf(F)):
		return (SAT, decList)
	if (all_vars_assigned(F, decList)):
		return (SAT, decList)
	decList.append(propList)
	p = select_prop_var(F)
	l = select_literal(p, F)
	level += 1
	if (dpll(land(F, l), decList, level) == SAT):
		return (SAT, decList)
	return dpll(land(F, lnot(l)), decList, level)

def exists_unit_clause(F):
	assert is_formula(F), "exists_unit_clause assert" + str(F)
	for clause in F:
		if (len(clause) == 1):
			return True

	return False

def find_unit_clause(F):
	assert is_formula(F), "find_unit_clause assert" + str(F)
	for clause in F:
		if (len(clause) == 1):
			return clause
	
	return None

# note that l is a literal, not prop var.
def resolve(l, F):
	assert is_literal(l), "resolve assert literal" + str(l)
	assert is_formula(F), "resolve assert formula" + str(F)
	newF = []

	for clause in F:
		if l in clause:
			continue
		elif lnot(l) in clause:
			newClause = copy.deepcopy(clause)
			newClause.remove(lnot(l))
			newF.append(newClause)
		else:
			newF.append(clause)
	
	return newF

def contains_empty_clause(F):
	assert is_formula(F), "contains_empty_clause assert" + str(F)
	for clause in F:
		if (len(clause) == 0):
			return True
	
	return False

def is_empty_cnf(F):
	assert is_formula(F), "is_empty_cnf assert" + str(F)
	return len(F) == 0

def all_vars_assigned(F, decList):
	assert is_formula(F), "all_vars_assigned assert" + str(F)
	return ap_formula(F) == set(map(ap_literal, flatten(decList)))

# TODO make this better
def select_prop_var(F):
	assert is_formula(F), "select_prop_var assert" + str(F)
	return ap_literal(F[0][0])

# TODO make this better
def select_literal(p, F):
	assert is_formula(F), "select_literal assert formula" + str(F)
	return p

# logical and
def land(F, l):
	assert is_literal(l), "land assert literal" + str(l)
	assert is_formula(F), "land assert formula" + str(F)
	newF = copy.deepcopy(F)
	newF.append(make_singleton_clause(l))
	return newF

# logical not
def lnot(l):
	assert is_literal(l), "lnot assert" + str(l)
	if (is_neg_literal(l)):
		return l[1:]
	else:
		return "~" + l

def is_neg_literal(l):
	assert is_literal(l), "is_neg_literal assert" + str(l)
	return l[0] == "~"

def ap_literal(l):
	assert is_literal(l), "ap_literal assert" + str(l)
	if (is_neg_literal(l)):
		return lnot(l)
	else:
		return l

def ap_clause(clause):
	assert is_clause(clause), "ap_clause assert" + str(clause)
	lit_set = set()
	for l in clause:
		lit_set.add(ap_literal(l))
	return lit_set

def ap_formula(F):
	assert is_formula(F), "ap_formula assert" + str(F)
	lit_set = set()
	for clause in F:
		lit_set = lit_set | ap_clause(clause)
	return lit_set

def is_literal(l):
	return isinstance(l, str)

def is_clause(clause):
	return isinstance(clause, list) and (len(clause) == 0 or is_literal(clause[0]))
	
def is_formula(F):
	return isinstance(F, list) and (len(F) == 0 or is_clause(F[0]))

def make_singleton_clause(l):
	return [l]

def unpack_singleton_clause(clause):
	return clause[0]

main()