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


		if check(F, result, file):
			print(file + " ok")
		else:
			perfect = False
			print(file + " FAIL")

	if (perfect):
		print("==============================\nALL TESTS PASSED\n==============================")

def check(F, result, file):
	if "uuf" in file:
		return not result[0]

	if not result[0]:
		return False
	
	tau = set(result[1])

	for clause in F:
		if set(clause.literals).intersection(tau) == set():
			return False
		
	return True

main()