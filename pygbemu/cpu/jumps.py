
from instructions import instruction


def jump(cpu, mem, target):
	cpu.regs.PC = target


@instruction(0xE9)
def jump_hl(code, cpu, mem):
	jump(cpu, mem, cpu.regs.HL)
	return 4
