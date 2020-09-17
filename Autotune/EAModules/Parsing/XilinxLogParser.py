import sys
import pandas as pd
import re
import codecs

class LogParser:

    def __init__(self, report_file_path):
        self.report = open(report_file_path, "r", newline="\n")


    def getVivadoVersion(self):
        self.report.seek(0)
        v = None
        for l in self.report:
                m = re.match("\#\s*(Vivado.*)\n", l)
                if not m is None: 
                    v = m.group(1)    
        self.report.seek(0)    
        return v

