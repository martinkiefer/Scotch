import re

class QsfParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def getSeed(self):
        f = open(self.file_path, "r")
        seed = 0
        for l in f:
            m = re.match("set_global_assignment\s*-name\s*SEED\s*(\d+)", l)    
            if not m is None:
                seed = m.groups()[0]
        f.close()
        return seed