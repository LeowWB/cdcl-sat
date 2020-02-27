def read_input():
	
	f = open("in.txt", "r");
	cnf = []

	for line in f:
		if len(line) > 0:
			props = line.split()
			cnf.append(props)
	
	return cnf