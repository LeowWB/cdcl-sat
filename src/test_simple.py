from cdcl import Cdcl
from util import *
from io import read_input
from os import listdir

def main():
	
	F = read_input("../test/simple/simple.cnf")
	result = Cdcl(F, False).solve()
	print(result)

main()