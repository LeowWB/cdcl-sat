import copy
from clause import Clause
from form import Form

def flatten(xs):
	if (xs == None or len(xs) == 0):
		return []

	ys = []
	for x in xs:
		if isinstance(x, list):
			ys = ys + flatten(x)
		else:
			ys.append(x)
	return ys

def is_literal(l):
	return isinstance(l, str)

def is_clause(clause):
	return isinstance(clause, Clause)
	
def is_formula(F):
	return isinstance(F, Form)

def make_singleton_clause(l):
	return Clause(-1, [l])

def unpack_unit_clause(clause):
	return clause.get_unit_literal()

# logical not
def lnot(l):
	assert is_literal(l), "lnot assert" + str(l)
	if (is_neg_literal(l)):
		return l[1:]
	else:
		return "-" + l

def is_neg_literal(l):
	assert is_literal(l), "is_neg_literal assert" + str(l)
	return l[0] == "-"

def ap_literal(l):
	assert is_literal(l), "ap_literal assert" + str(l)
	if (is_neg_literal(l)):
		return lnot(l)
	else:
		return l

def ap_clause(clause):
	assert is_clause(clause), "ap_clause assert" + str(clause)
	lit_set = set()
	for l in clause.all_literals():
		lit_set.add(ap_literal(l))
	return lit_set

def ap_formula(F):
	assert is_formula(F), "ap_formula assert" + str(F)
	lit_set = set()
	for clause in F.all_clauses():
		lit_set = lit_set | ap_clause(clause)
	return lit_set

def is_empty_cnf(F):
	assert is_formula(F), "is_empty_cnf assert" + str(F)
	return len(F) == 0

def contains_empty_clause(F):
	assert is_formula(F), "contains_empty_clause assert" + str(F)
	for clause in F.all_clauses():
		if (len(clause) == 0):
			# because of our implementation, non-original clauses should never be found empty.
			#assert (clause.id >= 0), "empty clause wasn't one of the original clauses!"
			return True
	
	return False

def find_empty_clause(F):
	assert is_formula(F), "find_empty_clause assert" + str(F)
	for clause in F.all_clauses():
		if (len(clause) == 0):
			# because of our implementation, non-original clauses should never be found empty.
			#assert (clause.id >= 0), "empty clause wasn't one of the original clauses!"
			return clause

def exists_unit_clause(F):
	assert is_formula(F), "exists_unit_clause assert" + str(F)
	for clause in F.all_clauses():
		if (len(clause) == 1):
			return True

	return False

def find_unit_clause(F):
	assert is_formula(F), "find_unit_clause assert" + str(F)
	for clause in F.all_clauses():
		if clause.id == -1:
			return clause
	for clause in F.all_clauses():
		if (len(clause) == 1):
			return clause
	
	return None
	
def final_dec_set_to_bool_arr(dec, num_vars):
	rv = []
	for i in range(1,num_vars+1):
		if str(i) in dec:
			rv.append((i,True))
		elif '-' + str(i) in dec:
			rv.append((i,False))
		else:
			rv.append((i,False))
	return rv