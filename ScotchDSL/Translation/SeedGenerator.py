from random import getrandbits, seed

class SeedGenerator:
    def __init__(self, package_name, constant_name, nseeds, width):
        self.package_name = package_name
        self.constant_name = constant_name
        self.nseeds = nseeds
        self.width = width
        seed(self.width)

    def generateIncludes(self):
        return """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
"""

    def generatePackage(self):
        frame = """
package {} is
    type {} is array({} downto 0) of std_logic_vector({} downto 0) ;
    constant {} : {} := (
       {}
    );
end package;
"""
        vectors = []
        for ns in range(0, self.nseeds):
            v = F"{ns} => "
            v += "\""
            for w in range(0, self.width):
                v += str(getrandbits(1))
            v += "\""
            vectors.append(v)
        vectors_string = ",\n       ".join(vectors)
        return frame.format(self.package_name, self.constant_name+"_type",
         self.nseeds-1, self.width-1, self.constant_name, self.constant_name+"_type",
         vectors_string)

    def generateFile(self, folder):
        f = open("{}/{}.vhd".format(folder, self.package_name), "w")
        content = self.generateIncludes()
        content += self.generatePackage()
        f.write(content)
        f.close()

if __name__ == "__main__":
    sfg = SeedGenerator("seeds_pkg", "seeds", 5, 33)
    sfg.generateFile("./")
