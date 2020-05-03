import re

class GlobalConfigParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.regex = r'\s*constant\s*(\w+)\s*:\s*(natural|string)\s*:=\s*(\d+|".*")\s*'
    
    def getParameterDict(self):
        d = {}
        f = open(self.file_path, "r")
        for l in f:
            m = re.match(self.regex, l)
            if not m is None:
                d[m.groups()[0]] = m.groups()[2]
        return d
