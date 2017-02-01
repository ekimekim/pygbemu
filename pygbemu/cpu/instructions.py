
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

instruction_map = {}


def iterable(x):
	try:
		iter(x)
	except TypeError:
		return False
	return True


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
