from util import ap_formula

def print_formula(F):
	out = "s============================================\n"
	for clause in F:
		out += str(clause) + "\n"
	out += "e=============================================="
	print(out)

# w - overwrite, a - append
def write_formula_dimacs(F, file, method):
	f = open(file, method)
	f.write("p cnf " + str(len(ap_formula(F))) + " " + str(len(F)) + "\n")

	for clause in F:
		for l in clause.literals:
			f.write(str(l) + " ")
		
		f.write("0\n")
	
	f.close()

def print_clause(clause):
	print(str(clause.id) + str(clause.literals))

def print_graph(graph):
	print("====GRAPH====")
	for node in graph.nodes:
		if node == None:
			continue
		nodeStr = (str(node.id) + " " + str(node.truth) + " ")
		for parent in node.parents:
			nodeStr += str(parent) + " "
		print(nodeStr)
	print("===ENDGRAPH====")
