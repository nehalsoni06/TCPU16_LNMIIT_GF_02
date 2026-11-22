# Gate-Level Simulation (GLS) — TCPU-16

## Overview

This directory contains the Gate-Level Simulation (GLS) verification artifacts for the synthesized TCPU-16 Tiny Tapeout design targeting GF180MCU-D.

The GLS testbench verifies the functional behaviour of the mapped standard-cell netlist using Icarus Verilog and the GF180MCU standard-cell models.

## Design Configuration

- **Top module:** `tt_um_nehalsoni06_tcpu16`
- **Technology:** GF180MCU-D
- **Library:** `gf180mcu_fd_sc_mcu7t5v0`
- **Simulator:** Icarus Verilog
- **Mapped netlist:** `signoff/standalone_synth/out/tt_um_nehalsoni06_tcpu16_mapped.v`

## Directory Contents

| File | Description |
|---|---|
| `tb_gls.v` | Gate-level simulation testbench |
| `gls_sim` | Compiled GLS executable |
| `compile.log` | Compilation log |
| `simulation.log` | Simulation output |
| `tcpu16_gls.vcd` | Simulation waveform |

## Verification Approach

The testbench interacts exclusively through the Tiny Tapeout external interface. It loads a program, enables execution, reads the accumulator bytes and checks the expected result.

## Test Program

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

Expected accumulator result: `16'h0120`.

- Lower byte: `8'h20`
- Upper byte: `8'h01`

## Complete Testbench Source

The following source is embedded directly from `tb_gls.v`.
```verilog
`timescale 1ns/1ps
`default_nettype none

module tb_gls;

    reg clk;
    reg rst_n;
    reg ena;
    reg [7:0] ui_in;
    reg [7:0] uio_in;

    wire [7:0] uo_out;
    wire [7:0] uio_out;
    wire [7:0] uio_oe;

    integer errors;
    integer cycles;

    tt_um_nehalsoni06_tcpu16 dut (
        .clk(clk),
        .rst_n(rst_n),
        .ena(ena),
        .ui_in(ui_in),
        .uo_out(uo_out),
        .uio_in(uio_in),
        .uio_out(uio_out),
        .uio_oe(uio_oe)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        $dumpfile("signoff/gls/tcpu16_gls.vcd");
        $dumpvars(0, tb_gls);
    end

    task load_word;
        input [7:0] word;
        begin
            @(negedge clk);
            ui_in = word;
            uio_in[0] = 1'b1;

            @(posedge clk);

            @(negedge clk);
            uio_in[0] = 1'b0;

            @(posedge clk);
        end
    endtask

    initial begin
        rst_n = 0;
        ena = 1;
        ui_in = 0;
        uio_in = 0;
        errors = 0;
        cycles = 0;

        // Reset
        repeat (3) @(posedge clk);
        @(negedge clk);
        rst_n = 1;

        // Load program
        load_word(8'h12); // LOAD 18
        load_word(8'h64); // SHL 4
        load_word(8'h23); // ADD 3
        load_word(8'h41); // SUB 1
        load_word(8'h41); // SUB 1
        load_word(8'h41); // SUB 1
        load_word(8'hE0); // HALT
        load_word(8'hE0); // Filler

        $display("GLS: Program loaded.");

        // Start execution
        @(negedge clk);
        uio_in[1] = 1'b1;

        // Bounded wait for program execution
        repeat (25) begin
            @(posedge clk);
            cycles = cycles + 1;
        end

        @(negedge clk);
        uio_in[1] = 1'b0;

        // Check lower accumulator byte
        uio_in[2] = 1'b0;
        #1;
        if (uo_out !== 8'h20) begin
            $display("FAIL: Lower byte expected 0x20, got 0x%02h", uo_out);
            errors = errors + 1;
        end else begin
            $display("PASS: Lower byte = 0x%02h", uo_out);
        end

        // Check upper accumulator byte
        uio_in[2] = 1'b1;
        #1;
        if (uo_out !== 8'h01) begin
            $display("FAIL: Upper byte expected 0x01, got 0x%02h", uo_out);
            errors = errors + 1;
        end else begin
            $display("PASS: Upper byte = 0x%02h", uo_out);
        end

        // Check unused outputs
        if (uio_out !== 8'h00) begin
            $display("FAIL: uio_out expected 0, got %02h", uio_out);
            errors = errors + 1;
        end

        if (uio_oe !== 8'h00) begin
            $display("FAIL: uio_oe expected 0, got %02h", uio_oe);
            errors = errors + 1;
        end

        if (errors == 0) begin
            $display("================================");
            $display("GLS PASS: ALL CHECKS PASSED");
            $display("Cycles waited: %0d", cycles);
            $display("================================");
            $finish;
        end else begin
            $display("================================");
            $display("GLS FAIL: %0d ERROR(S)", errors);
            $display("================================");
            $fatal(1);
        end
    end

    initial begin
        #10000;
        $display("GLS FAIL: Simulation timeout.");
        $fatal(1);
    end

endmodule

`default_nettype wire
```
