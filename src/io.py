"""
	NOTE:
		we're reading from dimacs format, but we ignore the 'p' lines, and we naively assume
		every clause is exactly one line.
"""

from string import strip
from clause import Clause

def read_input(file):
	cnf = []
	f = open(file, "r")
	clause_id = 0

	for line in f:
		if len(line) < 3:
			continue

		if line[0] in ["c", "p", "%"]:
			continue

		props = strip(line)[:-1].split()		# get rid of the trailing 0
		clause = Clause(clause_id, props)
		cnf.append(clause)
		clause_id += 1
	
	return cnf