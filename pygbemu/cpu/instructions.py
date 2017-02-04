
"""
Instruction map maps to one of:
	an inner map - get another byte of opcode and recurse
	an instruction function which takes (opcode, cpu, mem) and returns t-cycles taken
	None (default) - no such opcode
Register instructions with @instruction(*opcode bytes).
Each byte may be a value or an iterable of values.
eg. to match "10101010 1xxx1001", use @instruction(0xAA, [0x89 + 0x10*i for i in range(8)])
@instruction will handle the sub-mapping above.
"""

from ..utils import iterable


instruction_map = {}


def instruction(*parts):
	if not parts:
		raise TypeError("opcode can not be zero length")
	parts = [part if iterable(part) else (part,) for part in parts]
	def _instruction(fn):
		_register(instruction_map, parts, fn)
		return fn
	return _instruction


def _register(map, parts, fn):
	part, parts = parts[0], parts[1:]
	# base case
	if not parts:
		for variant in part:
			if variant in map:
				raise ValueError("opcode collision with other opcode or prefix")
			map[variant] = fn
		return
	# recurse
	for variant in part:
		submap = map.setdefault(variant, {})
		if callable(submap):
			raise ValueError("opcode collision with opcode prefix")
		_register(submap, parts, fn)


# Helpers for parsing register specification from opcodes

REG_TABLE_8BIT = {
	0: 'B',
	1: 'C',
	2: 'D',
	3: 'E',
	4: 'H',
	5: 'L',
	7: 'A',
}

REG_TABLE_16BIT = {
	0: 'BC',
	1: 'DE',
	2: 'HL',
	3: 'AF',
}

def get_reg(table, cpu, index):
	reg = table[index]
	return getattr(cpu.regs, reg)

def get_reg_8(cpu, index):
	return get_reg(REG_TABLE_8BIT, cpu, index)

def get_reg_16(cpu, index):
	return get_reg(REG_TABLE_16BIT, cpu, index)

def set_reg(table, cpu, index, value):
	reg = table[index]
	setattr(cpu.regs, reg, value)

def set_reg_8(cpu, index, value):
	set_reg(REG_TABLE_8BIT, cpu, index, value)

def set_reg_16(cpu, index, value):
	set_reg(REG_TABLE_16BIT, cpu, index, value)

def reg_values(table, base, shift):
	return [base | (n << shift) for n in table]

def reg_values_8(shift):
	return reg_values(REG_TABLE_8BIT, shift)

def reg_values_16(shift):
	return reg_values(REG_TABLE_16BIT, shift)

def parse_reg_8(shift, code):
	return (code >> shift) & 7

def parse_reg_16(shift, code):
	return (code >> shift) & 3
