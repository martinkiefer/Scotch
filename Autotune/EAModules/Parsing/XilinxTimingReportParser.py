import sys
import re

class TimingReportParser:

    def __init__(self, report_file_path):
        self.f = open(report_file_path)

    def getFmax(self, clock_name):
        self.f.seek(0)
        
        period = None
        wns = None
        #Find the period
        for l in self.f:
            if "Clock Summary" in l:
                break

        for l in self.f:
            first_part = F"^{clock_name}"
            m = re.search(first_part+"\s*\{.*\}\s*(\d+[.]?\d*?)\s",l)
            if not m is None:
                period = float(m.group(1))
                break

        for l in self.f:
            if "Intra Clock Table" in l:
                break
        
        for l in self.f:
            first_part = F"^{clock_name}"
            m = re.search(first_part+"\s*(-?\d+[.]?\d*?)\s",l)
            if not m is None:
                wns = float(m.group(1))
                break
        self.f.seek(0)
        #Return max operating frequency in MHz by accounting for negative slack.
        #May even be higher than the operating frequency demanded by the I/O controller.
        return 1000/(period-wns)

    def timing_met(self):
        self.f.seek(0)

        for l in self.f:
            m = re.search("\s*(\d+)\s*Failing Endpoints,", l)
            if not m is None:
                if int(m.group(1)) > 0:
                    return False 
        self.f.seek(0)
        return True

