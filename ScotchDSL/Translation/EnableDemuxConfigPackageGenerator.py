class EnableDemuxConfigPackageGenerator:
    def __init__(self, num, mux_factor):
        self.content = """
library IEEE;
USE IEEE.std_logic_1164.all;
USE WORK.functions_pkg.all;

package enable_demux_config_pkg is
	constant ENABLE_DEMUX_NUM : natural := {};
    constant ENABLE_DEMUX_FACTOR : natural := {};

    constant ENABLE_DEMUX_STAGES : natural := ceil_log_n(ENABLE_DEMUX_FACTOR, ENABLE_DEMUX_NUM);
    constant ENABLE_DEMUX_INDEX_WIDTH : natural := ceil_log_n(2, ENABLE_DEMUX_NUM);
    
    type enable_demux_index_array_type is array (natural range <>) of std_logic_vector(ENABLE_DEMUX_INDEX_WIDTH-1 downto 0);
end package;
""".format(num, mux_factor)

    def generateFile(self, folder):
        f = open("{}/{}".format(folder, "enable_demux_config_pkg.vhd"), "w")
        f.write(self.content)
        f.close()