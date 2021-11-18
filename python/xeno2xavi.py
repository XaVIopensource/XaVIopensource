
def xeno2xavi(in_filename="xeno_disassembly.txt", intermediate_filename="xavi_intermediate.asm", out_filename="xavi_translated.asm")
    ############################################
    # Pass no. 1: create label dictionary; do some basic conversions (handy midpoint for debugging)
    ############################################
    fin = open(in_filename, 'r')
    fout = open(intermediate_filename, 'w') 
    for line in fin:
        out = upper(line) # translation goes from upper to lower case
               
        # Re-assign register names
        out = re.sub("r31", "SR", out)
        out = re.sub("r31", "R2", out)
        out = re.sub("r30", "PC", out)
        out = re.sub("r30", "R0", out)
        out = re.sub("r1",  "SP", out) # Same
        #    (R4...R15 can stay the same; r2 and r3 are spare)
               
        # Re-name mnemonics
               
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
