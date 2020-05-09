from cdcl import Cdcl
from util import *
from io_cnf import read_input
from os import listdir, getcwd
from debug import *
from pdb import *

"""
	F = read_input("test/simple/simple2.cnf")
	F = read_input("test/test/uf20-01.cnf")
	F = read_input("test/test/uf50-01.cnf")
	F = read_input("test/test/uuf50-01.cnf")
"""

def main():
	
	F = read_input("test/simple/simple2.cnf")
	# print('Clauses input: ')
	# print_formula(F)
	cdcl = Cdcl(F, False)
	result = cdcl.solve()
	print(result)

main()