

from utils import get_all_subclasses, Blank, Offset


def lookup_cart_type(indicator):
	for cls in {Cart} | get_all_subclasses(Cart):
		if indicator in cls.type_codes:
			return cls
	raise ValueError("Bad cart type indicator: {}".format(indicator))


class InterceptWrites(object):
	"""Implements setitem and getitem, but only allows getitem to underlying
	base, with writes instead being directed to write_fn(addr, value)"""
	def __init__(self, base, write_fn):
		self.base = base
		self.write_fn = write_fn

	def __getitem__(self, index):
		return self.base[index]

	def __setitem__(self, index, value):
		self.write_fn(index, value)


class Cart(object):
	"""Base cart that implements most shared functionality between cart types.
	Defaults to acting like a cart without MBC
	"""
	ROM_BANK_SIZE = 0x4000
	RAM_BANK_SIZE = 0x2000

	RAM_SIZE_MAP = {
		1: 1, # XXX this should only be 2k, not a full 8k bank
		2: 1,
		3: 4,
		4: 16,
	}

	type_codes = 0, 8, 9
	allow_rom_bank_zero = False

	def __init__(self, contents):
		self.rom = InterceptWrites(contents, self.rom_write)
		if len(contents) % self.BANK_SIZE != 0:
			raise ValueError("ROM content not a full bank")
		self.rom_banks = len(contents) / self.ROM_BANK_SIZE
		self.set_rom_bank(1)
		self.ram = [0] * self.ram_banks
		self.set_ram_bank(None)

	@property
	def ram_banks(self):
		return self.RAM_SIZE_MAP.get(self.rom[0x149], 0)

	def set_rom_bank(self, bank):
		if bank == 0 and not self.allow_rom_bank_zero:
			bank = 1
		if bank >= self.rom_banks:
			self.rom_bank = Blank()
		else:
			self.rom_bank = InterceptWrites(Offset(self.rom, self.ROM_BANK_SIZE * bank), self.rom_bank_write)

	def set_ram_bank(self, bank):
		if bank is None or bank >= self.ram_banks:
			self.ram_bank = Blank()
		else:
			self.ram_bank = Offset(self.ram, self.RAM_BANK_SIZE * bank)

	def rom_write(self, index, value):
		pass # ignore writes, but subclasses may trigger bank switching here

	def rom_bank_write(self, index, value):
		# for simplicity, pass through to rom_write after adjusting to original mem addr
		return self.rom_write(index + self.ROM_BANK_SIZE, value)


class MBC1(object):
	type_codes = 1, 2, 3
	memory_mode = 0 # 0 = 128/1 mode, 1 = 32/4 mode
	rom_bank_low = 0 # lower 5 bits of rom bank
	rom_bank_high = 0 # top 2 bits of rom bank

	# XXX enabling/disabling of ram

	def rom_write(self, index, value):
		if index in xrange(0x2000, 0x4000):
			self.rom_bank_low = value % 32
		elif index in xrange(0x6000, 0x8000):
			self.memory_mode = value % 2
		elif index in range(0x4000, 0x6000):
			if self.memory_mode == 0:
				self.rom_bank_high = value % 4
			else:
				self.set_ram_bank(value % 4)
				return
		rom_bank = self.rom_bank_low
		if self.memory_mode == 0:
			rom_bank += self.rom_bank_high << 5
		self.set_rom_bank(rom_bank)


# XXX other carts not implemented
