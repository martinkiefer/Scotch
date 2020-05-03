class EnableDemuxSingleGenerator:
    def __init__(self):
        self.entity_name = "enable_demux_single"

    def generateIncludes(self):
        return """
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use WORK.enable_demux_config_pkg.all;
"""


    def getEntitySignals(self):
        signals = []
        signals += [("clk", "in", "std_logic")]
        signals += [("enable_in", "in", "std_logic")]
        signals += [("index_in", "in", "std_logic_vector(ENABLE_DEMUX_INDEX_WIDTH-1 downto 0)")]
        signals += [("enable_out", "out", "std_logic_vector(0 to ENABLE_DEMUX_FACTOR-1)")]
        signals += [("rest_out", "out", "enable_demux_index_array_type(0 to ENABLE_DEMUX_FACTOR-1)")]

        return signals

    def getEntityGenericVariables(self):
        signals = []
        signals += [("STAGE_FACTOR", "integer")] 
        return signals

    def generateEntityDeclaration(self):
        frame = """
entity {} is
generic (
    {}
);
port (
    {}
);
end {};
"""
        generics = []
        for signal in self.getEntityGenericVariables():
            generics += ["\n{} : {}".format(signal[0], signal[1])]

        signals = []
        for signal in self.getEntitySignals():
            signals += ["\n{} : {} {}".format(signal[0], signal[1], signal[2])]		
        return frame.format(self.entity_name, ";".join(generics), ";".join(signals), self.entity_name)

    def generateComponentDeclaration(self):
        entity_declaration = self.generateEntityDeclaration()
        component_declaration = entity_declaration.replace("entity {}".format(self.entity_name), "component {}".format(self.entity_name))
        component_declaration = component_declaration.replace("end {}".format(self.entity_name), "end component {}".format(self.entity_name))
        return component_declaration

    def generateArchitectureDefinition(self):
        return """
architecture rtl of {} is
begin
process(clk, enable_in, index_in)
	variable factor : natural;
    variable index_in_nat : natural;
    variable index_out_nat : natural;
    variable rest : natural;
	begin
    if rising_edge(clk) then
        factor := ENABLE_DEMUX_FACTOR ** STAGE_FACTOR;
        index_in_nat := to_integer(unsigned(index_in));
		index_out_nat := index_in_nat / factor;
        rest := index_in_nat mod factor;
        
    	enable_out <= (others => '0');
        if enable_in = '1' then
            enable_out(index_out_nat) <= '1';
       	end if;
        
		rest_out <= (others => std_logic_vector(to_unsigned(rest, ENABLE_DEMUX_INDEX_WIDTH)));
	end if;
end process;
end rtl;
""".format(self.entity_name)

    def generateFile(self, folder):
        f = open("{}/{}.vhd".format(folder, self.entity_name), "w")
        content = self.generateIncludes()
        content += self.generateEntityDeclaration()
        content += self.generateArchitectureDefinition()
        f.write(content)
        f.close()

if __name__ == "__main__":
    msg = EnableDemuxSingleGenerator()
    msg.generateFile("./output")