from EnableDemuxSingleGenerator import EnableDemuxSingleGenerator
from GeneratorUtils import generateComponentInstantiation
from MuxConfigPackageGenerator import MuxConfigPackageGenerator

class EnableDemuxGenerator:
    def __init__(self):
        self.entity_name = "enable_demux"
        self.dsg = EnableDemuxSingleGenerator()

    def generateIncludes(self):
        return """
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use WORK.enable_demux_config_pkg.all;
"""

    def generateDeclarationSignals(self):
        signals = []
        signals += [("clk", "in", "std_logic")]
        signals += [("enable_in", "in", "std_logic")]
        signals += [("index_in", "in", "std_logic_vector(ENABLE_DEMUX_INDEX_WIDTH-1 downto 0)")]
        signals += [("enable_out", "out", "std_logic_vector(0 to ENABLE_DEMUX_NUM-1)")]

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

	type enable_stage_type is array(natural range <>) of std_logic_vector(0 to ENABLE_DEMUX_NUM-1 + ENABLE_DEMUX_FACTOR);
    signal enable_stage : enable_stage_type(0 to ENABLE_DEMUX_STAGES);
    
    type index_stage_type is array(natural range <>) of enable_demux_index_array_type(0 to ENABLE_DEMUX_NUM-1 + ENABLE_DEMUX_FACTOR);
    signal index_stage : index_stage_type(0 to ENABLE_DEMUX_STAGES);
    
{}
begin

	enable_stage(0)(0) 	<= enable_in;
    index_stage(0)(0) 	<= index_in;

    GEN_STAGES: for s in 0 to ENABLE_DEMUX_STAGES-1 generate
    	GEN_STAGE: for i in 0 to (ENABLE_DEMUX_NUM-1) / (ENABLE_DEMUX_FACTOR ** (ENABLE_DEMUX_STAGES - s)) generate
{}
        end generate GEN_STAGE;
    end generate GEN_STAGES;
    
    enable_out <= enable_stage(ENABLE_DEMUX_STAGES)(0 to ENABLE_DEMUX_NUM-1);
    
end rtl;	
"""
        component_declaration = self.dsg.generateComponentDeclaration()

        signal_map = {
            "clk" : "clk",
            "enable_in" : "enable_stage(s)(i)",
            "index_in" : "index_stage(s)(i)",
            "enable_out" : "enable_stage(s+1)(0 + i*ENABLE_DEMUX_FACTOR to ENABLE_DEMUX_FACTOR-1 + i*ENABLE_DEMUX_FACTOR)",
            "rest_out" :    "index_stage(s+1)(0 + i*ENABLE_DEMUX_FACTOR to ENABLE_DEMUX_FACTOR-1 + i*ENABLE_DEMUX_FACTOR)"

        }
        generic_map = {
            "STAGE_FACTOR" : "ENABLE_DEMUX_STAGES-1 - s"
        }
        component_instantiation = generateComponentInstantiation("ENABLE_DEMUX_SINGLE_INST", self.dsg.entity_name, signal_map, generic_map)


        return architecture.format(self.entity_name, component_declaration, component_instantiation)

    def generateFile(self, folder):
        f = open("{}/{}.vhd".format(folder, self.entity_name), "w")
        content = self.generateIncludes()
        content += self.generateEntityDeclaration()
        content += self.generateArchitectureDefinition()
        f.write(content)
        f.close()

        self.dsg.generateFile(folder)

if __name__ == "__main__":
    atg =  MuxConfigPackageGenerator(10,3,16)
    atg.generateFile("./output")

    dg = EnableDemuxGenerator()
    dg.generateFile("./output")