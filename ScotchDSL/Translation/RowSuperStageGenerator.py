from math import ceil, log2, floor
from MemoryComponentGenerator import MemoryComponentGenerator
from HashConverterGenerator import HashConverterGenerator
from DFUGenerator import DFUGenerator
from GeneratorUtils import generateComponentInstantiation, generateSignalMap, generateAssignments
from ForwardingUpdateFunctionGenerator import ForwardingUpdateFunctionGenerator
from DChainVectorGenerator import DChainVectorGenerator
from DChainSignalGenerator import DChainSignalGenerator
from MemoryBufferGenerator import MemoryBufferGenerator

def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

class RowSuperStageGenerator:
    def __init__(self, sizes, wsseed, wuseed, wvalue, 
    wstate, memory_segment_generator, memory_buffer_generator, selector_generator, dvector_generator, dsignal_generator, update_generator,
    dfu_generator, hash_converter_generator, identifier):
        self.sizes = sizes
        self.total_size = sum(self.sizes)
        self.waddr = int(ceil(log2(self.total_size)))
        self.wsseed = wsseed
        self.wuseed = wuseed
        self.wvalue = wvalue
        self.wstate= wstate
        self.dvg = dvector_generator
        self.dsg = dsignal_generator
        self.identifier = identifier
        
        self.mbg = memory_buffer_generator
        self.msg = memory_segment_generator
        self.mcg = MemoryComponentGenerator(self.sizes, self.wstate, self.wvalue, self.msg, self.mbg, self.identifier)
        self.sg = selector_generator
        self.ug = update_generator
        self.hcg = None
        if not is_power_of_two(self.total_size):
            self.hcg = hash_converter_generator
        self.dfug = dfu_generator

        self.entity_name = "super_stage_{}".format(identifier)

        self.signals = self.generateDeclarationSignals()

    def computeMemoryLatency(self):
        return len(self.sizes)+1

    def computeDFULatency(self):
        return self.computeMemoryLatency()+1

    def computeEnablePipelineLatency(self):
        latency = 0
        if not self.hcg is None:
            latency += 1
        latency += self.sg.computeLatency()
        latency += self.computeDFULatency()
        latency += self.computeMemoryLatency()
        latency += 1 #For the update stage
        return latency

    def computeValuePipelineLatency(self):
        latency = 0
        if not self.hcg is None:
            latency += 1
        latency += self.sg.computeLatency()
        latency += self.computeDFULatency()
        latency += self.computeMemoryLatency()
        latency -= self.ug.computeLatency()
        latency += 1 #For the update stage
        return latency    
        
    def generateIncludes(self):
        return """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
"""


    def generateDeclarationSignals(self):
        signals = []
        signals += [("clk", "in", "std_logic")]

        #Signals for direct reading from read stage overrides value_enable
        signals += [("rd_en_in", "in", "std_logic")]
        signals += [("rd_addr_in", "in", "std_logic_vector({} downto 0)".format(self.waddr-1))]
        signals += [("rd_data_out", "out", "std_logic_vector({} downto 0)".format(self.wstate-1))]
        signals += [("rd_valid_out", "out", "std_logic")]

        #Signals for value processing
        signals += [("val_en_in", "in", "std_logic")]
        signals += [("val_in", "in", "std_logic_vector({} downto 0)".format(self.wvalue-1))]
        signals += [("sseed_in", "in", "std_logic_vector({} downto 0)".format(self.wsseed-1))]
        signals += [("useed_in", "in", "std_logic_vector({} downto 0)".format(self.wuseed-1))]

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

        decl = ""
        #Declarations
        ## Memory component according to provided sizes
        decl += self.mcg.generateComponentDeclaration()

        ## Selector Stage       
        decl += self.sg.generateComponentDeclaration()

        ## Update Stage       
        decl += self.ug.generateComponentDeclaration()

        decl += self.dvg.generateComponentDeclaration()
        decl += self.dsg.generateComponentDeclaration()

        ## Optional: Modulo arithmetic if log2(sum(sizes)) != wselector
        if not self.hcg is None:
            decl += self.hcg.generateComponentDeclaration()

        ## DFU
        decl += self.dfug.generateComponentDeclaration()

        ## Connecting signals
        for signal in self.mcg.generateDeclarationSignals():
            decl += "\nsignal mc_{} : {};".format(signal[0],signal[2])       
        
        for signal in self.sg.generateDeclarationSignals():
            decl += "\nsignal s_{} : {};".format(signal[0],signal[2])       

        for signal in self.ug.generateDeclarationSignals():
            decl += "\nsignal u_{} : {};".format(signal[0],signal[2]) 

        for signal in self.dvg.getEntitySignals():
            dec = "\nsignal vdv_{} : {};".format(signal[0],signal[2]) 
            decl += dec.replace("WIDTH", str(self.wvalue))

        for signal in self.dsg.getEntitySignals():
            decl += "\nsignal rds_{} : {};".format(signal[0],signal[2]) 

        for signal in self.dsg.getEntitySignals():
            decl += "\nsignal eds_{} : {};".format(signal[0],signal[2])

        if not self.hcg is None:
            for signal in self.hcg.getEntitySignals():
                dec = "\nsignal hc_{} : {};".format(signal[0],signal[2])
                dec = dec.replace("ADDR_WIDTH", str(self.waddr)) 
                decl += dec

        for signal in self.dfug.getEntitySignals():
            dec = "\nsignal dfu_{} : {};".format(signal[0],signal[2])
            dec = dec.replace("ADDR_WIDTH", str(self.waddr))
            dec = dec.replace("MEM_WIDTH", str(self.wstate))  
            decl += dec

        #Architecture behavior
        ## Generate component instanciations
        bhv = ""
        signal_map = generateSignalMap(self.mcg.generateDeclarationSignals(), "mc_")
        bhv += generateComponentInstantiation("mc", self.mcg.entity_name, signal_map, None)

        signal_map = generateSignalMap(self.sg.generateDeclarationSignals(), "s_")
        bhv += generateComponentInstantiation("s", self.sg.entity_name, signal_map, None)

        signal_map = generateSignalMap(self.ug.generateDeclarationSignals(), "u_")
        bhv += generateComponentInstantiation("u", self.ug.entity_name, signal_map, None)

        signal_map = generateSignalMap(self.dsg.getEntitySignals(), "rds_")
        generic_map = {"STAGES" : self.computeMemoryLatency()}
        bhv += generateComponentInstantiation("rds", self.dsg.entity_name, signal_map, generic_map)

        if not self.hcg is None:
            signal_map = generateSignalMap(self.hcg.getEntitySignals(), "hc_")
            generic_map = {"ADDR_WIDTH" : self.waddr, "MAX_VAL" : self.total_size}
            bhv += generateComponentInstantiation("hc", self.hcg.entity_name, signal_map, generic_map)

        signal_map = generateSignalMap(self.dfug.getEntitySignals(), "dfu_")
        generic_map = {"MEM_WIDTH" : self.wstate, "ADDR_WIDTH" : self.waddr, "DFU_WIDTH" : self.computeDFULatency()}
        bhv += generateComponentInstantiation("dfux", self.dfug.entity_name, signal_map, generic_map)

        vdv_latency = self.computeValuePipelineLatency()
        if vdv_latency > 0:
            signal_map = generateSignalMap(self.dvg.getEntitySignals(), "vdv_")
            generic_map = {"STAGES" : vdv_latency, "WIDTH" : self.wvalue}
            bhv += generateComponentInstantiation("vdv", self.dvg.entity_name, signal_map, generic_map)

            vdv_inputs = { 
                "vdv_data_in" : "val_in",
                "vdv_clk" : "clk"
            }
            bhv += generateAssignments(vdv_inputs)

        assert vdv_latency >= 0, "The update function latency is currently not allowed to exceed the latency of all previous stages plus one."

        signal_map = generateSignalMap(self.dsg.getEntitySignals(), "eds_")
        generic_map = {"STAGES" : self.computeEnablePipelineLatency()}
        bhv += generateComponentInstantiation("eds", self.dsg.entity_name, signal_map, generic_map)


        input_to_sel = {
            "s_clk" : "clk",
            "s_v" : "val_in",
            "s_seed" : "sseed_in",

            "eds_data_in" : "val_en_in",
            "eds_clk" : "clk",

            "rds_data_in" : "rd_en_in",
            "rds_clk" : "clk"
        }
        bhv += generateAssignments(input_to_sel)

        if not self.hcg is None:
            sel_to_hcg = {
                "hc_clk" : "clk",
                "hc_addr_in" : "s_offset({} downto 0)".format(self.waddr-1),
            }
            bhv += generateAssignments(sel_to_hcg)

            hcg_to_mc = {
                "mc_clk" : "clk",
                "mc_rd_addr_in" : "hc_addr_out when rd_en_in = '0' else rd_addr_in"             
            } 
            bhv += generateAssignments(hcg_to_mc)
        else:
            sel_to_mc = {
                "mc_clk" : "clk",
                "mc_rd_addr_in" : "s_offset({} downto 0) when rd_en_in = '0' else rd_addr_in".format(self.waddr-1)
            } 
            bhv += generateAssignments(sel_to_mc)

        mc_to_dfu = {
            "dfu_clk" : "clk",
            "dfu_addr_in" : "mc_rd_addr_out",
            "dfu_data_in" : "mc_rd_data_out",
        } 
        bhv += generateAssignments(mc_to_dfu)

        dfu_to_up = {
            "u_clk" : "clk",
            "u_v" : "vdv_data_out",
            "u_seed" : "useed_in",
            "u_state" : "dfu_data_out",
            "u_addr_in" : "dfu_addr_out",
            "u_fwd_enable_in" : "eds_data_out",
            "u_cmp_in": "dfu_cmp_out"
        } 
 
        up_to_mcg_dfu = {
            "mc_wr_en_in" : "eds_data_out",
            "mc_wr_addr_in" : "u_addr_out",
            "mc_wr_data_in" : "u_outstate",
            "dfu_enable_r_in" : "eds_data_out",
            "dfu_addr_r_in" : "u_addr_out",
            "dfu_data_r_in" : "u_outstate"
        }
        bhv += generateAssignments(up_to_mcg_dfu) 

        if vdv_latency == 0:
            up_to_mcg_dfu["u_v"] = "val_in"
        bhv += generateAssignments(dfu_to_up)    

        mcg_to_out = {
            "rd_data_out" : "mc_rd_data_out",
            "rd_valid_out" : "rds_data_out"           
        }
        bhv += generateAssignments(mcg_to_out) 

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

        self.mcg.generateFile(folder)

if __name__ == "__main__":

    from ParserInterface import *
    from Functions import SelectorFunctionGenerator, UpdateFunctionGenerator
    from FunctionPackageGenerator import FunctionPackageGenerator
    from MemorySegmentGenerator import MemorySegmentGenerator

    msg = MemorySegmentGenerator()
    with open(sys.argv[1]) as f:
        data = json.load(f)

        outdir = "./output"
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        selector_list = create_selector_function_statement_list(data)
        update_list = create_update_function_statement_list(data)

        dvg = DChainVectorGenerator()
        dvg.generateFile("./output")

        dsg = DChainSignalGenerator()
        dsg.generateFile("./output")

        fpg = FunctionPackageGenerator()
        fpg.generateFile("./output")

        sfg = SelectorFunctionGenerator(selector_list, data["value_size"], data["selector_seed_size"], data["offset_max_size"], True)
        sfg.generateFile("./output")

        waddr = int(ceil(log2(sum([512, 512, 1024, 1024, 512]))))
        ufg = ForwardingUpdateFunctionGenerator(update_list, data["value_size"], data["update_seed_size"], data["state_size"], waddr, True)
        ufg.generateFile("./output")

        msg = MemorySegmentGenerator()
        msg.generateFile("./output") 

        mbg = MemoryBufferGenerator()
        msg.generateFile("./output") 

        dfug = DFUGenerator()
        dfug.generateFile("./output")

        hcg = HashConverterGenerator()
        hcg.generateFile("./output")

        ssg = RowSuperStageGenerator([512, 512, 1024, 1024, 512], data["selector_seed_size"], data["update_seed_size"], data["value_size"], data["state_size"], msg, mbg, sfg, dvg, dsg, ufg, dfug, hcg, 1)
        ssg.generateFile("./output")
