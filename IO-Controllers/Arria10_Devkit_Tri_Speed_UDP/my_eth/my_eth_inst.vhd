	component my_eth is
		port (
			control_port_readdata    : out std_logic_vector(31 downto 0);                    -- readdata
			control_port_read        : in  std_logic                     := 'X';             -- read
			control_port_writedata   : in  std_logic_vector(31 downto 0) := (others => 'X'); -- writedata
			control_port_write       : in  std_logic                     := 'X';             -- write
			control_port_waitrequest : out std_logic;                                        -- waitrequest
			control_port_address     : in  std_logic_vector(7 downto 0)  := (others => 'X'); -- address
			control_port_clk_clk     : in  std_logic                     := 'X';             -- clk
			mac_misc_xon_gen         : in  std_logic                     := 'X';             -- xon_gen
			mac_misc_xoff_gen        : in  std_logic                     := 'X';             -- xoff_gen
			mac_misc_ff_tx_crc_fwd   : in  std_logic                     := 'X';             -- ff_tx_crc_fwd
			mac_misc_ff_tx_septy     : out std_logic;                                        -- ff_tx_septy
			mac_misc_tx_ff_uflow     : out std_logic;                                        -- tx_ff_uflow
			mac_misc_ff_tx_a_full    : out std_logic;                                        -- ff_tx_a_full
			mac_misc_ff_tx_a_empty   : out std_logic;                                        -- ff_tx_a_empty
			mac_misc_rx_err_stat     : out std_logic_vector(17 downto 0);                    -- rx_err_stat
			mac_misc_rx_frm_type     : out std_logic_vector(3 downto 0);                     -- rx_frm_type
			mac_misc_ff_rx_dsav      : out std_logic;                                        -- ff_rx_dsav
			mac_misc_ff_rx_a_full    : out std_logic;                                        -- ff_rx_a_full
			mac_misc_ff_rx_a_empty   : out std_logic;                                        -- ff_rx_a_empty
			pcs_ref_clk_clk          : in  std_logic                     := 'X';             -- clk
			receive_data             : out std_logic_vector(31 downto 0);                    -- data
			receive_endofpacket      : out std_logic;                                        -- endofpacket
			receive_error            : out std_logic_vector(5 downto 0);                     -- error
			receive_empty            : out std_logic_vector(1 downto 0);                     -- empty
			receive_ready            : in  std_logic                     := 'X';             -- ready
			receive_startofpacket    : out std_logic;                                        -- startofpacket
			receive_valid            : out std_logic;                                        -- valid
			receive_clk_clk          : in  std_logic                     := 'X';             -- clk
			reset_reset              : in  std_logic                     := 'X';             -- reset
			serdes_export            : out std_logic;                                        -- export
			serial_rxp_0             : in  std_logic                     := 'X';             -- rxp_0
			serial_txp_0             : out std_logic;                                        -- txp_0
			status_led_crs           : out std_logic;                                        -- crs
			status_led_link          : out std_logic;                                        -- link
			status_led_panel_link    : out std_logic;                                        -- panel_link
			status_led_col           : out std_logic;                                        -- col
			status_led_an            : out std_logic;                                        -- an
			status_led_char_err      : out std_logic;                                        -- char_err
			status_led_disp_err      : out std_logic;                                        -- disp_err
			transmit_data            : in  std_logic_vector(31 downto 0) := (others => 'X'); -- data
			transmit_endofpacket     : in  std_logic                     := 'X';             -- endofpacket
			transmit_error           : in  std_logic                     := 'X';             -- error
			transmit_empty           : in  std_logic_vector(1 downto 0)  := (others => 'X'); -- empty
			transmit_ready           : out std_logic;                                        -- ready
			transmit_startofpacket   : in  std_logic                     := 'X';             -- startofpacket
			transmit_valid           : in  std_logic                     := 'X';             -- valid
			transmit_clk_clk         : in  std_logic                     := 'X'              -- clk
		);
	end component my_eth;

	u0 : component my_eth
		port map (
			control_port_readdata    => CONNECTED_TO_control_port_readdata,    --     control_port.readdata
			control_port_read        => CONNECTED_TO_control_port_read,        --                 .read
			control_port_writedata   => CONNECTED_TO_control_port_writedata,   --                 .writedata
			control_port_write       => CONNECTED_TO_control_port_write,       --                 .write
			control_port_waitrequest => CONNECTED_TO_control_port_waitrequest, --                 .waitrequest
			control_port_address     => CONNECTED_TO_control_port_address,     --                 .address
			control_port_clk_clk     => CONNECTED_TO_control_port_clk_clk,     -- control_port_clk.clk
			mac_misc_xon_gen         => CONNECTED_TO_mac_misc_xon_gen,         --         mac_misc.xon_gen
			mac_misc_xoff_gen        => CONNECTED_TO_mac_misc_xoff_gen,        --                 .xoff_gen
			mac_misc_ff_tx_crc_fwd   => CONNECTED_TO_mac_misc_ff_tx_crc_fwd,   --                 .ff_tx_crc_fwd
			mac_misc_ff_tx_septy     => CONNECTED_TO_mac_misc_ff_tx_septy,     --                 .ff_tx_septy
			mac_misc_tx_ff_uflow     => CONNECTED_TO_mac_misc_tx_ff_uflow,     --                 .tx_ff_uflow
			mac_misc_ff_tx_a_full    => CONNECTED_TO_mac_misc_ff_tx_a_full,    --                 .ff_tx_a_full
			mac_misc_ff_tx_a_empty   => CONNECTED_TO_mac_misc_ff_tx_a_empty,   --                 .ff_tx_a_empty
			mac_misc_rx_err_stat     => CONNECTED_TO_mac_misc_rx_err_stat,     --                 .rx_err_stat
			mac_misc_rx_frm_type     => CONNECTED_TO_mac_misc_rx_frm_type,     --                 .rx_frm_type
			mac_misc_ff_rx_dsav      => CONNECTED_TO_mac_misc_ff_rx_dsav,      --                 .ff_rx_dsav
			mac_misc_ff_rx_a_full    => CONNECTED_TO_mac_misc_ff_rx_a_full,    --                 .ff_rx_a_full
			mac_misc_ff_rx_a_empty   => CONNECTED_TO_mac_misc_ff_rx_a_empty,   --                 .ff_rx_a_empty
			pcs_ref_clk_clk          => CONNECTED_TO_pcs_ref_clk_clk,          --      pcs_ref_clk.clk
			receive_data             => CONNECTED_TO_receive_data,             --          receive.data
			receive_endofpacket      => CONNECTED_TO_receive_endofpacket,      --                 .endofpacket
			receive_error            => CONNECTED_TO_receive_error,            --                 .error
			receive_empty            => CONNECTED_TO_receive_empty,            --                 .empty
			receive_ready            => CONNECTED_TO_receive_ready,            --                 .ready
			receive_startofpacket    => CONNECTED_TO_receive_startofpacket,    --                 .startofpacket
			receive_valid            => CONNECTED_TO_receive_valid,            --                 .valid
			receive_clk_clk          => CONNECTED_TO_receive_clk_clk,          --      receive_clk.clk
			reset_reset              => CONNECTED_TO_reset_reset,              --            reset.reset
			serdes_export            => CONNECTED_TO_serdes_export,            --           serdes.export
			serial_rxp_0             => CONNECTED_TO_serial_rxp_0,             --           serial.rxp_0
			serial_txp_0             => CONNECTED_TO_serial_txp_0,             --                 .txp_0
			status_led_crs           => CONNECTED_TO_status_led_crs,           --       status_led.crs
			status_led_link          => CONNECTED_TO_status_led_link,          --                 .link
			status_led_panel_link    => CONNECTED_TO_status_led_panel_link,    --                 .panel_link
			status_led_col           => CONNECTED_TO_status_led_col,           --                 .col
			status_led_an            => CONNECTED_TO_status_led_an,            --                 .an
			status_led_char_err      => CONNECTED_TO_status_led_char_err,      --                 .char_err
			status_led_disp_err      => CONNECTED_TO_status_led_disp_err,      --                 .disp_err
			transmit_data            => CONNECTED_TO_transmit_data,            --         transmit.data
			transmit_endofpacket     => CONNECTED_TO_transmit_endofpacket,     --                 .endofpacket
			transmit_error           => CONNECTED_TO_transmit_error,           --                 .error
			transmit_empty           => CONNECTED_TO_transmit_empty,           --                 .empty
			transmit_ready           => CONNECTED_TO_transmit_ready,           --                 .ready
			transmit_startofpacket   => CONNECTED_TO_transmit_startofpacket,   --                 .startofpacket
			transmit_valid           => CONNECTED_TO_transmit_valid,           --                 .valid
			transmit_clk_clk         => CONNECTED_TO_transmit_clk_clk          --     transmit_clk.clk
		);

