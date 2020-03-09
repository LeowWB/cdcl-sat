from cdcl import solve
from util import *
from io import read_input
from os import listdir

def main():
	
	F = read_input("../test/simple/simple.cnf")
	result = solve(F)
	print(result)
	
main()