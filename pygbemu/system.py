
from cpu import CPU
from memory import Memory
from display import Display
from cart import lookup_cart_type


class System(object):
	def __init__(self, cart_contents):
		self.cart = lookup_cart_type(cart_contents)(self, cart_contents)
		self.display = Display(self)
		self.cpu = CPU(self)
		self.memory = Memory(self)

	def run_one(self):
		self.cpu.run_one()
		# do something with time?
