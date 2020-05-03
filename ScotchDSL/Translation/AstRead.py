import AstNodes

class AssignmentCollectingVisitor:
	def __init__(self):
		self.assignments = []

	def visit(self,x):
		if isinstance(x, AstNodes.GeneralAssignment):
			self.assignments.append(x) 
		elif isinstance(x, AstNodes.ForLoop) and not x.unrolled:
			raise Exception("Tried to perform collect on an non-unrolled for loop.")
		else:
			pass

class ArithmeticTypeInferenceVisitor:
	def __init__(self):
		self.type = None

	def visit(self,x):
		if isinstance(x, AstNodes.Vector2ArithmeticConversion):
			if self.type is None:
				self.type = x.operator
			elif self.type != x.operator:
				raise Exception("Conflicting typecasts in arithmetic expression.")
			else:
				pass

class SignalDeclarationVisitor:
	def __init__(self, direction):
		self.signal_list = []
		self.direction = direction

	def visit(self,x):
		if isinstance(x, AstNodes.VectorVariable) or isinstance(x, AstNodes.IndexedVectorVariable):
			signal = "{} : {} {}"
			self.signal_list.append(signal.format(x.get_full_name(), self.direction, x.getVHDLType()))
		else:
			pass

class SignalMappingVisitor:
	def __init__(self, direction, node_name):
		self.signal_list = []
		self.direction = direction
		self.node_name = node_name

	def visit(self,x):
		if isinstance(x, AstNodes.VectorVariable) or isinstance(x, AstNodes.IndexedVectorVariable):
			signal = "{} => {}_{}_{}"
			self.signal_list.append(signal.format(x.get_full_name(), self.node_name, x.get_full_name(), self.direction))
		else:
			pass

class NodeCollectingVisitor:
	def __init__(self, node_type):
		self.node_list = []
		self.node_type = node_type

	def visit(self,x):
		if isinstance(x, self.node_type):
			self.node_list.append(x)
		else:
			pass

def collectAssignments(x):
    visitor = AssignmentCollectingVisitor()
    x.acceptTopDown(visitor)
    return visitor.assignments

def collectVectorVariables(x):
    plain_visitor = NodeCollectingVisitor(AstNodes.VectorVariable)
    x.acceptTopDown(plain_visitor)

    indexed_visitor = NodeCollectingVisitor(AstNodes.IndexedVectorVariable)
    x.acceptTopDown(indexed_visitor)

    return plain_visitor.node_list + indexed_visitor .node_list