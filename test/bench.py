"""Pin-level helpers. Only top-level pins are touched, so the same tests run on RTL and the gate netlist."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge, Timer

PERIOD_NS = 40   # relaxed for GLS unit delays; STA covers real timing
SETTLE_NS = 8


class Bench:
    def __init__(self, dut):
        self.dut, self.load, self.run, self.bsel = dut, 0, 0, 0

    def _uio(self):
        self.dut.uio_in.value = self.load | (self.run << 1) | (self.bsel << 2)

    async def start(self):
        d = self.dut
        d.ena.value, d.ui_in.value, d.rst_n.value = 1, 0, 0
        self._uio()
        cocotb.start_soon(Clock(d.clk, PERIOD_NS, unit="ns").start())
        await self.reset()

    async def reset(self, cycles=2):
        d = self.dut
        await FallingEdge(d.clk)
        d.rst_n.value = 0
        self.load = self.run = 0
        self._uio()
        await ClockCycles(d.clk, cycles)
        await FallingEdge(d.clk)
        d.rst_n.value = 1

    async def load_word(self, word, hold=1):
        """prog_load high for `hold` rising edges (loader is rising-edge triggered)."""
        d = self.dut
        await FallingEdge(d.clk)
        d.ui_in.value = word
        self.load = 1
        self._uio()
        await ClockCycles(d.clk, hold)
        await FallingEdge(d.clk)
        self.load = 0
        self._uio()
        await RisingEdge(d.clk)

    async def load_program(self, prog):
        for w in (list(prog) + [0xE0] * 8)[:8]:
            await self.load_word(w)

    async def run_cycles(self, n):
        d = self.dut
        await FallingEdge(d.clk)
        self.run = 1
        self._uio()
        await ClockCycles(d.clk, n)
        await FallingEdge(d.clk)
        self.run = 0
        self._uio()

    async def idle(self, n):
        await ClockCycles(self.dut.clk, n)

    async def read_acc(self):
        """Read both bytes via byte_sel; int() raises on X/Z so unknowns fail the test."""
        d = self.dut
        await FallingEdge(d.clk)
        v = []
        for b in (0, 1):
            self.bsel = b
            self._uio()
            await Timer(SETTLE_NS, "ns")
            v.append(int(d.uo_out.value))
        self.bsel = 0
        self._uio()
        return v[0] | (v[1] << 8)

