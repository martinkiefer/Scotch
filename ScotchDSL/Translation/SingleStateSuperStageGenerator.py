from GeneratorUtils import generateComponentInstantiation, generateSignalMap, generateAssignments

#TODO: Add additional delay to account for update function latency.
class SingleStateSuperStageGenerator:
    def __init__(self, wuseed, wvalue, wstate, initial_state, update_generator, dsignal_generator):
        self.wuseed = wuseed
        self.wvalue = wvalue
        self.wstate= wstate

        self.ug = update_generator
        self.initial_state = initial_state
        self.dsg = dsignal_generator
        self.entity_name = "super_stage"

        self.signals = self.generateDeclarationSignals()

        
    def generateIncludes(self):
        return """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
"""


    def generateDeclarationSignals(self):
        signals = []
        signals += [("clk", "in", "std_logic")]

        signals += [("val_en_in", "in", "std_logic")]
        signals += [("val_in", "in", "std_logic_vector({} downto 0)".format(self.wvalue-1))]
        signals += [("useed_in", "in", "std_logic_vector({} downto 0)".format(self.wuseed-1))]

        signals += [("rd_data_out", "out", "std_logic_vector({} downto 0)".format(self.wstate-1))]

        return signals


    def generateEntityDeclaration(self):
        frame = """
ENTITY {} IS
PORT (
{}
);
END {};"""
        signals = map(lambda x : "{} : {} {}".format(x[0], x[1], x[2]), self.signals)
        return frame.format(self.entity_name, ";\n".join(signals), self.entity_name)


    def generateArchitectureDefinition(self):
        if not self.ug.synchronous:
            return self.generateAsynchronousArchitectureDefinition()
        else:
            return self.generateSynchronousArchitectureDefinition()

    def generateAsynchronousArchitectureDefinition(self):
        frame = """
ARCHITECTURE a{} OF {} IS
{}
BEGIN

process(clk)
begin
if rising_edge(clk) then
    if val_en_in = '1' then
        state <= u_outstate;
    end if;
end if;
end process;

{}
END a{};
"""        

        decl = ""
        #Declarations
        ## Update Stage       
        decl += self.ug.generateComponentDeclaration()

        ## Connecting signals
        for signal in self.ug.generateDeclarationSignals():
            decl += "\nsignal u_{} : {};".format(signal[0],signal[2]) 
        decl += "\nsignal state : std_logic_vector({} downto 0) := {};".format(self.wstate-1, self.initial_state)

        #Architecture behavior
        ## Generate component instanciations
        bhv = ""
        signal_map = generateSignalMap(self.ug.generateDeclarationSignals(), "u_")
        bhv += generateComponentInstantiation("u", self.ug.entity_name, signal_map, None)


        uin = {
            "u_clk" : "clk",
            "u_v" : "val_in",
            "u_seed" : "useed_in",
            "u_state" : "state",
        } 
        bhv += generateAssignments(uin)     

        uout = {
            "rd_data_out" : "state",
        }
        bhv += generateAssignments(uout) 

        return frame.format(self.entity_name, self.entity_name, decl, bhv, self.entity_name)

    def generateSynchronousArchitectureDefinition(self):
        frame = """
ARCHITECTURE a{} OF {} IS
{}
BEGIN

process(clk)
begin
if rising_edge(clk) then
    if eds_data_out = '1' then
        state <= u_outstate;
    end if;
end if;
end process;

{}
END a{};
"""        

        decl = ""
        #Declarations
        ## Update Stage       
        decl += self.ug.generateComponentDeclaration()

        ## Connecting signals
        for signal in self.ug.generateDeclarationSignals():
            decl += "\nsignal u_{} : {};".format(signal[0],signal[2]) 

        decl += self.dsg.generateComponentDeclaration()

        for signal in self.dsg.getEntitySignals():
            decl += "\nsignal eds_{} : {};".format(signal[0],signal[2])

        decl += "\nsignal state : std_logic_vector({} downto 0) := {};".format(self.wstate-1, self.initial_state)
        #Architecture behavior
        ## Generate component instanciations
        bhv = ""
        signal_map = generateSignalMap(self.ug.generateDeclarationSignals(), "u_")
        bhv += generateComponentInstantiation("u", self.ug.entity_name, signal_map, None)

        signal_map = generateSignalMap(self.dsg.getEntitySignals(), "eds_")
        generic_map = {"STAGES" : self.ug.computeLatency() }
        bhv += generateComponentInstantiation("eds", self.dsg.entity_name, signal_map, generic_map)

        eds = {
            "eds_clk" : "clk",
            "eds_data_in" : "val_en_in"
        } 
        bhv += generateAssignments(eds)    

        uin = {
            "u_clk" : "clk",
            "u_v" : "val_in",
            "u_seed" : "useed_in",
            "u_state" : "state",
        } 
        bhv += generateAssignments(uin)     

        uout = {
            "rd_data_out" : "state",
        }
        bhv += generateAssignments(uout) 

        return frame.format(self.entity_name, self.entity_name, decl, bhv, self.entity_name)

    def generateComponentDeclaration(self):
        entity_declaration = self.generateEntityDeclaration()
        component_declaration = entity_declaration.replace("ENTITY {}".format(self.entity_name), "COMPONENT {}".format(self.entity_name))
        component_declaration = component_declaration.replace("END {}".format(self.entity_name), "END COMPONENT {}".format(self.entity_name))
        return component_declaration

    def generateFile(self, folder):
        f = open("{}/{}.vhd".format(folder, self.entity_name), "w")
        content = self.generateIncludes()
        content += self.generateEntityDeclaration()
        content += self.generateArchitectureDefinition()
        f.write(content)
        f.close()
