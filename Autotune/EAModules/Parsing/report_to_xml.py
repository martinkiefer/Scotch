import sys
import re
import gzip
import os
import random
import string
import codecs

def build_header_map(header):
    values = header.split(";")
    values = values[1:-1]
    values = map(lambda x : re.sub("\[.*\]","",x).lstrip().rstrip(), values )
    return list(values)

def string_to_value_map(header_map, rpt_str):   
    values = rpt_str.split(";")
    values = list(map(lambda x : x.lstrip().rstrip(), values ))
    values = values[1:-1] 

    regex = re.compile("(-?\d+\.?\d*)\s*\((-?\d+\.?\d*)\)") 
    i = 0
    d = {}
    for v in values:
        if "(" in v:
            m = regex.match(v)
            assert(not m is None)
            d[header_map[i]+" (total)"] = m.group(1)
            d[header_map[i]] = m.group(2)
        else:
            d[header_map[i]] = v
        i += 1    

    return d

class EntityNode:
    def __init__(self, header_map, report_string):
        self.children = []
        self.resource_dict = string_to_value_map(header_map, report_string)

    def addChild(self, node):
        self.children.append(node)

    def generateXML(self,level = 0):
        prefix = "    "
        s = ""
        s += "{}<fitter_node>\n".format(prefix*level)
        s += "{}<hierarchy_name>{}</hierarchy_name>\n".format(prefix*(level+1), self.resource_dict["Full Hierarchy Name"])
        s += "{}<entity_name>{}</entity_name>\n".format(prefix*(level+1), self.resource_dict["Entity Name"])
        s += "{}<library_name>{}</library_name>\n".format(prefix*(level+1), self.resource_dict["Library Name"])
        s += self.generate_dict_xml(level+1)
        for child in self.children:
            s += child.generateXML(level+1)
        s += "{}</fitter_node>\n".format(prefix*level)
        return s

    def generate_dict_xml(self, level = 0):
        d = dict(self.resource_dict)
        #First, remove the name entries from the dict
        del d["Compilation Hierarchy Node"]
        del d["Full Hierarchy Name"]
        del d["Entity Name"]
        del d["Library Name"]

        prefix = "    "
        s = ""     
        element_string = "{}<resource name=\"{}\" consumption=\"{}\" />\n"
        for key, value in d.items():
          s += element_string.format(prefix*level, key, value)
        return s

def generateEntityTree(infile):
    f = codecs.open(infile, "r", 'iso-8859-1')

    #Find the first line
    first=True
    for l in f:
        if "Fitter Resource Utilization by Entity" in l:
            if first:
                first=False
            else:
                break

    #Progress to the first line of content
    f.readline()
    header_map = build_header_map(f.readline())
    f.readline()

    node_dict = {}
    first = True
    head_name = None
    for l in f:
        if "+----" in l:
            break

        #Generate node
        en = EntityNode(header_map,l)
        en_dict = en.resource_dict
        full_name = en_dict["Full Hierarchy Name"]

        #Make old quartus hierarchy names starting with | compliant
        if full_name != "|" and full_name[0] == '|':
            full_name = full_name[1:]


        node_dict[full_name] = en
        if first:
            first = False
            head_name = full_name
            continue

        #Newr quartus versions just call the top-level entity |
        if full_name.count("|") == 0:
            node_dict["|"].addChild(en)
            continue
        else:
            levels = full_name.split("|")
            #Remove own name
            parent_id = "|".join(levels[:-1])
            node_dict[parent_id].addChild(en)
            continue

    return node_dict[head_name]    
    
    
    
def timingReportToXML(infile, outfile, gz = False):
    if gz:
        f = gzip.open(outfile, "wb")
    else:
        f = open(outfile, "wb")

    
    node = generateEntityTree(infile)
    f.write(node.generateXML().encode())

    f.close()

def timingReportToBinaryArrayXML(infile):
    letters = string.ascii_lowercase
    sq = ''.join(random.choice(letters) for i in range(10))
    
    tmpf = F"/tmp/{sq}-scotch-rpt-xml.tar.gz"
    timingReportToXML(infile, tmpf, True)
    
    f = open(tmpf, "rb")
    content = f.read()
    f.close()

    os.remove(tmpf)
    return content
  
if __name__ == "__main__":
    timingReportToXML(sys.argv[1], sys.argv[2])
