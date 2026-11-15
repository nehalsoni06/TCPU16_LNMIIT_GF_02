# TCPU-16 Feature-Based Verification, Cocotb and GF180MCU

## 1. Introduction

This document describes the feature-based verification of the TCPU-16 processor, including individual Verilog test files, Cocotb-based verification, simulation using Icarus Verilog, waveform analysis using GTKWave, and gate-level verification targeting the GF180MCU technology.

The objective is to verify important processor features independently and ensure that the RTL design behaves correctly under different operating conditions.

The selected features are:

- F05 – Program Loader Edge Detection
- F11 – ADD Carry Across Bytes
- F30 – HALT Freeze

## 2. Feature Test Directory

The feature tests are maintained separately from the main CPU verification environment.

```text
tcpu16/
│
├── rtl/
│   ├── alu.v
│   ├── dec.v
│   ├── loader.v
│   ├── npc.v
│   ├── omux.v
│   ├── pmem.v
│   ├── toy_cpu16.v
│   ├── ops.vh
│   │
│   └── feature_tests/
│       ├── tb_feature_tests.v
│       └── README.md
│
├── src/
│   ├── project.v
│   ├── toy_cpu16.v
│   ├── alu.v
│   ├── dec.v
│   ├── loader.v
│   ├── npc.v
│   ├── omux.v
│   ├── pmem.v
│   └── ops.vh
│
├── test/
│   ├── Makefile
│   ├── test.py
│   ├── tb.v
│   ├── tb.gtkw
│   └── requirements.txt
│
└── README.md
```

The feature testbench is intended to test selected functionality independently of the complete Cocotb test suite.

## 3. Feature F05 – Program Loader Edge Detection

### Objective

Verify that the program loader generates only one memory write event when `prog_load` remains HIGH for multiple clock cycles.

### Design Concept

The loader uses an edge-detection mechanism.

```verilog
wire lp = prog_load & ~plq & ~run;
```

Here:

- `prog_load` is the program loading input.
- `plq` stores the previous value of `prog_load`.
- `run` prevents loading during CPU execution.
- `lp` generates the one-cycle loading pulse.

### Test Procedure

1. Apply reset.
2. Set `prog_load` HIGH.
3. Keep it HIGH for five rising clock edges.
4. Monitor the write enable.
5. Check that only one write event occurs.
6. Verify that the loader address increments only once.

### Expected Result

| Parameter | Expected Behaviour |
|---|---|
| `prog_load` | Remains HIGH |
| Write enable | One active clock event |
| Loader address | Increments once |
| Multiple writes | Not allowed |

### Important Waveform Signals

```text
clk
rst_n
prog_load
run
dut.u_ld.we
dut.u_ld.wa
dut.u_ld.la
```

The waveform should show one write-enable pulse even though `prog_load` remains HIGH.

---

## 4. Feature F11 – ADD Carry Across Bytes

### Objective

Verify that the 16-bit ALU correctly propagates carry from the lower byte to the upper byte during addition.

### Test Program

The following instructions are loaded into program memory.

| Address | Instruction | Machine Code | Expected ACC |
|---|---|---|---|
| 0 | LOAD 31 | `8'h1F` | `16'h001F` |
| 1 | SHL 3 | `8'h63` | `16'h00F8` |
| 2 | ADD 7 | `8'h27` | `16'h00FF` |
| 3 | ADD 1 | `8'h21` | `16'h0100` |

### Explanation

Initially, the accumulator is zero.

**Instruction 1: LOAD 31**

```text
ACC = 0000 + 001F
ACC = 001F
```

**Instruction 2: SHL 3**

```text
ACC = 001F << 3
ACC = 00F8
```

**Instruction 3: ADD 7**

```text
ACC = 00F8 + 0007
ACC = 00FF
```

**Instruction 4: ADD 1**

```text
ACC = 00FF + 0001
ACC = 0100
```

The last instruction produces a carry from the lower byte into the upper byte.

### Expected Result

```text
0000 → 001F → 00F8 → 00FF → 0100
```

### Important Waveform Signals

```text
clk
run
dut.pc
dut.ir
dut.acc
dut.u_alu.an
```

The final accumulator value must be `16'h0100`.

---

## 5. Feature F30 – HALT Freeze

### Objective

Verify that the processor stops executing instructions after encountering the HALT instruction.

### Test Program

| Address | Instruction | Machine Code |
|---|---|---|
| 0 | LOAD 5 | `8'h05` |
| 1 | HALT | `8'hE0` |

### Test Procedure

1. Reset the processor.
2. Load the two instructions.
3. Enable execution using `run`.
4. Allow the LOAD instruction to execute.
5. Allow the HALT instruction to execute.
6. Monitor the `halted` signal.
7. Continue applying clock cycles.
8. Verify that the accumulator and program counter remain unchanged.

### Expected Result

| Signal | Expected Value After HALT |
|---|---|
| `dut.halted` | 1 |
| `dut.acc` | `16'h0005` |
| `dut.pc` | `3'd1` |
| `dut.ir` | `8'hE0` |

The program counter and accumulator should remain unchanged after the processor enters the halted state.

### Important Waveform Signals

```text
clk
run
dut.pc
dut.ir
dut.acc
dut.halted
```

The `halted` signal should become HIGH and remain HIGH until reset.

---

## 6. Verilog Feature Testbench

The feature testbench is used to apply stimulus to the processor and verify its behaviour.

File:

```text
rtl/feature_tests/tb_feature_tests.v
```

The testbench is responsible for:

- Generating the clock.
- Applying reset.
- Loading test instructions.
- Enabling CPU execution.
- Monitoring internal CPU signals.
- Checking expected results.
- Reporting PASS or FAIL for each feature.

### Example Testbench Structure

```verilog
`timescale 1ns/1ps

module tb_feature_tests;

    reg clk;
    reg rst_n;
    reg prog_load;
    reg [7:0] prog_data;
    reg run;

    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test sequence
    initial begin

        rst_n = 0;
        prog_load = 0;
        prog_data = 0;
        run = 0;

        repeat (3) @(posedge clk);
        rst_n = 1;

        // Feature-specific stimulus
        // and assertions are added here.

        #100;
        $finish;
    end

endmodule
```

This is a basic structural example. The actual feature testbench should instantiate the correct CPU module and include the complete test sequences and assertions.

---

## 7. Cocotb Verification

### Introduction

Cocotb is a Python-based co-simulation framework used to verify digital hardware designs written in Verilog or VHDL.

Unlike a traditional Verilog testbench, Cocotb allows test sequences and checking logic to be written in Python.

In this project, Cocotb is used as part of the main CPU verification environment.

### Role of Cocotb

Cocotb performs the following tasks:

1. Generates clock signals.
2. Applies reset conditions.
3. Controls program loading.
4. Enables CPU execution.
5. Monitors internal signals.
6. Checks accumulator and program counter values.
7. Verifies expected processor behaviour.
8. Reports test results.

### Cocotb Verification Flow

```text
        Python Testbench
               |
               v
            Cocotb
               |
               v
       Icarus Verilog
               |
               v
         Verilog RTL
               |
               v
        CPU Simulation
               |
               v
       Result Comparison
               |
               v
         PASS / FAIL
```

### Main Cocotb Files

| File | Purpose |
|---|---|
| `test.py` | Python-based Cocotb tests |
| `Makefile` | Simulation configuration |
| `requirements.txt` | Python dependencies |
| `tb.v` | Simulation top-level testbench |
| `tb.gtkw` | GTKWave signal configuration |

### Install Dependencies

From the test directory:

```bash
cd ~/Desktop/tcpu16/test
pip install -r requirements.txt
```

### Run Cocotb Tests

```bash
make clean
make
```

The Makefile configures the simulator, compiles the RTL, and runs the Cocotb test module.

**Note:** The standalone feature testbench and the Cocotb test suite are separate verification methods unless explicitly integrated into the same simulation flow.

---

## 8. Icarus Verilog Simulation

Icarus Verilog is used to compile and simulate the RTL design.

### Run the Main Simulation

```bash
cd ~/Desktop/tcpu16/test
make clean
make
```

### Run Standalone Feature Testbench

From the feature test directory, compile the testbench with the required RTL source files.

For example:

```bash
cd ~/Desktop/tcpu16/rtl/feature_tests

iverilog -g2012 -I.. -o feature_test.out \
tb_feature_tests.v \
../toy_cpu16.v \
../alu.v \
../dec.v \
../loader.v \
../npc.v \
../omux.v \
../pmem.v
```

Run the simulation:

```bash
vvp feature_test.out
```

The exact compile command may need adjustment if the testbench uses a different module name, file list, or source directory.

---

## 9. Waveform Analysis Using GTKWave

GTKWave is used to visualize the signal transitions generated during simulation.

### Open the Waveform

For the main Cocotb simulation, use the waveform file generated by the Makefile:

```bash
gtkwave tb.fst tb.gtkw
```

For standalone Verilog simulation, enable waveform dumping in the testbench using `$dumpfile` and `$dumpvars`, then open the generated file.

### Signals to Observe

| Signal | Purpose |
|---|---|
| `clk` | Clock |
| `rst_n` | Reset |
| `prog_load` | Program loading |
| `prog_data` | Instruction input |
| `run` | Execution enable |
| `dut.pc` | Program counter |
| `dut.acc` | Accumulator |
| `dut.ir` | Instruction register |
| `dut.halted` | Halt state |
| `dut.u_ld.we` | Loader write enable |
| `dut.u_ld.wa` | Loader write address |
| `dut.u_ld.la` | Loader address |
| `dut.u_alu.an` | ALU output |

The hierarchy names depend on the module instance names in the actual RTL.

---

## 10. GF180MCU Technology

### Introduction

GF180MCU is an open-source semiconductor process design kit used for ASIC design and fabrication.

It provides the technology libraries and design information required to convert RTL into a physical chip layout.

The TCPU-16 project targets the GF180MCU process through the Tiny Tapeout implementation environment.

### Important Components

- Standard-cell libraries
- Technology-specific timing information
- Process design rules
- Physical design information
- Technology mapping files

### Role in This Project

The GF180MCU technology configuration is used during the implementation and gate-level verification stages.

The RTL is synthesized and mapped to the target technology's standard cells.

This allows the design to move from a functional Verilog description toward a physical ASIC implementation.

---

## 11. Gate-Level Simulation

Gate-level simulation checks the behaviour of the synthesized netlist.

Unlike RTL simulation, gate-level simulation uses the technology-mapped representation of the circuit.

The project Makefile supports gate-level simulation through the `GATES` option.

### Run Gate-Level Simulation

```bash
cd ~/Desktop/tcpu16/test

make clean
make GATES=yes
```

### Purpose

Gate-level simulation helps verify:

- Synthesized logic functionality
- Compatibility with technology-specific cells
- Correct operation of the mapped netlist
- Behaviour after synthesis

The gate-level test requires the appropriate synthesized netlist and GF180MCU simulation libraries.

---

## 12. RTL-to-GDS Implementation Flow

The general implementation flow is:

```text
       Verilog RTL
            |
            v
      RTL Verification
            |
            v
         Synthesis
            |
            v
    Technology Mapping
            |
            v
       Floorplanning
            |
            v
         Placement
            |
            v
     Clock Tree Synthesis
            |
            v
          Routing
            |
            v
       Design Checks
            |
            v
        GDS Generation
```

### GitHub Actions

The project uses GitHub Actions to automate verification and implementation tasks.

The GDS workflow uses the Tiny Tapeout action:

```yaml
tt-gds-action@ttsky26d
```

The workflow uses the repository configuration, RTL sources, and target technology setup to run the implementation process.

Successful RTL simulation and successful GDS generation are separate milestones and should be verified independently through their respective workflow results.

---

## 13. Difference Between RTL, Cocotb and GF180MCU

| Component | Role |
|---|---|
| Verilog RTL | Describes processor hardware |
| Feature Testbench | Tests selected hardware features |
| Cocotb | Python-based functional verification |
| Icarus Verilog | Runs RTL and supported gate-level simulations |
| GTKWave | Displays simulation waveforms |
| Yosys | Performs logic synthesis |
| GF180MCU | Provides target semiconductor technology |
| Tiny Tapeout | Provides the ASIC submission and implementation platform |
| GDS | Final physical layout database |

These components work together to take the project from hardware design to verification and physical implementation.

---

## 14. Conclusion

The TCPU-16 feature-based verification environment focuses on three important processor features: program loader edge detection, 16-bit carry propagation, and HALT freeze functionality.

Standalone Verilog testbenches provide targeted testing of these features, while Cocotb provides a Python-based environment for broader functional verification.

Icarus Verilog is used for simulation, and GTKWave provides a visual representation of internal signal behaviour.

The GF180MCU technology setup and Tiny Tapeout implementation flow provide the foundation for synthesizing and preparing the processor for ASIC fabrication.

Together, these tools and verification methods form an RTL-to-ASIC development workflow for the TCPU-16 processor.

## 15. Repository

GitHub:

https://github.com/nehalsoni06/TCPU16_LNMIIT_GF_02

**Design:** TCPU-16

**HDL:** Verilog

**Verification:** Verilog Testbench and Cocotb

**Simulator:** Icarus Verilog

**Waveform Viewer:** GTKWave

**Target Technology:** GF180MCU

**Implementation Platform:** Tiny Tapeout
