class FunctionPackageGenerator:
    def __init__(self):
        self.content = """
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

package functions_pkg is
        function parity(v: std_logic_vector) return std_logic;
        function ceil_log_n(val : natural; n : natural) return natural;
end package;

package body functions_pkg is

        function parity(v: std_logic_vector) return std_logic is

                constant n: natural := v'length;
                constant t: std_logic_vector(n - 1 downto 0) := v;

                begin
                if n = 0 then
                        return '0';
                elsif n = 1 then
                        return t(0);
                else
                        return parity(t(n - 1 downto n / 2)) xor parity(t(n / 2 - 1 downto 0));
                end if;
        end function parity;

        function ceil_log_n(val : natural; n : natural) return natural is
    	        variable factor : natural := n - 1;
                variable r : natural := 0;
                        begin  
                        while factor > 0 loop
                                factor := factor / val;
                                r := r + 1;
                        end loop;
                        return r;
        end function ceil_log_n;

end package body;
"""

    def generateFile(self, folder):
        f = open("{}/{}".format(folder, "functions_pkg.vhd"), "w")
        f.write(self.content)
        f.close()