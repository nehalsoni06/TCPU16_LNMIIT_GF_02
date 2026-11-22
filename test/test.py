# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

"""TCPU-16 cocotb suite. Pin-level only -> runs unchanged for RTL (make) and GLS (make -B GATES=yes)."""
import os
import random

import cocotb

from bench import Bench
from reference_model import ADD, HALT, JMP, JZ, LOAD, SHL, SUB, XOR, Model, enc

EXAMPLE = [0x12, 0x64, 0x23, 0x41, 0x41, 0x41, 0xE0, 0x00]


async def check(b, prog, cycles, label=""):
    """reset -> load -> run -> compare ACC with the model."""
    await b.reset()
    await b.load_program(prog)
    await b.run_cycles(cycles)
    got, exp = await b.read_acc(), Model(prog).run(cycles)
    assert got == exp, f"{label}: ACC=0x{got:04x}, expected 0x{exp:04x}"


@cocotb.test()
async def test_reset_outputs(dut):
    """After reset: ACC=0 on both bytes, uio_out/uio_oe driven to 0."""
    b = Bench(dut)
    await b.start()
    assert await b.read_acc() == 0
    assert int(dut.uio_out.value) == 0 and int(dut.uio_oe.value) == 0


@cocotb.test()
async def test_example_program(dut):
    """Spec example: ACC=0x0120, low byte 0x20, high byte 0x01."""
    b = Bench(dut)
    await b.start()
    await b.load_program(EXAMPLE)
    await b.run_cycles(12)
    assert await b.read_acc() == 0x0120


@cocotb.test()
async def test_instructions(dut):
    """Each opcode incl. wrap/truncation, jumps, JZ taken/not taken."""
    b = Bench(dut)
    await b.start()
    H = enc(HALT)
    progs = {
        "LOAD max":      ([enc(LOAD, 31), H], 3),
        "ADD":           ([enc(LOAD, 20), enc(ADD, 11), H], 4),
        "ADD wrap":      ([enc(LOAD, 0), enc(SUB, 1), enc(ADD, 2), H], 5),
        "SUB underflow": ([enc(LOAD, 0), enc(SUB, 31), H], 4),
        "SHL 7":         ([enc(LOAD, 31), enc(SHL, 7), H], 4),
        "SHL truncate":  ([enc(LOAD, 31), enc(SHL, 7), enc(SHL, 7), H], 5),
        "SHL 0":         ([enc(LOAD, 9), enc(SHL, 0), H], 4),
        "XOR":           ([enc(LOAD, 0x15), enc(XOR, 0x1F), H], 4),
        "JMP":           ([enc(JMP, 3), enc(LOAD, 1), enc(LOAD, 2), enc(LOAD, 5), H], 5),
        "JZ taken":      ([enc(LOAD, 0), enc(JZ, 4), enc(LOAD, 9), H, enc(LOAD, 7), H], 6),
        "JZ not taken":  ([enc(LOAD, 1), enc(JZ, 4), enc(LOAD, 9), H, enc(LOAD, 7), H], 6),
        "JZ loop":       ([enc(LOAD, 3), enc(SUB, 1), enc(JZ, 4), enc(JMP, 1), H], 12),
    }
    for name, (p, n) in progs.items():
        await check(b, p, n, name)


@cocotb.test()
async def test_halt_freezes(dut):
    """HALT holds ACC/PC however long run stays high."""
    b = Bench(dut)
    await b.start()
    await b.load_program(EXAMPLE)
    await b.run_cycles(8)
    assert await b.read_acc() == 0x0120
    await b.run_cycles(20)
    assert await b.read_acc() == 0x0120


@cocotb.test()
async def test_run_and_ena_gating(dut):
    """No execution with run=0 or ena=0; pause/resume continues where it stopped."""
    b = Bench(dut)
    await b.start()
    await b.load_program(EXAMPLE)
    await b.idle(5)
    assert await b.read_acc() == 0, "executed with run=0"
    dut.ena.value = 0
    await b.run_cycles(5)
    dut.ena.value = 1
    assert await b.read_acc() == 0, "executed with ena=0"
    m = Model(EXAMPLE)
    for n in (2, 3, 4):                       # pause between slices
        await b.run_cycles(n)
        await b.idle(3)
        assert await b.read_acc() == m.run(n)


@cocotb.test()
async def test_reset_keeps_program(dut):
    """Reset clears ACC/PC/halted but program memory is retained."""
    b = Bench(dut)
    await b.start()
    await b.load_program(EXAMPLE)
    await b.run_cycles(4)
    await b.reset()
    assert await b.read_acc() == 0
    await b.run_cycles(8)                     # no reload
    assert await b.read_acc() == 0x0120
    await b.reset()                           # reset after HALT clears halted
    await b.run_cycles(2)
    assert await b.read_acc() == Model(EXAMPLE).run(2)


@cocotb.test()
async def test_reset_mid_run(dut):
    """Reset asserted while running restarts from address 0."""
    b = Bench(dut)
    await b.start()
    await b.load_program(EXAMPLE)
    await b.run_cycles(3)
    await b.reset()
    assert await b.read_acc() == 0
    await b.run_cycles(3)
    assert await b.read_acc() == Model(EXAMPLE).run(3)


@cocotb.test()
async def test_loader(dut):
    """Edge-triggered load (held prog_load writes once), 9th word wraps to 0, load ignored while run=1."""
    b = Bench(dut)
    await b.start()
    # held prog_load = a single write
    await b.load_word(enc(LOAD, 3), hold=4)
    await b.load_word(enc(ADD, 4))
    for _ in range(6):
        await b.load_word(enc(HALT))
    await b.run_cycles(5)
    assert await b.read_acc() == 7
    # wrap: 8 words + 9th overwrites address 0
    await b.reset()
    await b.load_program([enc(LOAD, 5)] + [enc(HALT)] * 7)
    await b.load_word(enc(LOAD, 7))
    await b.run_cycles(2)
    assert await b.read_acc() == 7
    # ignored while run=1: try to overwrite address 0 mid-run (JMP 0 loop re-reads it)
    await b.reset()
    await b.load_program([enc(LOAD, 5), enc(JMP, 0)] + [enc(LOAD, 0)] * 6)
    await b.run_cycles(1)
    b.load = 1
    b.run = 1
    b._uio()
    dut.ui_in.value = enc(LOAD, 31)
    await b.idle(1)
    b.load = 0
    b._uio()
    await b.run_cycles(2)
    assert await b.read_acc() == 5, "program memory written while run=1"


@cocotb.test()
async def test_random_programs(dut):
    """Random 8-word programs vs reference model (seeded)."""
    rng = random.Random(int(os.environ.get("SEED", "16")))
    b = Bench(dut)
    await b.start()
    for i in range(int(os.environ.get("N_RANDOM", "100"))):
        prog = [rng.randrange(256) for _ in range(8)]
        await check(b, prog, rng.randrange(1, 25), f"random #{i} {[hex(x) for x in prog]}")

