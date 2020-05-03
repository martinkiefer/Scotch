class MuxConfigPackageGenerator:
    def __init__(self, num, mux_factor, data_width):
        self.content = """
library IEEE;
use IEEE.std_logic_1164.all;
use WORK.functions_pkg.all;

package mux_config_pkg is
	constant MUX_NUM : natural := {};
    constant MUX_FACTOR : natural := {};
    constant MUX_DATA_WIDTH : natural := {};

    constant MUX_STAGES : natural := ceil_log_n(MUX_FACTOR, MUX_NUM);
    constant MUX_INDEX_WIDTH : natural := ceil_log_n(2, MUX_NUM);

    type mux_data_array_type is array (natural range <>) of std_logic_vector (MUX_DATA_WIDTH-1 downto 0);
    type mux_index_array_type is array(natural range <>) of std_logic_vector (MUX_INDEX_WIDTH-1 downto 0);
end package;
""".format(num, mux_factor, data_width)

    def generateFile(self, folder):
        f = open("{}/{}".format(folder, "mux_config_pkg.vhd"), "w")
        f.write(self.content)
        f.close()