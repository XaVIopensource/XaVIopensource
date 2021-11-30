
# XaVI: A 16-bit Processor for Analog ICs

{Wikipedia-like editorial warning: this article is starting to get a bit rambling and needs tidying up eventually, when the concepts start to settle.}

# 1. Not Another One!

Why do we need _another_ processor?
* **For Analog/Mixed-Signal**: Many analog/mixed-signal chip providers have developed their own proprietary little processor for embedding into their chips. But there is no _standard_, _open_ 16-bit processor: the ARM or MIPS of the mixed-signal world. This 'tiny' CPU sits below a CPU in ARM's 'big.LITTLE' system concept. Not so tiny (8-bit) that its code density adversely affects dynamic power consumption but not so large (32-bit 'LITTLE') that its area adversely affects dynamic power consumption. 16 bits is _just_ right - just a bit bigger than the size of an ADC or DAC. 
* **Low Area**: Whilst 32-bit processors like ARM Cortex-M are making their way into the microcontroller market, running application software, they are still far too large for most analog chips. The aim is to push the programmability of processors into places that don't normally afford that programmability - which are generally not on small process nodes, for good reasons.
* **Ultra-Low Power**: Low area means low leakage, but the objective is also to have minimal signal transitions to perform the computation in order to minimize dynamic power. There will be some particular characteristics that will make XaVI particularly good for some ultra-low power techniques.
* **High code density** is critical in achieving low _system_ area and power. Being able to customize the instruction set takes this further.
* **Open**: without most restrictions on commercial use. This includes not needing to acknowledge the presence of XaVI CPUs to customers where their embedding is hidden from them.
* **Free**: free from the risk of clone claims from legal heavyweights, regardless of their legitimacy.
* **Compiler**: It needs to have a proven C compiler. 

Enter XaVI: XVI for 16, and the 'a' can stand for analog.


# 1.1. Concept Summary

The basic approaches to achieve low area and power are to have:
* Minimal datapath hardware, as a combinatorial path that can be optimized in synthesis and layout for the user-specific application to reduce unnecessary signal transitions.
* User-defined compression of the instruction set to achieve maximum code density for the user-specific application.

Between a fixed C compiler and the Datapath hardware, the software and hardware can be changed, optimized to the application:
* Software: translation (Huffman coding) of (perhaps multiple) 32-bit compiler instructions to the (often multiple) 16-bit instructions stored in memory.
* Hardware: decompressing the 16-bit instructions to (perhaps multiple cycles of) Datapath processing cycles.

The minimal `Datapath` comprises just an adder, a shifter and a logic unit. The shift unit can be configured for single-bit shifting or barrel shifting. A multiplier can be provided through an expansion interface. The register bank of configurable size (compiler switch). The compiler can be configured accordingly: for the number of registers and presence/absence of barrel shifter and multiplier.



Below are 3 examples to provide some context applications.

# 1.2. First example 'Programmable State Machines' System

Two XaVI subsystems on an Analog IC:
* One is needed for the receive part of the IC, for some specific dynamic control of the analog front end. The best control methods are dependent on the application and it is not possible to anticipate future requirements. The host downloads its code at power-up.  
* Another 'Programmable State Machine' is needed for the transmitter. The host downloads a tailored program immediately prior to transmitting data.
* In both cases, the CPUs are used to write to control registers with very specific timing sequences.
* Each CPU has only 32 words of memory! These are primarily for instructions (XaVI's internal registers provide the necessary data space for these simple timer programs).
* An external host processor downloads code to the subsystem at power-up and possibly during operation.
* The host processor can thereby access those control/status registers, but the architecture allows faster, less noisy control than if directed from the host. And it is more flexible than if there were hard-wired circuits instead.
* Both processors have the same customization: a 'decrement Rx and jump-relative if non-zero' instruction that  can be used to jump back to self in a low-power state. This is effectively a sleep/'wait for' timer but uses the resources of the CPU (i.e. adder and registers).
* {Although the final 32-word programs may be hand-assembled, the C compiler accelerates development.}


# 1.3. Second example 'Local Processor' System

A Local processor on an Analog IC.
* XaVI masters a SPI bus to which a serial EEPROM is connected. 
* 2K words of memory, acting as an instruction cache (caching EEPROM code) and for local data space.
* At start-up, parameters are transferred from EEPROM into control registers. At periodic intervals, diagnostics are performed to check correct operation. At periodic intervals, or as dictated by temperature changes, re-calibration firmware is executed.
* The processor is also available for use in evaluation and production test.
* Hardware outside of XaVI can compare 2 registers with the program count and halt the CPU on a match. This can provide the minimal debug logic with 2 hardware breakpoints. In this case, those registers are obviously not usable by the compiler. After most code has been developed and debugged, the user can choose to sacrific these breakpoints for greater code efficiency.


# 1.4. Third example Embedded System

An embedded energy-scavenging XaVI must perform a lot of various DSP filtering on sense signals before a neural net classifier. It also manages the overall application in this TinyML system.
* 64Kbyte Flash provides 48Kbytes data constants and 8Kwords of program space. 
* 2Kword instruction cache.
* 8Kbytes data RAM 
* The XaVI hardware is modified to implement various specific sequences of instructions (such as a sum-of-products) as single instructions, in order to reduce memory accesses to save power.
* Tightly-coupled hardware provides a multiply-accumulator with saturation and also ReLU (rectified linear) and SoftMax operations.


# 1.5. Block Diagram Example System

The block digram shows a superset of another possible small system.
* XaVI is executing code in iCache for 99% of time with occassional access to SPI flash. Code could be in RAM but this is not used.
* In some implementations there may be no RAM at all.
* A host can control XaVI and also write to CSR directly through the SPI interface. This includes controlling debug hardware for XaVI (halt/step and breakpoints).
* XaVI will copy setup parameters from SPI flash to CSRs on startup and store diagnostic information into SPI flash.

![A possible XaVI subsystem](https://github.com/XaVIopensource/XaVIopensource/blob/main/images/CPU_bus_and_memory.jpg)



# 2. The Instructions Concept

The CPU comprises:
* `Fetch` unit
* `Decode` unit 
* `Datapath` unit
* `Control` unit

![`Fetch`, `Schedule`, `Decode`, `Datapath`](https://github.com/XaVIopensource/XaVIopensource/blob/main/images/Fetch_Schedule_Decode_Datapath.jpg)

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


## 2.1 Atoms, Ions and Hadrons

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


## 2.2 Instruction Sets

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



## 2.3 Atomic Instructions

Many 'basic' instructions will actually be formed from multiple atomic hadrons. For example:
- `PUSH Rx` will be implemented as `SUB #1, SP`; `MOVE Rx, (SP)`.
- `POP  Rx` will be implemented as `MOVE (SP), Rx`; `ADD #1, SP`.
- `JSR aaaa` will be implemented as `SUB #1, SP`; `MOVE PC, (SP)`; `MOVE aaaa, PC`.
- `RETN` will be implemented as `MOVE (SP), PC`; `ADD #1, SP` (i.e. `POP PC`).
- `RETI` (return from interrupt) will be implemented as `POP PC`, `POP SF` (4 hadrons). 
And the `Scheduler` also handles interrupts by inserting instructions: `PUSH SF`, `PUSH PC`, `MOVE #0000, PC`.
{Query: do we want the stack to move up or down memory? Answer: top down}

Hadrons part of the same ion will obviously be atomic. A general indicator of whether something should be atomic is if an ion writes to `PC`, `SF` or `SP`. It may be that an instruction needs to be ftched before it can be determined whether a pending interupt can be accepted.


## 2.4 An Instruction Set / Compiler Strategy

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



# 3. Datapath

The capabilities of the `Datapath` unit define tha VLIW instructions and therefore also the Uncompressed instructions.
The design of the unit will be bigger than most actual XaVI implementations, relying on synthesis to remove unused parts.

The minimum components for a low-area CPU will be:
* registers,
* an arithmetic unit,
* a logic unit,
* a shift unit, and
* a data memory interface.
Here, we add an expansion/extension/coprocessor interface (e.g. for a hardware multiplier).

The arithmetic unit performs adds, subtracts and compares which clearly require the same underlying hardware. The other components of an 'Arithmetic Logic Unit' do not and so have been split. No hardware can be used twice within one hadron instruction cycle. Thus, `SUB (0x1234+Rx), Ry` is not possible as there are two tasks for the Arithmetic Unit here. The datapath should be structured to allow the most compute to be performed given the hardware resources. Thus, it should not preclude `AND (0x1234+Rx), Ry`, for example. On the other hand, the _possibility_ of having this instruction does not mean that the `Fetch` unit _will_ support this.

The `Datapath` traverses are shown in the figures below. {Shows what could be done. Actual may be simpler. Work in progress; will move away from Graphviz!}

![A possible XaVI datapath](https://github.com/XaVIopensource/XaVIopensource/blob/main/images/datapath.jpg)

To summarize valid arcs:
* The destination is either `Rd` or data memory via `DWDATA`.
* Immediate, register, indirect and absolute addressing modes can support `SHU` -> `LU` -> `AU` -> either `Rd` or `DWDATA`
* Indexed addressing mode can only support `SHU` -> `LU` -> either `Rd` or `DWDATA`

This has been arranged so that the `Datapath` is capable, in principle, of implementing the code:
`    R1 = ((*R2 >> 5) & 0x7) + R3;`
(i.e. peeling a 3-bit number out of a packed word in memory) in a single instruction.

{Writing into packed words, e.g. packed control registers, would need read-modify-write atomic sequences. I presume that there is the freedom to allocate control bits sensibly whereas this luxury is not often possible in packed code/data from flash.}


## 3.1 The Register Set

The framework provides for between 8 and 32 registers. Included within these are:
* `R0` = `RZ`: is only ever zero.
* `R1` = `SP` stack pointer - actually just the same as other registers. The compiler sould use any register above 2 for the stack pointer.
* `R30` = `PC`: Program Count
* `R31` = `SF`: Status Flags - a quite standard set comprising `Z`, `I`, `N`, `C` and `V` flags for zero, interrupt-enable, negative, carry and overflow.

(Note: Huffman instructions are likely only to be able to access registers 0...7 with single-word instructions. Interaction with flags and `PC` is normally only via conditional branches.)

The `PC` size is parameterized from full size '15:1' down to '5:1' minimum. Note this is always an even byte address. Program and data memory are separate (XaVI has a Harvard architecture) but the memory may be unified beyond the Instruction Cache. 


## 3.2 Operations

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

| Unary   | Operations                 | V | N | Z | C |
|---------|----------------------------|---|---|---|---|
| `MOVE`  | Move (pass through)        | * | * | * | * |
| `ROLC`  | Rotate left thru carry     | * | * | * | * |
| `RORC`  | Rotate right thru carry    | * | * | * | * |
| `SHRA`  | Signed shift right, arithmetic    | (0) | * | * | * |
| `SEXT`  | Sign-extend byte           | (0) | * | * | * |
| `SWPB`  | Swap bytes                 | - | - | - | - |


| Dyadic    | Operations                                | V | N | Z | C |
|-----------|-------------------------------------------|---|---|---|---|
| `ADD`     | Add                                       | * | * | * | * |
| `ADDC`    | Add with carry                            | * | * | * | * |
| `SUB`     | Subtract                                  | * | * | * | * |
| `SUBC`    | Subtract with carry                       | * | * | * | * |
| `CMP`     | Compare  (`SUB` without write-back)       | * | * | * | * |
| `AND`     | Logical AND                               | 0 | * | * | * |
| `OR`      | Logical OR, equivalent to `SET`           | * | * | * | * |
| `XOR`     | Exclusive OR                              | * | * | * | * |
| `BIT`     | Bit test (logical AND without write-back) | 0 | * | * | * |
| `CLR`     | Clear bits (logical AND with 1's complement)   | - | - | - | - |
| `SET`     | Set bits (logical OR)                          | - | - | - | - |

Notes: 
- There is no `ROLA` or `RORA`. `SHRA` shifts right with bit zero going into the carry.
- `OR`: additional
- { is the clearing of V for `AND` and `BIT` just a consequence of operation and not actually an exception?}
- `ROLC  Rx` rotate left through carry can be achieved with `ADDC Rx, Rx`.
- `SHLA Rx` shift arithmetic left can be achieved with `ADD  Rx, Rx`.
- `SWPB` is the equivalent of `RORA` 8 times.

{What about `SHR`, `SHLL` and `SHLA` arithmetic and logical shifts left and right? Is `RORA` really Arithmetic Shift Right? i.e. MSB stays the same. Could a sign-extend be achieved by `RORA.B Rx`; `ADDC.W Rx,Rx` (if a byte rotate sets all upper-byte bits to bit 7)?


By convention, 'Jumps' are long absolute (example `MOVE aaaa, PC`) whereas 'branches' are short relative, conditional on the `SF` flags. But the Uncompressed instructions need not make the distinction. Relative addressing just performs an `ADD` using the `ALU`.

| Opcode | Condition |
|--------|-------|
| `BNZ`  | `Z`=0 |
| `BZ`   | `Z`=1 |
| `BPOS` | `N`=0 |
| `BNEG` | `N`=1 |
| `BNC`  | `C`=0 |
| `BC`   | `C`=1 |
| `BGE`  | '>=' : `N`=`V` |
| `BL`   | '<' : not `N`=`V` |
| `BRA`  | always |

Note:
- `Z` zero flag set on bits 15:0 of the result being zero.
- `N` negative flag set on bit 15 of the result being set (word) or bit 8 (byte).
- `C` carry flag and `V` overflow flag: result is too big to fit into the required size of the result (word or byte). For `V`, the resultant sign is wrong.
- `BNL`: additional
- No 'Jump less' (`N`=0 and `Z`=0)


## 3.3 Fences

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



# 4. Port Interface

The _basic_ port interface is as follows:

| dir.n  | Port      | Description |
|--------|-----------|---|
| input  | `RSTN`         | Reset, active low |
| input  | `CKEN[:0]`     | Clocks, including phased ones for the fences |
| output | `PREAD`        | Program instruction bus: read enable |
| output | `PADDR[:1]`    | Program instruction bus: address |
| input  | `PRDATA[15:0]` | Program instruction bus: read data |
| output | `DREAD`        | Data bus: read enable |
| output | `DWRITE`       | Data bus: write enable |
| output | `DADDR[:1]`    | Data bus: address |
| output | `DWDATA[15:0]` | Data bus: write data |
| input  | `DRDATA[15:0]` | Data bus: read data |
| input  | `IRQ`          | Interrupt request, active high |
| output | `R[:1][:]`     | Register values, observable for co-processor |
| output | `BRKPT`        | `PC` matches `Rt` (where 't' is the number of the last register) |

This excludes the `Control` block, hence the source clock. The table excludes other signals that aid expansion and customization.

The Debug interface is part of the system outside of the core XaVI processor. However, it does provide one debug resource: the `BRKPT` output.
The `Control` unit handles starting and stopping (and single-stepping) of the processor. If the hardware breakpoint is enabled, the `Control` unit should halt execution when `BRKPT` is asserted, indicating that the `PC` has reached the hardware breakpoint. Code used during debugging must be generated from a compiler that does not use the top register. The compiler configuration could be modified for final code generation for a more optimum execution. This means that a register is not 'wasted' in such an area-critical design.



# 5. Compiler Specification and Implementation

## 5.1 General Approach

For the compiler, either LLVM or GCC could be used. The linker is going to be non-standard though because it needs to handle the custom instruction compression. Here is a proposal:
1. LLVM compiler to hadronic uncompressed 32-bit instructions.
2. LLVM-LD linker to produce (very inefficient) executables, for linking 'large' programs and for compiler verification.
3. Custom linker in Python is a multi-pass assembler (more passes than necessary, but this allows user customization between the steps)...
4. Concatenate all code into fixed order. All labels have are uniquified (prefixed with the function name or a shortform).
5. Custom compression into application-specific encoding.
6. Building up a dictionary of labels.
7. Producing code with correct absolute and relative addressing.
8. If relative addressing range is too large, change to hops around absolute jumps and go back to step 6.
9. Generate 'binary' (.elf).


## 5.2 Compiler Switches

* Number of registers (counted 1...n where n<29 since `R0`=0, `R31`=`SF` and `R30`=`PC`. Register n+1 is reserved as an intermediate holding register for atomic instructions that the compiler does not need to be aware of). Typically, n=7.
* Presence of a hardware multiplier.
* Presence of a barrel shifter {or the linker can just detect multiple 
* Maximum relative jump size.


## 5.3 Documentation

The compiler will generate code for uncompressed hadrons. The linker will then aggregate into Huffman instructions. The compiler code generation (sequence of hadrons) will need to be made availlable to users in a way not normally done for compilers, in order for hardware designers to know how to aggregate hadrons into single or atomic instructions. It needs to be documented where to look in the compiler source code so that designers can engineer rather than reverse-engineer solutions. 

For example, instead of generating a `PUSH R1`, it will generate `MOVE R1, 0(SP)` followed by `SUB #1, SP`. For `PUSH R1, R3, R4, R7` it would generate `MOVE R1, 0(SP); MOVE R3, -1(SP); MOVE R4, -2(SP); MOVE R7, -3(SP); SUB #4, SP`. The linker would then have the option of creating a 'Push multiple' from this.


# 6. Application-Specific Instruction Coding

The following gives some indication of how instructions might be encoded.


But first look at some very good 16-bit instruction sets for reference...

## MSP430

Key to the summary tables:
* '-': 0 or 1 to encode the instruction
* 'o': operand selection
* 'n': number (immediate value, offset, absolute or relative address)
* 'r': register identifier (source, destination)
* 'a': addressing mode selection
* 'f': flags (indication which selection of registers)
* 'x': extra, such as byte/word selection


## MSP430

Instruction set summary:
* https://www.ti.com/sc/docs/products/micro/msp430/userguid/as_5.pdf
* https://phas.ubc.ca/~michal/phys319/MSP430Reference-RyansEdit.pdf

Highly orthogonal, with just three types of instruction...

| Type | Description    | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|------|----------------|----|----|----|----|----|----|---|---|---|---|---|---|---|---|---|---|
| I    | Single-operand | -  | -  | -  | -  | -  | -  | o | o | o | x | a | a | r | r | r | r |
| II   | Two-operand    | -  | -  | -  | c  | c  | c  | n | n | n | n | n | n | n | n | n | n |
| III  | Condition jump | o  | o  | o  | o  | r  | r  | r | r | a | x | a | a | r | r | r | r |

using these addressing modes...

| Mode            | 2 | 1 | 0 |
|-----------------|---|---|---|
| OP Rs, Rd       | 0 | 0 | 0 |
| OP n(Rs), Rd    | 0 | 0 | 1 |
| OP a, Rd        | 0 | 1 | 0 |
| OP &a, Rd       | 0 | 1 | 1 |
| OP Rs, m(Rd)    | 1 | 0 | 0 |
| OP n(Rs), m(Rd) | 1 | 0 | 1 |
| OP a, m(Rd)     | 1 | 1 | 0 |
| OP &a, m(Rd)    | 1 | 1 | 1 |



## MSP430X

TBD: Differences w.r.t MSP430


## ARM Thumb

Table derived from https://developer.arm.com/documentation/ddi0210/c/Introduction/Instruction-set-summary/Thumb-instruction-summary.

More irregular, with the addressing mode determined by type...


| Type | Description                   | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|------|-------------------------------|----|----|----|----|----|----|---|---|---|---|---|---|---|---|---|---|
| 1    | MOVE shifted register         | -  | -  | -  | o  | o  | n  | n | n | n | n | r | r | r | r | r | r |
| 2    | ADD/SUB                       | -  | -  | -  | -  | -  | -  | o | r | r | r | r | r | r | r | r | r |
| 3    | MOVE, CMP, ADD, SUB immediate | -  | -  | -  | o  | o  | r  | r | r | n | n | n | n | n | n | n | n |
| 4    | ALU                           | -  | -  | -  | -  | -  | -  | o | o | o | r | r | r | r | r | r | r |
| 5    | High register                 | -  | -  | -  | -  | -  | -  | o | o | x | x | r | r | r | r | r | r |
| 6    | PC-relative load              | -  | -  | -  | -  | -  | r  | r | r | n | n | n | n | n | n | n | n |
| 7    | LD/ST with relative offset    | -  | -  | -  | -  | o  | x  | - | n | n | n | r | r | r | r | r | r |
| 8    | LD/ST byte/half-word          | -  | -  | -  | -  | o  | x  | - | n | n | n | r | r | r | r | r | r |
| 9    | LD/ST with immediate offset   | -  | -  | -  | x  | o  | n  | n | n | n | n | r | r | r | r | r | r |
| 10   | LD/ST half-word               | -  | -  | -  | -  | o  | n  | n | n | n | n | r | r | r | r | r | r |
| 11   | LD/ST stack pointer relative  | -  | -  | -  | -  | o  | r  | r | r | n | n | n | n | n | n | n | n |
| 12   | LD address                    | -  | -  | -  | -  | r  | r  | r | r | n | n | n | n | n | n | n | n |
| 13   | ADD offset to stack pointer   | -  | -  | -  | -  | -  | -  | - | - | x | n | n | n | n | n | n | n |
| 14   | PUSH/POP                      | -  | -  | -  | -  | o  | -  | - | r | f | f | f | f | f | f | f | f |
| 15   | LD/ST multiple                | -  | -  | -  | -  | o  | r  | r | r | f | f | f | f | f | f | f | f |
| 16   | Conditional branch            | -  | -  | -  | -  | -  | c  | c | c | n | n | n | n | n | n | n | n |
| 17   | Software interrupt            | -  | -  | -  | -  | -  | -  | - | - | n | n | n | n | n | n | n | n |
| 18   | Unconditional branch          | -  | -  | -  | -  | -  | n  | n | n | n | n | n | n | n | n | n | n |
| 19   | Long branch with link         | -  | -  | -  | -  | x  | n  | n | n | n | n | n | n | n | n | n | n |



## ARM Thumb2

TBD: Differences w.r.t MSP430




## XaVI hadrons, compared with MSP430 and ARM

(Recap on'Hadrons': uncompressed instructions executed on the `Datapath` unit. Multiple such instructions may be derived from a single compressed instruction.)

* Uncompressed instructions are orthogonal, like MSP430 (simpler coding - because it is already part-decoded!).
* PUSH, POP, JSR, RET are all split into hadrons as would load/store multiples be.


## Example XaVI compression

This sets out the way instructions may be compression in an imagined implementation.

(Note: 'Extend' means extending a 16-bit instruction into a 28-bit instruction.)

The instruction set would be mainly based on the MSP430, but with the following able to be performed more efficiently (i.e. higher instruction compression):

1. Single-word immediates, perhaps covering all integers -2...16 plus 0xF0, 0x1F, 0x3F, 0x7F, 0x80.
2. R8 (ordinarily needing to be accessed through extension) being used for three-operand instructions for more complex atomic instructions, e.g.
3. Read-modify-writes to packed registers, e.g. atomic `AND &0xFACE, ASL 3, 0x3F, R8` then `OR R2, R8, SHL 3, &0xFACE`, achieving a setting of register bits [8:3]; MOVE R8, &0xFACE
4. Saturated ADD instructions.

And to achieve these extra encodings, the following will need to be sacrificed (reduced compression):
1. Need to extend to access `PC` and `SF` (flags) registers.
2. Some two-operand instructions relegated for some addressing modes (ADDC, SUBC).
3. Sticky `SF` flag to set byte selection.
4. Reduced range of relative jumps.



