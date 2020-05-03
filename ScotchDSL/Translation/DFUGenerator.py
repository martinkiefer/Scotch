class DFUGenerator:
    def __init__(self):
        self.entity_name = "dfu"

    def generateIncludes(self):
        return """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
"""

    def getEntitySignals(self):
        signals = []
        signals += [("clk", "in", "std_logic")]  

        signals += [("addr_in", "in", "std_logic_vector(ADDR_WIDTH-1 downto 0)")] 
        signals += [("data_in", "in", "std_logic_vector(MEM_WIDTH-1 downto 0)")] 
        
        signals += [("enable_r_in", "in", "std_logic")]
        signals += [("addr_r_in", "in", "std_logic_vector(ADDR_WIDTH-1 downto 0)")] 
        signals += [("data_r_in", "in", "std_logic_vector(MEM_WIDTH-1 downto 0)")] 

        signals += [("addr_out", "out", "std_logic_vector(ADDR_WIDTH-1 downto 0)")] 
        signals += [("data_out", "out", "std_logic_vector(MEM_WIDTH-1 downto 0)")] 
        signals += [("cmp_out", "out", "std_logic")] 

        return signals

    def getEntityGenericVariables(self):
        signals = []
        signals += [("DFU_WIDTH", "natural")] 
        signals += [("MEM_WIDTH", "natural")] 
        signals += [("ADDR_WIDTH", "natural")] 
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
architecture rtl of {}  is
	type stage_addr_type is array(natural range <>) of std_logic_vector(ADDR_WIDTH-1 downto 0);
	type stage_data_type is array(natural range <>) of std_logic_vector(MEM_WIDTH-1 downto 0);

	begin
    
    process(clk)
    
    variable stage_r_en : unsigned(0 to DFU_WIDTH-1) := (others => '0');
	 
	 variable tick_tock : unsigned(0 to DFU_WIDTH-1) := (others => '0');
	 variable tick_match : unsigned(0 to DFU_WIDTH-1) := (others => '0');
	 variable tock_match : unsigned(0 to DFU_WIDTH-1) := (others => '0');

    
	variable stage_addr : stage_addr_type(0 to DFU_WIDTH) := (others => (others => '0'));
	variable stage_r_addr : stage_addr_type(0 to DFU_WIDTH-1) := (others => (others => '0'));
	variable stage_data_tick, stage_data_tock, stage_r_data : stage_data_type(0 to DFU_WIDTH-1) := (others => (others => '0'));
	
	begin
	
	if rising_edge(clk) then
		
        stage_addr(0) := addr_in;
		  
        stage_data_tick(0) := data_in;
        stage_data_tock(0) := data_in;
	tick_tock(0) := '0';
	tock_match(0) := '0';
	tick_match(0) := '0';
		  
        stage_r_en(0) := enable_r_in;
        stage_r_addr(0) := addr_r_in;
        stage_r_data(0) := data_r_in;
		
		for i in 0 to DFU_WIDTH-1 loop
				tick_tock(i) := (not tick_match(i)) and (tick_tock(i) or tock_match(i));
            if i /= DFU_WIDTH-1 then
					-- The element compared in tick is always more recent then in tock
                                        if stage_r_en(DFU_WIDTH-1 - i) = '1' and stage_addr(i) = stage_r_addr(DFU_WIDTH-1 - i) then
                                                 stage_data_tock(i) := stage_r_data(DFU_WIDTH-1 - i);
                                                 tock_match(i) := '1';
                                        else                                    
                                                 tock_match(i) := '0';
                                        end if;
                                        if stage_r_en(DFU_WIDTH-2 - i) = '1' and stage_addr(i) = stage_r_addr(DFU_WIDTH-2 - i) then
						 stage_data_tick(i) := stage_r_data(DFU_WIDTH-2 - i);
                                                 tick_match(i) := '1';
                                        else                                    
                                                 tick_match(i) := '0';
                                        end if;

				else
					if stage_r_en(DFU_WIDTH-1 - i) = '1' and stage_addr(i) = stage_r_addr(DFU_WIDTH-1 - i) then
						 data_out <= stage_r_data(DFU_WIDTH-1 - i);
					else
						 if tick_tock(i) = '0' then
							data_out <=stage_data_tick(i);
						 else
							data_out <= stage_data_tock(i);
						 end if;
					end if;					
				end if;
		end loop;
		
		addr_out <= stage_addr(DFU_WIDTH-1);
		if stage_addr(DFU_WIDTH-1) = stage_addr(DFU_WIDTH) then
			cmp_out <= '1';
		else
			cmp_out <= '0';
		end if;
		
      	-- Shift pipelines for next stage
		stage_addr(1 to DFU_WIDTH)	:= stage_addr(0 to DFU_WIDTH-1);
		stage_data_tick(1 to DFU_WIDTH-1)	:= stage_data_tick(0 to DFU_WIDTH-2);
      		stage_data_tock(1 to DFU_WIDTH-1)	:= stage_data_tock(0 to DFU_WIDTH-2);

		
 		stage_r_en	:= shift_right(stage_r_en, 1);
		tick_tock	:= shift_right(tick_tock, 1);
                tick_match      := shift_right(tick_match, 1);
                tock_match      := shift_right(tock_match, 1);


		stage_r_addr(1 to DFU_WIDTH-1)	:= stage_r_addr(0 to DFU_WIDTH-2);
		stage_r_data(1 to DFU_WIDTH-1)	:= stage_r_data(0 to DFU_WIDTH-2);

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
