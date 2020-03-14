from cdcl import Cdcl
from util import *
from io import read_input
from os import listdir
from debug import *

def main():
	
	F = read_input("../test/simple/simple2.cnf")
	cdcl = Cdcl(F, False)
	result = cdcl.solve()
	print(result)
	print_graph(cdcl.graph)

main()