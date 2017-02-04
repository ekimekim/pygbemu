
from .instructions import instruction
from .cpu import ADDR_LCD_CONTROL


@instruction(0x00)
def nop(code, cpu, mem):
	return 4


@instruction(0x76)
def halt(code, cpu, mem):
	if cpu.interrupts_enabled:
		cpu.halted = True
	else:
		cpu.halt_quirk = True
	return 4


@instruction(0x10, 0x00)
def stop(code, cpu, mem):
	cpu.stopped = True
	cpu.stopped_prev_lcd_value = mem[ADDR_LCD_CONTROL]
	return 4


@instruction(0xF3)
def di(code, cpu, mem):
	cpu.interrupts_enabled_next = False
	return 4


@instruction(0xFB)
def ei(code, cpu, mem):
	cpu.interrupts_enabled_next = True
	return 4
