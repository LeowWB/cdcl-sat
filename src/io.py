"""
	NOTE:
		we're reading from dimacs format, but we ignore the 'p' lines, and we naively assume
		every clause is exactly one line.
"""

from string import strip

def read_input(file):
	cnf = []
	f = open(file, "r")

	for line in f:
		if len(line) < 5:
			continue

		if line[0] in ["c", "p", "%"]:
			continue

		props = strip(line)[:-1].split()		# get rid of the trailing 0
		cnf.append(props)
	
	return cnf