	component my_eth_eth_tse_0 is
		port (
			ff_tx_clk      : in  std_logic                     := 'X';             -- clk
			ff_rx_clk      : in  std_logic                     := 'X';             -- clk
			ff_rx_data     : out std_logic_vector(31 downto 0);                    -- data
			ff_rx_eop      : out std_logic;                                        -- endofpacket
			rx_err         : out std_logic_vector(5 downto 0);                     -- error
			ff_rx_mod      : out std_logic_vector(1 downto 0);                     -- empty
			ff_rx_rdy      : in  std_logic                     := 'X';             -- ready
			ff_rx_sop      : out std_logic;                                        -- startofpacket
			ff_rx_dval     : out std_logic;                                        -- valid
			ff_tx_data     : in  std_logic_vector(31 downto 0) := (others => 'X'); -- data
			ff_tx_eop      : in  std_logic                     := 'X';             -- endofpacket
			ff_tx_err      : in  std_logic                     := 'X';             -- error
			ff_tx_mod      : in  std_logic_vector(1 downto 0)  := (others => 'X'); -- empty
			ff_tx_rdy      : out std_logic;                                        -- ready
			ff_tx_sop      : in  std_logic                     := 'X';             -- startofpacket
			ff_tx_wren     : in  std_logic                     := 'X';             -- valid
			xon_gen        : in  std_logic                     := 'X';             -- xon_gen
			xoff_gen       : in  std_logic                     := 'X';             -- xoff_gen
			ff_tx_crc_fwd  : in  std_logic                     := 'X';             -- ff_tx_crc_fwd
			ff_tx_septy    : out std_logic;                                        -- ff_tx_septy
			tx_ff_uflow    : out std_logic;                                        -- tx_ff_uflow
			ff_tx_a_full   : out std_logic;                                        -- ff_tx_a_full
			ff_tx_a_empty  : out std_logic;                                        -- ff_tx_a_empty
			rx_err_stat    : out std_logic_vector(17 downto 0);                    -- rx_err_stat
			rx_frm_type    : out std_logic_vector(3 downto 0);                     -- rx_frm_type
			ff_rx_dsav     : out std_logic;                                        -- ff_rx_dsav
			ff_rx_a_full   : out std_logic;                                        -- ff_rx_a_full
			ff_rx_a_empty  : out std_logic;                                        -- ff_rx_a_empty
			clk            : in  std_logic                     := 'X';             -- clk
			reset          : in  std_logic                     := 'X';             -- reset
			reg_data_out   : out std_logic_vector(31 downto 0);                    -- readdata
			reg_rd         : in  std_logic                     := 'X';             -- read
			reg_data_in    : in  std_logic_vector(31 downto 0) := (others => 'X'); -- writedata
			reg_wr         : in  std_logic                     := 'X';             -- write
			reg_busy       : out std_logic;                                        -- waitrequest
			reg_addr       : in  std_logic_vector(7 downto 0)  := (others => 'X'); -- address
			ref_clk        : in  std_logic                     := 'X';             -- clk
			led_crs        : out std_logic;                                        -- crs
			led_link       : out std_logic;                                        -- link
			led_panel_link : out std_logic;                                        -- panel_link
			led_col        : out std_logic;                                        -- col
			led_an         : out std_logic;                                        -- an
			led_char_err   : out std_logic;                                        -- char_err
			led_disp_err   : out std_logic;                                        -- disp_err
			rx_recovclkout : out std_logic;                                        -- export
			rxp            : in  std_logic                     := 'X';             -- rxp_0
			txp            : out std_logic                                         -- txp_0
		);
	end component my_eth_eth_tse_0;

	u0 : component my_eth_eth_tse_0
		port map (
			ff_tx_clk      => CONNECTED_TO_ff_tx_clk,      --     transmit_clock_connection.clk
			ff_rx_clk      => CONNECTED_TO_ff_rx_clk,      --      receive_clock_connection.clk
			ff_rx_data     => CONNECTED_TO_ff_rx_data,     --                       receive.data
			ff_rx_eop      => CONNECTED_TO_ff_rx_eop,      --                              .endofpacket
			rx_err         => CONNECTED_TO_rx_err,         --                              .error
			ff_rx_mod      => CONNECTED_TO_ff_rx_mod,      --                              .empty
			ff_rx_rdy      => CONNECTED_TO_ff_rx_rdy,      --                              .ready
			ff_rx_sop      => CONNECTED_TO_ff_rx_sop,      --                              .startofpacket
			ff_rx_dval     => CONNECTED_TO_ff_rx_dval,     --                              .valid
			ff_tx_data     => CONNECTED_TO_ff_tx_data,     --                      transmit.data
			ff_tx_eop      => CONNECTED_TO_ff_tx_eop,      --                              .endofpacket
			ff_tx_err      => CONNECTED_TO_ff_tx_err,      --                              .error
			ff_tx_mod      => CONNECTED_TO_ff_tx_mod,      --                              .empty
			ff_tx_rdy      => CONNECTED_TO_ff_tx_rdy,      --                              .ready
			ff_tx_sop      => CONNECTED_TO_ff_tx_sop,      --                              .startofpacket
			ff_tx_wren     => CONNECTED_TO_ff_tx_wren,     --                              .valid
			xon_gen        => CONNECTED_TO_xon_gen,        --           mac_misc_connection.xon_gen
			xoff_gen       => CONNECTED_TO_xoff_gen,       --                              .xoff_gen
			ff_tx_crc_fwd  => CONNECTED_TO_ff_tx_crc_fwd,  --                              .ff_tx_crc_fwd
			ff_tx_septy    => CONNECTED_TO_ff_tx_septy,    --                              .ff_tx_septy
			tx_ff_uflow    => CONNECTED_TO_tx_ff_uflow,    --                              .tx_ff_uflow
			ff_tx_a_full   => CONNECTED_TO_ff_tx_a_full,   --                              .ff_tx_a_full
			ff_tx_a_empty  => CONNECTED_TO_ff_tx_a_empty,  --                              .ff_tx_a_empty
			rx_err_stat    => CONNECTED_TO_rx_err_stat,    --                              .rx_err_stat
			rx_frm_type    => CONNECTED_TO_rx_frm_type,    --                              .rx_frm_type
			ff_rx_dsav     => CONNECTED_TO_ff_rx_dsav,     --                              .ff_rx_dsav
			ff_rx_a_full   => CONNECTED_TO_ff_rx_a_full,   --                              .ff_rx_a_full
			ff_rx_a_empty  => CONNECTED_TO_ff_rx_a_empty,  --                              .ff_rx_a_empty
			clk            => CONNECTED_TO_clk,            -- control_port_clock_connection.clk
			reset          => CONNECTED_TO_reset,          --              reset_connection.reset
			reg_data_out   => CONNECTED_TO_reg_data_out,   --                  control_port.readdata
			reg_rd         => CONNECTED_TO_reg_rd,         --                              .read
			reg_data_in    => CONNECTED_TO_reg_data_in,    --                              .writedata
			reg_wr         => CONNECTED_TO_reg_wr,         --                              .write
			reg_busy       => CONNECTED_TO_reg_busy,       --                              .waitrequest
			reg_addr       => CONNECTED_TO_reg_addr,       --                              .address
			ref_clk        => CONNECTED_TO_ref_clk,        --  pcs_ref_clk_clock_connection.clk
			led_crs        => CONNECTED_TO_led_crs,        --         status_led_connection.crs
			led_link       => CONNECTED_TO_led_link,       --                              .link
			led_panel_link => CONNECTED_TO_led_panel_link, --                              .panel_link
			led_col        => CONNECTED_TO_led_col,        --                              .col
			led_an         => CONNECTED_TO_led_an,         --                              .an
			led_char_err   => CONNECTED_TO_led_char_err,   --                              .char_err
			led_disp_err   => CONNECTED_TO_led_disp_err,   --                              .disp_err
			rx_recovclkout => CONNECTED_TO_rx_recovclkout, --     serdes_control_connection.export
			rxp            => CONNECTED_TO_rxp,            --             serial_connection.rxp_0
			txp            => CONNECTED_TO_txp             --                              .txp_0
		);

