
from .instructions import instruction, get_reg_16, set_reg_16, parse_reg_16, reg_values_16


def push(cpu, mem, value):
	cpu.regs.SP = (cpu.regs.SP - 1) % 2**16
	mem[cpu.regs.SP] = value


def pop(cpu, mem):
	value = mem[cpu.regs.SP]
	cpu.regs.SP = (cpu.regs.SP + 1) % 2**16
	return value


@instruction(reg_values_16(0xC5, 4))
def push_qq(code, cpu, mem):
	index = parse_reg_16(4, code)
	value = get_reg_16(cpu, index)
	high, low = divmod(value, 256)
	push(cpu, mem, high)
	push(cpu, mem, low)
	return 16


@instruction(reg_values_16(0xC1, 4))
def pop_qq(code, cpu, mem):
	index = parse_reg_16(4, code)
	low = pop(cpu, mem)
	high = pop(cpu, mem)
	value = (high << 256) | low
	set_reg_16(cpu, index, value)
	return 12
