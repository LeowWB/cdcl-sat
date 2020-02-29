import copy

def flatten(xs):
	if (xs == None or len(xs) == 0):
		return xs

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
	return isinstance(clause, list) and (len(clause) == 0 or is_literal(clause[0]))
	
def is_formula(F):
	return isinstance(F, list) and (len(F) == 0 or is_clause(F[0]))

def make_singleton_clause(l):
	return [l]

def unpack_singleton_clause(clause):
	return clause[0]

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
	for l in clause:
		lit_set.add(ap_literal(l))
	return lit_set

def ap_formula(F):
	assert is_formula(F), "ap_formula assert" + str(F)
	lit_set = set()
	for clause in F:
		lit_set = lit_set | ap_clause(clause)
	return lit_set

def is_empty_cnf(F):
	assert is_formula(F), "is_empty_cnf assert" + str(F)
	return len(F) == 0

def all_vars_assigned(F, decList):
	assert is_formula(F), "all_vars_assigned assert" + str(F)
	return ap_formula(F) == set(map(ap_literal, flatten(decList)))

def contains_empty_clause(F):
	assert is_formula(F), "contains_empty_clause assert" + str(F)
	for clause in F:
		if (len(clause) == 0):
			return True
	
	return False

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
