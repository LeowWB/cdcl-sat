"""
	implement cnf formula as array of clauses. implement clause as array of literals.
"""

from io import read_input

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
	pass

def find_unit_clause(F):
	pass

# note that l is a literal, not prop var.
def resolve(l, F):
	pass

def contains_empty_clause(F):
	pass

def is_empty_cnf(F):
	pass

def all_vars_assigned(F, decList):
	pass

def select_prop_var(F):
	pass

def select_literal(p, F):
	pass

def land(F, l):
	pass

def lnot(l):
	pass

main()