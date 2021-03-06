

# Project Management #


## Key Concepts ##

### Of the hardware/system

Allow the user to modify the hardware _without changing the core compiler_, in order to get:
1. higher code density: more efficient instruction coding, hence lower power.
2. higher performance: hence able to power off sooner.
3. and critically: fewer instruction fetches from memory, hence lower power (by having aggregated common code sequences within the `Fetch` unit - i.e. splitting Huffman instructions into many hadrons)

Provides a hardware platform with particular features for exploring hardware power miniization techniques:
* Includes the use of layout-in-the-loop automated optimization of the hardware/software combination.


### Of the compiler

* Allow architectural tradeoffs to minimize power (e.g. a bottom-end system with only 4 general-purpose registers, no multiplier or barrel shifter).

### Of the project organization

Translation stepping-stone:
* Reference point to provide a robust (verified) model and test suite for the start of compiler development.
* Allow compiler development to start before the base (starting-point) Huffman instructions can be defined
* Allow the concept of optimizable instruction sets to be evaluated early







## Details of Identified Tasks ##


### MODEL: Generate C model 

Simple C, written wherever possible in a style that will allow easy translation across to Verilog (reason for 'ugly' use of global variables etc).

An output of this activity is the definition of the Uncompressed instruction code format.


### XLAT: Translate C code to binaries for XaVI 

...going via the Xeno C compiler:
* Compile C using Xeno's compiler toolchain.
* Used `objdump` to produce a disassembly of the binary.
* Create a Python script to convert the disassembly file to XaVI uncompressed assembly code. Every XaVI instruction will be given a label based on the Xeno address; disassembling jumps can refer to these labels. (Note: In some cases, one Xeno instruction will produce more than 1 XaVI instruction.)
* Create a Python script to compress XaVI uncompressed assembly code into Huffman instructions. Produces statistics on distributions of e.g. range of jumps, sizes of small constants, for later analysis.
* Create a Python script to generate a XaVI binary from the Huffman assembly code. Calssic two-pass: 1st to build up dictionary of labels' addresses, 2nd to output code. (No linking is needed as such - all code originates from the one Xeno disassembly file.)
* Numerous small scripts rather than more capable scripts, for flexibility.

Note:
* Initially, there is no Huffman code: _every_ instruction is stored uncompressed.
* It is the output of analysis of tentative Huffman coding schemes that determines what that code should be.


### VER: Verification of Translation and the Model 

This:
1. verifies the C model, and also
2. verifies the translation process (conversion from Xeno source to XaVI binaries).

Generate known-good references:
* Python script to randomly generate (constrained-random) binaries for Xeno-processor: (i) ALU, (ii) Load/store, (iii) Conditional jumps or (preferably) mixed together.
* Perhaps: a subroutine, frequently called, updates a CRC based on all registers (including Flags). The CRC values are logged (pushed) to Data Space. This allows easier identification of failure points.
* C code for Xeno-processor loads binaries into 'program-space' and 'data-space' parts of memory, executes the 'program-space' code that runs exclusively on the 'data-space' and then dumps the data space to a file.
* Constraints on the randomization ensure the above holds true (no scribbling, etc.).
* Start of binary: loads all registers with known values.
* End of binary: stores all registers into Data Space.
* Frequently observes Status Flags registers (copies to registers or memory).

Then:
* Run all binaries on the XaVI C model and dump Data Space at end.
* Compare against the known-good Xeno hardware results.


### ISA: Instruction Set Analysis 

* Collate a test suite to be used for analysis. Suggest initially look around for low-level C source e.g. in drivers, APIs - as representative of the target application.
* This test suite does not need to be verified. The tests will just be compiled/assembled/disassembled/reassembled but never actually executed.
* Uses scripts generated in XLAT task.
* Create Python scripts for analysis.
* Provides evidence for how successful the instruction compression is being.
* Want to be able to detect _sequences_ - to identify what ions could be fused (into multi-hadron ions).


### ICUSTOM: ISA Customization 

The Innovative part, putting it altogether

Design a methodology to 
* ... use the analysis results from task ISA (using a new set of representative code)
* ... to enable the definition a new Huffman coding
* ... that gets implemented in a custom translator (XLAT task)
* ... and (in reverse) in the `Fetch` unit within the Verilog.

... and demonstrate code density improvements.


### RTL: Verilog 

Up to now: no mention of processor hardware!
Only when the model and translater have been verified (and the general concept has been validated), is the RTL code produced - and it will follow easily.


### COMP: Compiler Generation 

* Assumed LLVM compiler development, just to 32-bit Uncompressed instructions.
* Inputs: (i) model, from MODEL task, and (ii) binaries from VER task.
* Compile switches: (i) no. registers, (ii) existence of hardware multiplier, (iii) existence of barrel shifter (iv) _preference_ to restrict usage to a subset of registers (to aid compression).

Initially, this task is just to achieve the above. But...

Critically: what other constraints will emerge from the knowledge gained in the above tasks (particularly from the ICUSTOM task)?
What other switches need to be added to the compiler, to allow it to be used with the methodology where the compiler doesn't need to change to 
produce a new Huffman ISA.


### POWER: Power Analysis

Develop a means of analyzing power consumption: See OpenPyPE in PowerEstimator.md.


### HCUSTOM: Hardware Customization 

* 'Search' lowest power architecture through varying parameters: (i) instruction compression schemes, at varying levels of hardware required to decompress, (ii) different 'fence' types at various parts of the `Datapath`, (iii) different number of registers.
* Automated processes from selection of parameters, through running the test suite and through hardware synthesis, layout and power analysis (using OpenROAD) to power consumption 'cost' results.
* Closing the loop: automated optimization  e.g. using Python scipy.optimize.minimize


