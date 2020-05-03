class DemuxConfigPackageGenerator:
    def __init__(self, num, mux_factor, data_width):
        self.content = """
library IEEE;
USE IEEE.std_logic_1164.all;
USE WORK.functions_pkg.all;

package demux_config_pkg is
	constant DEMUX_NUM : natural := {};
    constant DEMUX_FACTOR : natural := {};
    constant DEMUX_DATA_WIDTH : natural := {};

    constant DEMUX_STAGES : natural := ceil_log_n(DEMUX_FACTOR, DEMUX_NUM);
    constant DEMUX_INDEX_WIDTH : natural := ceil_log_n(2, DEMUX_NUM);
    
    type demux_data_array_type is array (natural range <>) of std_logic_vector (DEMUX_DATA_WIDTH-1 downto 0);  
    type demux_index_array_type is array (natural range <>) of std_logic_vector(DEMUX_INDEX_WIDTH-1 downto 0);
end package;
""".format(num, mux_factor, data_width)

    def generateFile(self, folder):
        f = open("{}/{}".format(folder, "demux_config_pkg.vhd"), "w")
        f.write(self.content)
        f.close()