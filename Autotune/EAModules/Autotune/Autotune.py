import sys
import os
import subprocess
import pandas as pd
import shutil
import json
import re
import numpy as np
#TODO: This is not the solution Gotham deserves, but the one Gotham needs. 
#In the future, this should be solved differently
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/../../../ScotchDSL/Translation")
from ReplicatedColumnSketchGenerator import ReplicatedColumnSketchGenerator
from DataParallelColumnSketchGenerator import DataParallelColumnSketchGenerator
from run import *
from Functions import UpdateFunctionGenerator
from Functions import DataParallelUpdateFunctionGenerator
from GlobalConfigPackageGenerator import GlobalConfigPackageGenerator
from ..Parsing.PlacementReportParser import PlacementReportParser
from ..Parsing.TimingReportParser import TimingReportParser
from ForwardingUpdateFunctionGenerator import ForwardingUpdateFunctionGenerator
from Functions import SelectorFunctionGenerator
from ReplicatedMatrixSketchGenerator import ReplicatedMatrixSketchGenerator
from math import ceil, log2
import glob

class AutotuneColumnSketchWrapper:
    def __init__(self, descriptor_path, dfactor, cfactor, dp=1):
        f = open(descriptor_path)
        self.data = json.load(f)
        
        self.dfactor = dfactor
        self.cfactor = cfactor
        self.dp = dp

        if not "initial_state" in self.data:
            selfdata["initial_state"] = "(others => '0')"

        cwd = os.getcwd()
        os.chdir(os.path.dirname(descriptor_path))
        self.update_list = create_update_function_statement_list(self.data)
        os.chdir(cwd)

    def generate(self, param, gendir):
        ufg = UpdateFunctionGenerator(self.update_list, self.data["value_size"], self.data["update_seed_size"], self.data["state_size"], True)
        ssg = ReplicatedColumnSketchGenerator(self.dp, param, self.data["update_seed_size"], self.data["value_size"], self.data["state_size"], self.data["initial_state"], ufg, 1, self.dfactor, self.cfactor)
        ssg.generateFile(gendir)
        ufg.generateFile(gendir)

class AutotuneDataParallelColumnSketchWrapper:
    def __init__(self, descriptor_path, dfactor, cfactor):
        f = open(descriptor_path)
        self.data = json.load(f)
        
        self.dfactor = dfactor
        self.cfactor = cfactor

        if not "initial_state" in self.data:
            self.data["initial_state"] = "(others => '0')"

        cwd = os.getcwd()
        os.chdir(os.path.dirname(descriptor_path))
        self.update_list = create_cupdate_function_statement_list(self.data)
        self.selector_list = create_compute_function_statement_list(self.data)
        os.chdir(cwd)

    def generate(self, param, gendir):
        cfg = SelectorFunctionGenerator(self.selector_list, self.data["value_size"], self.data["update_seed_size"], self.data["compute_out_size"], True)
        ufg = DataParallelUpdateFunctionGenerator(self.update_list, self.data["compute_out_size"], self.data["update_seed_size"], self.data["state_size"], int(self.data["parallel_values"]), True)
        ssg = DataParallelColumnSketchGenerator(param, int(self.data["parallel_values"]), self.data["compute_neutral"], self.data["update_seed_size"], self.data["value_size"], self.data["compute_out_size"], self.data["state_size"], self.data["initial_state"], cfg, ufg, 1, self.dfactor, self.cfactor)
        ssg.generateFile(gendir)
        ufg.generateFile(gendir)
        cfg.generateFile(gendir)

class AutotuneMatrixSketchWrapper:
    def __init__(self, descriptor_path, block_size, dfactor, cfactor, dp=1, fixcol=None, fixrow=None):
        f = open(descriptor_path)
        self.data = json.load(f)
        
        cwd = os.getcwd()
        os.chdir(os.path.dirname(descriptor_path))
        self.selector_list = create_selector_function_statement_list(self.data)
        self.update_list = create_update_function_statement_list(self.data)
        os.chdir(cwd)

        self.fixcol = fixcol
        self.fixrow = fixrow
        self.dp = dp

        self.dfactor = dfactor
        self.cfactor = cfactor

        self.block_size = block_size

        if self.fixcol is None and self.fixrow is None:
            raise Exception("Only one parameter is allowed to remain free.")

        if not self.fixcol is None and not self.fixrow is None:
            raise Exception("Only one parameter is allowed to be fixed.")        

    def generate(self, param, gendir):
        sfg = SelectorFunctionGenerator(self.selector_list, self.data["value_size"], self.data["selector_seed_size"], self.data["offset_max_size"], True)
        sfg.generateFile(gendir)


        if not self.fixcol is None:
            matrix = [[self.block_size]*self.fixcol]*param
        else:
            matrix = [[self.block_size]*param]*self.fixrow

        waddr = int(ceil(log2(sum(matrix[0]))))
        ufg = ForwardingUpdateFunctionGenerator(self.update_list, self.data["value_size"], self.data["update_seed_size"], self.data["state_size"], waddr, True)
        ufg.generateFile(gendir)

        ssg = ReplicatedMatrixSketchGenerator(self.dp, matrix, self.data["selector_seed_size"], self.data["update_seed_size"], self.data["value_size"], self.data["state_size"], 
                                    sfg, ufg, 1, self.dfactor, self.cfactor)
        ssg.generateFile(gendir)

class Optimizer:
    def __init__(self, sketch, quartus_prefix, project_folder_path, initial_guess=16):
        self.quartus_prefix = quartus_prefix
        self.project_folder_path = project_folder_path
        self.initial_guess = initial_guess
        self.iteration = 1
        self.retries = 5
        self.interval_threshold = 0.01
        self.sketch = sketch
        
        self.gendir = "./sketch"
        self.workdir = "./work"

        if os.path.exists(self.workdir) and os.path.isdir(self.workdir):
            shutil.rmtree(self.workdir)

        os.makedirs(self.workdir)

    def optimize(self):
        print("- Staring parameter optimization -")
        df_history = pd.DataFrame()
        #First, we will start with the initial guess
        print("- Finding initial value -")
        state, df = self.run_repeat(self.initial_guess)
        df_history = df_history.append(df)
        u_param = None
        while state != "SUCCESS":
            u_param = self.initial_guess
            self.initial_guess = int(self.initial_guess/2)
            if self.initial_guess == 1:
                raise Exception("Unable to find an initial parameter that satisfies resources and / or timing.")
            state, df = self.run_repeat(self.initial_guess)
            df_history = df_history.append(df)
        
        print("- Found valid initial value {}".format(self.initial_guess))

        #Okay, now we have the initial parameter. Type to set up our intervals
        l_param = self.initial_guess
        #If the initial guess did not provide an upper bound, we have to find one for ourselves
        if u_param is None:
            u_param = Optimizer.computeMaxTarget(df, self.initial_guess)

        current_parameter = self.initial_guess
        while (u_param-l_param)/u_param > self.interval_threshold and u_param - l_param > 1: 
            current_parameter = int(l_param + (u_param - l_param) // 2.0)
            print("-- Current state [{},{})".format(l_param, u_param))
            state, df = self.run_repeat(current_parameter)
            df_history = df_history.append(df)
            if state == "SUCCESS":
                l_param = current_parameter
            else:
                u_param = current_parameter

        return current_parameter, df_history   

    @staticmethod        
    def computeMaxTarget(df, parameter):
        b =  df[["ALMs", "M20Ks", "M10Ks"]].to_numpy() - df[["SKETCH_ALMs", "SKETCH_M20Ks", "SKETCH_M10Ks"]].to_numpy()
        target = df[["MAX_ALMs", "MAX_M20Ks", "MAX_M10Ks",]].to_numpy()
        a = df[["SKETCH_ALMs", "SKETCH_M20Ks", "SKETCH_M10Ks"]].to_numpy() / parameter
        
        #Handle the case where no M{10,20}Ks are consumed by the sketch 
        if a[0,1] == 0:
            a[0,1] = a[0,0]
            b[0,1] = b[0,0]
            target[0,1] = target[0,0]
        if a[0,2] == 0:
            a[0,2] = a[0,0]
            b[0,2] = b[0,0]
            target[0,2] = target[0,0]
        return int(np.ceil(np.amin((target-b)/a)))

    def run_repeat(self, param):
        print("-- Trying parameter {} --".format(param))
        for seed in range(1,6):
            state, df = self.run(param, seed)
            if state == "SUCCESS" or state == "OUT_OF_RESOURCES":
                self.iteration += 1
                return state, df
        self.iteration += 1
        return state, df

    def run(self, param, seed, fmax = ""):
        #print("--- Trying param {} with seed {}".format(param, seed))
        #First, we have to generate the code
        if os.path.exists(self.gendir) and os.path.isdir(self.gendir):
            shutil.rmtree(self.gendir)
        
        if not os.path.exists(self.gendir):
            os.makedirs(self.gendir)

        #Second, we copy to the work directory
        shutil.copytree(self.project_folder_path, "./{}/{}-{}".format(self.workdir, self.iteration, seed))
        
        self.sketch.generate(param, self.gendir)

        shutil.move(self.gendir, "./{}/{}-{}".format(self.workdir, self.iteration, seed))

        #Third, we trigger the compile process
        os.chdir("./{}/{}-{}".format(self.workdir, self.iteration, seed))

        #Fourth, we run the compile.sh script
        process = subprocess.run("bash ./compile.sh {} {} {}".format(self.quartus_prefix, seed, fmax), shell=True)           
        rc = process.returncode

        STATE=None
        if rc == 0:
            #Compilation process succeeded. Time to check whether timing is met as well.
            
            srf = glob.glob(F"./output_files/*.sta.rpt")
            srf = srf[0]
            trp = TimingReportParser(srf)
            if trp.timing_met():
                STATE = "SUCCESS"
            else:
                STATE = "TIMING_FAILED"
        elif rc == 3: 
            STATE = "OUT_OF_RESOURCES"
        elif rc == 2:
            raise Exception("Compile script failed in synthesis. Errors in HDL files?".format(rc)) 
        else:
            raise Exception("Compile script returned with unexpected exit code {}.".format(rc)) 

        prf = glob.glob(F"./output_files/*.fit.rpt")
        prf = prf[0]
        p = PlacementReportParser(prf)
        df = p.getOptimizerDataFrame(param)

        #Fifth, we return a data frame with the parameters
        os.chdir("../..")
        print("--- Returned with state {}".format(STATE))
        print(df)
        return STATE, df
    
