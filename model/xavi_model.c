// datapath.c, to #include

// Status:
// * Initial coding pass of datapath

// Registers /////////////////////////////////////////

UINT regs[31:0];
UINT pc;
UINT flag_z, flag_n, flag_n, flag_c, flag_v;

UINT au_carry_out;

// Functions /////////////////////////////////////////

UINT get_reg(ULONG sel) {
	case(sel){
		case 0  : return 0;
		case 30 : return flag_z<<4 | flag_n<<3 | flag_n<<2 | flag_c<<1 | flag_v;
		case 31 : return pc;
		default : return regs[sel];
	}
}

// !!! None of these factor in byte_mode
UINT rotate_right_through_carry(UINT data, UINT size, UINT carry_in){ 
	switch (size){                   // returns 17 bits with carry at top
		case 0 : return( carry_in<<16 | data ); 
		case 1 : return( data<<1 | carry_in );
		default: return( bits(data, 16-size, 0)<<size | carry_in<<(size-1) | bits(data, 15, 17-size) );
	}
}

UINT rotate_right(UINT data, UINT size){ 
	switch (size){                   // returns 17 bits with carry at top
		case 0 : return( data ); 
		default: return( bits(data, 15-size, 0)<<size | bits(data, 15, 16-size) );
	}
}

UINT arithmetic_shift_left(UINT data, UINT size){ 
    return( bits(data, 15, 15) | data >> size ); // Sign-extended
}

UINT logical_shift_left(UINT data, UINT size){ 
    return( data >> size ); // Zero-extended
}

UINT add_or_subtract(op_a, op_b, func_sel, carry_in, byte_mode);
	UINT result, operand;
	operand = op_b; 
	if (func_sel==1){ operand = 65535-operand; } // ones-complement; 
	result = op_a + operand + carry_in
	au_carry_out = byte_mode ? bits(result,8,8) | bits(result,16,16)  ; // static
    return( bits(result,15,0) );
}

// execute_vliw: /////////////////////////////////////////

// drdata input depends of daddr output.
// Therefore the function will need calling twice.
// Note: it therefore does _not_ update any static variables.
void execute_vliw(ULONG vliw, constant) {
	// actual vliw is formed from vliw (upper bits) and constant (16 bits)

	// Assigning VLIW bits ////////////////

	a_mux_sel    = bits(vliw,  4,  0); // Register operand #1
	b_mux_sel    = bits(vliw,  9,  5); // Register operand #2
	c_mux_sel    = bits(vliw, 11, 10); // Register operand #1 or alternative source
	sl_mux_sel   = bits(vliw, 13, 12); // Select input to SLU (shift) unit function
	au_mux_sel   = bits(vliw, 13, 12); // Select input to AU (arithmetic) unit function
	shu_func_sel = bits(vliw, 14, 12); // SLU (shift) unit function
	// lu input is shu output
	au_func_sel  = bits(vliw, 15, 15); // AU (arithmetic) unit
	shu_size     = bits(vliw, 19, 16); // Shift no. bits
	byte_mode    = bits(vliw, 20, 20); // Data size: byte or word
	d_mux_sel    = bits(vliw, 21, 21); // Select for DWDATA
	e_mux_sel    = bits(vliw, 23, 22); // Select for DADDR | reg
	write_mem    = bits(vliw, 24, 24); // Enable write to memory (DWRITE)
	write_req    = bits(vliw, 25, 25); // Enable write to register
	reg_wr_sel   = bits(vliw, 26, 26); // Select register to write to

	// Operand muxing ////////////////

	a_mux <= get_reg(a_sel);
	b_mux <= get_reg(b_sel);
	case(c_sel){
		case 0  : c_mux = b_mux;
		case 1  : c_mux = constant;
		case 2  : c_mux = drdata; // resulting from a read
		default : c_mux = INVALID;
	}
	shu_mux  = sl_mux_sel ? c_mux | b_mux;
	au_mux   = au_mux_sel ? c_mux | b_mux;

	// SHU, LU, AU functions ////////////////

	shu_out_flag_c = flag_c; // default
	case(shu_sel){
		case 0  : shu_out = rotate_right_through_carry(shu_mux, flag_c, byte_mode);
		case 1  : shu_out =               rotate_right(shu_mux, flag_c, byte_mode);
		case 2  : shu_out =      arithmetic_shift_left(shu_mux, flag_c, byte_mode);
		case 3  : shu_out =         logical_shift_left(shu_mux, flag_c, byte_mode);
		default : shu_out = c_mux; // pass through
	}
	lu_out_flag_c = shu_out_flag_c; // default
	case(lu_mux_sel){
		case 0  : lu_out = a_mux & shu_out; // AND    (!!! not affected by byte_mode?)
		case 1  : lu_out = a_mux | bits(!shu_out,15,0); // CLR    (!!! not affected by byte_mode?)
		case 2  : lu_out = a_mux | shu_out; // OR|SET (!!! not affected by byte_mode?)
		case 3  : lu_out = a_mux ^ shu_out; // XOR    (!!! not affected by byte_mode?)
		default : lu_out = shu_out; // pass through
	}
	au_out = add_or_subtract(a_mux, au_mux, au_func_sel, flag_c, byte_mode);
	
	// Results ////////////////

	// !!!These must be static variables...
	d_mux_out = d_mux_sel ? au_out | shu_out; // Select for DWDATA
	case(e_mux_sel){  // Select for DADDR or Reg
		case 0  : e_mux_out = au_out; 
		case 1  : e_mux_out = shu_out ; 
		case 2  : e_mux_out = b_mux_out; 
		default : e_mux_out = INVALID;
	}
	
	// write_back needs to be used outside of this !!! Need to assign VLIW bits outside of this function
	
}

