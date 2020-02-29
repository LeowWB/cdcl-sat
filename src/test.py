from cdcl import cdcl
from io import read_input

def main():
	F = read_input()
	print("Input:")
	print(F)
	print("\nOutput:")
	print(cdcl(F, [], 0))

main()