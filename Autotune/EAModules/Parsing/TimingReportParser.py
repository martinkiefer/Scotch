import sys
import re

class TimingReportParser:

    def __init__(self, report_file_path):
        self.f = open(report_file_path)

    def getFmax(self, clock_name):
        self.f.seek(0)
        
        l = "x"
        found = False
        l_fmax = []
        while l != "":
            l = self.f.readline()
            if not found:
                m = re.match(";.*Model Fmax Summary\s*;",l)
                if m:
                    found = True
            else:
                if clock_name in l:
                    m = re.search("^;\s(\d+[.]?\d*?)\sMHz",l)
                    l_fmax.append(float(m.group(1)))
                    found = False
        self.f.seek(0)
        return min(l_fmax)

    def timing_met(self):
        pairs = self.find_clock_slack_pairs()
        for _, slack in pairs:
            if slack < 0.0:
                return False
        return True

    def find_clock_slack_pairs(self):
        self.f.seek(0)
        STATE = "FIND_TABLE"
        clock_slack_pairs = []
        for l in self.f:
            if STATE == "FIND_TABLE":
                if l[0] == ";" and "Clock" in l and "Slack" in l and "End Point TNS" in l:
                    STATE = "SKIP_LINE"
                    continue
            elif STATE == "SKIP_LINE":
                STATE = "COLLECT"
                continue
            elif STATE == "COLLECT":
                if l[0] == "+":
                    STATE = "FIND_TABLE"
                else:
                    match = re.match(";\s*([.\w~|\[\]]*)\s*;\s*(-?\d+\.\d+)", l)
                    clock_slack_pairs.append((match.group(1), float(match.group(2))))
        self.f.seek(0)
        return clock_slack_pairs

    def getValueCSV(self):
        d = self.__dict__
        vnames = sorted(d.keys())
        values = list(map(lambda x : str(d[x]), vnames))
        return ",".join(values)

    def getKeyCSV(self):
        d = self.__dict__
        vnames = sorted(d.keys())
        return ",".join(vnames)
