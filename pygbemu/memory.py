
from .utils import Blank


class Proxy(object):
	"""Takes __getitem__ and __setitem__ and converts them into reading/writing a particular
	attribute of a class.
	For example, given p = Proxy(foo, 'bar'), then p[0] returns foo.bar and p[0] = 'baz' sets
	foo.bar = 'baz'.
	"""
	def __init__(self, parent, attr):
		self.parent = parent
		self.attr = attr

	def __getitem__(self, index):
		return getattr(self.parent, self.attr)

	def __setitem__(self, index, value):
		setattr(self.parent, self.attr, value)


class IORegisters(object):
	def __init__(self, system):
		# Maps addresses to IO actions, which are one of either:
		#   A tuple (getter, setter) where either can be None
		#     getter takes no args, setter takes arg value.
		#   An object that takes getitem and setitem, eg. a Proxy()
		self.map = {
			# TODO lots of unimplemented here
			# don't forget, index is lower byte only, ie. 0 not ff00
			0x0f: (lambda: system.cpu.pending_interrupts, None),
			0x40: Proxy(system.display, 'control'),
			0x41: (lambda: system.display.status, None),
			0x42: Proxy(system.display, 'scroll_x'),
			0x43: Proxy(system.display, 'scroll_y'),
		}

	def __getitem__(self, index):
		handler = self.map.get(index, (None, None))
		if isinstance(handler, tuple):
			getter, setter = handler
			return 0 if getter is None else getter()
		else:
			return handler[0]

	def __setitem__(self, index, value):
		handler = self.map.get(index, (None, None))
		if isinstance(handler, tuple):
			getter, setter = handler
			if setter is not None:
				setter(value)
		else:
			handler[0] = value


class Memory(object):
	def __init__(self, system):
		self.system = system
		self.ram = [0] * 0x2000
		self.hram = [0] * 0x7f
		self.ioregs = IORegisters(system)
		blank = Blank()
		# List of (start addr, handler)
		# where handler implements getitem and setitem for address range 0 to (length until end addr)
		# End addr is the next start addr.
		# For example, if the start addr is 0x4000 and the next addr is 0x6000, the handler should
		# handle addresses [0, 0x2000).
		self.memory_map = [
			# ROM Home bank
			(0x0000, system.cart.rom),
			# ROM Switched bank
			(0x4000, system.cart.rom_bank),
			# VRAM
			(0x8000, system.display.tile_data),
			(0x9800, system.display.tile_maps),
			# External bank-switched RAM
			(0xA000, system.cart.ram_bank),
			# Internal RAM
			(0xC000, self.ram),
			# Internal RAM echoed (covers same range as previous)
			(0xE000, self.ram),
			# Sprite RAM
			(0xFE00, system.display.sprite_data),
			# Unused
			(0xFEA0, blank),
			# memory-mapped IO registers
			(0xFF00, self.ioregs),
			# Unused
			(0xFF4C, blank),
			# High RAM (Internal RAM with faster access instructions)
			(0xFF80, self.hram),
			# Interrupt mask register
			(0xFFFF, Proxy(system.cpu, 'interrupt_mask')),
		]

	def resolve(self, addr):
		# pick highest start address below addr
		start_addr, handler = max(
			(start_addr, handler)
			for start_addr, handler in self.memory_map
			if start_addr <= addr
		)
		index = addr - start_addr
		return index, handler

	def __getitem__(self, addr):
		index, handler = self.resolve(addr)
		return handler[index]

	def __setitem__(self, addr, value):
		index, handler = self.resolve(addr)
		handler[index] = value
