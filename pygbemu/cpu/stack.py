
from .instructions import instruction


def push(cpu, mem, value):
	cpu.regs.SP = (cpu.regs.SP - 1) % 2**16
	mem[cpu.regs.SP] = value


def pop(cpu, mem):
	value = mem[cpu.regs.SP]
	cpu.regs.SP = (cpu.regs.SP + 1) % 2**16
	return value


@instruction(0xC5 + i * 0x10 for i in range(4))
def push_qq(code, cpu, mem):
	index = (code & 0x30) >> 8
	regs = ['BC', 'DE', 'HL', 'AF'][index]
	high, low = [cpu.regs.getattr(reg) for reg in regs]
	push(cpu, mem, high)
	push(cpu, mem, low)
	return 16


@instruction(0xC1 + i * 0x10 for i in range(4))
def pop_qq(code, cpu, mem):
	index = (code & 0x30) >> 8
	regs = ['BC', 'DE', 'HL', 'AF'][index]
	low = pop(cpu, mem)
	high = pop(cpu, mem)
	for reg, value in zip(regs, (high, low)):
		cpu.regs.setattr(reg, value)
	return 12
