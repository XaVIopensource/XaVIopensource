
# XaVI: A 16-bit Processor for Analog ICs

{Wikipedia-like editorial warning: this article is starting to get a bit rambling and needs tidying up eventually, when the concepts start to settle.}

# 1. Introduction


# 1.1 Not Another One!

Why do we need _another_ processor?
* **For Analog/Mixed-Signal**: Many analog/mixed-signal chip providers have developed their own proprietary little processor for embedding into their chips. But there is no _standard_, _open_ 16-bit processor: the ARM or MIPS of the mixed-signal world. This 'tiny' CPU sits below a CPU in ARM's 'big.LITTLE' system concept. Not so tiny (8-bit) that its code density adversely affects dynamic power consumption but not so large (32-bit 'LITTLE') that its area adversely affects dynamic power consumption. 16 bits is _just_ right - just a bit bigger than the size of an ADC or DAC. 
* **Low Area**: Whilst 32-bit processors like ARM Cortex-M are making their way into the microcontroller market, running application software, they are still far too large for most analog chips. The aim is to push the programmability of processors into places that don't normally afford that programmability - which are generally not on small process nodes, for good reasons.
* **Ultra-Low Power**: Low area means low leakage, but the objective is also to have minimal signal transitions to perform the computation in order to minimize dynamic power. There will be some particular characteristics that will make XaVI particularly good for some ultra-low power techniques.
* **High code density** is critical in achieving low _system_ area and power. Being able to customize the instruction set takes this further.
* **Open**: without most restrictions on commercial use. This includes not needing to acknowledge the presence of XaVI CPUs to customers where their embedding is hidden from them.
* **Customizable**: able to change to produce the best system performance, radically in some cases.
* **Free**: free from the risk of clone claims from legal heavyweights, regardless of their legitimacy.
* **Compiler**: But in all cases, there will be a proven C compiler. 

Enter XaVI: XVI for 16, and the 'a' can stand for analog.


# 1.2. Concept Summary

The basic approaches to achieve low area and power are to have:
* Minimal datapath hardware, as a combinatorial path that can be optimized in synthesis and layout for the user-specific application to reduce unnecessary signal transitions.
* User-defined compression of the instruction set to achieve maximum code density for the user-specific application.
* Flexibility to add not just _tightly-coupled_ hardware acceleration, but _completely-integrated_ hardware acceleration that shares the processor's resources. 

Between a fixed C compiler and the Datapath hardware, the software and hardware can be changed, optimized to the application:
* Software: translation (Huffman coding) of (perhaps multiple) 32-bit compiler instructions to the (often multiple) 16-bit instructions stored in memory.
* Hardware: decompressing the 16-bit instructions to (perhaps multiple cycles of) Datapath processing cycles.

The minimal `Datapath` comprises just an adder, a shifter and a logic unit. The shift unit can be configured for single-bit shifting or barrel shifting. A multiplier can be provided through an expansion interface. The register bank of configurable size (compiler switch). The compiler can be configured accordingly: for the number of registers and presence/absence of barrel shifter and multiplier.


Below are some examples to provide some context applications.

# 1.3. A Sorry Tale

First, an example of how _not_ to do things. Custom hardware is developed in order to improve performance and power consumption. The processor is kept in a sleep state during this time and the custom pipelined hardware performs numerous arithmetic operations per clock cycle. Unfortunately, the requirements for the custom block change slightly (perhaps because of new customer requirements or perhaps from needing to work around analog issues). The hard-coded processing can no longer be used in this scenario and the application must revert to using the processor. The custom hardware was too brittle. The result is a system that is _larger_ and _more_ power-hungry than the original processor on its own. 


# 1.4. First example Embedded System

An embedded energy-scavenging XaVI must perform a lot of various DSP filtering on sense signals before a neural net classifier. It also manages the overall application in this TinyML IoT system.
* 64Kbyte Flash provides 48Kbytes data constants and 8Kwords of program space. 
* 2Kword instruction cache.
* 8Kbytes data RAM.
* The XaVI hardware is modified to implement various specific sequences of instructions (such as a sum-of-products) as single instructions, in order to reduce instruction memory accesses to save power.
* The XaVI standard datapath hardware basically comprising shift, logic and arithmetic units is modified to add _four_ multiply-accumulates that can be arranged either as a biquad filter or a 4-stage FIR filter. One MAC is used to provide multiply and multiply-accumulate instructions.
* The compiler is not told of the extra registers but they are available for customized assembly code routines. 
* It also has 'maximum' and 'minimum' instructions. These are used for rectified-linear functions for the neural net but are also usable for hand-coded DSP saturation in-line assembler. The augmented processor can perform a rectified sum of products with just two instructions and with 100% utilization of the data memory interface.
* All the added capabilities can be used together but they can be used separately, put together in similar situations, such as when requirements have changed.


# 1.5. Second example 'Programmable State Machines' System

Two XaVI subsystems on an Analog IC:
* One is needed for the receive part of the IC, for some specific dynamic control of the analog front end. The best control methods are dependent on the application and it is not possible to anticipate future requirements. The host downloads its code at power-up.  
* Another 'Programmable State Machine' is needed for the transmitter. The host downloads a tailored program immediately prior to transmitting data.
* In both cases, the CPUs are used to write to control registers with very specific timing sequences.
* Each CPU has only 32 words of memory! These are primarily for instructions (XaVI's internal registers provide the necessary data space for these simple timer programs).
* An external host processor downloads code to the subsystem at power-up and possibly during operation.
* The host processor can thereby access those control/status registers, but the architecture allows faster, less noisy control than if directed from the host. And it is more flexible than if there were hard-wired circuits instead.
* Both processors have the same customization: a 'decrement Rn and jump-relative if non-zero' instruction that can be used to jump back to self in a low-power state. This is what is effectively used as a sleep/'wait for' timer but it is using the resources of the CPU (i.e. the adder and pne register). Another register retains contents but everything else in the processor and wider system is powered down during sleep.
* Both processors have an otherwise simplified instruction decoding. Multi-cycle instructions such as 'push' and must be implemented as separate (but atomic) 'move rx, (sp)' then 'sub #1, sp' instructions, but these are not used in this simple system.
* Although the final 32-word programs may be hand-assembled, the C compiler accelerates development and evaluation.


# 1.6. Thrid example 'Local Processor' System

A Local processor on an Analog IC.
* XaVI masters a SPI bus to which a serial EEPROM is connected. 
* 2K words of memory, acting as an instruction cache (caching EEPROM code) and for local data space.
* At start-up, parameters are transferred from EEPROM into control registers. At periodic intervals, diagnostics are performed to check correct operation. At periodic intervals, or as dictated by temperature changes, re-calibration firmware is executed.
* The processor is also available for use in evaluation and production test.
* Hardware outside of XaVI can compare 2 registers with the program count and halt the CPU on a match. This can provide the minimal debug logic with 2 hardware breakpoints. In this case, those registers are obviously not usable by the compiler. After most code has been developed and debugged, the user can choose to sacrific these breakpoints for greater code efficiency.



# 1.7. Block Diagram Example System

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

* The `Fetch` unit gets Huffman instructions from memory and uncompresses them to one _or more_ Uncompressed instructions. Emphasize again: one _or more_.
* The Huffman instruction stream may get interrupted by the (single) hardware interrupt.
* The `Decode` unit produces a VLIW instruction from an Uncompresssed instruction.
* The `Datapath` unit contains everything needed to execute a single instruction. Its contents define what is possible at any one time.
* The `Control` unit provides clock, reset and low-power controls to the rest of the CPU.


## 2.1 Atoms, Ions, Hadrons and Quarks

The term 'atomic' refers to the idea that consecutive CPU instructions are inseparable. The CPU cannot be interrupted between these instructions.

I'll expand on this analogy. First, some physics:
* Molecules are made out of atoms that are bound together (reminder, irrelevant here: ionically or covalently).
* Atoms that are unbound are _ions_ (reminder, irrelevant here: which will have some +ve or -ve charge)
* Ions are mainly made up of _hadrons_ (reminder, irrelevant here: protons and neutrons; electrons are tiny in comparison)
* Hadrons are mainly made up of _quarks_ (irrelevant here: such as the 'Up', 'Down' and 'Charm' quarks, bound together by _gluon_ glue.)

And now the analogy:
* The `Datapath` of a CPU has some separate components. For XaVI: `RU`, `MU`, `AU`, `LU`, `SU`, `KU` and `CU` register, memory, arithmetic, logic, shift, konstant and conditional units, involved in instructions such as `MOVE`, `STORE`, `ADD`/`SUB`, `AND`/`XOR`, `LSR`/`ROLC`, `LD #1, R2` and `BRNZ` respectively.
* Operations on these units are called _quarks_. They are the smallest processing operation.
* A number of _quarks_ combine to form a _hadron_: the smallest possible instruction, performed within 1 processing clock cycle. An important constraint: there cannot be more than 1 type of quark in any hadron. You cannot use the `AU` hardware to do more than one thing at a time, for example. A hypothetical hadronic instruction such as `AND.NZ #4(R1), R2` can be broke down to (i) `RU` provides R1 and R2, (ii) `KU` provides '#4', (iii) `AU` provides 'R1+4', (iv) `MU` provides the contents of address `R1+4`, (v) `LU` performs the AND operation, (vi) `CU` decides whether the result will be stored in R2 based upon the state of the zero flag. The `SU` shift unit is not used. It would not be possible to change this hadron to `ADD.NZ #4(R1), R2` unless there was an additional adder within the datapath. This sets out the _maximum_ that a hadron could implement, irrespective of how these units are wired up (glued together). The CPU might support a conditional jumps but not conditional-ANDs.
* A number of _hadrons_ can combine to for an _ion_. Every ion involves an instruction fetch and most ions will have only 1 hadron (irrelevant fact: Hydrogen H+ ion is a 1-hadron ion and Hydrogen is the most abundant element in the universe, accounting for about 75% of all matter). A multi-hadron ion is needed for an operation where 1 hardware unit is needed to do more than 1 thing. For example, a hypothetical `RETI` return-from-interrupt instruction pulls both the `PC` program count and `SF` status flags from memory. The `MU` cannot do both of these in the same processor cycle.
* A number of _ions_ can combine to form a _molecule_. For example, a read-modify-write molecule might consist of the ions (i) disable interrupt, (ii) OR memory with register, (iii) store register to memory, and (iv) enable interrupts. This is , using the computing term 'atomic'

Ultimately, processing is one long stream of _quarks_. Conventionally, a C compiler transforms C source code into such a stream, packaged up into _ions_.

Matching up terminology:
* 'Huffman' instructions apply to ions
* 'Uncompressed' instructions apply to hadrons
* 'VLIW' instructions split this out to independent control of the quarks.

The `Fetch` unit gets Huffman ions from memory and decodes them to Uncompressed hadrons, handling atomicity to determine when interrupts can occur.


# 3. Datapath

The capabilities of the `Datapath` unit define tha VLIW instructions and therefore also the Uncompressed instructions.
The actual (Verilog code) design of the unit will be bigger than most actual XaVI implementations. For example, it will support more registers than are actually present. But logic synthesis will simply remove the unusable parts. The XaVI architecture is aiming for minimal hardware so it only provides the minimum number of sub-units. These are:
* `RU` register unit: see below for setails of the register set.
* `KU` constant unit: provides constants used for immediate, absolute and indexed-indirect addressing modes.
* `SU` shift unit: arithmetic and logical shifts and rotates, plus sign-extension. This is optionally a barrel shifter.
* `LU` logic unit: and/or/xor bitwise operations
* `XU` extension unit: This is not minimal and completely optional. It provides an interface for extended instructions, including multiplication.
* `AU` arithmetic unit: additions and subtractions
* `CU` conditional unit: such as for conditional jumps and not writing the result back to `RU` as with a 'compare' instruction.
* `MU` memory unit: for memory reads and writes.
There is no hardware for pre- or post- increment/decrement, for example. There is only one adder. This also means that it cannot simultaneously calculate an offset address _and_ do a subtraction. Thus it cannot perform a `SUB 12(R2), R3` hadron but it could _in principle_ perform an `XOR 12(R2), R3` hadron.

## 3.1 The Datapath Concept

The aim of the datapath design is to allow as many of the sub-units to be usable in parallel in order to maximize the computation performed in a single cycle. The Huffman ions _might_ be encoded such that only `SU` _or_ `LU` _or_ `AU` is used for data manipulation on any one processor cycle. And yet, internal to XaVI, it could still have a `Fetch` unit that, for example, decoded a single Huffman instruction into a sequence of many VLIW instructions performing a [CORDIC](https://en.wikipedia.org/wiki/CORDIC) arctangent function. This would have the `SU`, `LU` and `AU` being used in parallel for over 20 processor cycles. 

This is a key concept behind XaVI:
* Avoid bolting on various co-processors which add significant area and power by trying to use the hardware resources that are available within XaVI.
* This 'compute in place' means that there is no moving of data into the co-processor or out of it.
* There is flexibility: perhaps a single instruction for only one CORDIC iteration rather than the whole algorithm would be more flexible.

The `Datapath` traverses are shown in the figures below. {This is a work in progress; and I will move away from Graphviz!}

![A possible XaVI datapath](https://github.com/XaVIopensource/XaVIopensource/blob/main/images/datapath.jpg)

To summarize valid arcs:
* The destination is either `Rd` or data memory via `DWDATA`.
* Immediate, register, indirect and absolute addressing modes can support `SU` -> `LU` -> `AU` -> either `Rd` or `DWDATA`
* Indexed addressing mode can only support `SHU` -> `LU` -> either `Rd` or `DWDATA`

This has been arranged so that the `Datapath` is capable, in principle, of implementing code such as:
* `    R1 = ((*R2 >> 5) & 0x7) + R3;` peeling fields out of words packed in memory,
* `???` TBD for a single-step multiply when there is no hardware multiply, and
* `???` TBD for a single-iteration CORDIC operation,
in a single cycle.


## 3.2 The Register Set

The framework provides for between 8 and 32 registers although most implementations would have around 8 registers. Included within these are:
* `R0` = `RZ`: is only ever zero.
* `R1` = `RI` intermediate register.
* `R2`...`Rn` = general-purpose registers with the last one being designated `SP` for use as the stack pointer (some applications might be so small there is only one level of hierarchy and hence don't need a stack - hence why `SP` is `Rn` not `R2`).
* `R30` = `PC`: Program Count
* `R31` = `SF`: Status Flags - a quite standard set comprising `Z`, `I`, `N`, `C` and `V` flags for zero, interrupt-enable, negative, carry and overflow.

The `PC` size is parameterized from full size '15:1' down to '5:1' minimum. Note this is always an even byte address. Program and data memory are separate (XaVI has a Harvard architecture) but the memory may be unified beyond the Instruction Cache. 

The `SF` size is parameterized from normal '4:0' up to full '15:0' with the higher bits available to the user (via assembler).


## 3.3 Operations

The `Datapath` provides a 3-operand RISC architecture: `c = func(a, b)` but quarks are limited to support only:
* `Ra = func(Ra, b)` i.e. 2-operand,
* `RI = func(Ra, b)` i.e. only one 3-operand register destination, or,
* `mem[c] = func(Ra, b)` i.e. memory destination (absolute addressing mode).
* `mem[Rc] = func(Ra, b)` i.e. memory destination (indirect addressing mode).
* `mem[Rc+b] = func(Ra)` i.e. memory destination (indexed indirect addressing mode)

Operations are generally available in both Byte and Word16 data widths.

`SU` operations are...

| Unary   | Operations                 | V | N | Z | C |
|---------|----------------------------|---|---|---|---|
| `MOVE`  | Move (pass through)        | * | * | * | * |
| `ROLC`  | Rotate left thru carry     | * | * | * | * |
| `RORC`  | Rotate right thru carry    | * | * | * | * |
| `SHRA`  | Signed shift right, arithmetic    | (0) | * | * | * |
| `SEXT`  | Sign-extend byte           | (0) | * | * | * |
| `SWPB`  | Swap bytes                 | - | - | - | - |


`LU` operations are...

| Dyadic    | Operations                                | V | N | Z | C |
|-----------|-------------------------------------------|---|---|---|---|
| `AND`     | Logical AND                               | 0 | * | * | * |
| `OR`      | Logical OR, equivalent to `SET`           | * | * | * | * |
| `XOR`     | Exclusive OR                              | * | * | * | * |
| `BIT`     | Bit test (logical AND without write-back) | 0 | * | * | * |
| `CLR`     | Clear bits (logical AND with 1's complement)   | - | - | - | - |
| `SET`     | Set bits (logical OR)                          | - | - | - | - |

`AU` operations are...

| Dyadic    | Operations                                | V | N | Z | C |
|-----------|-------------------------------------------|---|---|---|---|
| `ADD`     | Add                                       | * | * | * | * |
| `ADDC`    | Add with carry                            | * | * | * | * |
| `SUB`     | Subtract                                  | * | * | * | * |
| `SUBC`    | Subtract with carry                       | * | * | * | * |
| `CMP`     | Compare  (`SUB` without write-back)       | * | * | * | * |

Notes: 
- There is no `ROLA` or `RORA`. `SHRA` shifts right with bit zero going into the carry.
- `OR`: additional
- { is the clearing of V for `AND` and `BIT` just a consequence of operation and not actually an exception?}
- `ROLC  Rx` rotate left through carry can be achieved with `ADDC Rx, Rx`.
- `SHLA Rx` shift arithmetic left can be achieved with `ADD  Rx, Rx`.
- `SWPB` is the equivalent of `RORA` 8 times.

{What about `SHR`, `SHLL` and `SHLA` arithmetic and logical shifts left and right? Is `RORA` really Arithmetic Shift Right? i.e. MSB stays the same. Could a sign-extend be achieved by `RORA.B Rx`; `ADDC.W Rx,Rx` (if a byte rotate sets all upper-byte bits to bit 7)?

By convention, 'Jumps' are long absolute (example `MOVE aaaa, PC`) whereas 'branches' are short relative, conditional on the `SF` flags. But the Uncompressed instructions need not make the distinction. Relative addressing just performs an `ADD` using the `ALU`.

Conditions are: 

| Opcode | Condition |
|--------|-------|
| `NZ`  | `Z`=0 |
| `Z`   | `Z`=1 |
| `POS` | `N`=0 |
| `NEG` | `N`=1 |
| `NC`  | `C`=0 |
| `C`   | `C`=1 |
| `GE`  | '>=' : `N`=`V` |
| `LESS` | '<' : not `N`=`V` |
| `ALL`  | always |
| `NULL`  | never |

Note:
- `Z` zero flag set on bits 15:0 of the result being zero. {or 7:0 for byte operations}
- `N` negative flag set on bit 15 of the result being set (word) or bit 8 (byte).
- `C` carry flag and `V` overflow flag: the result is too big to fit into the required size of the result (word or byte). For `V`, the resultant sign is wrong.


## 3.3 Fences

The combinatorial path through `Datapath` might be long. For example, in executing a `MOVE (Rx+#nnnn), Ry` instruction:
- Register Rx,
- Select multiplexer for operand A,
- `AU` creates the indexed address,
- out to `DADDR` data memory address,
- through memory subsystem ...
- address decoding
- memory,
- read data multiplexing, and
- back to `DRDATA` read data,
- through to the input of register Ry.

New terminology: 'fence'. At various points, fences will need to be inserted into the datapath. (I use the term 'fence' when 'gate' would have made a better analogy - except of course that 'gate' is fundamentally defined already.) These fences may be one of:
- AND gates, to force downstream nodes to to reduce unnecessary transitions.
- latches, to hold downstream nodes stable to reduce unnecessary transitions during part of the dataflow through the `Datapath`.
- flip-flops, performing the same roll as latches, but in the context of added pipelining.
- wires as it were, i.e. no fence at all.

There is no pipelining in the basic XaVI but flip-flop fences could be inserted into the `Datapath` if pipelining was to be added.

The controls for these fences will come from the `Control` block. Design experimentation can lead to the more power-optimal implementations. (Note: synthesis tools can perform  data path gating to reduce power. Generally introducing sequential cells is not an option. 
Adding in fences may reduce dynamic power but it will increase area and hence leakage to. There is a tradeoff here.
This fencing allows experimentation regardless of the synthesis tool capability.

This is a key XaVI concept: to allow exploration of different fence configurations in order to minimize overall power consumption. This exploration can be automated.

The general strategy is arrange timing from `Control` so that logic is _not_ getting constrained (i.e. leading to an increase in area). An exception here is addition within `AU`. A Brent-Kung Adder (BKA, a parallel prefix adder: PPA; a form of carry-lookahead adder: CLA) is likely to have lower power than a Ripple Carry Adder (RCA). There is the option to explicitly use such an adder rather than letting the synthesis tool build the adder.

The clock provided to XaVI will generally be faster than the 'processor cycle'. This allows the `Control` unit to generate the controls for the fences to minimize signal transitions.



# 4 Compilers, Linkers and Decoders


# Quark Instruction Set

The compiler generates streams of quark instructions, with no attempt to encode instructions efficiently, hence the arbitrary coding here:
* nibble 3 (top) indicates quark type (R, K, S, L, A, C, M),
* nibble 2 indicates the instruction within that quark type,
* nibble 1 selects operands and also the word size, and
* nibble 0 (bottom) selects the X operand and number of bit shifts.

Reminder: multiple quarks will be executed per processor instruction cycle.

The VLIW instruction codes that control the `Datapath` hardware are easily derived from these quark instruction codings.


| Mnemonic       | Size  | 15 | 14 | 13 | 12 | 11 | 10 | 9  | 8  | 7  | 6  | 5  | 4  | 3  | 2  | 1  | 0  | 15:0    | Description                         | Pseudocode                                  |
|----------------|-------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|---------|-------------------------------------|---------------------------------------------|
| R.NUL          | W     | 0  | 0  | 0  | 0  | 0  | -  | -  | -  | -  | -  | -  | -  | -  | -  | -  | -  | -       | (Register unit null operation)      | X=reg[0]; Y=reg[0];                         |
| R.SEL   r2, r3 | W     | 0  | 0  | 0  | 0  | 1  | -  | x4 | y4 | y3 | y2 | y1 | y0 | x3 | x2 | x1 | x0 | -       | Register selects                    | X=reg[x]; Y=reg[y];                         |
| K.IMM   0x1234 | W     | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | -  | -  | -  | -  | -  | -  | -  | -  | n[15:0] | Set immediate constant              | K=n;                                        |
| K.IMM   0x56   | B     | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 1  | n7 | n6 | n5 | n4 | n3 | n2 | n1 | n0 | -       | Set immediate constant (byte)       | K=n;                                        |
| K.RD           | B/W   | 0  | 0  | 0  | 1  | 0  | 0  | 1  | 0  | b  | -  | -  | -  | -  | -  | -  | -  | -       | Select memory read                  | K=mem[daddr];                               |
| S.NUL          |       | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | -  | -  | -  | -  | -  | -  | -  | -  | -       | (Shift unit null operation)         | S =  op1                                    |
| S.LA   K       | W     | 0  | 0  | 1  | 0  | 0  | 1  | 0  | 0  | -  | -  | s5 | s4 | n3 | n2 | n1 | n0 | -       | Shift left arithmetic               | S =  op1 << n                               |
| SWAB           | B<->B | 0  | 0  | 1  | 0  | 1  | 0  | 0  | 0  | -  | -  | s5 | s4 | -  | -  | -  | -  | -       | Swap bytes                          | S = { op1[7:0], op1[15:8] }                 |
| S.EXT          | B->W  | 0  | 0  | 1  | 0  | 1  | 0  | 0  | 1  | -  | -  | s5 | s4 | -  | -  | -  | -  | -       | Sign extend                         | S = { 8{op1[7]}, op1[7:0] }                 |
| S.RA           | B/W   | 0  | 0  | 1  | 0  | 1  | 1  | 0  | 0  | -  | -  | s5 | s4 | n3 | n2 | n1 | n0 | -       | Shift right arithmetic              | S =  op1 >> n                               |
| S.RR           | B/W   | 0  | 0  | 1  | 0  | 1  | 1  | 0  | 1  | b  | -  | s5 | s4 | n3 | n2 | n1 | n0 | -       | Shift: right rotation               | S =  rotate( op1  >> n )                    |
| S.RRC          | B/W   | 0  | 0  | 1  | 0  | 1  | 1  | 1  | 0  | b  | -  | s5 | s4 | n3 | n2 | n1 | n0 | -       | Shift: right rotation through carry | S =  rotate({ c, op1 } >> n )               |
| L.NUL          | B/W   | 0  | 0  | 1  | 1  | 1  | 0  | 0  | 0  | b  | -  | -  | -  | -  | -  | -  | -  | -       | (Logic unit null operation)         | L = op1                                     |
| L.AND          | B/W   | 0  | 0  | 1  | 1  | 1  | 0  | 0  | 0  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Logical AND                         | L = op1 & op2                               |
| L.OR           | B/W   | 0  | 0  | 1  | 1  | 1  | 0  | 0  | 1  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Logical OR                          | L = op1 | op2                               |
| L.XOR          | B/W   | 0  | 0  | 1  | 1  | 1  | 0  | 1  | 0  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Logical XOR                         | L = op1 ^ op2                               |
| L.ANT          | B/W   | 0  | 0  | 1  | 1  | 1  | 0  | 1  | 1  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Logical And-NoT: a&~b               | L = op1 & ~op2                              |
| A.NUL          |       | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | b  | -  | -  | -  | -  | -  | -  | -  | -       | Arithmetic: add                     | A = op1 + op2                               |
| ADD            | B/W   | 0  | 1  | 0  | 0  | 1  | 0  | 0  | 0  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Arithmetic: add                     | A = op1 + op2                               |
| ADC            | B/W   | 0  | 1  | 0  | 0  | 1  | 0  | 0  | 1  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Arithmetic: add with carry          | A = op1 + op2 + C                           |
| A.SUB          | B/W   | 0  | 1  | 0  | 0  | 1  | 0  | 1  | 0  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Arithmetic: subtract                | A = op1 + ~op2 + 1                          |
| A.SBC          | B/W   | 0  | 1  | 0  | 0  | 1  | 0  | 1  | 1  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Arithmetic: subtract with carry     | A = op1 + ~op2 + ~C                         |
| C.NO           |       | 0  | 1  | 0  | 1  | 0  | 0  | 0  | 0  | -  | -  | -  | -  | -  | -  | -  | -  | -       | Condition: write never              |                                             |
| C.YES          |       | 0  | 1  | 0  | 1  | 0  | 0  | 0  | 1  | -  | s6 | s5 | s4 | -  | -  | -  | -  | -       | Condition: write always             | r[op1] = s6 ? A : L                         |
| C.NZ           |       | 0  | 1  | 0  | 1  | 1  | 0  | 0  | 0  | -  | s6 | s5 | s4 | -  | -  | -  | -  | -       | Condition: write Rx if Z=0          | if (Z==0){ r[op1] = s6 ? A : L }            |
| C.Z            |       | 0  | 1  | 0  | 1  | 1  | 0  | 0  | 1  | -  | s6 | s5 | s4 | -  | -  | -  | -  | -       | Condition: write Rx if Z=1          | if (Z==1){ r[op1] = s6 ? A : L }            |
| C.NC           |       | 0  | 1  | 0  | 1  | 1  | 0  | 1  | 0  | -  | s6 | s5 | s4 | -  | -  | -  | -  | -       | Condition: write Rx if C=0          | if (C==0){ r[op1] = s6 ? A : L }            |
| C.C            |       | 0  | 1  | 0  | 1  | 1  | 0  | 1  | 1  | -  | s6 | s5 | s4 | -  | -  | -  | -  | -       | Condition: write Rx if C=1          | if (C==1){ r[op1] = s6 ? A : L }            |
| C.NN           |       | 0  | 1  | 0  | 1  | 1  | 1  | 0  | 0  | -  | s6 | s5 | s4 | -  | -  | -  | -  | -       | Condition: write Rx if N=0          | if (N==0){ r[op1] = s6 ? A : L }            |
| C.NEG          |       | 0  | 1  | 0  | 1  | 1  | 1  | 0  | 1  | -  | s6 | s5 | s4 | -  | -  | -  | -  | -       | Condition: write Rx if N=1          | if (N==1){ r[op1] = s6 ? A : L }            |
| C.GTE          |       | 0  | 1  | 0  | 1  | 1  | 1  | 1  | 0  | -  | s6 | s5 | s4 | -  | -  | -  | -  | -       | Condition: write Rx if N=V          | if (N==V){ r[op1] = s6 ? A : L }            |
| C.LT           |       | 0  | 1  | 0  | 1  | 1  | 1  | 1  | 1  | -  | s6 | s5 | s4 | -  | -  | -  | -  | -       | Condition: write Rx if N!=V         | if (N!=V){ r[op1] = s6 ? A : L }            |
| M.NUL          |       | 0  | 1  | 1  | 0  | 0  | 0  | 0  | 0  | -  | -  | -  | -  | -  | -  | -  | -  | -       | (Memory unit null operation)        |                                             |
| M.RD           | B/W   | 0  | 1  | 1  | 0  | 1  | 0  | 0  | 0  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Memory read request                 | daddr = s5 ? A : L                          |
| M.WR           | B/W   | 0  | 1  | 1  | 0  | 1  | 0  | 0  | 1  | b  | -  | s5 | s4 | -  | -  | -  | -  | -       | Memory write                        | daddr = s5 ? A : L; mem[daddr] = s4 ? A : L |



The operands referred to in the table above are selected as per the table below.

| Instruction   | s5 | s4 | Description                                                  |
|---------------|----|----|--------------------------------------------------------------|
| L.xx    Y, X  | 0  | 0  | Operand is X; operator is Y                                  |
| L.xx    K, X  | 0  | 1  | Operand is X; operator is K                                  |
| L.xx    S, X  | 1  | 0  | Operand is X; operator is S                                  |
|               | 1  | 1  | (N/A: reserved for expansion)                                |
| A.xx    Y, X  | 0  | 0  | Operand is X; operator is Y                                  |
| A.xx    K, X  | 0  | 1  | Operand is X; operator is K                                  |
| A.xx    S, X  | 1  | 0  | Operand is X; operator is S                                  |
|               | 1  | 1  | (N/A: reserved for expansion)                                |
| C.xx    A, X  | 0  | 0  | Conditionally write AU result to register selected for X     |
| C.xx    A, RI | 0  | 1  | Conditionally write AU result to intermediate register `RI`  |
| C.xx    A, PC | 1  | 0  | Conditionally write AU result to `PC` for X                  |
|               | 1  | 1  | (N/A: reserved for expansion)                                |
| C.xx    L, RX | 0  | 0  | Conditionally write LU result to register selected for X     |
| C.xx    L, RI | 0  | 1  | Conditionally write LU result to intermediate register `RI`  |
| C.xx    L, PC | 1  | 0  | Conditionally write LU result to `PC` for X                  |
|               | 1  | 1  | (N/A: reserved for expansion)                                |
| M.xx          | x  | 0  | Address is AU result, write data is LU result, if applicable |
| M.xx          | x  | 1  | Address is LU result, write data is AU result, if applicable |

{ some minor fixes needed to the above }

!!!!!!!! Up to here in the updating !!!!!!!!!!!!!!

Update with info on:
* Quark compiler
* Sequence R-K-S-L-A-C-M
* Quark instruction set
* Gluer sequence



### Generating custom instructions using the compiler???

{analysis of quark sequences or hadron sequences? }

Custom instructions for a CORDIC arctan accelerator, for example, could be created by:
1. Writing the algorithm in C.
2. Compiling it to a quark sequence.
3. Deciding which parts of the sequence are to be chunked together in hardware.
4. Breaking the sequence to be implemented in hardware down to VLIW hadrons
5. Changing the `Fetch` unit to implement those ions.

A slight modification to the code would lead to a different quark sequence, leading to those special instructions not being chosen. The same C compiler can be used for hardware that supports CORDIC arctan in multiple different ways.





## 2.2 Compilers, Linkers and Decoders

However, a compiler could just spit out the raw stream of _quarks_, leaving it up to something downstream to package them up into ions. This would allow the hardware engineer to determine whether the `Datapath` unit had its various sub-units connected together in the most optimum way!

Perhaps the assembly code format could be based around the VLIW
`RU`, `MU`, `AU`, `LU`, `SU`, `KU` and `CU`
REG R4  NZ

Perhaps a conditional `AND.NZ` _would_ be really #4(R1), R2`






This would mean the same compiler could be used for a _variety_ of hardware implementations, ranging from a 'quark processor' (very small area but very poor code density) to an 'ion processor' that might bundle _many_ quarks into a single instruction over _many_ processor cycles (such as ARM's 'load/store multiple'). The hardware could be customized to get the best combination of code density, power and area that was possible.

The compiler writer needs to think in terms of hadrons even though the compiler outputs quarks. They need to have the structure of the `Datapath` unit in mind in order to generate quark streams that could compressed as efficiently as possible. For example, if the `SU` comes before the `AU` in the datapath then it would be possible to do 'a + (b<<1)' in one cycle. But if it comes afterwards then it must take 2. The `Datapath` hardware engineer needs to determine that possible ordering of quarks.

The downstream tool to bundle quarks together into ions is the 'gluer' which sits before the linker. It will produce application-specific instructions that get stored in memory. Within the hardware, the `Fetch` unit decodes the instructions into hadrons - the symmetrical opposite of the gluer. The `Datapath` unit then executes the quarks.

The Datapath is the essential core of the XaVI processor architecture and defines what is needed of the compiler. Both are fixed. The system architect siigns off the (ion) instruction set (following analysis), the hardware engineer can change the instruction decoding and a software engineer needs to be able to change the gluer (and likely, the linker too). That gluing needs to be made simple enough for the non-expert to do this. The definition of the instruction set follows analysis of representative code. Tools are ultimately needed to help this analysis:
1. To determine which hardware options (with corresponding compiler switches) are best.
2. To detect which hadrons get executed most frequently, and
3. To detect which hadron sequences get executed most frequently (to bind into ions).
For the last item, the (open-source) compiler needs to have the transparency for users to know what hadron sequences will be produced.

(See section 5 for more info.)


## 2.3 Instruction Sets

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



## 2.4 Atomic Instructions

Many 'basic' instructions will actually be formed from multiple atomic hadrons. For example:
- `PUSH Rx` will be implemented as `SUB #1, SP`; `MOVE Rx, (SP)`.
- `POP  Rx` will be implemented as `MOVE (SP), Rx`; `ADD #1, SP`.
- `JSR aaaa` will be implemented as `SUB #1, SP`; `MOVE PC, (SP)`; `MOVE aaaa, PC`.
- `RETN` will be implemented as `MOVE (SP), PC`; `ADD #1, SP` (i.e. `POP PC`).
- `RETI` (return from interrupt) will be implemented as `POP PC`, `POP SF` (4 hadrons). 
And the `Scheduler` also handles interrupts by inserting instructions: `PUSH SF`, `PUSH PC`, `MOVE #0000, PC`.
{Query: do we want the stack to move up or down memory? Answer: top down}

Hadrons part of the same ion will obviously be atomic. A general indicator of whether something should be atomic is if an ion writes to `PC`, `SF` or `SP`. It may be that an instruction needs to be fetched before it can be determined whether a pending interupt can be accepted.


## 2.5 An Instruction Set / Compiler Strategy

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

https://developer.arm.com/documentation/ddi0484/b/CHDCICDF



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



## Copyright

Copyright (c) 2021 Neil Howard <xaviopensource@aol.com>.
All Rights Reserved.
GPLv3 license https://www.gnu.org/licenses/gpl-3.0.en.html
(The licence is expected to become less restrictive at some point in the future.)

 


