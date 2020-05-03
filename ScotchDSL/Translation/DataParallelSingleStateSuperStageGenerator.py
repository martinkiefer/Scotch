from GeneratorUtils import generateComponentInstantiation, generateSignalMap, generateAssignments
from SingleStateSuperStageGenerator import SingleStateSuperStageGenerator

#TODO: Add additional delay to account for update function latency.
class DataParallelSingleStateSuperStageGenerator(SingleStateSuperStageGenerator):
    def __init__(self, n_parallel, neutral_compout, wuseed, wvalue, wcompout, wstate, initial_state, compute_generator, update_generator, dsignal_generator):
        self.wcomput = wcompout
        self.cg = compute_generator
        self.n_parallel = n_parallel
        self.neutral_compout = neutral_compout
        self.initial_state = initial_state
        super().__init__(wuseed, wvalue, wstate, initial_state, update_generator, dsignal_generator)

    def generateDeclarationSignals(self):
        signals = []
        signals += [("clk", "in", "std_logic")]

        signals += [("useed_in", "in", "std_logic_vector({} downto 0)".format(self.wuseed-1))]

        signals += [("rd_data_out", "out", "std_logic_vector({} downto 0)".format(self.wstate-1))]
        for i in range(0,self.n_parallel):
            signals += [("val{}_en_in".format(i), "in", "std_logic")]
            signals += [("val{}_in".format(i), "in", "std_logic_vector({} downto 0)".format(self.wvalue-1))]

        return signals

    def generateArchitectureDefinition(self):
        if not self.cg.synchronous:
            return self.generateAsynchronousArchitectureDefinition()
        else:
            return self.generateSynchronousArchitectureDefinition()

    def generateAsynchronousArchitectureDefinition(self):
        frame = """
ARCHITECTURE a{} OF {} IS
{}
BEGIN

process(clk)
begin
if rising_edge(clk) then
        state <= u_outstate;
end if;
end process;

{}
END a{};
"""        

        decl = ""
        #Declarations
        ## Functions      
        decl += self.ug.generateComponentDeclaration()
        decl += self.cg.generateComponentDeclaration()

        ## Connecting signals
        for signal in self.ug.generateDeclarationSignals():
            decl += "\nsignal u_{} : {};".format(signal[0],signal[2]) 
        
        for signal in self.cg.generateDeclarationSignals():
            for i in range(0,self.n_parallel):
                decl += "\nsignal c{}_{} : {};".format(i, signal[0],signal[2]) 

        decl += "\nsignal state : std_logic_vector({} downto 0) := {};".format(self.wstate-1, self.initial_state) 
        #Architecture behavior
        ## Generate component instanciations
        bhv = ""
        signal_map = generateSignalMap(self.ug.generateDeclarationSignals(), "u_")
        bhv += generateComponentInstantiation("u", self.ug.entity_name, signal_map, None)

        for i in range(0, self.n_parallel):
            signal_map = generateSignalMap(self.cg.generateDeclarationSignals(), "c{}_".format(i))
            bhv += generateComponentInstantiation("c{}".format(i), self.cg.entity_name, signal_map, None)
   

        for i in range(0, self.n_parallel):
            cin = {
                "c{}_clk".format(i) : "clk",
                "c{}_v".format(i) : "val{}_in".format(i),
                "c{}_seed".format(i) : "useed_in",
            } 
            bhv += generateAssignments(cin)

        uin = {
            "u_clk" : "clk",
            "u_seed" : "useed_in",
            "u_state" : "state",
        } 
        bhv += generateAssignments(uin)      

        for i in range(0, self.n_parallel):
            uin = {
                "u_v{}".format(i) : "c{}_offset when val{}_en_in = '1' else {}".format(i, i, self.neutral_compout),
            } 
            bhv += generateAssignments(uin)      

        uout = {
            "rd_data_out" : "state",
        }
        bhv += generateAssignments(uout) 

        return frame.format(self.entity_name, self.entity_name, decl, bhv, self.entity_name)

    def generateSynchronousArchitectureDefinition(self):
        frame = """
ARCHITECTURE a{} OF {} IS
{}
BEGIN

process(clk)
begin
if rising_edge(clk) then
        state <= u_outstate;
end if;
end process;

{}
END a{};
"""        

        decl = ""
        #Declarations
        ## Functions      
        decl += self.ug.generateComponentDeclaration()
        decl += self.cg.generateComponentDeclaration()

        ## Connecting signals
        for signal in self.ug.generateDeclarationSignals():
            decl += "\nsignal u_{} : {};".format(signal[0],signal[2]) 
        
        for signal in self.cg.generateDeclarationSignals():
            for i in range(0,self.n_parallel):
                decl += "\nsignal c{}_{} : {};".format(i, signal[0],signal[2]) 

        decl += self.dsg.generateComponentDeclaration()

        for signal in self.dsg.getEntitySignals():
            for i in range(0,self.n_parallel):
                decl += "\nsignal eds{}_{} : {};".format(i, signal[0],signal[2])

        decl += "\nsignal state : std_logic_vector({} downto 0) := {};".format(self.wstate-1, self.initial_state) 
        #Architecture behavior
        ## Generate component instanciations
        bhv = ""
        signal_map = generateSignalMap(self.ug.generateDeclarationSignals(), "u_")
        bhv += generateComponentInstantiation("u", self.ug.entity_name, signal_map, None)

        for i in range(0, self.n_parallel):
            signal_map = generateSignalMap(self.cg.generateDeclarationSignals(), "c{}_".format(i))
            bhv += generateComponentInstantiation("c{}".format(i), self.cg.entity_name, signal_map, None)

            signal_map = generateSignalMap(self.dsg.getEntitySignals(), "eds{}_".format(i))
            generic_map = {"STAGES" : self.cg.computeLatency() }
            bhv += generateComponentInstantiation("eds{}".format(i), self.dsg.entity_name, signal_map, generic_map)
   

        for i in range(0, self.n_parallel):
            eds = {
                "eds{}_clk".format(i) : "clk",
                "eds{}_data_in".format(i) : "val{}_en_in".format(i)
            } 
            bhv += generateAssignments(eds) 

            cin = {
                "c{}_clk".format(i) : "clk",
                "c{}_v".format(i) : "val{}_in".format(i),
                "c{}_seed".format(i) : "useed_in",
            } 
            bhv += generateAssignments(cin)

        uin = {
            "u_clk" : "clk",
            "u_seed" : "useed_in",
            "u_state" : "state",
        } 
        bhv += generateAssignments(uin)      

        for i in range(0, self.n_parallel):
            uin = {
                "u_v{}".format(i) : "c{}_offset when eds{}_data_out = '1' else {}".format(i, i, self.neutral_compout),
            } 
            bhv += generateAssignments(uin)      

        uout = {
            "rd_data_out" : "state",
        }
        bhv += generateAssignments(uout) 

        return frame.format(self.entity_name, self.entity_name, decl, bhv, self.entity_name)
