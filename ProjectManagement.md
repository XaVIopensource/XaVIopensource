




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

