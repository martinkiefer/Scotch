class MemorySegmentGenerator:
	def __init__(self):
		self.entity_name = "memory_pipeline_segment"

	def generateIncludes(self):
		return """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
"""

	def getEntitySignals(self):
		signals = []
		signals += [("clk", "in", "std_logic")] 
		signals += [("rd_addr_in", "in", "std_logic_vector(ADDR_WIDTH_FULL-1 downto 0)")] 
		signals += [("rd_data_in", "in", "std_logic_vector(MEM_WIDTH-1 downto 0)")]

		signals += [("rd_addr_out", "out", "std_logic_vector(ADDR_WIDTH_FULL-1 downto 0)")] 
		signals += [("rd_data_out", "out", "std_logic_vector(MEM_WIDTH-1 downto 0)")]	

		signals += [("wr_en_in", "in", "std_logic")] 
		signals += [("wr_addr_in", "in", "std_logic_vector(ADDR_WIDTH_FULL-1 downto 0)")] 
		signals += [("wr_data_in", "in", "std_logic_vector(MEM_WIDTH-1 downto 0)")]

		signals += [("wr_en_out", "out", "std_logic")] 
		signals += [("wr_addr_out", "out", "std_logic_vector(ADDR_WIDTH_FULL-1 downto 0)")] 
		signals += [("wr_data_out", "out", "std_logic_vector(MEM_WIDTH-1 downto 0)")]

		return signals

	def getEntityGenericVariables(self):
		signals = []
		signals += [("ADDR_WIDTH_FULL", "natural")] 
		signals += [("ADDR_WIDTH", "natural")] 
		signals += [("VAL_WIDTH", "natural")] 
		signals += [("MEM_WIDTH", "natural")] 
		signals += [("LO", "natural")]
		signals += [("HI", "natural")] 
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
	-- Memory
	type mem_type is array(2 ** ADDR_WIDTH-1 downto 0) of std_logic_vector(MEM_WIDTH-1 downto 0);
	shared variable mem : mem_type := (others => (others => '0'));
        signal tmp_rd_data_in : std_logic_vector(MEM_WIDTH-1 downto 0);
	signal tmp_ram : std_logic_vector(MEM_WIDTH-1 downto 0);
	signal tmp_wr_data_in : std_logic_vector(MEM_WIDTH-1 downto 0);
	signal tmp_wr_addr_in : std_logic_vector(ADDR_WIDTH_FULL-1 downto 0);
	signal tmp_rd_addr_in : std_logic_vector(ADDR_WIDTH_FULL-1 downto 0);
	signal tmp_wr_en_in : std_logic;
	
	begin
	-- Signal Buffering
	process(clk)
	begin
		if rising_edge(clk) then
			rd_addr_out <= rd_addr_in;
			
			wr_en_out  <= wr_en_in;
			wr_addr_out <= wr_addr_in;
			wr_data_out <= wr_data_in;

			tmp_rd_data_in <= rd_data_in;
			tmp_wr_addr_in <= wr_addr_in;
			tmp_rd_addr_in <= rd_addr_in;
			tmp_wr_data_in <= wr_data_in;

			tmp_ram <= mem(to_integer(unsigned(rd_addr_in(ADDR_WIDTH-1 downto 0))));
			tmp_wr_en_in <= wr_en_in;
		end if;
	end process;
	
	
	
	-- Write Port
        process(tmp_ram, tmp_rd_data_in, tmp_wr_data_in, tmp_rd_addr_in, tmp_wr_addr_in, tmp_wr_en_in)
        begin
                        if to_integer(unsigned(tmp_rd_addr_in)) >= LO and to_integer(unsigned(tmp_rd_addr_in)) <= HI then
                                rd_data_out <= tmp_ram;
                        else
                                rd_data_out <= tmp_rd_data_in;
                        end if;
        end process;

	process(clk)
	begin
		if rising_edge(clk) then

			if wr_en_in = '1' and to_integer(unsigned(wr_addr_in)) >= LO and to_integer(unsigned(wr_addr_in)) <= HI then
				mem(to_integer(unsigned(wr_addr_in(ADDR_WIDTH-1 downto 0)))) := wr_data_in;
			end if;
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
