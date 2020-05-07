"""
	NOTE:
		we're reading from dimacs format, but we ignore the 'p' lines, and we naively assume
		every clause is exactly one line.
"""

# from string import strip
import string
from clause import Clause
from form import Form

def read_input(file):
	cnf = []
	f = open(file, "r")
	clause_id = 0

	for line in f:
		if len(line) < 3:
			continue

		if line[0] in ["c", "p", "%"]:
			continue

		# props = strip(line)[:-1].split()		# get rid of the trailing 0
		props = (line[:-2]).split()				# for lines, last character is newline character.
		clause = Clause(clause_id, props)
		cnf.append(clause)
		clause_id += 1
	
	return Form(cnf)