def generateComponentInstantiation(name, ctype, signal_map, generic_map):
		frame = None
		
		signal_assignments = []
		for k,v in signal_map.items():
			signal_assignments += ["\n{} => {}".format(k,v)]

		generic_assignments = []
		if not generic_map is None: 
			for k,v in generic_map.items():
				generic_assignments += ["\n{} => {}".format(k,v)]  
			frame = """
{}: {}
GENERIC MAP(
{}
)
PORT MAP(
{}
);
"""       
			return frame.format(name, ctype, ",".join(generic_assignments), ",".join(signal_assignments))
		else:
			frame = """
{}: {}
PORT MAP(
{}
);
""" 
			return frame.format(name, ctype, ",".join(signal_assignments))

def generateSignalMap(signal_triples, prefix):
	m = {}
	for t in signal_triples:
		m[t[0]] = "{}{}".format(prefix, t[0])
	return m

def generateAssignments(signal_map):
	l = ""
	for lhs,rhs in signal_map.items():
		l += "{} <= {};\n".format(lhs,rhs)
	return l


	
	    