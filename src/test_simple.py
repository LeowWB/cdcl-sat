from cdcl import Cdcl
from util import *
from io_cnf import read_input
from os import listdir, getcwd
from debug import *

def main():
	
	F = read_input("test/test/uf50-01.cnf")
	# print('Clauses input: ')
	# print_formula(F)
	cdcl = Cdcl(F, False)
	result = cdcl.solve()
	print(result)
	print_graph(cdcl.graph)

main()