class DChainVectorGenerator:
    def __init__(self):
        self.entity_name = "dchain_vector"

    def generateIncludes(self):
        return """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
"""

    def getEntitySignals(self):
        signals = []
        signals += [("clk", "in", "std_logic")] 
        signals += [("data_in", "in", "std_logic_vector(WIDTH-1 downto 0)")] 
        signals += [("data_out", "out", "std_logic_vector(WIDTH-1 downto 0)")] 
        return signals

    def getEntityGenericVariables(self):
        signals = []
        signals += [("STAGES", "natural")]
        signals += [("WIDTH", "natural")] 
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
type pipeline_type is array(STAGES-1 downto 0) of std_logic_vector(WIDTH-1 downto 0);
begin
	process(clk)
    variable pipeline : pipeline_type;
    begin
	if rising_edge(clk) then
        for i in STAGES-1 downto 1 loop
        	pipeline(i) := pipeline(i-1);
        end loop;
        pipeline(0) := data_in;
        data_out <= pipeline(STAGES-1);
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
    hcg = DChainVectorGenerator()
    hcg.generateFile("./")
