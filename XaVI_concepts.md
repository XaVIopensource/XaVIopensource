
# XaVI: A 16-bit Processor for Analog ICs


## Not Another One!

Why do we need _another_ processor?
* **For Analog/Mixed-Signal**: Many analog/mixed-signal chip providers have developed their own proprietary little processor for embedding into their chips. But there is no _standard_, _open_ 16-bit processor: the ARM or MIPS of the mixed-signal world. It needs to be little. Not so '8-bit' little that its code density adversely affects dynamic power consumption but not so '32-bit' big that its area adversely affects dynamic power consumption. 16 bits is _juuuust_ right - just a bit bigger than the ENOB of an ADC or DAC. Digi-people say an ARM Cortex-M is small, and that is true in 22nm [footnote]. But you don't want non-analog factors determining what process node you use for your analog chips.
* **Open**: _Truly_ open source: without any commercial restrictions.
* **Low Area**: seriously low. See above, and below. 
* **Low Power**: seriously low. Low area = low leakage but the objective is to have minimal signal transitions to perform the computation in order to minimize power. There will be some particular characteristics that will make XaVI particularly good for some ultra-low power techniques.
* **High code density** is part and parcel of low power above. Tweaked for the target application helps further.
* **Compiler**: It needs to have a _proven_ C compiler. More precisely, there needs to be a way to write C and get machine code out of it - a subtle difference. 

Enter XaVI: XVI for 16 and 'a' for analog.


[footnote]: Silly Marketing... On a 22nm CMOS process, the processor should fit within an area less than 30μm x 30μm. That's over 1000 processors per square millimeter. At 2021 bleeding edge node 5nm, that's over a _billion_ processors per 12" wafer! (Raw CPUs, without memory though.) Standard size reference points:
* a hair's breadth is nominally 75μm.
* Wales is about 2 x 10^22μm^2.


## Concepts


### Instructions

The CPU comprises:
* `Fetch` unit
* `Decode` unit 
* `Datapath` unit
* `Control` unit

Processor instructions may be considered at 3 levels:
* 'VLIW': between the `Decode` and `Datapath`.
* 'Uncompressed': between `Fetch` and the `Decode`.
* 'Huffman': between program memory and `Fetch`.

'VLIW' instructions provide:
* control inputs to the ALUs,
* selects for multiplexers, and
* enables for registers
within the `Datapath` unit.

In principle, it could be 'Uncompressed' or `VLIW` instructions stored in memory, but that would be grossly inefficient. The 'Huffman' instructions compress the 'Uncompressed' instructions for efficient storage. XaVI will have 32-bit 'Uncompressed' and 16-bit 'Huffman' instructions. The Huffman encoding scheme aims to compress the large majority of 32-bit instructions into 16-bit ones.

* The `Fetch` unit gets Huffman instructions from memory and uncompresses them to one _or more_ Uncompressed instructions. 
* The Huffman instruction stream may get interrupted by the (single) hardware interrupt.
* The `Decode` unit produces a VLIW instruction from an Uncompresssed instruction.
* The `Datapath` unit contains everything needed to execute a single instruction. Its contents define what is possible at any one time.
* The `Control` unit provides clock, reset and low-power controls to the rest of the CPU.


### Atoms, Ions and Hadrons

The term 'atomic' refers to the idea that consecutive instructions must not be interrupted. 
With that analogy, we may think of (Huffman) instructions as 'ions'; the binding of ions into atoms shall not be broken.
Within the `Fetch` unit, ionic instructions may be broken down into more than one Uncompressed instruction. 
Taking that analogy further, these Uncompressed instruction are 'hadrons' (protons and neutrons). 

Instruction execution is like a temporal stream of unbound ions. 
Most of the ions are Hydrogen (a single proton): one Huffman fetch leads to one Uncompressed instruction. Example: `ADD (R1), R2`
Occasionally, there may be some Deuterium (1 proton + 1 neutron: one Huffman fetch leads to two Uncompressed instructions) or heavier ions within the stream of Hydrogen. 
Example: `ADD (R1+), R2` gets broken down into `ADD (R1), R2` and `INC R1`==`ADD #1, R1`. 
The `Datapath` does not have the hardware resources to do this in a single hadron.
Occasionally, there may be some molecule in the atomic operation: H2 (2 protons); the chemical bonds make the two ions inseparate; a hardware interrupt will have to wait. 
Example: a read-modify-write `ADD (R1), R2; MOVE R2, (R1)`. This chemical bonding is unrelated to the nuclear binding of hadrons. 
There could be both chemical and nuclear: a molecule of Hydrogen plus Deuterium: `ADD (R1), R2; MOVE R2, (R1); INC R1`. 
You get the idea: the fundamental execution 'primitive' is the hadron.
one Huffman fetch leads to two Uncompressed instructions.

The `Fetch` unit gets Huffman ions from memory and decodes them to Uncompressed hadrons, handling atomicity to determine when interrupts can occur.


### Instruction Sets

XaVI has a defined Uncompressed instruction set, defining the hadrons.

In order to minimize power consumption, code density (the compression ratio) must be maximized. 
The more the Huffman instructions are tailored to the target application, the better.

There are 3 components between high-level C and Uncompressed instructions:
* the compiler,
* the linker, and
* the `Fetch` unit.

The compiler software is the most fixed. The `Fetch` unit is less fixed (the hardware is softer than the software) as it can be changed from one silicon design to the next. 
The linker must adjust to marry the two together to make the correct chain.

The compiler produces streams of hadrons. The linker bundles them up into ions, _aware of what ions the `Fetch` unit can support_. 
(Note: there is _no_ re-ordering!)

For example, perhaps some application has the need to do lots of sums of products, for example, executing code such as

`for(; i>0; i--){sum+=x[i]+w[i]}` 

leading to hadronic sequences like

`MOVE (R1), R2; ADD #1, R1; MUL (R3), R2; ADD #1, R3; ADD R2, R4; SUB #1, R5; BRNZ -6` 

(the relative jump here being measured in hadrons).
The XaVI for the silicon for this application could have a single Huffman ion instruction for this 7-hadron sequence. 
Its `Fetch` unit would break it down into the separate hadrons.

Another XaVI implementation may have no such need and would use some other Huffman coding. (The above example is rather extreme.)

(As long as the Uncompressed instruction set is sufficiently orthogonal, the compiler can produce consistent hadronic sequences that are also efficient.)


### An Instruction Set / Compiler Strategy

Given that the application is not defined before the compiler is produced, there is this strategy:
1. Generate a representative test suite (of C code) for the anticipated _type_ of application.
2. Define an Uncompressed ISA.
3. Choose a similar processor (the foreign 'Xeno') that has an existing compiler.
4. Create a Linker that maps Xeno instructions to Uncompressed XaVI hadrons. 
5. Develop the prototype CPU hardware. This will require two 16-bit memory words for every 32-bit Uncompressed instruction. The `Fetch` unit will be simple as a result.
6. Verify the CPU using the test suite.
7. Develop a compiler to generate Uncompressed XaVI hadrons (now that the concept implementation has been verified).

Then for a more _specific application_, having custom silicon:
8. Generate a representative test suite (of C code) for the anticipated _specific application_.
9. Analyze usage and hadron sequences.
10. Determine a particular compression scheme - this defines the application-specific XaVI's Huffman instruction set.
11. Develop a Linker for this specific scheme.
12. Verify the Linker-`Fetch` software-hardware combination.

Initially, the linker can be simple:
* Accepts single concatenated Xeno assembly code.
* Two-pass re-assembler (second pass to determine labels)
(To make things simpler, there will be restrictions on address ranges.)
A more capable linker could follow.

So there is a progression of the project from existing compiler + simple linker to custom compiler and linker.

It means that hardware development (step 5) and compiler development (step 7) is not held up by the critical instruction set definition.



## Datapath

To follow


