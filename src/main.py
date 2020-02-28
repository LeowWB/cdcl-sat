"""
	implement cnf formula as array of clauses. implement clause as array of literals.

	TODO
	can probably combine exists_unit_clause with find_unit_clause and save the looping.
	use profiler to see where time wasted
	discard tautologies?
	remove pure literals?
"""

from io import read_input
import copy

UNSAT = False
SAT = True

def main():
	F = read_input()
	print(F)

def unitProp(F):
	propList = [] # vars assigned thru inference
	while (exists_unit_clause(F)):
		l = find_unit_clause(F)
		propList.append(l)
		F = resolve(l, F)
	return (propList, F)


def dpll(F, decList, level):
	(propList, F) = unitProp(F)
	if (contains_empty_clause(F)):
		return UNSAT
	if (is_empty_cnf(F)):
		return SAT
	if (all_vars_assigned(F, decList)):
		return SAT
	decList[level] = propList
	p = select_prop_var(F)
	l = select_literal(p, F)
	level += 1
	if (dpll(land(F, l), decList, level) == SAT):
		return SAT
	return dpll(land(F, lnot(l)), decList, level)

def exists_unit_clause(F):
	for clause in F:
		if (len(clause) == 1):
			return True

	return False

def find_unit_clause(F):
	for clause in F:
		if (len(clause) == 1):
			return clause
	
	return None

# note that l is a literal, not prop var.
def resolve(l, F):
	pass

def contains_empty_clause(F):
	for clause in F:
		if (len(clause) == 0):
			return True
	
	return False

def is_empty_cnf(F):
	return len(F) == 0

def all_vars_assigned(F, decList):
	pass

def select_prop_var(F):
	pass

def select_literal(p, F):
	pass

# logical and
def land(F, l):
	pass

# logical not
def lnot(l):
	if (is_neg_literal(l)):
		return l[1:]
	else:
		return "~" + l

def is_neg_literal(l):
	return l[0] == "~"

def ap_literal(l):
	if (is_neg_literal(l)):
		return lnot(l)
	else:
		return l

main()