import sys
import pandas as pd
import re
import codecs

class PlacementReportParser:

    def __init__(self, report_file_path):
        self.f = codecs.open(report_file_path, "r", 'iso-8859-1')

        self.alms = self.getGlobalParameter("Logic utilization")
        self.alms_max = self.getGlobalParameter("Logic utilization", True)
        self.labs = self.getGlobalParameter("Total LABs")
        self.labs_max = self.getGlobalParameter("Total LABs", True)
        self.m20k = self.getGlobalParameter("M20K blocks")
        self.m20k_max = self.getGlobalParameter("M20K blocks", True)
        self.m10k = self.getGlobalParameter("M10K blocks")
        self.m10k_max = self.getGlobalParameter("M10K blocks", True)

        self.alms_sketch, self.m20k_sketch, self.m10k_sketch = self.getSketchOnlyParameters()

    def getQuartusVersion(self):
        self.f.seek(0)
        m = None
        pro = None
        for l in self.f:
                m = re.match("^Quartus", l)
                if not m is None: 
                    break 
        self.f.seek(0)    
        return l.rstrip()

    def getGlobalParameter(self, key, maximum = False, cast=int ):
        self.f.seek(0)
        v = 0.0
        for l in self.f:
            if key in l:
                if not maximum:
                    m = re.search(r";\s*(\d+([,]\d+)*)", l)
                    if m:
                        v = cast(m.group(1).replace(",", ""))
                        break
                else:
                    m = re.search(r";\s*(\d+([,]\d+)*)\s[/]\s(\d+([,]\d+)*)", l)
                    if m:
                        v = cast(m.group(3).replace(",",""))
                        break
        self.f.seek(0)
        return v

    def getSketchOnlyParameters(self):
        self.f.seek(0)
        v = None
        out_l = None
        has_m10k = False
        
        for l in self.f:
            if "M10K" in l:
                has_m10k = True
            
            m = re.search(r";\s*sketch\s*;", l)
            if not m is None:
                if not out_l is None:
                    raise Exception("Couldn't retreive sketch only parameters due to multiple sketch lines.") 
                else:
                    out_l = l
        out_l = out_l.replace(" ", "")
        split_l = out_l.split(";")
        alms = float(split_l[2].split("(")[0]) 
        if split_l[11] != "N/A":
            if has_m10k:
                m20ks = 0.0
                m10ks = int(split_l[11])
            else:
                m20ks = int(split_l[11])
                m10ks = 0.0
        else:
                m20ks = None
                m10ks = None
        self.f.seek(0)
        return alms, m20ks, m10ks

    

    def getOptimizerDataFrame(self, parameter):
        d ={"ALMs" : [self.alms], "MAX_ALMs" : [self.alms_max], "SKETCH_ALMs" : [self.alms_sketch],
            "M20Ks" : [self.m20k], "MAX_M20Ks" : [self.m20k_max], "SKETCH_M20Ks" : [self.m20k_sketch],
            "M10Ks" : [self.m10k], "MAX_M10Ks" : [self.m10k_max], "SKETCH_M10Ks" : [self.m10k_sketch]}
        df = pd.DataFrame(data=d, index=[parameter])
        return df
                
    def getValueCSV(self):
        d = self.__dict__
        vnames = sorted(d.keys())
        values = list(map(lambda x : str(d[x]), vnames))
        return ",".join(values)
        
    def getKeyCSV(self):
        d = self.__dict__
        vnames = sorted(d.keys())
        return ",".join(vnames)

# pc = PlacementReportParser(sys.argv[1])
# df = pc.getDataFrame(16)
# b =  df[["ALMs", "M20Ks"]].to_numpy() - df[["SKETCH_ALMs", "SKETCH_M20Ks"]].to_numpy()
# target = df[["MAX_ALMs", "MAX_M20Ks"]].to_numpy()
# a = df[["SKETCH_ALMs", "SKETCH_M20Ks"]].to_numpy() / 16
# print(a)
# print(target)
# print(b)
# print((target-b)/a)
