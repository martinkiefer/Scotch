from math import ceil, log2, floor
from GeneratorUtils import generateComponentInstantiation

class MemoryComponentGenerator:
    def __init__(self, sizes, depth, val_width, memory_segment_generator, memory_buffer_generator, identifier):
        self.sizes = sizes
        self.width = int(ceil(log2(sum(self.sizes))))
        self.depth = depth
        self.val_width = val_width
        self.msg = memory_segment_generator
        self.mbg = memory_buffer_generator
        self.identifier = identifier

        self.entity_name = "memory_component_{}".format(self.identifier)

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

        signals += [("rd_addr_in", "in", "std_logic_vector({} downto 0)".format(self.width-1))]

        signals += [("rd_addr_out", "out", "std_logic_vector({} downto 0)".format(self.width-1))]
        signals += [("rd_data_out", "out", "std_logic_vector({} downto 0)".format(self.depth-1))]  

        signals += [("wr_en_in", "in", "std_logic")]
        signals += [("wr_addr_in", "in", "std_logic_vector({} downto 0)".format(self.width-1))]
        signals += [("wr_data_in", "in", "std_logic_vector({} downto 0)".format(self.depth-1))]

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
        frame = """
ARCHITECTURE a{} OF {} IS
{}
BEGIN
{}
END a{};
"""        

        #Declare memory pipeline segments
        declarations = self.msg.generateComponentDeclaration()

        #Generate connection signals. One connecting signal for each in and out signal per clock.
        signals = []
        for index, size in enumerate(self.sizes):
            for signal in self.msg.getEntitySignals():
                dec = "\nsignal stage{}_{} : {}".format(index, signal[0],signal[2])
                #There are logic vector sizes depending on the generic variables. We need to replace those.
                dec = dec.replace("ADDR_WIDTH_FULL", str(self.width))
                dec = dec.replace("MEM_WIDTH", str(self.depth))
                dec = dec.replace("VAL_WIDTH", str(self.val_width))
                signals += [dec]

        declarations += self.mbg.generateComponentDeclaration()
        for signal in self.mbg.getEntitySignals():
            dec = "\nsignal buf_{} : {}".format(signal[0],signal[2])
            #There are logic vector sizes depending on the generic variables. We need to replace those.
            dec = dec.replace("ADDR_WIDTH_FULL", str(self.width))
            dec = dec.replace("MEM_WIDTH", str(self.depth))
            dec = dec.replace("VAL_WIDTH", str(self.val_width))
            signals += [dec]
        declarations += "\n"+";".join(signals)+";"

        #BEGIN
        #Instantiate memory segment components
        bhv = ""
        lo = 0
        for index, size in enumerate(self.sizes):
            args = {}
            for signal in self.msg.getEntitySignals():
                args[signal[0]] = "stage{}_{}".format(index, signal[0])
            generic_values = {"ADDR_WIDTH_FULL" : self.width, "VAL_WIDTH" : self.val_width, "MEM_WIDTH" : self.depth}
            generic_values["ADDR_WIDTH"] = int(log2(size))
            generic_values["LO"] = lo
            generic_values["HI"] = lo+size-1
            bhv += generateComponentInstantiation("stage{}".format(index),self.msg.entity_name, args, generic_values)
            lo += size

        args = {}
        for signal in self.mbg.getEntitySignals():
            args[signal[0]] = "buf_{}".format(signal[0])
        generic_values = {"ADDR_WIDTH_FULL" : self.width, "VAL_WIDTH" : self.val_width, "MEM_WIDTH" : self.depth}
        bhv += generateComponentInstantiation("buf",self.mbg.entity_name, args, generic_values)

        #Connect Signals
        #First connect input signals to first stage.
        signals = []

        signals += ["buf_clk <= clk"]
        signals += ["buf_rd_data_in <= (others => '0')"]
        signals += ["buf_rd_addr_in <= rd_addr_in"] 
        signals += ["buf_wr_en_in <= wr_en_in"]
        signals += ["buf_wr_addr_in <= wr_addr_in"]
        signals += ["buf_wr_data_in <= wr_data_in"]

        signals += ["stage0_clk <= clk"]
        signals += ["stage0_rd_data_in <= buf_rd_data_out"]
        signals += ["stage0_rd_addr_in <= buf_rd_addr_out"] 
        signals += ["stage0_wr_en_in <= buf_wr_en_out"]
        signals += ["stage0_wr_addr_in <= buf_wr_addr_out"]
        signals += ["stage0_wr_data_in <= buf_wr_data_out"]       

        #Connect pipeline stages
        for index in range(1,len(self.sizes)):
            signals += ["stage{}_clk <= clk".format(index)]

            signals += ["stage{}_rd_addr_in <= stage{}_rd_addr_out".format(index,index-1)]
            signals += ["stage{}_rd_data_in <= stage{}_rd_data_out ".format(index,index-1)]

            signals += ["stage{}_wr_en_in <= stage{}_wr_en_out".format(index,index-1)]
            signals += ["stage{}_wr_addr_in <= stage{}_wr_addr_out".format(index,index-1)]
            signals += ["stage{}_wr_data_in <= stage{}_wr_data_out".format(index,index-1)]

        #Finally, connect the output signals to the last stage
        last_stage_index = len(self.sizes)-1
        signals += ["rd_addr_out <= stage{}_rd_addr_out".format(last_stage_index)]
        signals += ["rd_data_out <= stage{}_rd_data_out".format(last_stage_index)]     

        bhv += "\n"+";\n".join(signals)+";"

        return frame.format(self.entity_name, self.entity_name, declarations, bhv, self.entity_name)

    def generateFile(self, folder):
        f = open("{}/{}.vhd".format(folder, self.entity_name), "w")
        content = self.generateIncludes()
        content += self.generateEntityDeclaration()
        content += self.generateArchitectureDefinition()
        f.write(content)
        f.close()

    def generateComponentDeclaration(self):
        entity_declaration = self.generateEntityDeclaration()
        component_declaration = entity_declaration.replace("ENTITY {}".format(self.entity_name), "COMPONENT {}".format(self.entity_name))
        component_declaration = component_declaration.replace("END {}".format(self.entity_name), "END COMPONENT {}".format(self.entity_name))
        return component_declaration

