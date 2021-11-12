
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


# 1. The Instructions Concept

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


## 1.1 Atoms, Ions and Hadrons

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
Example: a read-modify-write is `ADD (R1), R2`; `MOVE R2, (R1)`. This chemical bonding is unrelated to the nuclear binding of hadrons. 
There could be both chemical and nuclear: a molecule of Hydrogen plus Deuterium: `ADD (R1), R2`; `MOVE R2, (R1)`; `INC R1`. 
You get the idea: the fundamental execution 'primitive' is the hadron.
one Huffman fetch leads to two Uncompressed instructions.

The `Fetch` unit gets Huffman ions from memory and decodes them to Uncompressed hadrons, handling atomicity to determine when interrupts can occur.


## 1.2 Instruction Sets

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

`MOVE (R1), R2`; `ADD #1, R1`; `MUL (R3), R2`; `ADD #1, R3`; `ADD R2, R4`; `SUB #1, R5`; `BRNZ -6` 

(the relative jump here being measured in hadrons).
The XaVI silicon for this application could have a single Huffman ion instruction for this 7-hadron sequence. 
Its `Fetch` unit would break it down into the separate hadrons.

Another XaVI implementation may have no such need and would use some other Huffman coding. (The above example is rather extreme.)

(As long as the Uncompressed instruction set is sufficiently orthogonal, the compiler can produce consistent hadronic sequences that are also efficient.)



## 1.3 Atomic Instructions

Many 'basic' instructions will actually be formed from multiple atomic hadrons. For example:
- `PUSH Rx` will be implemented as `SUB #1, SP`; `MOVE Rx, (SP)`.
- `POP  Rx` will be implemented as `MOVE (SP), Rx`; `ADD #1, SP`.
- `JSR aaaa` will be implemented as `SUB #1, SP`; `MOVE PC, (SP)`; `MOVE aaaa, PC`.
- `RETN` will be implemented as `MOVE (SP), PC`; `ADD #1, SP` (i.e. `POP PC`).
- `RETI` (return from interrupt) will be implemented as `POP PC`, `POP SF` (4 hadrons). 
And the `Scheduler` also handles interrupts by inserting instructions: `PUSH SF`, `PUSH PC`, `MOVE #0000, PC`.
{Query: do we want the stack to move up or down memory? Answer: top down}


## 1.4 An Instruction Set / Compiler Strategy

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



# 2. Datapath

The capabilities of the `Datapath` unit define tha VLIW instructions and therefore also the Uncompressed instructions.
The design of the unit will be bigger than most XaVI implementation, relying on synthesis to remove unused parts.


## 2.1 The Register Set

The framework provides for between 8 and 32 registers. Included within these are:
* `R0` = `RZ`: is only ever zero.
* `R1` = `SF`: Status Flags - a quite standard set comprising `Z`, `I`, `N`, `C` and `V` flags for zero, interrupt-enable, negative, carry and overflow.
* `R2` = `PC`: Program Count
* `R3` = `SP` stack pointer - actually just the same as higher registers. The compiler sould use any register above 2 for the stack pointer.

The `PC` and `SP` size is parameterized from full size '15:1' down to '5:1' minimum. Note this is always an even byte address. Program and data memory are separate (XaVI has a Harvard architecture) but the memory may be unified beyond the Instruction Cache. 


## 2.2 Operations

The `Datapath` provides a 3-term RISC architecture: `c = func(a, b)` where a and b can be one of:
* A register `Ra`, `Rb` ('register' addressing mode)
* A value `n` ('immediate' addressing mode)
* The contents of data memory `mem[n]` ('absolute' addressing mode)
* The contents of data memory `mem[Ra+n]` or `mem[Rb+n]` ('indexed indirect' addressing mode)

Note: the 16-bit Huffman instruction width means that Huffman instructions will generally be 2-term `b = func(a, b)` and with no 3-term instructions. 

The destination may be one of:
* Register `Rc`.
* Memory write mem[c]

The function may be derived from one of:
* `ALU`: unary arithmetic logic unit
* `ALU1`: dyadic arithmetic logic unit
* `SU3`: unary shift unit, fundamentally providing `SL`, `ROL`, `SR` and `ROR` instructions
* `XU4`: optional external custom unit. This is likely to provide multiply and multiply-accumulate instructions but the precise form can be customized.

Operations are generally available in both Byte and Word16 data widths.

| Unary   | Operations |
|---------|---|
| `MOVE`  | Move (pass through) |
| `RORC`  | Rotate right thru carry  |
| `RORA`  | Rotate right, arithmetic  |
| `SEXT`  | Sign-extend byte |
| `SWPB`  | Swap bytes  |


| Dyadic    | Operations |
|-----------|---|
| `ADD`     | Add |
| `ADDC`    | Add with carry |
| `SUB`     | Subtract |
| `SUBC`    | Subtract with carry |
| `CMP`     | Compare  (`SUB` without write-back) |
| `AND`     | Logical AND |
| `CLR`     | Clear (logical AND with 1's complement) |
| `OR`      | Logical OR, equivalent to `SET` |
| `XOR`     | Exclusive OR |
| `BIT`     | Bit test (logical AND without write-back) |

Note: 
- `ROLC  Rx` rotate left through carry can be achieved with `ADDC Rx, Rx`.
- `SHAL Rx` shift arithmetic left can be achieved with `ADD  Rx, Rx`.
- `SWPB` is the equivalent of `RORA` 8 times.

{What about `SHR`, `SHLL` and `SHLA` arithmetic and logical shifts left and right? Is `RORA` really Arithmetic Shift Right? i.e. MSB stays the same. Could a sign-extend be achieved by `RORA.B Rx`; `ADDC.W Rx,Rx` (if a byte rotate sets all upper-byte bits to bit 7)?


By convention, 'Jumps' are long absolut (example `MOVE aaaa, PC`) whereas 'branches' are short relative, conditional on the `SF` flags. But the Uncompressed instructions need not make the distinction. Relative addressing just performs an `ADD` using the `ALU`.

| Opcode | Condition |
|--------|--|
| `BN`Z  | `Z`=0 |
| `BZ`   | `Z`=1 |
| `BPOS` | `N`=0 |
| `BNEG` | `N`=1 |
| `BNC`  | `C`=0 |
| `BC`   | `C`=1 |
| `BGE`  | `N`=`V` |
| `BL`   | not `N`=`V` |
| `BRA`  | always |



## 2.3 Fences

The combinatorial path through `Datapath` might be long. For example, in executing a `MOVE (Rx+#nnnn), Ry` instruction:
- Register Rx,
- Select multiplexer for operand A,
- `ALU`
- out to `DADDR` data memory address,
- through memory subsystem ...
- address decoding
- memory,
- read data multiplexing, and
- back to `DRDATA` read data,
- through to the input of register Ry.

At various points, 'fence' will be inserted into the datapath. I use the term 'fence' when 'gate' would have made a better analogy - except of course that 'gate' is fundamentally defined already. These fence may be one of:
- AND gates, to force downstream nodes to to reduce unnecessary transitions.
- latches, to hold downstream nodes stable to reduce unnecessary transitions during part of the dataflow through the `Datapath`.
- flip-flops, performing the same roll as latches, but in the context of added pipelining.
- wires as it were, i.e. no fence at all.

There is no pipelining of instructions in the basic XaVI but flip-flop fences could be inserted into the `Datapath` if it was to be added.

The controls for these fences will come from the `Control` block. Design experimentation can lead to the more power-optimal implementations. (Note: synthesis tools can perform  data path gating to reduce power. Generally introducing sequential cells is not an option. 
Adding in fences may reduce dynamic power bit but it will increase area and hence leakage to. There is a tradeoff here.
This fencing allows experimentation regardless of synthesis tool capability.

The general strategy is arrange timing from `Control` so that logic is _not_ getting constrained (i.e. leading to an increase in area). An exception here is additiona within `ALU1`. A Brent-Kung Adder (BKA, a parallel prefix adder: PPA; a form of carry-lookahead adder: CLA) is likely to have lower power than a Ripple Carry Adder (RCA). There is the option to explicitly use such an adder rather than letting the synthesis tool build an adder.

A single Uncompressed instruction cycle will likely be done over a number of processor clock cycles - the processor clock is deliberately designed to be faster so as to generate controls for the fences to minimize signal transitions. This phasing is handled by the `Control` block. 




