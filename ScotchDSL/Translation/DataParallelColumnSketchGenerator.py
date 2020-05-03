from GeneratorUtils import generateComponentInstantiation, generateSignalMap, generateAssignments
from DataParallelSingleStateSuperStageGenerator import DataParallelSingleStateSuperStageGenerator
from FunctionPackageGenerator import FunctionPackageGenerator
from SeedGenerator import SeedGenerator
from MuxGenerator import MuxGenerator
from MuxConfigPackageGenerator import MuxConfigPackageGenerator
from EnableDemuxGenerator import EnableDemuxGenerator
from EnableDemuxConfigPackageGenerator import EnableDemuxConfigPackageGenerator
from GlobalConfigPackageGenerator import GlobalConfigPackageGenerator
from DChainSignalGenerator import DChainSignalGenerator
from ColumnSketchGenerator import ColumnSketchGenerator

import math
import os

def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

class DataParallelColumnSketchGenerator(ColumnSketchGenerator):
    def __init__(self, size, n_parallel, neutral_compout, wuseed, wvalue, wcompout, 
    wstate, initial_state, compute_generator, update_generator, ss_factor, dfactor, cfactor):
        self.n_parallel = n_parallel
        self.neutral_compout = neutral_compout
        self.cg = compute_generator
        self.wcompout = wcompout
        super().__init__(size, wuseed, wvalue, wstate, initial_state, update_generator, ss_factor, dfactor, cfactor)
        self.gcpg = GlobalConfigPackageGenerator("map-reduce", self.wstate, self.wvalue, 0, self.n_parallel, 0, self.wuseed, 
    dfactor, cfactor, 1, 1, self.size, 1)
        self.ssg = DataParallelSingleStateSuperStageGenerator(self.n_parallel, self.neutral_compout, self.wuseed, self.wvalue, self.wcompout, self.wstate, initial_state, self.cg, self.ug, self.dsg)


    def generateDeclarationSignals(self):
        signals = []
        signals += [("clk", "in", "std_logic")]

        #Signals for direct reading from read stage overrides value_enable
        signals += [("rd_en_in", "in", "std_logic")]
        signals += [("rd_data_out", "out", "std_logic_vector({} downto 0)".format(self.wstate-1))]
        signals += [("rd_valid_out", "out", "std_logic")]


        for i in range(0,self.n_parallel):
            #Signals for value processing
            signals += [("val{}_en_in".format(i), "in", "std_logic")]
            signals += [("val{}_in".format(i), "in", "std_logic_vector({} downto 0)".format(self.wvalue-1))]

        return signals

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
        decl += self.ssg.generateComponentDeclaration()

        decl += self.muxg.generateComponentDeclaration()

        decl += self.demuxg.generateComponentDeclaration()

        ## Connecting signals
        for i in range(0, self.size):
            for signal in self.ssg.generateDeclarationSignals():
                decl += "\nsignal ss{}_{} : {};".format(i, signal[0],signal[2])       

        for signal in self.muxg.generateDeclarationSignals():
            decl += "\nsignal smux_{} : {};".format(signal[0],signal[2])     

        for signal in self.demuxg.generateDeclarationSignals():
            decl += "\nsignal sdemux_{} : {};".format(signal[0],signal[2])

        decl += "\nsignal index : std_logic_vector({}-1 downto 0) := (others => '0');".format(int(math.ceil(math.log2(self.size))))
        decl += "\ntype mem_type is array({} downto 0) of std_logic_vector({} downto 0);".format(self.nss_per_package-1, self.wvalue-1)

        #Architecture behavior
        ## Generate component instanciations
        bhv = ""
        for i in range(0, self.size):
            signal_map = generateSignalMap(self.ssg.generateDeclarationSignals(), "ss{}_".format(i))
            bhv += generateComponentInstantiation("ss{}".format(i), self.ssg.entity_name, signal_map, None)


        signal_map = generateSignalMap(self.muxg.generateDeclarationSignals(), "smux_")
        bhv += generateComponentInstantiation("smux", self.muxg.entity_name, signal_map, None)

        signal_map = generateSignalMap(self.demuxg.generateDeclarationSignals(), "sdemux_")
        bhv += generateComponentInstantiation("sdemux", self.demuxg.entity_name, signal_map, None)

        clk_map = {}
        clk_map["smux_clk"] = "clk"
        clk_map["sdemux_clk"] = "clk"

        seed_map = {}
        for i in range(0, self.size):
            clk_map["ss{}_clk".format(i)] = "clk" 
            seed_map["ss{}_useed_in".format(i)] = "update_seeds({})".format(i)
        bhv += generateAssignments(clk_map) 
        bhv += generateAssignments(seed_map)

        demux_inmap = {
            "sdemux_enable_in" : "rd_en_in",
            "sdemux_index_in" : "index"
        }
        bhv += generateAssignments(demux_inmap)

        mux_outmap = {
            "rd_data_out" : "smux_data_out",
            "rd_valid_out" : "smux_enable_out"
        }
        bhv += generateAssignments(mux_outmap)

        assignments = ""
        for i in range(0, self.size):
            for j in range(0, self.n_parallel):
                assignments += "        ss{}_val{}_en_in <= enable_pipe{}({});\n".format(i,j, j, i // self.ss_factor)
                assignments += "        ss{}_val{}_in <= value_pipe{}({});\n".format(i, j, j, i // self.ss_factor)

        for i in range(0, self.size):
            #Connect demux output to read inputs
            bhv += "smux_data_in({}) <= ss{}_rd_data_out ;\n".format(i, i)

        bhv += "smux_enable_in <= sdemux_enable_out;\n"

        process_declaration = ""
        for i in range(0, self.n_parallel):
            process_declaration += "variable enable_pipe{} : std_logic_vector({} downto 0) := (others => '0');\n".format(i, self.nss_per_package-1)
            process_declaration += "variable value_pipe{} : mem_type;\n".format(i)

        loop_assignments = ""
        for i in range(0, self.n_parallel):
            loop_assignments += "enable_pipe{}(i+1) := enable_pipe{}(i);\n".format(i, i)
            loop_assignments += "value_pipe{}(i+1) := value_pipe{}(i);\n".format(i, i)

            assignments += "enable_pipe{}(0) := val{}_en_in;\n".format(i,i)
            assignments += "value_pipe{}(0) := val{}_in;\n".format(i,i)

        bhv += """
	process(clk)
    begin
    if rising_edge(clk) then
        if rd_en_in = '1' then
            if to_integer(unsigned(index)) >= {} then
                index <= (others => '0');
            else
                index <= std_logic_vector(to_unsigned(to_integer(unsigned(index)) + 1, index'LENGTH));
            end if;
        end if;
    end if;
    end process;

	process(clk)
        {}
	begin
    if rising_edge(clk) then
{}
        for i in {} downto 0 loop
            {}
        end loop;
    end if;
    end process;
        """.format(self.size-1, process_declaration, assignments, self.nss_per_package-2, loop_assignments)

        return frame.format(self.entity_name, self.entity_name, decl, bhv, self.entity_name)


    def generateFile(self, folder):
        f = open("{}/{}.vhd".format(folder, self.entity_name), "w")
        content = self.generateIncludes()
        content += self.generateEntityDeclaration()
        content += self.generateArchitectureDefinition()
        f.write(content)
        f.close()

        self.ssg.generateFile(folder)
        self.dsg.generateFile(folder)
        self.gcpg.generateFile(folder)
        self.fpg.generateFile(folder)
        self.usg.generateFile(folder)
        self.muxg.generateFile(folder)
        self.mux_pkg.generateFile(folder)
        self.demuxg.generateFile(folder)
        self.demux_pkg.generateFile(folder)


if __name__ == "__main__":

    from ParserInterface import *
    from Functions import DataParallelUpdateFunctionGenerator
    from Functions import SelectorFunctionGenerator
    from GlobalConfigPackageGenerator import GlobalConfigPackageGenerator

    with open(sys.argv[1]) as f:
        data = json.load(f)

        if len(sys.argv) == 6:
            outdir = sys.argv[5]
        else:
            outdir = "./output"

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        cwd = os.getcwd()
        os.chdir(os.path.dirname(sys.argv[1]))
        selector_list = create_compute_function_statement_list(data)
        update_list = create_cupdate_function_statement_list(data)
        os.chdir(cwd)
        
        cfg = SelectorFunctionGenerator(selector_list, data["value_size"], data["update_seed_size"], data["compute_out_size"], True)
        cfg.generateFile(outdir)

        ufg = DataParallelUpdateFunctionGenerator(update_list, data["compute_out_size"], data["update_seed_size"], data["state_size"], int(data["parallel_values"]), True)
        ufg.generateFile(outdir)

        if not "initial_state" in data:
            data["initial_state"] = "(others => '0')"
        ssg = DataParallelColumnSketchGenerator(int(sys.argv[2]), int(data["parallel_values"]), data["compute_neutral"], data["update_seed_size"], data["value_size"], data["compute_out_size"], data["state_size"], data["initial_state"], cfg, ufg, 1, int(sys.argv[3]), int(sys.argv[4]))
        ssg.generateFile(outdir)


