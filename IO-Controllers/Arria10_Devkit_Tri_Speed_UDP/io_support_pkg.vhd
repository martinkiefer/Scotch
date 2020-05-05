library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package io_support_pkg is
        function xor_reduce(v: std_logic_vector) return std_logic;
        function ones_complement_add_general(v: std_logic_vector) return std_logic_vector;
        function ones_complement_add(a: std_logic_vector(15 downto 0); b: std_logic_vector(15 downto 0)) return std_logic_vector;
end package;
package body io_support_pkg is

        function xor_reduce(v: std_logic_vector) return std_logic is

                constant n: natural := v'length;
                constant t: std_logic_vector(n - 1 downto 0) := v;

                begin
                if n = 0 then
                        return '0';
                elsif n = 1 then
                        return t(0);
                else
                        return xor_reduce(t(n - 1 downto n / 2)) xor xor_reduce(t(n / 2 - 1 downto 0));
                end if;
        end function xor_reduce;

        function ones_complement_add(a: std_logic_vector(15 downto 0); b: std_logic_vector(15 downto 0)) return std_logic_vector is
                        variable reg : unsigned(16 downto 0);
        begin
                reg := unsigned('0' & a)+unsigned('0' & b);
                if(reg(16) = '1') then
                        reg := reg + 1;
                end if;

                return std_logic_vector(reg(15 downto 0));

        end function ones_complement_add;

        function ones_complement_add_general(v: std_logic_vector) return std_logic_vector is
                        variable reg : std_logic_vector(15 downto 0) := X"0000";
                        constant n: natural := v'length;
        begin
                for i in 0 to (n-1)/16
                loop
                        reg := ones_complement_add(v(i*16+15 downto i*16), reg);
                        --reg := one_somplement_add(reg,v((i*16+15) downto (i*16)));
                end loop;

                return reg;
        end function ones_complement_add_general;

end package body;