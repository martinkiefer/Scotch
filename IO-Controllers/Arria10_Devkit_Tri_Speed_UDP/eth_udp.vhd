library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.io_support_pkg.all;
use WORK.global_config_pkg.all;

entity eth_udp is

--Parameters. Need to be adapted depending on configuration of the Tri-Speed Ethernet IP
generic(
	 ETH_MODE                 	: integer := 1000 ; --Needs to be adapted for Gigabit (1000)
	 HD_ENA                   	: boolean := FALSE ; -- Half-Duplex. Nobody uses that anymore.
	 PROMIS_ENA               	: boolean := FALSE ; -- Promiscuous Mode. If enabled, we see packages for different Ethernet adresses as well.
	 MACPADEN              		: boolean := TRUE ;  -- Even more parameters. See Tri-Speed ethernet manual for explanations.
	 MACFWDCRC             		: boolean := FALSE ;
	 MACFWD_PAUSE          		: boolean := FALSE ; 
	 MACIGNORE_PAUSE       		: boolean := FALSE ; 
	 MACINSERT_ADDR        		: boolean := TRUE ;
	 
	 
    SGMII_ENA                : boolean := TRUE ; -- Enable SGMII Interface
    SGMII_AUTO_CONF          : boolean := TRUE ; -- Enable SGMII Auto-Configuration
    SGMII_1000               : boolean := TRUE ; -- Enable SGMII Gigabit
    SGMII_100                : boolean := FALSE ; -- Enable SGMII 100Mbps
    SGMII_10                 : boolean := FALSE ; -- Enable SGMII 10Mbps
    SGMII_HD                 : boolean := FALSE; --Enable SGMII Half-Duplex Operation
	 
	 IPG_LENGTH               : integer := 12 ;
	 MACLENMAX                : integer := 1518 ; -- max. frame length configuration of MAC
	 MACPAUSEQ                : integer := 15 ; -- pause quanta configuration of MAC
    
	 RX_FIFO_SECTION_EMPTY       : integer := 16 ; -- Section Empty Threshold
    RX_FIFO_SECTION_FULL        : integer := 16 ; -- Section Full Threshold
    TX_FIFO_SECTION_EMPTY       : integer := 512 ; -- Section Empty Threshold
    TX_FIFO_SECTION_FULL        : integer := 16 ; -- Section Full Threshold
    RX_FIFO_AE                  : integer := 8 ; -- Almost Empty Threshold
    RX_FIFO_AF                  : integer := 8 ; -- Almost Full Threshold
    TX_FIFO_AE                  : integer := 8 ; -- Almost Empty Threshold
    TX_FIFO_AF                  : integer := 3 ;  -- Almost Full Threshold
	 
	SKETCHES_PER_PACKAGE : natural := 128
	
	 
); -- end generic

port (
	xref_clk 												  : in std_logic;
	--prog_clk 												  : in std_logic;
	serial_connection_txp_0           : out std_logic;
	serial_connection_rxp_0           : in  std_logic;
	reset_out  										  : out std_logic
);
end entity eth_udp;

architecture eth_udp_architecture of eth_udp is

component my_eth is
	port (
		control_port_readdata    : out std_logic_vector(31 downto 0);                    --     control_port.readdata
		control_port_read        : in  std_logic                     := '0';             --                 .read
		control_port_writedata   : in  std_logic_vector(31 downto 0) := (others => '0'); --                 .writedata
		control_port_write       : in  std_logic                     := '0';             --                 .write
		control_port_waitrequest : out std_logic;                                        --                 .waitrequest
		control_port_address     : in  std_logic_vector(7 downto 0)  := (others => '0'); --                 .address
		control_port_clk_clk     : in  std_logic                     := '0';             -- control_port_clk.clk
		mac_misc_xon_gen         : in  std_logic                     := '0';             --         mac_misc.xon_gen
		mac_misc_xoff_gen        : in  std_logic                     := '0';             --                 .xoff_gen
		mac_misc_ff_tx_crc_fwd   : in  std_logic                     := '0';             --                 .ff_tx_crc_fwd
		mac_misc_ff_tx_septy     : out std_logic;                                        --                 .ff_tx_septy
		mac_misc_tx_ff_uflow     : out std_logic;                                        --                 .tx_ff_uflow
		mac_misc_ff_tx_a_full    : out std_logic;                                        --                 .ff_tx_a_full
		mac_misc_ff_tx_a_empty   : out std_logic;                                        --                 .ff_tx_a_empty
		mac_misc_rx_err_stat     : out std_logic_vector(17 downto 0);                    --                 .rx_err_stat
		mac_misc_rx_frm_type     : out std_logic_vector(3 downto 0);                     --                 .rx_frm_type
		mac_misc_ff_rx_dsav      : out std_logic;                                        --                 .ff_rx_dsav
		mac_misc_ff_rx_a_full    : out std_logic;                                        --                 .ff_rx_a_full
		mac_misc_ff_rx_a_empty   : out std_logic;                                        --                 .ff_rx_a_empty
		pcs_ref_clk_clk          : in  std_logic                     := '0';             --      pcs_ref_clk.clk
		receive_data             : out std_logic_vector(31 downto 0);                    --          receive.data
		receive_endofpacket      : out std_logic;                                        --                 .endofpacket
		receive_error            : out std_logic_vector(5 downto 0);                     --                 .error
		receive_empty            : out std_logic_vector(1 downto 0);                     --                 .empty
		receive_ready            : in  std_logic                     := '0';             --                 .ready
		receive_startofpacket    : out std_logic;                                        --                 .startofpacket
		receive_valid            : out std_logic;                                        --                 .valid
		receive_clk_clk          : in  std_logic                     := '0';             --      receive_clk.clk
		reset_reset              : in  std_logic                     := '0';             --            reset.reset
		serdes_export            : out std_logic;                                        --           serdes.export
		serial_rxp_0             : in  std_logic                     := '0';             --           serial.rxp_0
		serial_txp_0             : out std_logic;                                        --                 .txp_0
		status_led_crs           : out std_logic;                                        --       status_led.crs
		status_led_link          : out std_logic;                                        --                 .link
		status_led_panel_link    : out std_logic;                                        --                 .panel_link
		status_led_col           : out std_logic;                                        --                 .col
		status_led_an            : out std_logic;                                        --                 .an
		status_led_char_err      : out std_logic;                                        --                 .char_err
		status_led_disp_err      : out std_logic;                                        --                 .disp_err
		transmit_data            : in  std_logic_vector(31 downto 0) := (others => '0'); --         transmit.data
		transmit_endofpacket     : in  std_logic                     := '0';             --                 .endofpacket
		transmit_error           : in  std_logic                     := '0';             --                 .error
		transmit_empty           : in  std_logic_vector(1 downto 0)  := (others => '0'); --                 .empty
		transmit_ready           : out std_logic;                                        --                 .ready
		transmit_startofpacket   : in  std_logic                     := '0';             --                 .startofpacket
		transmit_valid           : in  std_logic                     := '0';             --                 .valid
		transmit_clk_clk         : in  std_logic                     := '0'              --     transmit_clk.clk
	);
end component my_eth;

component sketch IS
PORT (
clk : in std_logic;
rd_en_in : in std_logic;
rd_data_out : out std_logic_vector(31 downto 0);
rd_valid_out : out std_logic;
val0_en_in : in std_logic;
val0_in : in std_logic_vector(31 downto 0)
);
END component sketch;
	
	-- Global states 
	type global_state is (	
							WAIT_RESET, WAIT_INIT, ENABLE
	);
	

	-- Device initialization states
	type stm_typ is (	
							pcs_set_timer1, pcs_set_timer2, pcs_wait_for_reset, pcs_reset, pcs_if_control, pcs_autoneg_enable, RUN, IDLE,
							MAC_CONFIG, WR_MAC1, WR_MAC2, WR_IPG_LEN, WR_FRM_LENGTH, WR_PAUSE_QUANTA,
							WR_RX_SE, WR_RX_SF, WR_TX_SE, WR_TX_SF, WR_RX_AE, WR_RX_AF, WR_TX_AF, WR_TX_AE, MAC_RESET, mac_wait_for_reset, MAC_CONFIG2 
	);
	
	-- Package processing states
	type processing_state is (	
                            WAIT_EOP, DESTINATION_MAC1, DESTINATION_MAC2, SOURCE_MAC1, SOURCE_MAC2_TYPE,
                            TYPES, SIZE_OP, 
									 ARP_REQ_SMAC1, ARP_REQ_SMAC2_READ_SIP1, ARP_REQ_SIP2_DMAC1,
                            ARP_REQ_DMAC2, ARP_REQ_DIP, 
									 ARP_RESP_SMAC1, ARP_RESP_SMAC2_READ_SIP1, ARP_RESP_SIP2_DMAC1,
                            ARP_RESP_DMAC2, ARP_RESP_DIP,
									 IP4_HSIZE_LEN, ID_FLAGS_FRAGMENT, TTL_PROTO_CHECKSUM, SRC_IP, DST_IP,
									 UDP_PORTS, UDP_CONTROL_LENCHECK, UDP_CONTROL_COMMAND, UDP_DATA_LENCHECK, UDP_PAYLOAD
	);
	
	-- Data trasmit states
	type transmit_state is (	
                            IDLE, ARP_WAIT_REPLY,
									 ARP_DESTINATION_MAC1, ARP_DESTINATION_MAC2, ARP_SOURCE_MAC1, ARP_SOURCE_MAC2_TYPE,
                            ARP_TYPES, ARP_SIZE_OP, ARP_SMAC1, ARP_SMAC2_SIP1, ARP_SIP2_DMAC1,
                            ARP_DMAC2, ARP_DIP, 
									 ARP_REQ_DESTINATION_MAC1, ARP_REQ_DESTINATION_MAC2, ARP_REQ_SOURCE_MAC1, ARP_REQ_SOURCE_MAC2_TYPE,
                            ARP_REQ_TYPES, ARP_REQ_SIZE_OP, ARP_REQ_SMAC1, ARP_REQ_SMAC2_SIP1, ARP_REQ_SIP2_DMAC1,
                            ARP_REQ_DMAC2, ARP_REQ_DIP,
									 ARP_RESP_DESTINATION_MAC1, ARP_RESP_DESTINATION_MAC2, ARP_RESP_SOURCE_MAC1, ARP_RESP_SOURCE_MAC2_TYPE,
                            ARP_RESP_TYPES, ARP_RESP_SIZE_OP, ARP_RESP_SMAC1, ARP_RESP_SMAC2_SIP1, ARP_RESP_SIP2_DMAC1,
                            ARP_RESP_DMAC2, ARP_RESP_DIP,
									 IP_WAIT, IP_DESTINATION_MAC1, IP_DESTINATION_MAC2, IP_SOURCE_MAC1, IP_SOURCE_MAC2_TYPE,
									 IP_VERSION_IHL_TOS_LEN, IP_ID_FLAGS_FRAGMENT, IP_TTL_PROTO_CHECKSUM, IP_DST, IP_SRC,
									 UDP_PORTS, UDP_WAIT_PIPELINE, UDP_LEN_CHECKSUM, UDP_PAYLOAD
	);
	
	attribute noprune : boolean;
	
	-- State signals
	signal state            : stm_typ := IDLE;
   signal nextstate        : stm_typ := pcs_set_timer1;
	
	signal gstate : global_state := WAIT_RESET;
	signal tstate : transmit_state := IDLE;
	signal pstate : processing_state := DESTINATION_MAC1;
	
	--Device MAC
	constant mac_addr         : std_logic_vector(47 downto 0) := X"5044332211EE";
	--Device IP
	constant ip_addr         : std_logic_vector(31 downto 0) := X"C0A80102";
	
	--MAC & IP of 
	signal target_mac_addr : std_logic_vector(47 downto 0) := X"000000000000";
	constant target_ip_addr         : std_logic_vector(31 downto 0) := X"C0A80101";	
	
	--MAC and IP registers for ARP requests
	signal req_mac          : std_logic_vector(47 downto 0) := X"000000000000";
	signal req_ip           : std_logic_vector(31 downto 0) := X"00000000";
	
	--IP Header Values for UDP/IP
	constant ip_version : std_logic_vector(3 downto 0) := X"4";
	constant ip_ihl : std_logic_vector(3 downto 0) := X"5";
	constant ip_tos : std_logic_vector(7 downto 0) := X"00";
	constant ip_id : std_logic_vector(15 downto 0) := X"0000";	
	constant ip_flags : std_logic_vector(2 downto 0) := "010";	
	constant ip_fragment : std_logic_vector(12 downto 0) := (others => '0');
	constant ip_ttl : std_logic_vector(7 downto 0) := X"40";
	constant ip_proto : std_logic_vector(7 downto 0) := X"11";

	constant tmp : std_logic_vector(111 downto 0) := ip_version & ip_ihl & ip_tos  & ip_flags & ip_fragment & (ip_ttl & ip_proto) & target_ip_addr & ip_addr;
	signal pre_checksum : std_logic_vector(15 downto 0) := ones_complement_add_general(tmp);
	attribute noprune of pre_checksum : signal is true;
	
	-- Tri-Speed Ehternet Signals
	signal sop				   : std_logic := '0';
	signal eop				   : std_logic := '0';
	signal transmit_sop				   : std_logic := '0';
	signal transmit_eop				   : std_logic := '0';
	signal transmit_ready				   : std_logic := '0';
	signal transmit_valid				   : std_logic := '0';
	signal transmit_empty				   : std_logic_vector(1 downto 0) := "00";
	
	signal reg_addr         : std_logic_vector(7 downto 0) ; 
	signal reg_data_in      : std_logic_vector(31 downto 0) ;
	signal reg_data_out     : std_logic_vector(31 downto 0) ;
	signal receive_out			: std_logic_vector(31 downto 0)  ;
	signal transmit_out			: std_logic_vector(31 downto 0)  := X"00000000";
	signal receive_valid			: std_logic  ;
	
	signal led_link         : std_logic ;
	signal reg_clk          : std_logic ;
	signal rec_clk          : std_logic ;
	signal trs_clk          : std_logic ;
	
	signal reg_busy			: std_logic ;
	signal reg_wr				: std_logic ;
	signal reg_rd				: std_logic ;
	
	--Helper Signals
	signal one				: std_logic := '1';
	signal zero				: std_logic := '0';
	signal reset			: std_logic := '1';
	signal pcsr				: std_logic := '1';
	signal macr				: std_logic := '1';
	signal arp_reply				   : std_logic := '0';
	signal arp_response				   : std_logic := '0';
	signal processing_active		: std_logic := '0';
	
	--signal udp_cnt		: std_logic_vector(15 downto 0)  := X"0000";
	--attribute noprune of udp_cnt : signal is true;
	
	signal sketch_rd_en_in : std_logic;
	signal sketch_rd_data_out : std_logic_vector(31 downto 0);
	signal sketch_rd_valid_out : std_logic;
	signal sketch_val_en_in : std_logic;
	signal sketch_val_in : std_logic_vector(31 downto 0);
	
	signal transfer_sketches		: std_logic := '0';
	signal tx_septy : std_logic := '0';
	
begin	
	reg_clk <= xref_clk;
	rec_clk <= xref_clk;
	trs_clk <= xref_clk;
	
	reset_out <= not reset; --Yes, the device resets on logic low. Very intuitive -.-
	
	e: my_eth
	port map(
		control_port_readdata => reg_data_out,
		control_port_read => reg_rd,
		control_port_writedata => reg_data_in,
		control_port_write => reg_wr,
		control_port_waitrequest => reg_busy,
		control_port_clk_clk => reg_clk,
		control_port_address => reg_addr,
		mac_misc_ff_tx_crc_fwd => open,
		mac_misc_ff_tx_septy => tx_septy,
		mac_misc_tx_ff_uflow => open,
		mac_misc_ff_tx_a_full => open,
		mac_misc_ff_tx_a_empty => open,
		mac_misc_rx_err_stat => open,
		mac_misc_ff_rx_dsav  => open,
		mac_misc_ff_rx_a_full => open,
		mac_misc_ff_rx_a_empty => open,
		pcs_ref_clk_clk => xref_clk,
		receive_data  => receive_out ,
		receive_endofpacket => eop,
		receive_error => open,       
		receive_empty => open,  
		receive_ready => one,
		receive_startofpacket => sop,
		receive_valid => receive_valid,
		receive_clk_clk => rec_clk,
		reset_reset => reset,
		serdes_export => open,
		serial_rxp_0 => serial_connection_rxp_0,
		serial_txp_0 => serial_connection_txp_0,
		status_led_crs => open,
		status_led_link => open,
		status_led_panel_link  => open,				
		status_led_col => open,		
		status_led_an => open,
		status_led_char_err => open,		
		status_led_disp_err => open,
		transmit_data => transmit_out,
		transmit_endofpacket => transmit_eop,
	   transmit_error => open,	
		transmit_empty => transmit_empty,
		transmit_ready => transmit_ready,
		transmit_startofpacket => transmit_sop,
		transmit_valid => transmit_valid,
		transmit_clk_clk => trs_clk
	);
	
	s: sketch
	port map(
		clk => xref_clk,
		rd_en_in => sketch_rd_en_in,
		rd_data_out => sketch_rd_data_out,
		rd_valid_out => sketch_rd_valid_out,
		val0_en_in => sketch_val_en_in,
		val0_in => sketch_val_in
	);
	
	-- State switching logic for initialization machine.
  process(reset, reg_clk)
  begin
			 if (reset='1') then
					   state <= IDLE ;
						--nextstate <= IDLE;
			 elsif (reg_clk='1') and (reg_clk'event) then
						state <= nextstate ;		
			 end if ;		 
  end process ;
	
	
	process(reg_clk,gstate)
	    constant bpms : integer :=  125000; --Number of switches to logic high per milisecond. (Depends on the speed of reg_clk)
	    variable loop_cnt : integer := 0;
	begin
	if ((reg_clk='0' and reg_clk'event)) then	
		if gstate = WAIT_RESET then
		   --Hardware reset for 10 miliseconds
			loop_cnt := loop_cnt+1;
			if loop_cnt > bpms*10 then
				gstate <= WAIT_INIT;
				loop_cnt := 0;
			end if;
		elsif gstate = WAIT_INIT then
			loop_cnt := loop_cnt+1;
			--Waiting for the device to initialize for 5 milisonds
			if loop_cnt > bpms*5 then
				gstate <= ENABLE;
				loop_cnt := 0;
			end if;	
		else
			gstate <= ENABLE;
		end if;
	end if;
		if gstate = WAIT_RESET then
		reset <= '1';
	else
		reset <= '0';
	end if;
	end process;
	
	
  --State transition logic for Tri-Speed Ethernet MAC initilization. (Based on Reference Design)
	process(state, reg_busy)
	    variable xstate : stm_typ := IDLE;
	begin
	if ((reg_busy='0' and reg_busy'event)) then
		case state is
			when IDLE =>
				if gstate = ENABLE then
					xstate := pcs_set_timer1;
				else
					xstate := IDLE;
				end if;				 
			when pcs_set_timer1 =>  
								 xstate := pcs_set_timer2;   

			when pcs_set_timer2=> 
								 xstate := pcs_if_control ;   		
			
			when pcs_if_control =>         
								 xstate := pcs_autoneg_enable;

			when pcs_autoneg_enable =>
								 xstate := pcs_reset;   
					  
			when pcs_reset=>
								 xstate := pcs_wait_for_reset; 	
					  
			when pcs_wait_for_reset =>
							if pcsr = '0' then
								 xstate := MAC_CONFIG;   
							else
								 xstate := pcs_wait_for_reset;   							
							end if;
			when MAC_CONFIG => 
					xstate := WR_MAC1;		

			when WR_MAC1 => 
					xstate := WR_MAC2;

			when WR_MAC2 => 
					xstate := WR_IPG_LEN;
					
			when WR_IPG_LEN => 
					xstate := WR_FRM_LENGTH;

			when WR_FRM_LENGTH => 
					xstate := WR_PAUSE_QUANTA;

			when WR_PAUSE_QUANTA => 
					xstate := WR_RX_SE;
					
			when WR_RX_SE => 
					xstate := WR_RX_SF;	

			when WR_RX_SF => 
					xstate := WR_TX_SE;
					
			when WR_TX_SE => 
					xstate := WR_TX_SF;	
					
			when WR_TX_SF => 
					xstate := WR_RX_AE;

			when WR_RX_AE => 
					xstate := WR_RX_AF;

			when WR_RX_AF => 
					xstate := WR_TX_AE ;

			when WR_TX_AE => 
					xstate := WR_TX_AF  ;

			when WR_TX_AF => 
					xstate := MAC_RESET  ;

			when MAC_RESET => 
					xstate := mac_wait_for_reset  ;

			when mac_wait_for_reset => 
					if macr = '0' then
						xstate := MAC_CONFIG2 ;
					else
						xstate := mac_wait_for_reset;
					end if;

			when MAC_CONFIG2 => 
					xstate := RUN ;

			when RUN => 
					xstate := RUN ;
					
			when others =>
				xstate := IDLE;
		end case;
		nextstate <= xstate;
		end if;

	end process;
	
	--Helper processes maintaining signals showing us whether the PCS and MAC soft resets were executed sucessfully.
	process(reg_clk,reset)
	begin
		if reset = '1' then
			macr <= '1';
		elsif (reg_clk='1') and (reg_clk'event) then
			if state = MAC_WAIT_FOR_RESET and reg_busy = '0' and reg_data_out(13) = '0' then
				macr <= '0';
			end if;
		end if;
	end process;

	process(reg_clk,reset)
	begin
		if reset = '1' then
			pcsr <= '1';
		elsif (reg_clk='1') and (reg_clk'event) then
			if state = pcs_wait_for_reset and reg_busy = '0' and reg_data_out(15) = '0' then
				pcsr <= '0';
			end if;
		end if;
	end process;
	
	
	-- State handlers for Tri-Speed Ethernet MAC Initialization. (See Tri-Speed ethernet MAC manual for details)
	process(reg_clk,reset)
	begin	
		if (reset='1') then
				reg_wr      <= '0' ;
				reg_rd      <= '0' ;
				reg_addr    <= (others=>'0') ;
				reg_data_in <= (others=>'0') ;
		elsif (reg_clk='1') and (reg_clk'event) then

			if (nextstate=pcs_set_timer1) then
				reg_addr    <= std_logic_vector(to_unsigned(146, 8));   
				reg_rd      <= '0';   
				reg_wr      <= '1';   
				reg_data_in <= x"00000D40";
			elsif (nextstate=pcs_set_timer2) then
				reg_addr    <= std_logic_vector(to_unsigned(147, 8));   
				reg_rd      <= '0';   
				reg_wr      <= '1';   
				reg_data_in <= x"00000030";    			

			elsif (nextstate=pcs_if_control ) then
				reg_addr  <= std_logic_vector(to_unsigned(148, 8));   
				reg_rd    <= '0';   
				reg_wr    <= '1';  

				if (sgmii_ena=TRUE) then
					reg_data_in(0) <= '1';
				else
					reg_data_in(0) <= '0';
				end if ;

				if (sgmii_auto_conf=TRUE) then       
					reg_data_in(1) <= '1';        
				else
					reg_data_in(1) <= '0';
				end if ;

				if (sgmii_auto_conf=TRUE) then
					reg_data_in(3 downto 2) <= "00";
				elsif (sgmii_1000=TRUE) then  
					reg_data_in(3 downto 2) <= "10";
				elsif (sgmii_100=TRUE) then       
					reg_data_in(3 downto 2) <= "01";        
				else       
					reg_data_in(3 downto 2) <= "00";        
				end if ;

				if (sgmii_hd=TRUE) then       
					reg_data_in(4) <= '1';
				else
					reg_data_in(4) <= '0';
				end if ;

				reg_data_in(31 downto 5) <= (others=>'0');
			
										  
		
 			elsif (nextstate=pcs_autoneg_enable ) then
				reg_addr    <= std_logic_vector(to_unsigned(128, 8));   
				reg_rd      <= '0';   
				reg_wr      <= '1';
				reg_data_in <= (others=>'0');  
				
				if(sgmii_auto_conf=TRUE) then			
					reg_data_in(12) <= '1';
				else 
					reg_data_in(12) <= '0';
				end if ;
				
				reg_data_in(6) <= '1';
				reg_data_in(8) <= '1';		


 			elsif (nextstate=pcs_reset ) then
				reg_addr    <= std_logic_vector(to_unsigned(128, 8));   
				reg_rd      <= '0';   
				reg_wr      <= '1';
				reg_data_in <= (others=>'0');  
				
				if(sgmii_auto_conf=TRUE) then			
					reg_data_in(12) <= '1';
				else 
					reg_data_in(12) <= '0';
				end if ;
				
				reg_data_in(6) <= '1';
				reg_data_in(8) <= '1';	

				reg_data_in(15) <= '1';
				
 			elsif (nextstate=pcs_wait_for_reset ) then
				reg_addr    <= std_logic_vector(to_unsigned(128, 8));   
				reg_rd      <= '1';   
				reg_wr      <= '0';
				reg_data_in <= (others=>'0');  

			elsif (nextstate=MAC_CONFIG) then
				reg_wr      <= '1';
				reg_rd      <= '0';
				reg_addr    <= std_logic_vector(to_unsigned(2, 8));
				reg_data_in <= (others=>'0');
				
				reg_data_in(0) <= '0';
				reg_data_in(1) <= '0';
				
				reg_data_in(2) <= '0';
				
				
				-- Speed Selection
				if (ETH_MODE=1000) then
					reg_data_in(3) <= '1';   
				else
					reg_data_in(3) <= '0';     
				end if ;
				
				if (PROMIS_ENA=TRUE) then
					 reg_data_in(4) <= '1'; 
				else
					 reg_data_in(4) <= '0';
				end if ;
				
				if (MACPADEN=TRUE) then
					reg_data_in(5) <= '1';
				else
					reg_data_in(5) <= '0';
				end if ;
				
				if (MACFWDCRC=TRUE) then
					reg_data_in(6) <= '1';
				else
					reg_data_in(6) <= '0';
				end if ;
				
				if (MACFWD_PAUSE=TRUE) then
					reg_data_in(7) <= '1';
				else
					reg_data_in(7) <= '0';
				end if ;

				if (MACIGNORE_PAUSE=TRUE) then
					reg_data_in(8) <= '1';
				else
					reg_data_in(8) <= '0';
				end if ;
				
				if (MACINSERT_ADDR=TRUE) then
					reg_data_in(9) <= '1';
				else
					reg_data_in(9) <= '0';
				end if ;
				
				if (HD_ENA=TRUE) then
					reg_data_in(10) <= '1';
				else
					reg_data_in(10) <= '0';
				end if ;	
	
			elsif (nextstate=WR_MAC1) then
				reg_wr      <= '1';
				reg_rd      <= '0';
				reg_addr    <= std_logic_vector(to_unsigned(3, 8));
				reg_data_in(31 downto 24) <= mac_addr(23 downto 16);
				reg_data_in(23 downto 16) <= mac_addr(31 downto 24);
				reg_data_in(15 downto 8) <= mac_addr(39 downto 32);
			   reg_data_in(7 downto 0) <= mac_addr(47 downto 40);
			  
			  
			elsif (nextstate=WR_MAC2) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(4, 8));
				reg_data_in(15 downto 8)  <= mac_addr(7 downto 0); 
				reg_data_in(7 downto 0)  <= mac_addr(15 downto 8); 
				reg_data_in(31 downto 16) <= (others=>'0');	
				
			elsif (nextstate=WR_IPG_LEN) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(23, 8));
				reg_data_in(15 downto 0)  <= std_logic_vector(to_unsigned(IPG_LENGTH, 16)); 
				reg_data_in(31 downto 16) <= (others=>'0'); 
				
			elsif (nextstate=WR_FRM_LENGTH) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(5, 8));
				reg_data_in(15 downto 0)  <= std_logic_vector(to_unsigned(MACLENMAX, 16)); 
				reg_data_in(31 downto 16) <= (others=>'0');  

			elsif (nextstate=WR_PAUSE_QUANTA) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(6, 8));
				reg_data_in(15 downto 0)  <= std_logic_vector(to_unsigned(MACPAUSEQ, 16)); 
				reg_data_in(31 downto 16) <= (others=>'0'); 					
				
			elsif (nextstate=WR_RX_SE) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(7, 8));
				reg_data_in               <= std_logic_vector(to_unsigned(RX_FIFO_SECTION_EMPTY, 32)); 
									  
			elsif (nextstate=WR_RX_SF) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(8, 8));
				reg_data_in               <= std_logic_vector(to_unsigned(RX_FIFO_SECTION_FULL, 32));
								  
			elsif (nextstate=WR_TX_SE) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(9, 8));
				reg_data_in               <= std_logic_vector(to_unsigned(TX_FIFO_SECTION_EMPTY, 32)); 

			elsif (nextstate=WR_TX_SF) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(10, 8));
				reg_data_in               <= std_logic_vector(to_unsigned(TX_FIFO_SECTION_FULL, 32));

			elsif (nextstate=WR_RX_AE) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(11, 8));
				reg_data_in(15 downto 0)  <= std_logic_vector(to_unsigned(RX_FIFO_AE, 16)); 
				reg_data_in(31 downto 16) <= (others=>'0');

			elsif (nextstate=WR_RX_AF) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(12, 8));
				reg_data_in(15 downto 0)  <= std_logic_vector(to_unsigned(RX_FIFO_AF, 16)); 
				reg_data_in(31 downto 16) <= (others=>'0');

			elsif (nextstate=WR_TX_AE) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(13, 8));
				reg_data_in(15 downto 0)  <= std_logic_vector(to_unsigned(TX_FIFO_AE, 16)); 
				reg_data_in(31 downto 16) <= (others=>'0');

			elsif (nextstate=WR_TX_AF) then
				reg_wr                    <= '1';
				reg_rd                    <= '0';
				reg_addr                  <= std_logic_vector(to_unsigned(14, 8));
				reg_data_in(15 downto 0)  <= std_logic_vector(to_unsigned(TX_FIFO_AF, 16)); 
				reg_data_in(31 downto 16) <= (others=>'0');
			elsif (nextstate=MAC_RESET) then
				reg_wr      <= '1';
				reg_rd      <= '0';
				reg_addr    <= std_logic_vector(to_unsigned(2, 8));
				reg_data_in <= (others=>'0');
				
				reg_data_in(0) <= '0';
				reg_data_in(1) <= '0';
				
				reg_data_in(2) <= '0';
				
				
				-- Speed Selection
				if (ETH_MODE=1000) then
					reg_data_in(3) <= '1';   
				else
					reg_data_in(3) <= '0';     
				end if ;
				
				if (PROMIS_ENA=TRUE) then
					 reg_data_in(4) <= '1'; 
				else
					 reg_data_in(4) <= '0';
				end if ;
				
				if (MACPADEN=TRUE) then
					reg_data_in(5) <= '1';
				else
					reg_data_in(5) <= '0';
				end if ;
				
				if (MACFWDCRC=TRUE) then
					reg_data_in(6) <= '1';
				else
					reg_data_in(6) <= '0';
				end if ;
				
				if (MACFWD_PAUSE=TRUE) then
					reg_data_in(7) <= '1';
				else
					reg_data_in(7) <= '0';
				end if ;

				if (MACIGNORE_PAUSE=TRUE) then
					reg_data_in(8) <= '1';
				else
					reg_data_in(8) <= '0';
				end if ;
				
				if (MACINSERT_ADDR=TRUE) then
					reg_data_in(9) <= '1';
				else
					reg_data_in(9) <= '0';
				end if ;
				
				if (HD_ENA=TRUE) then
					reg_data_in(10) <= '1';
				else
					reg_data_in(10) <= '0';
				end if ;	
				reg_data_in(13) <= '1';
					
				
			elsif (nextstate=mac_wait_for_reset) then
				reg_wr      <= '0';
				reg_rd      <= '1';
				reg_addr    <= std_logic_vector(to_unsigned(2, 8));
				reg_data_in <= (others=>'0');

			elsif (nextstate=MAC_CONFIG2) then
				reg_wr      <= '1';
				reg_rd      <= '0';
				reg_addr    <= std_logic_vector(to_unsigned(2, 8));
				reg_data_in <= (others=>'0');
				
				reg_data_in(0) <= '1';
				reg_data_in(1) <= '1';
				
				reg_data_in(2) <= '0';
				
				
				-- Speed Selection
				if (ETH_MODE=1000) then
					reg_data_in(3) <= '1';   
				else
					reg_data_in(3) <= '0';     
				end if ;
				
				if (PROMIS_ENA=TRUE) then
					 reg_data_in(4) <= '1'; 
				else
					 reg_data_in(4) <= '0';
				end if ;
				
				if (MACPADEN=TRUE) then
					reg_data_in(5) <= '1';
				else
					reg_data_in(5) <= '0';
				end if ;
				
				if (MACFWDCRC=TRUE) then
					reg_data_in(6) <= '1';
				else
					reg_data_in(6) <= '0';
				end if ;
				
				if (MACFWD_PAUSE=TRUE) then
					reg_data_in(7) <= '1';
				else
					reg_data_in(7) <= '0';
				end if ;

				if (MACIGNORE_PAUSE=TRUE) then
					reg_data_in(8) <= '1';
				else
					reg_data_in(8) <= '0';
				end if ;
				
				if (MACINSERT_ADDR=TRUE) then
					reg_data_in(9) <= '1';
				else
					reg_data_in(9) <= '0';
				end if ;
				
				if (HD_ENA=TRUE) then
					reg_data_in(10) <= '1';
				else
					reg_data_in(10) <= '0';
				end if ;	
				
			elsif (nextstate=RUN) then
				reg_addr    <= std_logic_vector(to_unsigned(0, 8));   
				reg_rd      <= '0';   
				reg_wr      <= '0';   
				reg_data_in <= (others=>'0'); 
			else
				reg_wr                    <= '0';
				reg_rd                    <= '0';
				reg_data_in 				  <= (others=>'0');
				reg_addr    <= (others=>'0') ;				
			end if;
		end if;
	end process;

   --Data Processing FSM. 								
	process(rec_clk,gstate,reset)
		variable data_counter : unsigned(15 downto 0) := to_unsigned(0,16);
	begin
		if (reset='1') then
				arp_reply <= '0';
				arp_response <= '0';				
				pstate <= DESTINATION_MAC1;
				processing_active <= '0';
				transfer_sketches <= '0';
		elsif (rec_clk='1') and (rec_clk'event) and gstate = ENABLE then
			arp_reply <= '0';
			arp_response <= '0';	
			sketch_val_en_in <= '0';
			transfer_sketches <= '0';
			if pstate=DESTINATION_MAC1 and receive_valid='1' and sop = '1' then
                pstate <= DESTINATION_MAC2;
			elsif pstate=DESTINATION_MAC2 and receive_valid='1' then
                pstate <= SOURCE_MAC1;
			elsif pstate=SOURCE_MAC1 and receive_valid='1' then
                pstate <= SOURCE_MAC2_TYPE;
			elsif pstate=SOURCE_MAC2_TYPE and receive_valid='1' then
				-- Check the underlying protocol
				if receive_out(15 downto 0) = X"0806" then -- This is an ARP Package. We will answer if the request concerns us.
                pstate <= TYPES;
				elsif receive_out(15 downto 0) = X"0800" then -- This is an IP Package, we need to check the rest.
                pstate <= IP4_HSIZE_LEN;					
				else
					 pstate <= WAIT_EOP;
				end if;
			
			-- Deal with IP package 
			elsif pstate=IP4_HSIZE_LEN and receive_valid='1' then
				--Are we talking IPv4? Else stop.
				if receive_out(31 downto 24) = X"45" then -- We only accept IPv4 with standard header sizes. TODO: Do we need to store the size of the entire header?
					pstate <= ID_FLAGS_FRAGMENT;
				else
					pstate <= WAIT_EOP;					
				end if;
			elsif pstate=ID_FLAGS_FRAGMENT and receive_valid='1' then
				--The package should not be fragmented, since we are not expecting packages from the actual internet. 
				--TODO: Implement a counter for the number of received values. 
					pstate <= TTL_PROTO_CHECKSUM;					
			elsif pstate=TTL_PROTO_CHECKSUM and receive_valid='1' then
				--The package should not be fragmented, since we are not expecting packages from the actual internet. 
				--TODO: Implement a counter for the number of received values. 
				--Are we talking IPv4? Else stop.
				if receive_out(23 downto 16) = X"11" then -- We only accept IPv4 with standard header sizes. TODO: Do we need to store the size of the entire header?
					pstate <= SRC_IP;
				else
					pstate <= WAIT_EOP;					
				end if;							
			elsif pstate=SRC_IP and receive_valid='1' then
				--We don't care about the source IP
					pstate <= DST_IP;		
			elsif pstate=DST_IP and receive_valid='1' then
				--Check dst_ip
				if receive_out(31 downto 0) = ip_addr(31 downto 0) then
					pstate <= UDP_PORTS;
				else
					pstate <= WAIT_EOP;
				end if;
			elsif pstate=UDP_PORTS and receive_valid='1' then
				--UDP 5000 is the control port 
				if receive_out(15 downto 0) = X"1388" then
					pstate <= UDP_CONTROL_LENCHECK;
				--UDP 5001 is the data port
				elsif receive_out(15 downto 0) = X"1389" and processing_active = '1' then
					pstate <= UDP_DATA_LENCHECK;
				else
					pstate <= WAIT_EOP;
				end if;	
					
			--Deal with a UDP control package		
			elsif pstate=UDP_CONTROL_LENCHECK and receive_valid='1' then
				--Our control messages are always 4 bytes long.
				if unsigned(receive_out(31 downto 16)) >= 4 then
					pstate <= UDP_CONTROL_COMMAND;
				else
					pstate <= WAIT_EOP;
				end if;					
			
			--Deal with a UDP control package
			elsif pstate=UDP_CONTROL_COMMAND and receive_valid='1' then
				-- If we receive the ASCII chain "run!", we run in summary construction mode.
				if receive_out(31 downto 0) = X"72756E21" then
					processing_active <= '1';
				-- If we receive the ASCII chain "run!", we run in summary construction mode.
				elsif receive_out(31 downto 0) = X"656e6421" then
					processing_active <= '0';
					transfer_sketches <= '1';
				end if;				
				pstate <= WAIT_EOP;
			
			--Deal with data packages.
			--TODO: Could it happen that our data is not aligned?	
			elsif pstate=UDP_DATA_LENCHECK and receive_valid='1' then
				--Our control messages are always 4 bytes long.
				--For now, let's just maintain the counter.
				data_counter := unsigned(receive_out(31 downto 16)) - 8;
				pstate <= UDP_PAYLOAD;
			
			elsif pstate=UDP_PAYLOAD and receive_valid='1' then
				sketch_val_en_in <= '1';
				sketch_val_in <= receive_out;
				data_counter := data_counter - 4;
				if data_counter = 0 then
					pstate <= WAIT_EOP;
				end if;
				
			-- Deal with ARP Package
			elsif pstate=TYPES and receive_valid='1' then
                if receive_out = X"00010800" then
                    pstate <= SIZE_OP;
                else
                    pstate <= WAIT_EOP;
                end if;
			elsif pstate=SIZE_OP and receive_valid='1' then
                if receive_out = X"06040001" then
                    pstate <= ARP_REQ_SMAC1;
                elsif receive_out = X"06040002" then
                    pstate <= ARP_RESP_SMAC1;
                else
                    pstate <= WAIT_EOP;
                end if;

            -- Deal with ARP Requests
			elsif pstate=ARP_REQ_SMAC1 and receive_valid='1' then
					req_mac(47 downto 16) <= receive_out(31 downto 0);
					pstate <= ARP_REQ_SMAC2_READ_SIP1;
			elsif pstate=ARP_REQ_SMAC2_READ_SIP1 and receive_valid='1' then
					req_ip(31 downto 16) <= receive_out(15 downto 0);
					req_mac(15 downto 0) <= receive_out(31 downto 16);
					pstate <= ARP_REQ_SIP2_DMAC1;
			elsif pstate=ARP_REQ_SIP2_DMAC1 and receive_valid='1' then
					req_ip(15 downto 0) <= receive_out(31 downto 16);
					pstate <= ARP_REQ_DMAC2;
			elsif pstate=ARP_REQ_DMAC2 and receive_valid='1' then
					pstate <= ARP_REQ_DIP; -- We don't care about the Destination MAC. It's probably broadcast anyway.
			elsif pstate=ARP_REQ_DIP and receive_valid='1' then
					 --Iniate ARP REPLY
                if receive_out(31 downto 0) = ip_addr(31 downto 0) then
							--TODO: Could bad things happen, when we receive to many ARP packages at once or want to transfer sketches simultaneously? Probably.
							arp_reply <= '1';
					end if;
					pstate <= WAIT_EOP;
					 
         -- Deal with ARP Response
			elsif pstate=ARP_RESP_SMAC1 and receive_valid='1' then
					req_mac(47 downto 16) <= receive_out(31 downto 0);
					pstate <= ARP_RESP_SMAC2_READ_SIP1;
			elsif pstate=ARP_RESP_SMAC2_READ_SIP1 and receive_valid='1' then
					req_mac(15 downto 0) <= receive_out(31 downto 16);
					if target_ip_addr(31 downto 16) = receive_out(15 downto 0) then
							pstate <= ARP_RESP_SIP2_DMAC1;
					else
							pstate <= WAIT_EOP;					
					end if;
			elsif pstate=ARP_RESP_SIP2_DMAC1 and receive_valid='1' then
					if target_ip_addr(15 downto 0) = receive_out(31 downto 16) then
							pstate <= ARP_RESP_DMAC2;
							target_mac_addr <= req_mac;
					else
							pstate <= WAIT_EOP;					
					end if;
			elsif pstate=ARP_RESP_DMAC2 and receive_valid='1' then
					pstate <= ARP_RESP_DIP; -- We don't care about the Destination MAC.
			elsif pstate=ARP_RESP_DIP and receive_valid='1' then
					--Iniate ARP REPLY
					if receive_out(31 downto 0) = ip_addr(31 downto 0) then
							--TODO: Could bad things happen, when we receive to many ARP packages at once or want to transfer sketches simultaneously? Probably.
							arp_response <= '1';
                end if;
                pstate <= WAIT_EOP;
         end if;
			
			if eop = '1' then
				 pstate <= DESTINATION_MAC1;
			end if;
	  end if;
    end process;

   --ARP Reply FSM. 								
	process(rec_clk,gstate,reset)
		variable sketches_sent : natural := 0;
		variable sketches_to_request : natural := 0;
		variable remaining_sketches : natural := 0;
		variable package_size : natural := 0;
		variable package_counter: natural := 16#8000#;
		variable tmp : std_logic_vector(47 downto 0) := X"000000000000";
	begin
		if (reset='1') then
				tstate <= IDLE;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '0';
				transmit_empty <= "00";
				transmit_out <= X"00000000";
				remaining_sketches := N_SKETCHES;
				sketches_sent := 0;
		elsif (rec_clk='1') and (rec_clk'event) and gstate = ENABLE then
			sketch_rd_en_in <= '0';
			if tstate = IDLE then
				--In case there is data stuck on the interface, we can only reset once the interface is ready again
				if transmit_ready='1' then
				    transmit_sop <= '0';
				    transmit_eop <= '0';
				    transmit_valid <= '0';
				    transmit_empty <= "00";
				    transmit_out <= X"00000000";
				end if;
				remaining_sketches := N_SKETCHES;
				sketches_sent := 0;
				if transfer_sketches ='1' then
					tstate <= ARP_REQ_DESTINATION_MAC1;
				elsif arp_reply = '1' then
					tstate <= ARP_DESTINATION_MAC1;
				end if;
			elsif tstate=ARP_DESTINATION_MAC1 and transmit_ready='1' then
				tstate <= ARP_DESTINATION_MAC2;
				transmit_sop <= '1';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(15 downto 0) <= req_mac(47 downto 32);
			elsif tstate=ARP_DESTINATION_MAC2 and transmit_ready='1' then
            tstate <= ARP_SOURCE_MAC1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= req_mac(31 downto 0);
			elsif tstate=ARP_SOURCE_MAC1 and transmit_ready='1' then
            tstate <= ARP_SOURCE_MAC2_TYPE;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= mac_addr(47 downto 16);
			elsif tstate=ARP_SOURCE_MAC2_TYPE and transmit_ready='1' then
				-- Check the underlying protocol
				tstate <= ARP_TYPES;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 16) <= mac_addr(15 downto 0);
				transmit_out(15 downto 0) <= X"0806";
			elsif tstate=ARP_TYPES and transmit_ready='1' then
				tstate <= ARP_SIZE_OP;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
            transmit_out <= X"00010800";
			elsif tstate=ARP_SIZE_OP and transmit_ready='1' then
				tstate <= ARP_SMAC1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
            transmit_out <= X"06040002";
			elsif tstate=ARP_SMAC1 and transmit_ready='1' then
				tstate <= ARP_SMAC2_SIP1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= mac_addr(47 downto 16);
			elsif tstate=ARP_SMAC2_SIP1 and transmit_ready='1' then
				tstate <= ARP_SIP2_DMAC1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(15 downto 0) <= ip_addr(31 downto 16);
				transmit_out(31 downto 16) <= mac_addr(15 downto 0);       
			elsif tstate=ARP_SIP2_DMAC1 and transmit_ready='1' then
				tstate <= ARP_DMAC2;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 16) <= ip_addr(15 downto 0);
            transmit_out(15 downto 0) <= req_mac(47 downto 32);        
			elsif tstate=ARP_DMAC2 and transmit_ready='1' then
            tstate <= ARP_DIP;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= req_mac(31 downto 0);
			elsif tstate=ARP_DIP and transmit_ready='1' then
            tstate <= IDLE;
				transmit_sop <= '0';
				transmit_eop <= '1';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= req_ip(31 downto 0);

			--Send an ARP request
			elsif tstate=ARP_REQ_DESTINATION_MAC1 and transmit_ready='1' then
				tstate <= ARP_REQ_DESTINATION_MAC2;
				transmit_sop <= '1';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(15 downto 0) <= X"ffff";
			elsif tstate=ARP_REQ_DESTINATION_MAC2 and transmit_ready='1' then
            tstate <= ARP_REQ_SOURCE_MAC1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= X"ffffffff";
			elsif tstate=ARP_REQ_SOURCE_MAC1 and transmit_ready='1' then
            tstate <= ARP_REQ_SOURCE_MAC2_TYPE;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= mac_addr(47 downto 16);
			elsif tstate=ARP_REQ_SOURCE_MAC2_TYPE and transmit_ready='1' then
				-- Check the underlying protocol
				tstate <= ARP_REQ_TYPES;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 16) <= mac_addr(15 downto 0);
				transmit_out(15 downto 0) <= X"0806";
			elsif tstate=ARP_REQ_TYPES and transmit_ready='1' then
				tstate <= ARP_REQ_SIZE_OP;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
            transmit_out <= X"00010800";
			elsif tstate=ARP_REQ_SIZE_OP and transmit_ready='1' then
				tstate <= ARP_REQ_SMAC1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
            transmit_out <= X"06040001";
			elsif tstate=ARP_REQ_SMAC1 and transmit_ready='1' then
				tstate <= ARP_REQ_SMAC2_SIP1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= mac_addr(47 downto 16);
			elsif tstate=ARP_REQ_SMAC2_SIP1 and transmit_ready='1' then
				tstate <= ARP_REQ_SIP2_DMAC1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(15 downto 0) <= ip_addr(31 downto 16);
				transmit_out(31 downto 16) <= mac_addr(15 downto 0);       
			elsif tstate=ARP_REQ_SIP2_DMAC1 and transmit_ready='1' then
				tstate <= ARP_REQ_DMAC2;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 16) <= ip_addr(15 downto 0);
            transmit_out(15 downto 0) <= X"0000";        
			elsif tstate=ARP_REQ_DMAC2 and transmit_ready='1' then
            tstate <= ARP_REQ_DIP ;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= X"00000000";--mac_addr(31 downto 0);
			elsif tstate=ARP_REQ_DIP and transmit_ready='1' then
            tstate <= ARP_WAIT_REPLY;
				transmit_sop <= '0';
				transmit_eop <= '1';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= target_ip_addr(31 downto 0);	
			elsif tstate=ARP_WAIT_REPLY  then
				if arp_response='1' then
					tstate <= IP_WAIT;
				else
					tstate <= ARP_WAIT_REPLY;
				end if;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '0';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= X"00000000";
	
			-- We have to wait for the ethernet interface to make enough room for the next package
			elsif tstate=IP_WAIT and transmit_ready='1' and tx_septy = '1' then
				tstate <= IP_DESTINATION_MAC1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '0';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= X"00000000";	
			elsif tstate=IP_WAIT and transmit_ready='1' and tx_septy = '0' then
				tstate <= IP_WAIT;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '0';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= X"00000000";				
			elsif tstate=IP_DESTINATION_MAC1 and transmit_ready='1' then
				tstate <= IP_DESTINATION_MAC2;
				transmit_sop <= '1';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(15 downto 0) <= target_mac_addr(47 downto 32);
			elsif tstate=IP_DESTINATION_MAC2 and transmit_ready='1' then
            tstate <= IP_SOURCE_MAC1;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= target_mac_addr(31 downto 0);
			elsif tstate=IP_SOURCE_MAC1 and transmit_ready='1' then
            tstate <= IP_SOURCE_MAC2_TYPE;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 0) <= mac_addr(47 downto 16);
			elsif tstate=IP_SOURCE_MAC2_TYPE and transmit_ready='1' then
				-- Check the underlying protocol
				tstate <= IP_VERSION_IHL_TOS_LEN;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 16) <= mac_addr(15 downto 0);
				transmit_out(15 downto 0) <= X"0800";	
			elsif tstate=IP_VERSION_IHL_TOS_LEN and transmit_ready='1' then
				tstate <= IP_ID_FLAGS_FRAGMENT;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 28) <= ip_version;
				transmit_out(27 downto 24) <= ip_ihl;
				transmit_out(23 downto 16) <= ip_tos;
				if remaining_sketches >= SKETCHES_PER_PACKAGE then
					package_size := 20 + 8 + SKETCHES_PER_PACKAGE*4;
				else
					package_size := 20 + 8 + remaining_sketches*4;
				end if;
				transmit_out(15 downto 0) <= std_logic_vector(to_unsigned(package_size,transmit_out(15 downto 0)'length));
				
			elsif tstate=IP_ID_FLAGS_FRAGMENT and transmit_ready='1' then
				tstate <= IP_TTL_PROTO_CHECKSUM;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";	
				transmit_out(31 downto 16) <= std_logic_vector(to_unsigned(package_counter,transmit_out(31 downto 16)'length));
				transmit_out(15 downto 13) <= ip_flags;
				transmit_out(12 downto 0) <= ip_fragment;
			elsif tstate=IP_TTL_PROTO_CHECKSUM and transmit_ready='1' then
				tstate <= IP_SRC;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";	
				transmit_out(31 downto 24) <= ip_ttl;
				transmit_out(23 downto 16) <= ip_proto;
				tmp := pre_checksum & std_logic_vector(to_unsigned(package_size,transmit_out(15 downto 0)'length)) & std_logic_vector(to_unsigned(package_counter,transmit_out(15 downto 0)'length));
				transmit_out(15 downto 0) <= not(ones_complement_add_general(tmp));
				package_counter := package_counter  + 1;
			elsif tstate=IP_SRC and transmit_ready='1' then
				tstate <= IP_DST;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";	
				transmit_out <= ip_addr;
			elsif tstate=IP_DST and transmit_ready='1' then
				tstate <= UDP_PORTS;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";	
				transmit_out <= target_ip_addr;
			elsif tstate=UDP_PORTS and transmit_ready='1' then
				tstate <= UDP_LEN_CHECKSUM;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 16) <= X"1389";
				transmit_out(15 downto 0) <= X"1389";
			elsif tstate=UDP_LEN_CHECKSUM and transmit_ready='1' then
				tstate <= UDP_PAYLOAD;
				transmit_sop <= '0';
				transmit_eop <= '0';
				transmit_valid <= '1';
				transmit_empty <= "00";
				transmit_out(31 downto 16) <= std_logic_vector(to_unsigned(package_size - 20,transmit_out(31 downto 16)'length));
				transmit_out(15 downto 0) <= X"0000";
				sketch_rd_en_in <= '1';
				if remaining_sketches >= SKETCHES_PER_PACKAGE then
					sketches_to_request := SKETCHES_PER_PACKAGE;
				else
					sketches_to_request := remaining_sketches;
				end if;
				sketches_to_request := sketches_to_request - 1;
			elsif tstate=UDP_PAYLOAD and transmit_ready='1' then
				if sketch_rd_valid_out = '1' then
					remaining_sketches := remaining_sketches - 1;
					sketches_sent := sketches_sent + 1;
				end if;
				transmit_sop <= '0';
				transmit_valid <= sketch_rd_valid_out;
				transmit_empty <= "00";
				transmit_out <= sketch_rd_data_out;
				
				if sketches_to_request = 0 then
					sketch_rd_en_in <= '0';
				else
					sketch_rd_en_in <= '1';
					sketches_to_request := sketches_to_request - 1;
				end if;
				
				if remaining_sketches = 0 then
					tstate <= IDLE;
					sketch_rd_en_in <= '0';
					transmit_eop <= '1';
					sketches_sent := 0;
				elsif sketches_sent = SKETCHES_PER_PACKAGE then
					tstate <= IP_WAIT;
					sketch_rd_en_in <= '0';
					transmit_eop <= '1';
					sketches_sent := 0;
				else
					tstate <= UDP_PAYLOAD;
					transmit_eop <= '0';
				end if;	
			end if;	
	  end if;
    end process;	
	
end eth_udp_architecture;
