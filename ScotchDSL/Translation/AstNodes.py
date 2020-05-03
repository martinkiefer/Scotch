from abc import ABC, abstractmethod
import inspect
import AstRead

#The most general kind of node. 
#It supports:
# - The visitor pattern (top-down, bottom-up)
class AstNode(ABC):
    def acceptTopDown(self, visitor):
        visitor.visit(self)
        self._accept(visitor,AstNode.acceptTopDown)

    def acceptBottomUp(self, visitor):
        self._accept(visitor,AstNode.acceptBottomUp) 
        visitor.visit(self)    

    @abstractmethod
    def _accept(self, visitor, accept):
        pass

#An AST node representing a unary operator.
class UnaryAstNode(AstNode):
    def __init__(self, operator, child):
        self.operator = operator
        self.child = child

    def __str__(self):
        return "{}({})".format(self.operator, self.child)

    __repr__ = __str__

    def _accept(self, visitor, accept):
        accept(self.child, visitor) 


#An AST node representing a binary operator.
class BinaryAstNode(AstNode):
    def __init__(self, operator, lchild, rchild):
        self.operator = operator
        self.lchild = lchild
        self.rchild = rchild

    def __str__(self):
        return "{} {} {}".format(self.lchild, self.operator, self.rchild)

    __repr__ = __str__

    def toVHDL(self):
        if self.operator == "^":
            return "({} xor {})".format(self.lchild.toVHDL(), self.rchild.toVHDL())
        elif self.operator == "&":
            return "({} and {})".format(self.lchild.toVHDL(), self.rchild.toVHDL())
        elif self.operator == "|":
            return "({} or {})".format(self.lchild.toVHDL(), self.rchild.toVHDL())
        elif self.operator == "=":
            return "({} = {})".format(self.lchild.toVHDL(), self.rchild.toVHDL())
        elif self.operator == ">":
            return "({} > {})".format(self.lchild.toVHDL(), self.rchild.toVHDL())
        elif self.operator == "<":
            return "({} < {})".format(self.lchild.toVHDL(), self.rchild.toVHDL())
        else:
            raise Exception("Unsupported operator: {}".format(self.operator))

    def _accept(self, visitor, accept):
        accept(self.lchild, visitor)
        accept(self.rchild, visitor)


#Leaf nodes like literals and variables are
#dead ends for the visitor
class LeafAstNode(AstNode):
    def _accept(self, visitor, accept):
        pass


class StatementList(AstNode):
    def __init__(self, statements):
        self.statements = statements

    def _accept(self, visitor, accept):
        if accept is AstNode.acceptTopDown:
            for s in self.statements:
                accept(s, visitor)
        else:
            for s in reversed(self.statements):
                accept(s, visitor)

    def __str__(self):
        #return "\n".join(map(lambda x : str(x),self.statements))
        return str(self.statements)

    __repr__ = __str__    


class ForLoop(AstNode):
    def __init__(self, statements, var, lbound, ubound):
        self.statements = statements
        self.var = var
        self.unrolled = False
        self.lbound = lbound
        self.ubound = ubound     
        
    def _accept(self, visitor, accept):
        accept(self.lbound,visitor)
        accept(self.ubound,visitor)
        accept(self.statements,visitor)

    def __str__(self):
        return "for({},{} {}), {}".format(self.var, self.lbound, self.ubound, self.statements)

    __repr__ = __str__

#class Conditional(AstNode):
#    def __init__(self, condition, if_block, else_block = None):
#        self.condition = condition
#        self.if_block = if_block
#        self.else_block = else_block

#    def _accept(self, visitor, accept):
#        accept(self.condition, visitor)
#        accept(self.if_block, visitor)
#        if not self.else_block is None:
#            accept(self.else_block, visitor)  

#    def __str__(self):
#        if self.else_block is None:
#            return "if {}: {}".format(self.condition,self.if_block)   
#        else:
#            return "if {}: {} else: {}".format(self.condition,self.if_block, self.else_block)

#    __repr__ = __str__

class GeneralAssignment(AstNode):
    common_signals = []
    common_signals += ["clk : in STD_LOGIC" ]

    def generateIncludes(self):
        return """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.functions_pkg.all;
"""

    def getNodeName(self):
        return "as{}".format(id(self))

    def generateFullDefinition(self, synchronous = True): 
        return self.generateIncludes() + self.generateEntityDeclaration() + self.generateArchitectureDefinition(synchronous)

    #We need an output signal for every assignment.
    def generateCommonInputOutputDeclarations(self):
        node_prefix = self.getNodeName()
        signal_list = []
        signal_list.append("signal {}_{}_out : {}".format(node_prefix, self.lchild.get_full_name(), self.lchild.getVHDLType()))
        signal_list.append("signal {}_{}_in : {}".format(node_prefix, "clk", "STD_LOGIC"))

        return ";\n".join(signal_list)+";\n"

    def generateSpecialSignalAssignments(self):
        node_prefix = self.getNodeName()
        signal_list = []

        #Deal with offset and stateout
        if self.lchild.name == "offset":
            signal_list.append("offset <= {}_offset_out".format(node_prefix))

        if self.lchild.name == "outstate":
            signal_list.append("outstate <= {}_outstate_out".format(node_prefix))
            
        variables = self.collectInputVariables()
        for v in variables:
            if v.name == "state":
                signal_list.append("{}_state_in <= state".format(node_prefix))
                break

        for v in variables:
            index_set = set()
            if v.name == "v":
                if isinstance(v, VectorVariable):
                    signal_list.append("{}_v_in <= v".format(node_prefix))
                    break
                elif isinstance(v, IndexedVectorVariable):
                    if not v.index in index_set:
                        index_set.add((v.index))
                        signal_list.append("{}_v_{}_in <= v{}".format(node_prefix,v.index, v.index))
                else:
                    raise("Unhanlded variable type detected.")

        for v in variables:
            if v.name == "seed":
                signal_list.append("{}_seed_in <= seed".format(node_prefix))
                break

        if len(signal_list) > 0:
            return ";\n".join(signal_list)+";\n"
        else:
            return ""

    def generateCommonIntermediateConnections(self):
        node_prefix = self.getNodeName()
        signal_list = []

        signal_list.append("{}_{}_in <= {}".format(node_prefix, "clk", "clk"))

        return ";\n".join(signal_list)+";\n"

    def generateCommonMappings(self):
        node_prefix = self.getNodeName()
        signal_list = []

        signal_list.append("{} => {}_{}_in".format("clk", node_prefix, "clk"))
        return ",\n".join(signal_list)+",\n"

    def generateEntityDeclaration(self):
        frame = """
ENTITY {} IS
PORT (
{}
);
END {};"""

        nname = self.getNodeName()
        port_block = self.generatePorts()
        return frame.format(nname, port_block, nname)

    def generateComponentDeclaration(self):
        frame = """
COMPONENT {} IS
PORT (
{}
);
END COMPONENT;"""

        nname = self.getNodeName()
        port_block = self.generatePorts()
        return frame.format(nname, port_block)

    def generatePortMappings(self):
        frame = """
{}_instance: {}
PORT MAP(
{}
);
"""

        nname = self.getNodeName()
        port_assignments = self.generateCommonMappings()+self.generatePortAssignments()
        return frame.format(nname, nname, port_assignments)

    def generateIntermediateConnections(self):
        node_prefix = self.getNodeName()

        commons = self.generateCommonIntermediateConnections()

        in_variables = self.collectInputVariables()

        signal_set = set()
        #Connect signals from other components to variables
        for v in in_variables:
            if isinstance(v.value, GeneralAssignment):
                signal_set.add("{}_{}_in <= {}_{}_out".format(node_prefix, v.get_full_name(), v.value.getNodeName(), v.get_full_name()))

        #FIXME: Right now we assume that all paths from sources to an operator have the same length.
        if len(signal_set) == 0:
            return commons
        else:
            return commons + ";\n".join(signal_set)+";\n"

    def generateArchitectureDefinition(self, synchronous=True):
        #Computation of outstate is always unpipelined
        if self.lchild.name == "outstate":
            synchronous = False
        asynchronous_frame = """
ARCHITECTURE a{} OF {} IS
BEGIN
{}
END a{};
"""

        synchronous_frame = """
ARCHITECTURE a{} OF {} IS
BEGIN
    process (clk)
    begin
        if rising_edge(clk) then
                {}
        end if;
    end process;
END a{};
"""
        assignment = self.generateVHDLSignalAssignment(synchronous)
        nname = self.getNodeName()
        
        variables = self.collectInputVariables()
        variables = set(map(lambda x : x.get_full_name(), variables))
        
        if synchronous:
            return synchronous_frame.format(nname, nname, assignment, nname)
        else:
            return asynchronous_frame.format(nname, nname, assignment, nname) 

class ConditionalAssignment(GeneralAssignment):
    def __init__(self, condition, lchild, tchild, fchild, tchild_arithmetic, fchild_arithmetic):
        self.condition = condition
        self.lchild = lchild
        self.tchild = tchild
        self.fchild = fchild
        self.tchild_arithmetic = tchild_arithmetic
        self.fchild_arithmetic = fchild_arithmetic

    def _accept(self, visitor, accept):
        accept(self.condition, visitor)
        accept(self.tchild, visitor)
        accept(self.fchild, visitor)
        accept(self.lchild, visitor)

    def generateVHDLSignalAssignment(self, synchronous=True):
        frame_asynchronous = "{} <= {} when {} else {} ;"
        frame_synchronous = """
IF {} then 
{} <= {} ;
else 
{} <= {} ;
end if;
"""


        type_visitor = AstRead.ArithmeticTypeInferenceVisitor()
        self.tchild.acceptTopDown(type_visitor)

        if self.tchild_arithmetic:
            if not type_visitor.type is None:
                tstatement = "std_logic_vector(to_{}({}, {}))".format(type_visitor.type ,self.tchild.toVHDL(),self.lchild.width)
            else:
                #If there was no arithmetic conversion operator, it's probably just some plain arithmetic.
                #TODO: In the future, we should do better than crossing fingers here.
                tstatement = "std_logic_vector(to_signed({}, {}))".format(self.tchild.toVHDL(),self.lchild.width)
        else:
            tstatement = self.tchild.toVHDL()

        type_visitor = AstRead.ArithmeticTypeInferenceVisitor()
        self.fchild.acceptTopDown(type_visitor)


        if self.fchild_arithmetic:
            if not type_visitor.type is None:
                fstatement = "std_logic_vector(to_{}({}, {}))".format(type_visitor.type ,self.fchild.toVHDL(),self.lchild.width)
            else:
                #If there was no arithmetic conversion operator, it's probably just some plain arithmetic.
                #TODO: In the future, we should do better than crossing fingers here.
                fstatement = "std_logic_vector(to_signed({}, {}))".format(self.fchild.toVHDL(),self.lchild.width)
 
        else:
            fstatement = self.fchild.toVHDL()
        
        if synchronous:
            assignment = frame_synchronous.format(self.condition.toVHDL(), self.lchild.toVHDL(), tstatement, self.lchild.toVHDL(), fstatement)
        else:
            assignment = frame_asynchronous.format(self.lchild.toVHDL(), tstatement, self.condition.toVHDL(), fstatement)

        return assignment

    def getNodeName(self):
        return "as{}".format(id(self))

    def collectInputVariables(self):
        in_variables = []
        in_variables += AstRead.collectVectorVariables(self.condition)
        in_variables += AstRead.collectVectorVariables(self.fchild)
        in_variables += AstRead.collectVectorVariables(self.tchild)
        return in_variables

    def generateInputOutputDeclarations(self):
        node_prefix = self.getNodeName()

        commons = self.generateCommonInputOutputDeclarations()

        in_variables = []
        in_variables += AstRead.collectVectorVariables(self.condition)
        in_variables += AstRead.collectVectorVariables(self.fchild)
        in_variables += AstRead.collectVectorVariables(self.tchild)

        declarations = set()
        for v in in_variables:
            declarations.add("signal {}_{}_in : {}".format(node_prefix, v.get_full_name(), v.getVHDLType()))

        return commons + ";\n".join(declarations)+";\n"
  
    def generatePortAssignments(self):
        node_prefix = self.getNodeName()
        signals = []

        in_visitor = AstRead.SignalMappingVisitor("in", node_prefix)
        self.tchild.acceptTopDown(in_visitor)
        self.fchild.acceptTopDown(in_visitor)
        self.condition.acceptTopDown(in_visitor)
        signals += in_visitor.signal_list

        out_visitor = AstRead.SignalMappingVisitor("out", node_prefix)
        self.lchild.acceptTopDown(out_visitor)
        signals += out_visitor.signal_list

        #Remove potential duplicates
        signals = set(signals)
        return ",\n".join(signals)

    def generatePorts(self):
        signals = list(GeneralAssignment.common_signals)

        in_visitor = AstRead.SignalDeclarationVisitor("in")
        self.tchild.acceptTopDown(in_visitor)
        self.fchild.acceptTopDown(in_visitor)
        self.condition.acceptTopDown(in_visitor)
        signals += in_visitor.signal_list

        out_visitor = AstRead.SignalDeclarationVisitor("out")
        self.lchild.acceptTopDown(out_visitor)
        signals += out_visitor.signal_list

        #Remove potential duplicates
        signals = set(signals)
        return ";\n".join(signals)

    def __str__(self):
        return "{} <= {} ? {} : {}\n".format(self.lchild, self.condition, self.tchild, self.fchild)

    __repr__ = __str__

class Assignment(GeneralAssignment):
    def __init__(self, lchild, rchild, arithmetic):
        self.lchild = lchild
        self.rchild = rchild
        self.arithmetic = arithmetic
        

    def _accept(self, visitor, accept):
        accept(self.rchild, visitor)
        accept(self.lchild, visitor)

    def generateVHDLSignalAssignment(self, synchronus = True):
        if not self.arithmetic:
            return "{} <= {};".format(self.lchild.toVHDL(), self.rchild.toVHDL())
        else:
            type_visitor = AstRead.ArithmeticTypeInferenceVisitor()
            self.rchild.acceptTopDown(type_visitor)
            if not type_visitor.type is None:
                assignment = "{} <= std_logic_vector(to_{}({}, {}));".format(self.lchild.toVHDL(), type_visitor.type ,self.rchild.toVHDL(),self.lchild.width)
            else:
                #If there was no arithmetic conversion operator, it's probably just some plain arithmetic.
                #TODO: In the future, we should do better than crossing fingers here.
                assignment = "{} <= std_logic_vector(to_signed({}, {}));".format(self.lchild.toVHDL(), self.rchild.toVHDL(),self.lchild.width)

            return assignment

    def collectInputVariables(self):
        return AstRead.collectVectorVariables(self.rchild)

    def generateInputOutputDeclarations(self):
        node_prefix = self.getNodeName()

        commons = self.generateCommonInputOutputDeclarations()

        in_variables = []
        in_variables += AstRead.collectVectorVariables(self.rchild)

        declarations = set()
        for v in in_variables:
            declarations.add("signal {}_{}_in : {}".format(node_prefix, v.get_full_name(), v.getVHDLType()))

        return commons + ";\n".join(declarations)+";\n"

    def generatePorts(self):
        signals = list(GeneralAssignment.common_signals)

        in_visitor = AstRead.SignalDeclarationVisitor("in")
        self.rchild.acceptTopDown(in_visitor)
        signals += in_visitor.signal_list

        out_visitor = AstRead.SignalDeclarationVisitor("out")
        self.lchild.acceptTopDown(out_visitor)
        signals += out_visitor.signal_list

        #Remove potential duplicates
        signals = set(signals)
        return ";\n".join(signals)

    def generatePortAssignments(self):
        node_prefix = self.getNodeName()
        signals = []

        in_visitor = AstRead.SignalMappingVisitor("in", node_prefix)
        self.rchild.acceptTopDown(in_visitor)
        signals += in_visitor.signal_list

        out_visitor = AstRead.SignalMappingVisitor("out", node_prefix)
        self.lchild.acceptTopDown(out_visitor)
        signals += out_visitor.signal_list

        #Remove potential duplicates
        signals = set(signals)
        return ",\n".join(signals)

    def __str__(self):
        return "{} <= {}\n".format(self.lchild, self.rchild)

    __repr__ = __str__

class VectorSelect(AstNode):
    def __init__(self, up, lo, child):
        self.up = up
        self.lo = lo
        self.child = child

    def _accept(self, visitor, accept):
        accept(self.up, visitor)
        accept(self.lo, visitor)
        accept(self.child, visitor)

    def toVHDL(self):
        if self.up.eval() - self.lo.eval() == 0:
            return "{}({})".format(self.child.toVHDL(), self.lo.toVHDL())
        elif self.up.eval() - self.lo.eval() < 0:
            raise Exception("Found vector select with empty range.") 
        else:
            return "{}({} downto {})".format(self.child.toVHDL(), self.up.toVHDL(), self.lo.toVHDL()) 

    def __str__(self):
        return "({}, {} : {})".format(self.child, self.up, self.lo)

    __repr__ = __str__

class IndexedVectorVariable(AstNode):
    def __init__(self, name,index, value = None, width = None):
        self.name = name
        self.value = value
        self.index = index
        self.width = width

    def _accept(self, visitor, accept):
        accept(self.index, visitor)

    def get_full_name(self):
        return "{}_{}".format(self.name, self.index) 

    def toVHDL(self):
        return self.get_full_name()

    def getVHDLType(self):
        if self.width == 1:
            variable_type = "STD_LOGIC"
        else:
            variable_type = "STD_LOGIC_VECTOR({} downto {})".format(self.width - 1, 0)
        return variable_type

    def __str__(self):
        if isinstance(self.value, Assignment) or isinstance(self.value, ConditionalAssignment):
            return "({},[{}],{})".format(self.name, self.index, "assignment-bound", self.width)
        else:
            return "({},[{}],{}, {})".format(self.name, self.index, self.value, self.width)

    __repr__ = __str__

 #   def __eq__(self, other):
 #       if isinstanceof(other, IndexedVectorVariable):
 #           return self.get_full_name() == other.get_full_name()
 #       else
 #           return false

 #   def __hash__(self):
 #       return hash(self.get_full_name())

class ArithmeticLiteral(LeafAstNode):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "{}".format(self.value)

    def eval(self):
        return self.value

    def toVHDL(self):
        return str(self.value)

    __repr__ = __str__


class VectorLiteral(LeafAstNode):
    def __init__(self, typ, value):
        self.typ = typ
        self.value = value

    def __str__(self):
        return "({},{})".format(self.typ, self.value)

    def toVHDL(self):
        if self.typ == "b2":
            if len(self.value) > 3:
                 return "{}".format(str(self.value).replace("'",'"'))
            return "{}".format(str(self.value))
        else:
            raise Exception("Unsupported literal type found: {}".format(self.typ))
    __repr__ = __str__


class ArithmeticVariable(LeafAstNode):
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __str__(self):
        return "({},{})".format(self.name, self.value)

    def eval(self):
        if self.value != "in" and self.value != None:
            return self.value
        else:
            raise Exception("Eval was called on an unbound variable.")

    def toVHDL(self):
        return "{}".format(str(self.eval()))

    __repr__ = __str__


class VectorVariable(LeafAstNode):
    def __init__(self, name,value = None, width = None):
        self.name = name
        self.value = value
        self.width = width

    def __str__(self):
        if isinstance(self.value, Assignment) or isinstance(self.value, ConditionalAssignment):
                return "({},{}, {})".format(self.name, "assignment-bound", self.width)
        else:
            return "({},{},{})".format(self.name, self.value, self.width)

    def get_full_name(self):
        return self.name

    def toVHDL(self):
        return self.get_full_name()

    def getVHDLType(self):
        if self.width == 1:
            variable_type = "STD_LOGIC"
        else:
            variable_type = "STD_LOGIC_VECTOR({} downto {})".format(self.width - 1, 0)
        return variable_type

    __repr__ = __str__

class BooleanExpression(BinaryAstNode):
    pass

class VectorOperation(BinaryAstNode):
    pass

class BinaryArithmeticOperation(BinaryAstNode):
    def eval(self):
        if self.operator == "*":
            return self.lchild.eval() * self.rchild.eval()
        elif self.operator == "+":
            return self.lchild.eval() + self.rchild.eval()
        elif self.operator == "/":
            return self.lchild.eval() / self.rchild.eval()
        elif self.operator == "-":
            return self.lchild.eval() - self.rchild.eval()
        else:
            raise Exception("Tried to evaluate an unknown operator.") 

    def toVHDL(self):
        return "({} {} {})".format(self.lchild.toVHDL(), self.operator, self.rchild.toVHDL())    
        
class UnaryArithmeticOperation(UnaryAstNode):
    def eval(self):
        if self.operator == "arith_neg":
            return - self.child.eval()
        else:
            raise Exception("Tried to evaluate an unknown operator.")
    def toVHDL(self):
        return "-({})".format(self.child.toVHDL())     


class Vector2ArithmeticConversion(UnaryAstNode):
    def toVHDL(self):
        return "to_integer({}({}))".format(self.operator,self.child.toVHDL())    

class ParityOperation(UnaryAstNode):
    def toVHDL(self):
        return "parity({})".format(self.child.toVHDL())

class ExpandOperation(AstNode):
    def __init__(self, child, width):
        self.child = child
        self.width = width

    def _accept(self, visitor, accept):
        accept(self.child, visitor)
        accept(self.width, visitor)

    def toVHDL(self):
        return "({} downto {} => {})".format(self.width.eval()-1, 0, self.child.toVHDL())

    def __str__(self):
        return "expand({},{})".format(self.child, self.width.eval())

    __repr__ = __str__
