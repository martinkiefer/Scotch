module my_eth_eth_tse_0 (
		input  wire        ff_tx_clk,      //     transmit_clock_connection.clk
		input  wire        ff_rx_clk,      //      receive_clock_connection.clk
		output wire [31:0] ff_rx_data,     //                       receive.data
		output wire        ff_rx_eop,      //                              .endofpacket
		output wire [5:0]  rx_err,         //                              .error
		output wire [1:0]  ff_rx_mod,      //                              .empty
		input  wire        ff_rx_rdy,      //                              .ready
		output wire        ff_rx_sop,      //                              .startofpacket
		output wire        ff_rx_dval,     //                              .valid
		input  wire [31:0] ff_tx_data,     //                      transmit.data
		input  wire        ff_tx_eop,      //                              .endofpacket
		input  wire        ff_tx_err,      //                              .error
		input  wire [1:0]  ff_tx_mod,      //                              .empty
		output wire        ff_tx_rdy,      //                              .ready
		input  wire        ff_tx_sop,      //                              .startofpacket
		input  wire        ff_tx_wren,     //                              .valid
		input  wire        xon_gen,        //           mac_misc_connection.xon_gen
		input  wire        xoff_gen,       //                              .xoff_gen
		input  wire        ff_tx_crc_fwd,  //                              .ff_tx_crc_fwd
		output wire        ff_tx_septy,    //                              .ff_tx_septy
		output wire        tx_ff_uflow,    //                              .tx_ff_uflow
		output wire        ff_tx_a_full,   //                              .ff_tx_a_full
		output wire        ff_tx_a_empty,  //                              .ff_tx_a_empty
		output wire [17:0] rx_err_stat,    //                              .rx_err_stat
		output wire [3:0]  rx_frm_type,    //                              .rx_frm_type
		output wire        ff_rx_dsav,     //                              .ff_rx_dsav
		output wire        ff_rx_a_full,   //                              .ff_rx_a_full
		output wire        ff_rx_a_empty,  //                              .ff_rx_a_empty
		input  wire        clk,            // control_port_clock_connection.clk
		input  wire        reset,          //              reset_connection.reset
		output wire [31:0] reg_data_out,   //                  control_port.readdata
		input  wire        reg_rd,         //                              .read
		input  wire [31:0] reg_data_in,    //                              .writedata
		input  wire        reg_wr,         //                              .write
		output wire        reg_busy,       //                              .waitrequest
		input  wire [7:0]  reg_addr,       //                              .address
		input  wire        ref_clk,        //  pcs_ref_clk_clock_connection.clk
		output wire        led_crs,        //         status_led_connection.crs
		output wire        led_link,       //                              .link
		output wire        led_panel_link, //                              .panel_link
		output wire        led_col,        //                              .col
		output wire        led_an,         //                              .an
		output wire        led_char_err,   //                              .char_err
		output wire        led_disp_err,   //                              .disp_err
		output wire        rx_recovclkout, //     serdes_control_connection.export
		input  wire        rxp,            //             serial_connection.rxp_0
		output wire        txp             //                              .txp_0
	);
endmodule

