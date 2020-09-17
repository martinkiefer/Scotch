import sys
import pandas as pd
import re
import codecs

class PlacementReportParser:

    def __init__(self, report_file_path, hierarchy_report):
        self.freport = open(report_file_path, "r", newline="\n")
        self.fhreport = open(hierarchy_report, "r", newline="\n")

        self.clbs = self.getGlobalParameter("CLB")
        self.clbs_max = self.getGlobalParameter("CLB", True)
        self.luts = self.getGlobalParameter("CLB LUTs")
        self.luts_max = self.getGlobalParameter("CLB LUTs", True)
        self.regs = self.getGlobalParameter("CLB Registers")
        self.regs_max = self.getGlobalParameter("CLB Registers", True)
        self.uram = self.getGlobalParameter("URAM")
        self.uram_max = self.getGlobalParameter("URAM", True)
        self.bram = self.getGlobalParameter("RAMB36/FIFO\*")
        self.bram_max = self.getGlobalParameter("RAMB36/FIFO\*", True)

        self.sketch_luts, self.sketch_regs, self.sketch_bram, self.sketch_uram = self.getSketchOnlyParameters()

    def getGlobalParameter(self, key, maximum = False, cast=int ):
        self.freport.seek(0)
        v = None
        for l in self.freport:
            m = re.search("^\|\s*"+key+"\s*\|\s*(\d+)\s*\|\s*\d+\s*\|\s*(\d+)\s*\|\s*\d+\.?\d*\s*\|\n", l)
            if not m is None:
                if maximum:
                    v =  cast(m.group(2))
                else:
                    v = cast(m.group(1))
        self.freport.seek(0)
        return v

    def getSketchOnlyParameters(self):
        self.fhreport.seek(0)
        
        for l in self.fhreport:
            m = re.search("^\|[^()]*\|\s*sketch\s*\|\s*(\d+)\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*\d+\s*\|\s*(\d+)\s*\|",l)
            if not m is None:
                self.fhreport.seek(0)
                return int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4))
        self.fhreport.seek(0)
        return None, None, None, None

    

    def getOptimizerDataFrame(self, parameter):
        d ={"LUTs" : [self.luts], "MAX_LUTs" : [self.luts_max], "SKETCH_LUTs" : [self.sketch_luts],
            "REGs" : [self.regs], "MAX_REGs" : [self.regs_max], "SKETCH_REGs" : [self.sketch_regs],
            "BRAMs" : [self.bram], "MAX_BRAMs" : [self.bram_max], "SKETCH_BRAMs" : [self.sketch_bram],
            "URAMs" : [self.uram], "MAX_URAMs" : [self.uram_max], "SKETCH_URAMs" : [self.sketch_uram]
        }
        df = pd.DataFrame(data=d, index=[parameter])
        return df

    def getVivadoVersion(self):
        self.freport.seek(0)
        v = None
        for l in self.freport:
                m = re.match("^\| Tool Version : (.*) \(lin64\).*\n", l)
                if not m is None: 
                    v = m.group(1)    
        self.freport.seek(0)    
        return v
