from cdcl import cdcl
from util import *
from io import read_input
from os import listdir

TEST_DIR = "../te/"

def main():
	count = 0

	for file in listdir(TEST_DIR):
		count += 1
		F = read_input(TEST_DIR + file)
		print("Input:")
		print(F)
		print("\nOutput:")
		print(cdcl(F, [], 0))

main()