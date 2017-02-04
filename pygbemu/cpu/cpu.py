
import math

from .instructions import instruction_map
from .calls import call


# This is a guess. The Z80 manual describes handling an interrupt
# 'as if it had recycled a restart instruction'. A RST on the GB takes 32 cycles.
INTERRUPT_HANDLE_TIME = 32

ADDR_LCD_CONTROL = 0xFF41


class RegPair(object):
	def __init__(self, desc):
		self.high, self.low = desc
	def __get__(self, instance, cls):
		if instance is None:
			return self
		return (getattr(instance, self.high) << 8) | getattr(instance, self.low)
	def __set__(self, instance, value):
		high, low = divmod(value, 256)
		setattr(instance, self.high, high)
		setattr(instance, self.low, low)


class Registers(object):
	A, F, B, C, D, E, H, L, SP, PC = [0] * 10
	AF = RegPair('AF')
	BC = RegPair('BC')
	DE = RegPair('DE')
	HL = RegPair('HL')


class CPU(object):
	"""
	Represents the CPU itself and associated state.
	cpu.time starts at 0 and is incremented for each clock cycle (T-cycle) an operation would take.
	This allows the user to, at a later time, sleep for the appropriate amount of real time
	to get real time operation, or any other desired effect.
	The original Game Boy CPU ran at 4.19MHz, so to get real-time speed you should delay
	for 0.00000023866 * number of cycles.
	(though frankly, I'll be surprised if this implementation can achieve such speeds)
	You should calculate this number by calling cpu.calc_realtime(num_cycles).
	"""
	INT_VBLANK, INT_LCD_STATUS, INT_TIMER, INT_SERIAL, INT_JOYPAD = range(5)

	def __init__(self, system):
		self.regs = Registers()
		self.time = 0
		self.freq = 4190000 # 4.19MHz
		self.mem = system.memory
		self.interrupts_enabled = False
		self.interrupt_mask = 0
		self.pending_interrupts = 0
		self.halted = False
		self.stopped = False
		self.stopped_prev_lcd_value = None
		# An architecture quirk is that if a 'halt' instruction is executed while interrupts
		# are disabled, the next instruction fetch will not increment PC.
		# Most things deal with this by always folloing halt with nop, but weird tricks may
		# use this so we must emulate it faithfully.
		self.halt_quirk = False
		# DI and EI instructions only take effect after next instruction, so we have a
		# temporary 'do this next' variable for it
		self.interrupts_enabled_next = False

	def calc_realtime(self, cycles):
		return float(cycles) / self.freq

	def fetch(self):
		"""Fetch next byte from the PC, return it and increment PC"""
		value = self.mem[self.regs.PC]
		if self.halt_quirk:
			self.halt_quirk = False
		else:
			self.regs.PC = (self.regs.PC + 1) % 2**16
		return value

	def run_one(self):
		"""Run one step. Increments time appropriately."""

		# halt ends on any interrupt, even if masked out
		if self.halted and self.pending_interrupts:
			self.halted = False

		# stop ends only on keypress
		if self.stopped and self.pending_interrupts & (1 << self.INT_JOYPAD):
			self.stopped = False
			self.mem[ADDR_LCD_CONTROL] = self.stopped_prev_lcd_value

		# this value might change again during run step, so save it
		interrupts_enabled_next = self.interrupts_enabled_next

		self.time += self._run_one()

		self.interrupts_enabled = interrupts_enabled_next

	def _run_one(self):
		if self.interrupts_enabled:
			pending = self.pending_interrupts & self.interrupt_mask
			if pending:
				int_num = int(math.log(pending, 2)) # hacky way to get position of first set bit
				self._handle_interrupt(int_num)
				return INTERRUPT_HANDLE_TIME

		if self.halted or self.stopped:
			return 4

		# no interrupts, proceed with standard fetch, decode, execute
		decoded = instruction_map
		full_opcode = []
		start_addr = self.regs.PC
		while isinstance(decoded, dict):
			opcode = self.fetch()
			full_opcode.append(opcode)
			decoded = decoded.get(opcode)
		if decoded is None:
			raise Exception("invalid opcode {code} at {addr:04x}".format(
				addr=start_addr,
				code=' '.join('{:02x}'.format(code) for code in full_opcode)
			))
		return decoded(full_opcode, self, self.mem)

	def interrupt(self, int_num):
		"""Trigger an interrupt of given number, which may occur immediately or when interrupts
		are next enabled."""
		self.pending_interrupts |= 1 << int_num

	def _handle_interrupt(self, int_num):
		handle_addr = 0x40 + 8 * int_num
		self.interrupts_enabled = False
		self.halted = False
		self.pending_interrupts &= ~(1 << int_num) # clear pending bit
		call(self, self.mem, handle_addr)
