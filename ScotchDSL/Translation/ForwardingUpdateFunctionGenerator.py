from Functions import UpdateFunctionGenerator, FunctionGenerator
from GeneratorUtils import generateComponentInstantiation

class ForwardingUpdateFunctionGenerator(FunctionGenerator):
    def __init__(self, statements, value_width, seed_width, state_width, addr_width, synchronous=False):
        self.ug = UpdateFunctionGenerator(statements, value_width, seed_width, state_width, synchronous)
        self.statements = statements
        self.value_width = value_width
        self.seed_width = seed_width
        self.state_width = state_width
        self.addr_width = addr_width
        self.synchronous = synchronous

        self.entity_name = "forwarding_update"
        self.signals = self.generateDeclarationSignals()

        self.architecture_frame = """
ARCHITECTURE a{} OF {} IS
{}
BEGIN
{}
END a{};
"""
        self.entity_frame = """
ENTITY {} IS
PORT (
    {}
);
END {};"""

    def generateSynchronousArchitecture(self):
        #Generate auxilliary signals
        sm = self.generateSignalTypeMap()
        aux_signals = ""

        update_declaration = self.ug.generateComponentDeclaration() 

        aux_signals += "\nsignal istate : {};".format(sm["state"])
        aux_signals += "\nsignal iladdress : {};".format(sm["addr_in"])
        aux_signals += "\nsignal ioutstate : {};".format(sm["outstate"])
        aux_signals += "\nsignal tstate : {};".format(sm["outstate"])

        update_signal_map = {
                "clk" : "clk",
                "v" : "v",
                "seed" : "seed",
                "state" : "istate",
                "outstate" : "ioutstate"
        } 
        update_component = generateComponentInstantiation("u", self.ug.entity_name, update_signal_map, None)

        bhv = """
istate <= tstate when fwd_enable_in = '1' and cmp_in = '1' else state ;
addr_out <= iladdress;
outstate <= tstate;

process(clk) 
begin
    if rising_edge(clk) then
        iladdress <= addr_in;
        tstate <= ioutstate;
    end if;
end process;
        """            


        return self.architecture_frame.format(self.entity_name, self.entity_name, update_declaration+aux_signals, update_component+bhv, self.entity_name)

    def generateAsynchronousArchitecture(self):
        #Generate auxilliary signals
        sm = self.generateSignalTypeMap()
        aux_signals = ""

        update_declaration = self.ug.generateComponentDeclaration() 

        aux_signals += "\nsignal istate : {};".format(sm["state"])
        aux_signals += "\nsignal ioutstate : {};".format(sm["outstate"])
        aux_signals += "\nsignal iloutstate : {};".format(sm["outstate"])
        aux_signals += "\nsignal iladdress : {};".format(sm["addr_in"])

        update_signal_map = {
                "clk" : "clk",
                "v" : "v",
                "seed" : "seed",
                "state" : "istate",
                "outstate" : "ioutstate"
        } 
        update_component = generateComponentInstantiation("u", self.ug.entity_name, update_signal_map, None)

        bhv = """
istate <= iloutstate when fwd_enable_in = '1' and cmp_in = '1' else state ;
outstate <= iloutstate;
addr_out <= iladdress;

process(clk) 
begin
    if rising_edge(clk) then
        iloutstate <= ioutstate;
        iladdress <= addr_in;
    end if;
end process;
        """

        return self.architecture_frame.format(self.entity_name, self.entity_name, update_declaration+aux_signals, update_component+bhv, self.entity_name)


    def generateArchitecture(self):
        if self.synchronous:
            return self.generateSynchronousArchitecture()
        else:
            return self.generateAsynchronousArchitecture()

    def generateDeclarationSignals(self):
        return self.ug.signals+[
            ("fwd_enable_in","in","std_logic"),
            ("cmp_in","in","std_logic"),
            ("addr_in","in","std_logic_vector({} downto 0)".format(self.addr_width-1)),
            ("addr_out","out","std_logic_vector({} downto 0)".format(self.addr_width-1))

        ]

    def computeLatency(self):
        if self.synchronous:
            return self.ug.computeLatency()+1
        else:
            latency = self.ug.computeLatency()+1
            assert latency == 1
            return latency

    def generateFile(self, folder):
        self.ug.generateFile(folder)
        f = open("{}/{}.vhd".format(folder, self.entity_name), "w")
        f.write(self.generateFunctionFile())
        f.close()
