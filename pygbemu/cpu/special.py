
from .instructions import instruction


@instruction(0x00)
def nop(code, cpu, mem):
	return 4
