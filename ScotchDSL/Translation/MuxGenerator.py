from MuxSingleGenerator import MuxSingleGenerator
from GeneratorUtils import generateComponentInstantiation

class MuxGenerator:
    def __init__(self):
        self.entity_name = "mux"
        self.msg = MuxSingleGenerator()

    def generateIncludes(self):
        return """
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use WORK.mux_config_pkg.all;
"""

    def generateDeclarationSignals(self):
        signals = []
        signals += [("clk", "in", "std_logic")]
        signals += [("enable_in", "in", "std_logic_vector(0 to MUX_NUM-1)")]
        signals += [("data_in", "in", "mux_data_array_type(0 to MUX_NUM-1)")]
        signals += [("enable_out", "out", "std_logic")]
        signals += [("data_out", "out", "std_logic_vector(MUX_DATA_WIDTH-1 downto 0)")]

        return signals

    def generateEntityDeclaration(self):
        frame = """
entity {} is
port (
    {}
);
end {};
"""
        signals = []
        for signal in self.generateDeclarationSignals():
            signals += ["\n{} : {} {}".format(signal[0], signal[1], signal[2])]		
        return frame.format(self.entity_name, ";".join(signals), self.entity_name)

    def generateComponentDeclaration(self):
        entity_declaration = self.generateEntityDeclaration()
        component_declaration = entity_declaration.replace("entity {}".format(self.entity_name), "component {}".format(self.entity_name))
        component_declaration = component_declaration.replace("end {}".format(self.entity_name), "end component {}".format(self.entity_name))
        return component_declaration

    def generateArchitectureDefinition(self):
        architecture = """
architecture rtl of {} is
	
    type data_stage_type is array(natural range <>) of mux_data_array_type(0 to MUX_NUM-1 + MUX_FACTOR);
    signal data_stage : data_stage_type(0 to MUX_STAGES);
    
    type enable_stage_type is array(natural range <>) of std_logic_vector(0 to MUX_NUM-1 + MUX_FACTOR);
    signal enable_stage : enable_stage_type(0 to MUX_STAGES);  
{}
begin

    enable_stage(0)(0 to MUX_NUM-1) <= enable_in;
	data_stage(0)(0 to MUX_NUM-1) <= data_in;

    GEN_STAGES: for s in 0 to MUX_STAGES-1 generate
    	GEN_STAGE: for i in 0 to (MUX_NUM-1) / (MUX_FACTOR**(s+1)) generate
{}
        end generate GEN_STAGE;
    end generate GEN_STAGES;
    
    enable_out <= enable_stage(MUX_STAGES)(0);
    data_out <= data_stage(MUX_STAGES)(0);
 
end rtl;	
"""
        component_declaration = self.msg.generateComponentDeclaration()

        signal_map = {
            "clk" : "clk",
            "enable_in" : "enable_stage(s)(0 + i*MUX_FACTOR to MUX_FACTOR-1 + i*MUX_FACTOR)",
            "data_in" : "data_stage(s)(0 + i*MUX_FACTOR to MUX_FACTOR-1 + i*MUX_FACTOR)",
            "enable_out" : "enable_stage(s+1)(i)",
            "data_out" : "data_stage(s+1)(i)"
        }
        component_instantiation = generateComponentInstantiation("MUX_SINGLE_INST", self.msg.entity_name, signal_map, None)


        return architecture.format(self.entity_name, component_declaration, component_instantiation)

    def generateFile(self, folder):
        f = open("{}/{}.vhd".format(folder, self.entity_name), "w")
        content = self.generateIncludes()
        content += self.generateEntityDeclaration()
        content += self.generateArchitectureDefinition()
        f.write(content)
        f.close()

        self.msg.generateFile(folder)

if __name__ == "__main__":
    mg = MuxGenerator()
    mg.generateFile("./output")