module my_eth (
		output wire [31:0] control_port_readdata,    //     control_port.readdata
		input  wire        control_port_read,        //                 .read
		input  wire [31:0] control_port_writedata,   //                 .writedata
		input  wire        control_port_write,       //                 .write
		output wire        control_port_waitrequest, //                 .waitrequest
		input  wire [7:0]  control_port_address,     //                 .address
		input  wire        control_port_clk_clk,     // control_port_clk.clk
		input  wire        mac_misc_xon_gen,         //         mac_misc.xon_gen
		input  wire        mac_misc_xoff_gen,        //                 .xoff_gen
		input  wire        mac_misc_ff_tx_crc_fwd,   //                 .ff_tx_crc_fwd
		output wire        mac_misc_ff_tx_septy,     //                 .ff_tx_septy
		output wire        mac_misc_tx_ff_uflow,     //                 .tx_ff_uflow
		output wire        mac_misc_ff_tx_a_full,    //                 .ff_tx_a_full
		output wire        mac_misc_ff_tx_a_empty,   //                 .ff_tx_a_empty
		output wire [17:0] mac_misc_rx_err_stat,     //                 .rx_err_stat
		output wire [3:0]  mac_misc_rx_frm_type,     //                 .rx_frm_type
		output wire        mac_misc_ff_rx_dsav,      //                 .ff_rx_dsav
		output wire        mac_misc_ff_rx_a_full,    //                 .ff_rx_a_full
		output wire        mac_misc_ff_rx_a_empty,   //                 .ff_rx_a_empty
		input  wire        pcs_ref_clk_clk,          //      pcs_ref_clk.clk
		output wire [31:0] receive_data,             //          receive.data
		output wire        receive_endofpacket,      //                 .endofpacket
		output wire [5:0]  receive_error,            //                 .error
		output wire [1:0]  receive_empty,            //                 .empty
		input  wire        receive_ready,            //                 .ready
		output wire        receive_startofpacket,    //                 .startofpacket
		output wire        receive_valid,            //                 .valid
		input  wire        receive_clk_clk,          //      receive_clk.clk
		input  wire        reset_reset,              //            reset.reset
		output wire        serdes_export,            //           serdes.export
		input  wire        serial_rxp_0,             //           serial.rxp_0
		output wire        serial_txp_0,             //                 .txp_0
		output wire        status_led_crs,           //       status_led.crs
		output wire        status_led_link,          //                 .link
		output wire        status_led_panel_link,    //                 .panel_link
		output wire        status_led_col,           //                 .col
		output wire        status_led_an,            //                 .an
		output wire        status_led_char_err,      //                 .char_err
		output wire        status_led_disp_err,      //                 .disp_err
		input  wire [31:0] transmit_data,            //         transmit.data
		input  wire        transmit_endofpacket,     //                 .endofpacket
		input  wire        transmit_error,           //                 .error
		input  wire [1:0]  transmit_empty,           //                 .empty
		output wire        transmit_ready,           //                 .ready
		input  wire        transmit_startofpacket,   //                 .startofpacket
		input  wire        transmit_valid,           //                 .valid
		input  wire        transmit_clk_clk          //     transmit_clk.clk
	);
endmodule

