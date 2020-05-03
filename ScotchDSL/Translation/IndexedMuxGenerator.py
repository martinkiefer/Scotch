from IndexedMuxSingleGenerator import IndexedMuxSingleGenerator
from GeneratorUtils import generateComponentInstantiation

class IndexedMuxGenerator:
    def __init__(self):
        self.entity_name = "mux"
        self.msg = IndexedMuxSingleGenerator()

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
        signals += [("data", "in", "mux_data_array_type(0 to MUX_NUM-1)")] 
        signals += [("enable", "in", "std_logic")] 
        signals += [("index", "in", "natural")] 
        signals += [("value", "out", "std_logic_vector(MUX_DATA_WIDTH-1 downto 0)")]
        signals += [("valid", "out", "std_logic")]

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
	constant STAGES : natural := mux_get_stages(MUX_FACTOR, MUX_NUM);
   
	type data_stage_type is array(natural range <>) of mux_data_array_type(0 to MUX_NUM-1 + MUX_FACTOR);
    signal data_stage : data_stage_type(0 to STAGES);

	signal enable_stage : std_logic_vector(0 to STAGES) := (others => '0');
    signal index_stage : mux_natural_array_type(0 to STAGES) := (others => 0);
    
{}
begin

	data_stage(0)(0 to MUX_NUM-1) <= data;
    
    SHIFT_STAGE : process(clk)
    	begin
    	if rising_edge(clk) then
        	for i in 0 to STAGES-1 loop
            	if i = 0 then 
                	index_stage(i+1) <= index / MUX_FACTOR;
  					enable_stage(i+1) <= enable;
                else
            		index_stage(i+1) <= index_stage(i) / MUX_FACTOR;
  					enable_stage(i+1) <= enable_stage(i);
                end if;
            end loop;
        end if;
    end process;
    
    -- Generate first stage seperately to pass it index directly
    GEN_FIRST_STAGE: for i in 0 to (MUX_NUM-1) / (MUX_FACTOR) generate
    	MUX_SINGLE_FIRST_INST : mux_single
      	port map(
        	clk => clk,
        	data => data_stage(0)(0 + i*MUX_FACTOR to MUX_FACTOR-1 + i*MUX_FACTOR),
        	index => index,
        	value => data_stage(1)(i)
      	);
    end generate GEN_FIRST_STAGE;

    GEN_STAGES: for s in 1 to STAGES-1 generate
    	GEN_STAGE: for i in 0 to (MUX_NUM-1) / (MUX_FACTOR**(s+1)) generate
            MUX_SINGLE_INST : mux_single
            port map(
                clk => clk,
                data => data_stage(s)(0 + i*MUX_FACTOR to MUX_FACTOR-1 + i*MUX_FACTOR),
                index => index_stage(s),
                value => data_stage(s+1)(i)
            );
        end generate GEN_STAGE;
    end generate GEN_STAGES;
    
    value <= data_stage(STAGES)(0);
    valid <= enable_stage(STAGES);
end rtl;	
"""
        component_declaration = self.msg.generateComponentDeclaration()
        return architecture.format(self.entity_name, component_declaration)

    def generateFile(self, folder):
        f = open("{}/{}.vhd".format(folder, self.entity_name), "w")
        content = self.generateIncludes()
        content += self.generateEntityDeclaration()
        content += self.generateArchitectureDefinition()
        f.write(content)
        f.close()

        self.msg.generateFile(folder)

if __name__ == "__main__":
    mg = IndexedMuxGenerator()
    mg.generateFile("./output")