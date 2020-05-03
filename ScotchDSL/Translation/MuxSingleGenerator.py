class MuxSingleGenerator:
	def __init__(self):
		self.entity_name = "mux_single"

	def generateIncludes(self):
		return """
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use WORK.mux_config_pkg.all;
"""

	def getEntitySignals(self):
		signals = []
		signals += [("clk", "in", "std_logic")]
		signals += [("enable_in", "in", "std_logic_vector(0 to MUX_FACTOR-1)")]
		signals += [("data_in", "in", "mux_data_array_type(0 to MUX_FACTOR-1)")]
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
		for signal in self.getEntitySignals():
			signals += ["\n{} : {} {}".format(signal[0], signal[1], signal[2])]		
		return frame.format(self.entity_name, ";".join(signals), self.entity_name)

	def generateComponentDeclaration(self):
		entity_declaration = self.generateEntityDeclaration()
		component_declaration = entity_declaration.replace("entity {}".format(self.entity_name), "component {}".format(self.entity_name))
		component_declaration = component_declaration.replace("end {}".format(self.entity_name), "end component {}".format(self.entity_name))
		return component_declaration

	def generateArchitectureDefinition(self):
		return """
architecture rtl of {} is
begin
process(clk, enable_in, data_in)
	begin
    if rising_edge(clk) then
		enable_out <= '0';
    	data_out <= (others => '0');
		for i in 0 to MUX_FACTOR-1 loop
        	if enable_in(i) = '1' then
				enable_out <= enable_in(i);
				data_out <= data_in(i);
			end if;
   		end loop;
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
    msg = MuxSingleGenerator()
    msg.generateFile("./output")