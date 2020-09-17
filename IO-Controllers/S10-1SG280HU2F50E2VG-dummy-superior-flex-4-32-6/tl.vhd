
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use WORK.functions_pkg.all;

ENTITY tl IS
PORT (
clk : in std_logic;
sin1 : in std_logic;
sout1 : out std_logic
);
END tl;
ARCHITECTURE atl OF tl IS
    signal input_chain : std_logic_vector(133 downto 0);

COMPONENT sketch IS
PORT (
clk : in std_logic;
rd_en_in : in std_logic;
rd_data_out : out std_logic_vector(5 downto 0);
rd_valid_out : out std_logic;
val0_en_in : in std_logic;
val0_in : in std_logic_vector(31 downto 0);
val1_en_in : in std_logic;
val1_in : in std_logic_vector(31 downto 0);
val2_en_in : in std_logic;
val2_in : in std_logic_vector(31 downto 0);
val3_en_in : in std_logic;
val3_in : in std_logic_vector(31 downto 0)
);
END COMPONENT sketch;signal sketch_clk : std_logic;
signal sketch_rd_en_in : std_logic;
signal sketch_rd_data_out : std_logic_vector(5 downto 0);
signal sketch_rd_valid_out : std_logic;
signal sketch_val0_en_in : std_logic;
signal sketch_val0_in : std_logic_vector(31 downto 0);
signal sketch_val1_en_in : std_logic;
signal sketch_val1_in : std_logic_vector(31 downto 0);
signal sketch_val2_en_in : std_logic;
signal sketch_val2_in : std_logic_vector(31 downto 0);
signal sketch_val3_en_in : std_logic;
signal sketch_val3_in : std_logic_vector(31 downto 0);

BEGIN
sketch_rd_en_in <= input_chain(0);
sketch_val0_en_in <= input_chain(1);
sketch_val0_in <= input_chain(33 downto 2);
sketch_val1_en_in <= input_chain(34);
sketch_val1_in <= input_chain(66 downto 35);
sketch_val2_en_in <= input_chain(67);
sketch_val2_in <= input_chain(99 downto 68);
sketch_val3_en_in <= input_chain(100);
sketch_val3_in <= input_chain(132 downto 101);

ssketch: sketch
PORT MAP(

clk => sketch_clk,
rd_en_in => sketch_rd_en_in,
rd_data_out => sketch_rd_data_out,
rd_valid_out => sketch_rd_valid_out,
val0_en_in => sketch_val0_en_in,
val0_in => sketch_val0_in,
val1_en_in => sketch_val1_en_in,
val1_in => sketch_val1_in,
val2_en_in => sketch_val2_en_in,
val2_in => sketch_val2_in,
val3_en_in => sketch_val3_en_in,
val3_in => sketch_val3_in
);


sketch_clk <= clk;

process(clk)
begin
	if rising_edge(clk) then
		input_chain(0) <= sin1;
		for i in 0 to input_chain'LENGTH-2 loop
			input_chain(i+1) <= input_chain(i);
		end loop;
	end if;
end process; 

process(clk)
begin
	if rising_edge(clk) then
		sout1 <= parity(sketch_rd_data_out) xor sketch_rd_valid_out;
	end if;
end process;

END atl;
