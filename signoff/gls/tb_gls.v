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
