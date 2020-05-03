import AstNodes
import copy

#Binds found variables in the tree to a constant value
#Doesn't matter whether it is applied top-down or bottom-up
class ConstantVariableBindingVisitor:
	def __init__(self, variable_dictionary, type):
		self.vd = variable_dictionary
		self.type = type

	def visit(self, x):
		if isinstance(x, self.type):
			if x.name in self.vd:
				if x is None:
					raise Exception("The variable {} was already bound.".format())
				x.value = self.vd[x.name]

#Visitor that looks for assignments and creates a reference on the next appearance
class AssignmentBindingVisitor:
	def __init__(self):
		self.signals = {}

	def visit(self, x):
		if isinstance(x, AstNodes.GeneralAssignment):
			y = x.lchild
			if isinstance(y, AstNodes.VectorVariable):
				y.value = 'out'
				self.signals[y.name] = x
			elif isinstance(y, AstNodes.IndexedVectorVariable):
				y.value = 'out'
				self.signals[(y.name, y.index.eval())] = x
			else:
				raise Exception("Unhandled variable type was found on lhs of assignment.")
		elif isinstance(x, AstNodes.VectorVariable):
			if x.name in self.signals:
				#We never assign output variables
				if x.value == "out" or x.value == "in":
					return
				elif x.value is None:
					x.value = self.signals[x.name]
				else:
					raise Exception("Trying to assign a bound vector variable.")

		elif isinstance(x, AstNodes.IndexedVectorVariable):
			if (x.name,x.index.eval()) in self.signals:
				if x.value == "out" or x.value == "in":
					return
				elif x.value is None:
					x.value = self.signals[(x.name,x.index.eval())]	
				else:
					raise Exception("Trying to assign a bound vector variable.")	
		else:
			pass

class VariableWidthSettingVisistor:
	def __init__(self,width_map):
		self.width_map = width_map

	def visit(self,x):
		if isinstance(x, AstNodes.VectorVariable) or isinstance(x, AstNodes.IndexedVectorVariable):
			if x.name in self.width_map:
				if not x.width is None:
					raise Exception("Width for this variable was set already.")
				x.width = self.width_map[x.name]
		else:
			pass

#Needs to be applied top-down.
class LoopUnrollingVisitor:
	def visit(self,x):
		if isinstance(x, AstNodes.ForLoop):
			new_statements = []
			for i in range(x.lbound.eval(), x.ubound.eval()+1):
				current = copy.deepcopy(x.statements)
				#A VB visitor in the Loop Visitor. What is this, a crossover episode?
				current.acceptTopDown(ConstantVariableBindingVisitor({x.var : i}, AstNodes.ArithmeticVariable))
				new_statements.extend(current.statements)
			x.statements.statements = new_statements
			x.unrolled = True

class EvaluationVisitor:
	def visit(self,x):
		if isinstance(x, AstNodes.IndexedVectorVariable):
			x.index = AstNodes.ArithmeticLiteral(x.index.eval())
		if isinstance(x, AstNodes.VectorSelect):
			x.lo = AstNodes.ArithmeticLiteral(x.lo.eval())
			x.up = AstNodes.ArithmeticLiteral(x.up.eval())