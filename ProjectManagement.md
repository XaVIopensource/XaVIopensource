




# Project Management #

Tasks:
* Concept documentation (datapath, ...)
* Compiler development proposal
* Define 32-bit instruction set.
* Create behavioural model of XaVI in C: Executing 32-bit instructions (or: 28-bit; every instruction is extended).
* Collate test suite #1 (analysis, not verification; no check / known good result): Look for low-level C source e.g. in drivers, APIs?
* Collate test suite #2 (verification): Hand-coded examples.
* Python script: Translate Xeno instructions to XaVI 32-bit instructions (interim: all one-to-many are hadronic so no re-linking?)
* Python script: Re-link.
* LLVM compiler development to 32-bit instructions.
* Determine method for custom ISA
* Verify behavioural model (using test suite #2).
* Power optimization (including layout), with scripting.


# Team Development Environment #

## EDA Tools ##

Open Source / free tools:
- FPGA implementation: [Intel Quartus Prime Lite](https://fpgasoftware.intel.com/?edition=lite)
- Verilog Simulation: (within Intel Quartus) Modelsim, within 'Intel FPGA standard edition' rather than v21.0 or later with Questa.
- ASIC Implementation: [Open-ROAD](https://theopenroadproject.org/), including Yosys for synthesis.


## FPGA development board ##

For verifying implementation (running regression suites).

'Hobby Components':
- [Altera Cyclone II EP2C5T144 FPGA Dev Board](https://hobbycomponents.com/altera/819-altera-cyclone-ii-es2c5t144-fpga-dev-board) £16.99
- [Altera FPGA/CPLD USB Programmer (USB Blaster Compatible)](https://hobbycomponents.com/featured/273-altera-fpga-cpld-usb-programmer-usb-blaster-compatible) £6.48
Or together:
- [programmer & devboard](https://www.ebay.co.uk/itm/141315924702?hash=item20e715e2de:g:B90AAOxyPFJTmEdS&var=440434835428)

Using Intel Quartus (see above).
