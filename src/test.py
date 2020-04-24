from cdcl import Cdcl
from util import *
from io_cnf import read_input
from os import listdir
from debug import *

TEST_DIR = "test/test/"

def main():
	count = 0
	perfect = True

	for file in listdir(TEST_DIR):
		count += 1
		F = read_input(TEST_DIR + file)

		solver = Cdcl(F)
		result = solver.solve()

		check_res = check(F, result, file)
		if check_res[0]:
			print(file + " ok")
		else:
			perfect = False
			print(file + " FAIL " + check_res[1])

	if (perfect):
		print("==============================\nALL TESTS PASSED\n==============================")

def check(F, result, file):
	if "uuf" in file:
		return not result[0], "wrong sat answer"

	if not result[0]:
		return False, "wrong sat answer"
	
	tau = set(result[1])

	for lit in tau:
		if lnot(lit) in tau:
			return False, "solution has opposing literals"

	for clause in F:
		if set(clause.literals).intersection(tau) == set():
			return False, "your solution doesn't satisfy the formula"
		
	return True, None

main()