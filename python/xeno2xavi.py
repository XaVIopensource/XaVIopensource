
def xeno2xavi(in_filename="xeno_disassembly.txt", intermediate_filename="xavi_intermediate.asm", out_filename="xavi_translated.asm")
    ############################################
    # Pass no. 1: create label dictionary; do some basic conversions (handy midpoint for debugging)
    ############################################
    fin = open(in_filename, 'r')
    fout = open(intermediate_filename, 'w') 
    for line in fin:
        out = upper(line) # translation goes from upper to lower case
               
        # #######################
        # Re-assign register names
        # #######################
        out = re.sub("r31", "SR", out)
        out = re.sub("r31", "R2", out)
        out = re.sub("r30", "PC", out)
        out = re.sub("r30", "R0", out)
        out = re.sub("r1",  "SP", out) # Same
        #    (R4...R15 can stay the same; r2 and r3 are spare)
               
        # #######################
        # Re-name mnemonics
        # #######################
		# Exclamation marks!: some special needed here
        out = re.sub("rorc", "RRC",  out)
        out = re.sub("swpb", "SWPB", out)
        out = re.sub("rora", "RRA",  out)
        out = re.sub("sext", "SXT",  out)
        out = re.sub("PSH!", "PUSH", out) # To 2 instructions
        out = re.sub("JSR!", "CALL", out) # To 2 instructions
        out = re.sub("RTI!", "RETI", out) # To 2 instructions
        out = re.sub("brnz", "JNE",  out)
        out = re.sub("brnz", "JNZ",  out)
        out = re.sub("brz",  "JEQ",  out)
        out = re.sub("brz",  "JZ",   out)
        out = re.sub("brnc", "JNC",  out)
        out = re.sub("brnc", "JLO",  out)
        out = re.sub("brc",  "JC",   out)
        out = re.sub("brc",  "JHS",  out)
        out = re.sub("brn",  "JN",   out)
        out = re.sub("brge", "JGE",  out)
        out = re.sub("brl",  "JL",   out)
        out = re.sub("bra",  "JMP",  out)
        out = re.sub("move", "MOV",  out)
        out = re.sub("addc", "ADDC", out)
        out = re.sub("add",  "ADD",  out)
        out = re.sub("subc", "SUBC", out)
        out = re.sub("sub",  "SUB",  out)
        out = re.sub("cmp",  "CMP",  out)
        out = re.sub("bit",  "BIT",  out)
        out = re.sub("clr",  "BIC",  out)
        out = re.sub("set",  "BIS",  out)
        out = re.sub("xor",  "XOR",  out)
        out = re.sub("and",  "AND",  out)
		# ... including de-aliasing...
		op1 = 999; op2 = 999; SF=31; # if these get assigned, they supercede
        out = re.sub("addc", "ADC",  out); op1=0; 
        out = re.sub("clr",  "CLRC", out); op1=1; op2=SF
        out = re.sub("clr",  "CLRN", out); op1=4; op2=SF
        out = re.sub("clr",  "CLRZ", out); op1=2; op2=SF
        out = re.sub("sub",  "DEC",  out); op1=1; 
        out = re.sub("sub",  "DECD", out); op1=2; 
        out = re.sub("clr",  "DINT", out); op1=8; op2=SF
        out = re.sub("set",  "EINT", out); op1=8; op2=SF
        out = re.sub("add",  "INC",  out); op1=1; 
        out = re.sub("add",  "INCD", out); op1=2; 
        out = re.sub("xor",  "INV",  out); op1=-1;
        out = re.sub("NOP!", "NOP",  out); 
        out = re.sub("POP!", "POP",  out); 
        out = re.sub("RET!", "RET",  out); 
        out = re.sub("rola", "RLA",  out); 
        out = re.sub("rolc", "RLC",  out); 
        out = re.sub("subc", "SBC",  out); op1=0;
        out = re.sub("set",  "SETC", out); op1=1; op2=SF
        out = re.sub("set",  "SETN", out); op1=4; op2=SF
        out = re.sub("set",  "SETZ", out); op1=2; op2=SF
        out = re.sub("cmp",  "TST",  out); op1=0; 
               
        # Create dictionary: Log labels and their corresponding addresses
        pass
        # Translation of line completed
        fout.write(out)

    try:
        fout.writelines(fin.readlines())
    except Exception as E:
        raise E

    fin.close()
    fout.close()
               
    ############################################    
    # Pass no. 2: create translated output
    ############################################
    fin = open(intermediate_filename, 'r')
    fout = open(out_filename, 'w')
    for line in fin:
        # The more difficult translations this time.

        # Translation of line completed
        fout.write(out)

    try:
        fout.writelines(fin.readlines())
    except Exception as E:
        raise E

    fin.close()
    fout.close()
