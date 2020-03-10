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

from util import *
from debug import *
from graph import Graph

UNSAT = False
SAT = True

def solve(F, flat=True):
	result = cdcl(F, [], 0)

	if flat:
		return (result[0], flatten(result[1]))
	else:
		return result

def unitProp(F):
	assert is_formula(F), "unitProp assert formula" + str(F)
	propList = [] # vars assigned thru inference
	while (exists_unit_clause(F)):
		l = unpack_unit_clause(find_unit_clause(F))
		propList.append(l)
		F = resolve(l, F)
	return (propList, F)


def cdcl(F, decList, level):
	(propList, F) = unitProp(F)
	decList.append(propList)
	if (contains_empty_clause(F)):
		return (UNSAT, None)
	if (is_empty_cnf(F)):
		return (SAT, decList)
	if (all_vars_assigned(F, decList)):
		return (SAT, decList)
	p = select_prop_var(F)
	l = select_literal(p, F)
	level += 1
	# result1 is the result of running cdcl over F ^ l
	result1 = cdcl(land(F, l), copy.copy(decList), level)
	if result1[0] == SAT:
		return result1
	return cdcl(land(F, lnot(l)), copy.copy(decList), level)

# note that l is a literal, not prop var.
def resolve(l, F):
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
def select_prop_var(F):
	assert is_formula(F), "select_prop_var assert" + str(F)
	return ap_literal(F[0].literals[0])

# TODO make this better
def select_literal(p, F):
	assert is_formula(F), "select_literal assert formula" + str(F)
	return p
