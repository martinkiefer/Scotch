import os

class GlobalConfigPackageGenerator:
    def __init__(self, model, ssize, vsize, memdepth, ivals, sseedsizem, useedsize, 
    dfactor, cfactor, drepfactor, srepfactor, rows, cols):
        version_file = open(os.path.dirname(os.path.realpath(__file__))+"/../VERSION", "r")
        version = version_file.read().rstrip()
        version_file.close()

        self.content = '''
library ieee;
use ieee.std_logic_1164.all;

package global_config_pkg is
    -- Global parameters
    constant MODEL : string := "{}";
    constant STATE_WIDTH : natural := {};
    constant VALUE_WIDTH : natural := {};
    constant MEMORY_SEGMENT_DEPTH : natural := {};
    constant INPUT_VALUES : natural := {};

    constant SELECT_SEED_WIDTH : natural := {};
    constant UPDATE_SEED_WIDTH : natural := {};

    constant DISPATCH_FACTOR : natural := {};
    constant COLLECT_FACTOR : natural := {};

    constant DATA_REPLICATION_FACTOR : natural := {};
    constant STREAMING_REPLICATION_FACTOR : natural := {};

    -- Per-Replica Parameters
    constant ROWS : natural := {};
    constant COLS : natural := {};
    
    -- Total number of sketches (over all data-parallel replicas, does not include streaming replicas)
    constant N_SKETCHES : natural := {};
    constant GEN_VERSION : string := "{}";

end package;
'''.format(model, ssize, vsize, memdepth, ivals, sseedsizem, 
useedsize, dfactor, cfactor, drepfactor, srepfactor, rows, cols, rows*cols*drepfactor, version)

    def generateFile(self, folder):
        f = open("{}/{}".format(folder, "global_config_pkg.vhd"), "w")
        f.write(self.content)
        f.close()
