from AstRead import collectVectorVariables
import AstNodes

class FunctionGenerator:
    def create_entity_declarations(self):
        return "".join(map(lambda x : x.generateEntityDeclaration(), self.statements))

    def create_io_signals(self):
        return "".join(map(lambda x : x.generateInputOutputDeclarations(), self.statements))

    def create_intermediate_connections(self):
        return "".join(map(lambda x : x.generateIntermediateConnections(), self.statements))

    def create_port_declarations(self):
        return "".join(map(lambda x : x.generateComponentDeclaration(), self.statements))

    def create_port_mappings(self):
        return "".join(map(lambda x : x.generatePortMappings(), self.statements))

    def create_special_signal_connections(self):
        return "".join(map(lambda x : x.generateSpecialSignalAssignments(), self.statements))

    def generateFunctionFile(self):
        return self.generateFunctionIncludes() + self.generateEntityDeclaration() + self.generateArchitecture()

    def generateFile(self, folder):
        f = open("{}/{}.vhd".format(folder, self.entity_name), "w")
        f.write(self.generateFunctionFile()+self.generateAssignmentFile())
        f.close()

    def generateEntityDeclaration(self):
        signals = map(lambda x : "{} : {} {}".format(x[0], x[1], x[2]), self.signals)
        return self.entity_frame.format(self.entity_name,";\n".join(signals), self.entity_name)

    def generateArchitecture(self):
        signal_declarations = self.create_io_signals()
        port_declarations = self.create_port_declarations()
        port_mappings = self.create_port_mappings()
        intermediate_connections = self.create_intermediate_connections()
        special_connections = self.create_special_signal_connections()
        return self.architecture_frame.format(self.entity_name, self.entity_name, signal_declarations+port_declarations, intermediate_connections + port_mappings + special_connections, self.entity_name)

    def generateComponentDeclaration(self):
        entity_declaration = self.generateEntityDeclaration()
        component_declaration = entity_declaration.replace("ENTITY {}".format(self.entity_name), "COMPONENT {}".format(self.entity_name))
        component_declaration = component_declaration.replace("END {}".format(self.entity_name), "END COMPONENT {}".format(self.entity_name))
        return component_declaration

    def generateFunctionIncludes(self):
        return """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.functions_pkg.all;
"""

    def generateAssignmentFile(self):
        return "".join(map(lambda x : x.generateFullDefinition(self.synchronous), self.statements))
    
    def generateSignalTypeMap(self):
        signals = self.generateDeclarationSignals()
        m = {}
        for s in signals:
            m[s[0]] = s[2]
        return m

    @staticmethod
    def dfs_distance(x):
        if isinstance(x, AstNodes.Assignment):
            vars = collectVectorVariables(x.rchild)
        elif isinstance(x, AstNodes.ConditionalAssignment):
            vars = collectVectorVariables(x.tchild)+collectVectorVariables(x.fchild) + collectVectorVariables(x.condition)
        else:
            raise Exception("Found a non assignment type during dfs.")

        #Filter all variables that are not assignment-bound.
        vars = list(filter(lambda x : isinstance(x.value, AstNodes.Assignment) or isinstance(x.value, AstNodes.ConditionalAssignment), vars))
        if not vars:
            return 1
        else:
            distances = list(map(lambda x : FunctionGenerator.dfs_distance(x.value), vars))
            all_equal = all(distances[0] == d for d in distances)
            if not all_equal:
                raise Exception("Found unequal distance to an assignment.")
            return distances[0]+1

class SelectorFunctionGenerator(FunctionGenerator):
    def __init__(self, statements, value_width, seed_width, offset_width, synchronous):
        self.statements = statements
        self.value_width = value_width
        self.seed_width = seed_width
        self.offset_width = offset_width
        self.synchronous = synchronous
        self.entity_name = "selector"
        self.signals = self.generateDeclarationSignals()
        self.entity_frame = """
ENTITY {} IS
PORT (
    {}
);
END {};
"""

        self.architecture_frame = """
ARCHITECTURE a{} OF {} IS
{}
BEGIN
{}
END a{};
"""

    def generateDeclarationSignals(self):
        signals = []
        signals += [("clk", "in", "STD_LOGIC")]
        signals += [("v", "in", "STD_LOGIC_VECTOR({} downto 0)".format(self.value_width-1))]
        signals += [("seed", "in", "STD_LOGIC_VECTOR({} downto 0)".format(self.seed_width-1))]
        signals += [("offset", "out", "STD_LOGIC_VECTOR({} downto 0)".format(self.offset_width-1))]
        return signals

    def computeLatency(self):
        #We start with the last assignment. This one should be the output variable.
        if not self.synchronous:
            return 0
        source = self.statements[-1]
        if source.lchild.name != "offset":
            raise Exception("Last assignment in selector was not to offset variable.")
        return FunctionGenerator.dfs_distance(source)

class UpdateFunctionGenerator(FunctionGenerator):
    def __init__(self, statements, value_width, seed_width, state_width, synchronous):
        self.statements = statements
        self.value_width = value_width
        self.seed_width = seed_width
        self.state_width = state_width
        self.synchronous = synchronous

        self.entity_name = "update"
        self.signals = self.generateDeclarationSignals()
 
        self.architecture_frame = """
ARCHITECTURE a{} OF {} IS
{}
BEGIN
{}
END a{};
"""
        self.entity_frame = """
ENTITY {} IS
PORT (
    {}
);
END {};"""

        #A final check whether this actually a synchronous function
        if self.computeLatency() == 0:
            self.synchronous = False

    def generateDeclarationSignals(self):
        signals = []
        signals += [("clk", "in", "STD_LOGIC")]
        signals += [("v", "in", "STD_LOGIC_VECTOR({} downto 0)".format(self.value_width-1))]
        signals += [("seed", "in", "STD_LOGIC_VECTOR({} downto 0)".format(self.seed_width-1))]
        signals += [("state", "in", "STD_LOGIC_VECTOR({} downto 0)".format(self.state_width-1))]
        signals += [("outstate", "out", "STD_LOGIC_VECTOR({} downto 0)".format(self.state_width-1))]
        return signals

    def computeLatency(self):
        if not self.synchronous:
            return 0
        #We start with the last assignment. This one should be the output variable.
        source = self.statements[-1]
        if source.lchild.name != "outstate":
            raise Exception("Last assignment in selector was not to offset variable.")
        return FunctionGenerator.dfs_distance(source)-1

class DataParallelUpdateFunctionGenerator(UpdateFunctionGenerator):

    def __init__(self, statements, value_width, seed_width, state_width, n_parallel, synchronous):
        self.n_parallel = n_parallel
        super().__init__(statements, value_width, seed_width, state_width, synchronous)
        

    def generateDeclarationSignals(self):
        signals = []
        signals += [("clk", "in", "STD_LOGIC")]
        signals += [("seed", "in", "STD_LOGIC_VECTOR({} downto 0)".format(self.seed_width-1))]
        signals += [("state", "in", "STD_LOGIC_VECTOR({} downto 0)".format(self.state_width-1))]
        signals += [("outstate", "out", "STD_LOGIC_VECTOR({} downto 0)".format(self.state_width-1))]

        for i in range(0, self.n_parallel):
            signals += [("v{}".format(i), "in", "STD_LOGIC_VECTOR({} downto 0)".format(self.value_width-1))]
        return signals
