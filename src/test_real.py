from cdcl import Cdcl
from util import *
from io_cnf import read_input
from os import listdir
from debug import *
from time import time

TEST_DIR = "real_test/"

def main():
	count = 0
	perfect = True
	very_start = time()
	total_branches = 0

	for file in listdir(TEST_DIR):
		start = time()
		count += 1
		F = read_input(TEST_DIR + file)
		solver = Cdcl(F)
		result = solver.solve()
		total_branches += result[2]

		check_res = (result[0] == cryptosolve(F)[0], None)
		#check_res = check(F, result, file)
		if check_res[0]:
			print(file + "\tok\t", end='')
			print("%.3f" % (time() - start), end='')
			print(f'\t{result[2]}')
		else:
			perfect = False
			print(file + " FAIL " + check_res[1])

	if (perfect):
		print("==============================\nALL TESTS PASSED\n==============================")
		print(f'count: {count}; time: ', end='')
		print("%.3f" % (time() - very_start), end='')
		print(f'; branches: {total_branches}')

def check(F, result, file):
	if "uuf" in file:
		return not result[0], "wrong sat answer"

	if not result[0]:
		return False, "wrong sat answer"
	
	tau = set(result[1])

	for lit in tau:
		if lnot(lit) in tau:
			return False, "solution has opposing literals"

	for clause in F.all_clauses():
		if clause.all_literals().intersection(tau) == set():
			return False, "your solution doesn't satisfy the formula"
		
	return True, None

main()