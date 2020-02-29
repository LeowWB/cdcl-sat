def flatten(xs):
	ys = []
	for x in xs:
		if isinstance(x, list):
			ys = ys + flatten(x)
		else:
			ys.append(x)
	return ys
