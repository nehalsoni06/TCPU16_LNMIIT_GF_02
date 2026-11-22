# Gate-Level Simulation (GLS) — TCPU-16

## 1. Overview

This directory contains the Gate-Level Simulation (GLS) verification artifacts for the synthesized TCPU-16 Tiny Tapeout design targeting the GF180MCU-D process.

GLS verifies the functional behaviour of the synthesized standard-cell netlist using Icarus Verilog and the GF180MCU standard-cell simulation models. Unlike RTL simulation, this verification operates on the mapped gate-level netlist, providing an additional verification stage after synthesis.

The testbench interacts exclusively through the external Tiny Tapeout interface and does not depend on internal RTL hierarchy.

---

## 2. Design Configuration

| Parameter | Value |
|---|---|
| Design | TCPU-16 |
| Top Module | `tt_um_nehalsoni06_tcpu16` |
| PDK | GF180MCU-D |
| Standard-Cell Library | `gf180mcu_fd_sc_mcu7t5v0` |
| Simulator | Icarus Verilog |
| Simulation Engine | `vvp` |
| Testbench | `tb_gls.v` |
| Gate-Level Netlist | `tt_um_nehalsoni06_tcpu16_mapped.v` |

---

## 3. Directory Contents

| File | Description |
|---|---|
| `tb_gls.v` | Verilog gate-level simulation testbench |
| `gls_sim` | Compiled GLS executable |
| `compile.log` | GLS compilation record |
| `simulation.log` | Captured simulation output |
| `tcpu16_gls.vcd` | VCD waveform generated during simulation |

The synthesized netlist used for simulation is located at:

`signoff/standalone_synth/out/tt_um_nehalsoni06_tcpu16_mapped.v`

---

## 4. Verification Approach

The GLS testbench performs the following operations:

1. Initializes the clock and Tiny Tapeout interface signals.
2. Applies reset to the design.
3. Loads the test program through the external programming interface.
4. Releases programming mode.
5. Enables CPU execution.
6. Waits for a bounded number of clock cycles for program execution.
7. Selects the accumulator output bytes using the external interface.
8. Checks the expected lower and upper accumulator bytes.
9. Reports PASS or FAIL conditions.
10. Generates a VCD waveform for waveform inspection and debugging.

All functional checks are performed using externally observable signals.

---

## 5. Test Program

The program loaded into the CPU during GLS is:

| Address | Instruction | Operation |
|---|---|---|
| 0 | `8'h12` | LOAD 18 |
| 1 | `8'h64` | SHL 4 |
| 2 | `8'h23` | ADD 3 |
| 3 | `8'h41` | SUB 1 |
| 4 | `8'h41` | SUB 1 |
| 5 | `8'h41` | SUB 1 |
| 6 | `8'hE0` | HALT |
| 7 | `8'hE0` | Filler |

The program exercises loading a value, shifting, arithmetic addition, subtraction and halt functionality.

The expected accumulator result is:

`16'h0120`

The accumulator is observed through the external interface in two byte selections.

| Output | Expected Value |
|---|---|
| Lower accumulator byte | `8'h20` |
| Upper accumulator byte | `8'h01` |

---

## 6. Complete Testbench Source

The actual testbench used for this GLS run is reproduced below.

> Paste the complete contents of `tb_gls.v` here, verbatim, inside the Verilog code block.

```verilog
// Paste the actual contents of signoff/gls/tb_gls.v here.
```

---

## 7. Reproducing the GLS

### Prerequisites

- Icarus Verilog
- GF180MCU-D PDK
- GF180MCU standard-cell Verilog models
- Synthesized mapped gate-level netlist

### 7.1 Environment Setup

Set the PDK root directory:

```bash
export PDK_ROOT=/home/vsduser/ttsetup/pdk
```

### 7.2 Standard-Cell Model Paths

The GLS uses the GF180MCU-D standard-cell Verilog models.

```bash
MODEL="$PDK_ROOT/ciel/gf180mcu/versions/54435919abffb937387ec956209f9cf5fd2dfbee/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog/gf180mcu_fd_sc_mcu7t5v0.v"

PRIMITIVES="$PDK_ROOT/ciel/gf180mcu/versions/54435919abffb937387ec956209f9cf5fd2dfbee/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog/primitives.v"
```

### 7.3 Compilation

Run the following command from the repository root:

```bash
iverilog -g2012 -DFUNCTIONAL \
-o signoff/gls/gls_sim \
"$PRIMITIVES" \
"$MODEL" \
signoff/standalone_synth/out/tt_um_nehalsoni06_tcpu16_mapped.v \
signoff/gls/tb_gls.v
```

The command compiles the GF180MCU standard-cell models, the synthesized mapped netlist and the GLS testbench into the `gls_sim` executable.

### 7.4 Simulation

Execute the simulation:

```bash
vvp signoff/gls/gls_sim 2>&1 | tee signoff/gls/simulation.log
```

The simulation output is captured in `simulation.log`.

### 7.5 Waveform Inspection

The testbench generates a VCD waveform:

`signoff/gls/tcpu16_gls.vcd`

Open it using GTKWave:

```bash
gtkwave signoff/gls/tcpu16_gls.vcd
```

---

## 8. Simulation Results

The completed gate-level simulation produced the following output:

```text
VCD info: dumpfile signoff/gls/tcpu16_gls.vcd opened for output.
GLS: Program loaded.
PASS: Lower byte = 0x20
PASS: Upper byte = 0x01
================================
GLS PASS: ALL CHECKS PASSED
Cycles waited: 25
================================
signoff/gls/tb_gls.v:128: $finish called at 452000 (1ps)
```

### Result

**GLS PASS — ALL CHECKS PASSED**

The synthesized gate-level netlist successfully executed the test program and produced the expected accumulator output.

| Check | Expected | Observed | Status |
|---|---|---|---|
| Lower accumulator byte | `0x20` | `0x20` | PASS |
| Upper accumulator byte | `0x01` | `0x01` | PASS |
| Simulation completion | Normal termination | `$finish` | PASS |

---

## 9. Verification Scope and Limitations

This GLS verifies the functional behaviour exercised by the testbench on the synthesized GF180MCU-D standard-cell netlist.

The simulation confirms the expected externally observable accumulator result for the executed test program.

This verification does **not** establish:

- Post-layout timing closure.
- Routed timing performance.
- Extracted parasitic analysis.
- Physical Design Rule Check (DRC) completion.
- Layout-versus-schematic (LVS) completion.
- Silicon characterization.

These require completion of the physical implementation, routing, extraction and signoff procedures.

---

## 10. Conclusion

Gate-Level Simulation of the synthesized TCPU-16 GF180MCU-D netlist completed successfully.

The testbench verified the expected accumulator result through the external Tiny Tapeout interface. The simulation completed with all checks passing.

The compilation log, simulation log and waveform are retained to support reproducibility, debugging and further verification.
