
"""Cycle-accurate Python model of TCPU-16 (matches RTL: SHL/JMP/JZ use operand[2:0])."""
M16 = 0xFFFF
LOAD, ADD, SUB, SHL, XOR, JMP, JZ, HALT = range(8)


def enc(op, operand=0):
    return ((op & 7) << 5) | (operand & 0x1F)


class Model:
    def __init__(self, prog):
        self.mem = (list(prog) + [enc(HALT)] * 8)[:8]
        self.reset()

    def reset(self):          # memory is NOT cleared (no reset on pmem)
        self.acc, self.pc, self.halted = 0, 0, False

    def step(self):
        if self.halted:
            return
        ins = self.mem[self.pc]
        op, imm, t = ins >> 5, ins & 0x1F, ins & 7
        npc = (self.pc + 1) & 7
        if op == LOAD:   self.acc = imm
        elif op == ADD:  self.acc = (self.acc + imm) & M16
        elif op == SUB:  self.acc = (self.acc - imm) & M16
        elif op == SHL:  self.acc = (self.acc << t) & M16
        elif op == XOR:  self.acc ^= imm
        elif op == JMP:  npc = t
        elif op == JZ:   npc = t if self.acc == 0 else npc
        elif op == HALT: self.halted, npc = True, self.pc
        self.pc = npc

    def run(self, n):
        for _ in range(n):
            self.step()
        return self.acc

